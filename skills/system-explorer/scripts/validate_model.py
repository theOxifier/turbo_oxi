#!/usr/bin/env python3
"""Validate system-explorer v1 models without external dependencies."""
import argparse
import json
import math
from pathlib import Path

STATUSES = {'observed', 'inferred', 'illustrative', 'proposed', 'unknown'}


def validate(model):
    errors = []
    def fail(path, msg):
        errors.append(f'{path}: {msg}')
    def string(obj, field, path, required=True):
        value = obj.get(field)
        if not required and field not in obj:
            return
        if not isinstance(value, str) or not value.strip():
            fail(f'{path}.{field}', 'expected a nonempty string')
    def collection(obj, field, path):
        items = obj.get(field)
        if not isinstance(items, list):
            fail(f'{path}.{field}', 'expected an array')
            return [], set()
        ids = set()
        valid = []
        for i, item in enumerate(items):
            ip = f'{path}.{field}[{i}]'
            if not isinstance(item, dict):
                fail(ip, 'expected an object')
                continue
            valid.append((item, ip))
            string(item, 'id', ip)
            item_id = item.get('id')
            if isinstance(item_id, str):
                if item_id in ids:
                    fail(ip + '.id', f'duplicate ID {item_id!r}')
                ids.add(item_id)
        return valid, ids
    def reference(value, ids, path):
        if not isinstance(value, str) or value not in ids:
            fail(path, f'unknown reference {value!r}')
    def evidence(obj, path, source_ids):
        ev = obj.get('evidence')
        if not isinstance(ev, dict):
            fail(path + '.evidence', 'expected an evidence object')
            return
        if not isinstance(ev.get('status'), str) or ev['status'] not in STATUSES:
            fail(path + '.evidence.status', 'invalid evidence status')
        string(ev, 'note', path + '.evidence')
        refs = ev.get('sources')
        if not isinstance(refs, list):
            fail(path + '.evidence.sources', 'expected an array')
            return
        for i, ref in enumerate(refs):
            reference(ref, source_ids, f'{path}.evidence.sources[{i}]')
        if ev.get('status') == 'observed' and not refs:
            fail(path + '.evidence.sources', 'observed claims require a source')
    def base(obj, path):
        for key in ('label', 'description'):
            string(obj, key, path)
        if 'properties' in obj and not isinstance(obj['properties'], dict):
            fail(path + '.properties', 'expected an object')
    def number(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0

    if not isinstance(model, dict):
        return ['model: expected an object']
    if type(model.get('schema_version')) is not int or model['schema_version'] != 1:
        fail('model.schema_version', 'expected integer 1')
    string(model, 'title', 'model')
    string(model, 'description', 'model')
    if model.get('perspective') not in ('current', 'proposed', 'illustrative'):
        fail('model.perspective', 'expected current, proposed, or illustrative')
    sources, source_ids = collection(model, 'sources', 'model')
    for obj, path in sources:
        string(obj, 'label', path)
        string(obj, 'uri', path)
    entities, entity_ids = collection(model, 'entities', 'model')
    if not entities:
        fail('model.entities', 'at least one entity required')
    parents = {}
    for obj, path in entities:
        base(obj, path)
        string(obj, 'kind', path)
        evidence(obj, path, source_ids)
        for key in ('group', 'initial_state'):
            string(obj, key, path, required=False)
        if 'parent_id' in obj:
            reference(obj['parent_id'], entity_ids, path + '.parent_id')
            if isinstance(obj.get('id'), str) and isinstance(obj['parent_id'], str):
                parents[obj['id']] = obj['parent_id']
        if ('x' in obj) != ('y' in obj):
            fail(path, 'coordinates require both x and y')
        for key in ('x', 'y'):
            if key in obj and not number(obj[key]):
                fail(path + '.' + key, 'expected a nonnegative finite number')
    for eid in parents:
        seen = set()
        cursor = eid
        while cursor in parents:
            if cursor in seen:
                fail('model.entities', f'parent cycle involving {eid!r}')
                break
            seen.add(cursor)
            cursor = parents[cursor]
    relationships, relationship_ids = collection(model, 'relationships', 'model')
    for obj, path in relationships:
        base(obj, path)
        string(obj, 'kind', path)
        evidence(obj, path, source_ids)
        for key in ('from', 'to'):
            reference(obj.get(key), entity_ids, path + '.' + key)
    scenarios, _ = collection(model, 'scenarios', 'model')
    for obj, path in scenarios:
        base(obj, path)
        evidence(obj, path, source_ids)
        string(obj, 'outcome', path, required=False)
        events, _ = collection(obj, 'events', path)
        previous_time = -1
        for event, ep in events:
            base(event, ep)
            evidence(event, ep, source_ids)
            if ('entity_id' in event) == ('relationship_id' in event):
                fail(ep, 'expected exactly one of entity_id or relationship_id')
            if 'entity_id' in event:
                reference(event['entity_id'], entity_ids, ep + '.entity_id')
            if 'relationship_id' in event:
                reference(event['relationship_id'], relationship_ids, ep + '.relationship_id')
            if 'time_ms' in event:
                t = event['time_ms']
                if not number(t):
                    fail(ep + '.time_ms', 'expected a nonnegative finite number')
                elif t < previous_time:
                    fail(ep + '.time_ms', 'timestamps must be nondecreasing')
                else:
                    previous_time = t
            changes = event.get('state_changes', {})
            if not isinstance(changes, dict):
                fail(ep + '.state_changes', 'expected an object')
            else:
                for target, state in changes.items():
                    reference(target, entity_ids, ep + '.state_changes')
                    if not isinstance(state, str) or not state.strip():
                        fail(ep + '.state_changes.' + target, 'expected a nonempty state string')
    return errors


def load_model(path):
    def reject_constant(value):
        raise ValueError(f'non-JSON numeric constant {value}')
    def reject_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON key {key!r}')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      parse_constant=reject_constant, object_pairs_hook=reject_duplicates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    args = parser.parse_args()
    try:
        errors = validate(load_model(args.model))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'{exc}\n')
    if errors:
        parser.exit(1, '\n'.join(errors) + '\n')
    print(f'Valid system-explorer v1 model: {args.model}')


if __name__ == '__main__':
    main()
