import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('qa_render', HERE/'render.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class AcceptanceReportTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((HERE/'template-data.json').read_text())

    def test_unrun_template_never_implies_pass_rate(self):
        renderer.validate(self.data)
        totals = renderer.summarize(self.data['cases'])
        self.assertEqual(totals['executed'], 0)
        self.assertIsNone(totals['pass_rate'])
        self.assertEqual(totals['pending'], len(self.data['cases']))

    def test_blocked_and_not_applicable_have_correct_denominators(self):
        totals = renderer.summarize([{'status': s} for s in ['pass','fail','blocked','not_run','na']])
        self.assertEqual(totals['planned'], 4)
        self.assertEqual(totals['executed'], 2)
        self.assertEqual(totals['pass_rate'], .5)

    def test_measurement_does_not_imply_accepted_threshold(self):
        row = copy.deepcopy(self.data['metrics'][0])
        row.update(value='1.0', evidence='run/metric.json', sample_size=10, status='not_run')
        self.assertEqual(renderer.metric_status(row), 'Đã đo · Chưa chốt ngưỡng')
        row['status'] = 'pass'
        self.data['mode'] = 'evidence'
        self.data['metrics'][0] = row
        with self.assertRaisesRegex(ValueError, 'chưa chốt ngưỡng'):
            renderer.validate(self.data)

    def test_case_cannot_pass_without_evidence_or_with_failed_assertion(self):
        self.data['mode'] = 'evidence'
        case = self.data['cases'][0]
        case['status'] = 'pass'
        with self.assertRaisesRegex(ValueError, 'actual và evidence'):
            renderer.validate(self.data)
        case.update(actual='Observed state', evidence=['run/state.json'])
        case['checks'][0]['status'] = 'fail'
        with self.assertRaisesRegex(ValueError, 'không thể đạt'):
            renderer.validate(self.data)

    def test_untrusted_output_is_escaped_in_standalone_html(self):
        attack = '</script><script>alert("x")</script>'
        self.data['cases'][0]['actual'] = attack
        doc = renderer.render_html(self.data)
        self.assertNotIn(attack, doc)
        self.assertIn('&lt;script&gt;', doc)
        self.assertEqual(doc.count('<script>'), 1)

    def test_template_rejects_fabricated_nested_results(self):
        self.data['cases'][0]['checks'][0].update(status='pass', actual='Invented success')
        with self.assertRaisesRegex(ValueError, 'template không được chứa kết quả check'):
            renderer.validate(self.data)

    def test_malformed_root_and_nested_check_are_validation_errors(self):
        with self.assertRaises(ValueError):
            renderer.validate([])
        self.data['mode'] = 'evidence'
        self.data['cases'][0].update(status='pass', actual='Observed', evidence=['trace.json'], checks=[None])
        with self.assertRaisesRegex(ValueError, 'check không hợp lệ'):
            renderer.validate(self.data)

    def test_zero_is_a_result_and_numbered_steps_are_not_duplicated(self):
        self.assertEqual(renderer.content(0), '0')
        self.assertIn('<li>Do the step</li>', renderer.items(['1. Do the step'], ordered=True))

    def test_frozen_example_preserves_audited_llm_outcome(self):
        path = HERE/'example-data.json'
        if not path.exists():
            self.skipTest('Example content has not been generated yet.')
        example = json.loads(path.read_text())
        renderer.validate(example)
        llm_ids={f'{prefix}{i:02}' for prefix,n in [('C',8),('R',8),('G',4),('J',4)] for i in range(1,n+1)}
        cases = [c for c in example['cases'] if c['id'] in llm_ids]
        self.assertEqual(len(cases), 24)
        self.assertEqual(sum(c['status']=='pass' for c in cases), 6)
        self.assertEqual(next(c for c in cases if c['id']=='R04')['status'], 'fail')
        self.assertTrue(all(c['status'] not in ('pass','fail') for c in example['cases'] if c['group']=='agent'))


if __name__ == '__main__':
    unittest.main()
