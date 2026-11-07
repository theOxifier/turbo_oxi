import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from render import render
from validate_model import load_model, validate


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.model = load_model(ROOT / 'examples/software-system.json')

    def test_examples_and_static_model(self):
        for path in (ROOT / 'examples').glob('*.json'):
            self.assertEqual(validate(load_model(path)), [], path)
        self.model['scenarios'] = []
        self.model['relationships'] = []
        self.assertEqual(validate(self.model), [])

    def test_dangling_event_and_state_targets(self):
        ev = self.model['scenarios'][0]['events'][0]
        ev['relationship_id'] = 'missing-edge'
        ev['state_changes'] = {'missing-entity': 'done'}
        errors = validate(self.model)
        self.assertTrue(any('relationship_id' in e for e in errors))
        self.assertTrue(any('state_changes' in e for e in errors))

    def test_cycle_and_duplicate_identity(self):
        self.model['entities'][0]['parent_id'] = 'api'
        self.model['entities'][1]['parent_id'] = 'client'
        self.model['entities'].append(copy.deepcopy(self.model['entities'][0]))
        errors = validate(self.model)
        self.assertTrue(any('cycle' in e for e in errors))
        self.assertTrue(any('duplicate ID' in e for e in errors))

    def test_observed_claim_requires_resolved_source(self):
        evidence = self.model['entities'][0]['evidence']
        evidence['status'] = 'observed'
        self.assertTrue(any('require a source' in e for e in validate(self.model)))
        evidence['sources'] = ['missing-source']
        self.assertTrue(any('unknown reference' in e for e in validate(self.model)))
        self.model['sources'] = [{'id':'missing-source','label':'Test fixture','uri':'example.txt:1'}]
        self.assertEqual(validate(self.model), [])

    def test_events_have_one_target_and_monotonic_time(self):
        first, second = self.model['scenarios'][0]['events'][:2]
        first['time_ms'] = 50
        second['time_ms'] = 20
        first['entity_id'] = 'client'
        errors = validate(self.model)
        self.assertTrue(any('exactly one' in e for e in errors))
        self.assertTrue(any('nondecreasing' in e for e in errors))

    def test_invalid_types_report_errors(self):
        self.model['entities'][0]['evidence']['status'] = []
        self.model['entities'][0]['x'] = True
        self.model['scenarios'][0]['events'][0]['state_changes'] = {'client':None}
        self.assertGreaterEqual(len(validate(self.model)), 3)
        self.assertTrue(validate([]))

    def test_render_rejects_invalid_model(self):
        self.model['relationships'][0]['to'] = 'missing'
        with self.assertRaises(ValueError):
            render(self.model)

    def test_script_termination_is_escaped_without_changing_data(self):
        attack = '</script><script>window.injected=true</script><b>&test</b>'
        self.model['title'] = attack
        html = render(self.model)
        self.assertNotIn(attack, html)
        data = html.split('<script type="application/json" id="model-data">',1)[1].split('</script>',1)[0]
        self.assertEqual(json.loads(data)['title'], attack)

    def test_duplicate_keys_and_nan_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            for value in ['{"id":1,"id":2}', '{"time_ms":NaN}']:
                path.write_text(value)
                with self.assertRaises(ValueError):
                    load_model(path)


if __name__ == '__main__':
    unittest.main()
