# Model format v1

All fields below are JSON. `schema_version` is exactly `1`. IDs are nonempty
strings unique within their collection. Every entity, relationship, scenario,
and event has an `evidence` object. Source IDs resolve against `sources`.

```json
{
  "schema_version": 1,
  "title": "A system people can explore",
  "description": "Scope, the question answered, and omitted detail.",
  "perspective": "illustrative",
  "sources": [],
  "entities": [],
  "relationships": [],
  "scenarios": []
}
```

`perspective`: `current`, `proposed`, or `illustrative`. It labels the overall
model; evidence records support for individual claims. Never label a proposed
model current. At least one entity is required. Relationships and scenarios may
be empty for a static model.

## Sources and evidence

A source is `{ "id": "s1", "label": "Worker implementation, revision abc123",
"uri": "src/worker.py:42" }`. Use a URL, repository file with line, trace ID,
or `user:conversation` plus a useful label. Sources are displayed as text;
only HTTP(S) URIs become links, opened by explicit user action.

Evidence is `{ "status": "inferred", "note": "Inferred from the producer and
consumer contracts; no runtime trace provided.", "sources": ["s1"] }`.
All three fields are required. Allowed statuses: `observed`, `inferred`,
`illustrative`, `proposed`, `unknown`. Observed claims require at least one
source. Inferred claims should name their basis. Empty source lists are allowed
for illustrative, proposed, and unknown claims. Evidence notes are shown when
users click the item. Do not include secret or personal payload data.

## Entities

Required: `id`, `label`, `kind`, `description`, `evidence`.
Optional: `group` (string), `parent_id` (entity ID), `properties` (JSON object),
`initial_state` (string), `x` and `y` (nonnegative finite coordinates, both or
neither). A parent cannot refer to itself or create a cycle. Coordinates are
relative to the current map scope. `kind` is unrestricted domain language:
service, team, person, stage, agent, store, machine, document, etc.

## Relationships

Required: `id`, `from`, `to` (entity IDs), `label`, `kind`, `description`,
`evidence`. Optional: `properties` (JSON object). Each relationship is directed;
model a response/reverse handoff separately. Several edges between the same
entities and self-edges are supported. `properties` may hold a contract,
transport, owner, data classification, approval rule, or reliability behavior.
A dependency edge is structural; the presence of an edge does not imply execution.

## Scenarios and events

Scenario required: `id`, `label`, `description`, `evidence`, `events` (array).
Optional: `outcome` (string). A scenario can have zero events, which renders as
an empty authored path. Use distinct scenarios for alternatives; array order is
the authored order, not a branching or concurrency execution engine.

Event required: `id` (unique within scenario), `label`, `description`, `evidence`,
and exactly one of `relationship_id` or `entity_id`. A relationship event inherits
its endpoints from that relationship; a local action uses `entity_id`.
Optional: `time_ms` (nonnegative finite number), `payload` (any JSON value),
`state_changes` (object mapping existing entity IDs to string states).
When timestamps are present, they must be nondecreasing in authored order.
Equal timestamps are permitted; the viewer shows authored order without claiming
causality or concurrency. Omit timings when unknown. Playback uses illustrative
pacing controlled by the viewer speed, never recorded wall-clock durations.

Events apply state changes cumulatively from each entity's `initial_state`
(default `unspecified`). Selecting an earlier event reconstructs only that
prefix; reset removes all event effects. Payloads are inspectable examples,
not a packet decoder or an executable contract. Escape and display them as text.

## Layout and scale

The default overview shows root entities. Selecting **Explore inside** on a
parent reveals its immediate children, with a breadcrumb back out. The map only
shows edges whose endpoints are both visible; it does not synthesize parent
edges. Search/group filters and scope never delete data from the model. Scenario
playback shows all participating entities across scopes to keep transfers visible.
The sequence view uses scenario participants and one row per authored event.

For hundreds of entities, create a readable overview and nested subsystems, or
several focused models sharing stable source IDs. This v1 viewer renders SVG,
not a virtualized graph engine. For ambiguous or partial models, put omissions
in `description` and unknown facts in evidence notes.
