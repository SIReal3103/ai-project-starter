import copy
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scoring import score_case,validate_cases
from main import adapter_input,controls,protected_response

class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.case={'id':'sample','category':'rag','question':'Giờ mở cửa?','expected_answer':'08:00 [a]',
                   'contexts':[{'id':'a','text':'Giờ mở cửa 08:00'},{'id':'b','text':'Nguồn khác'}],
                   'expected':{'answer_contains_all':['08:00'],'expected_context_ids':['a'],'required_citation_ids':['a'],
                               'required_guardrail_action':'allow','forbidden_tools':['send_email'],
                               'tool_calls':[{'name':'search','arguments':{'q':'giờ'}}],'max_tool_calls':1,'answer_not_contains':['PRIVATE-DEMO']}}
        self.response={'case_id':'sample','answer':'08:00 [a]','retrieved_contexts':[{'id':'a','text':'Giờ mở cửa 08:00'}],
                       'citations':['a'],'tool_calls':[{'name':'search','arguments':{'q':'giờ'}}],'guardrail':{'action':'allow'},'latency_ms':1}
    def test_complete_response_passes(self):
        self.assertEqual(score_case(self.case,self.response,'demo')['status'],'pass')
    def test_invented_source_fails_even_when_answer_contains_fact(self):
        self.response['citations']=['a','invented']
        self.assertEqual(score_case(self.case,self.response,'demo')['status'],'fail')
    def test_wrong_tool_arguments_fail(self):
        self.response['tool_calls'][0]['arguments']={'q':'sai'}
        self.assertEqual(score_case(self.case,self.response,'demo')['status'],'fail')
    def test_no_guardrail_telemetry_does_not_pass_refusal_gate(self):
        self.case['expected']['must_refuse']=False
        self.response.pop('guardrail')
        self.assertEqual(score_case(self.case,self.response,'demo')['status'],'fail')
    def test_duplicate_context_cannot_inflate_retrieval(self):
        self.response['retrieved_contexts']*=2
        result=score_case(self.case,self.response,'demo')
        self.assertEqual(result['status'],'fail')
        self.assertLessEqual(result['retrieval_metrics']['ndcg_at_k'],1)
    def test_missing_response_is_error(self):
        self.assertEqual(score_case(self.case,{'error':'timeout'},'demo')['status'],'error')
    def test_adapter_never_receives_oracles(self):
        self.case['tags']=['gold']; self.case['history']=[]
        request=adapter_input(self.case)
        self.assertEqual(set(request),{'id','question','history'})
        self.assertNotIn('contexts',request)
        demo=adapter_input(self.case,True)
        self.assertIn('contexts',demo)
        self.assertNotIn('expected',demo)
    def test_invalid_oracle_does_not_silently_pass(self):
        self.case['expected']={'unsupported_gate':True}
        self.assertTrue(validate_cases([self.case]))
    def test_no_empty_oracles(self):
        self.case['expected']={'answer_contains_all':[]}
        self.assertTrue(validate_cases([self.case]))
    def test_false_json_flag_is_not_a_check(self):
        self.case['expected']={'output_json':False}
        self.assertTrue(validate_cases([self.case]))
    def test_zero_calls_is_a_real_contract(self):
        self.case['expected']={'tool_calls':[]}
        self.assertFalse(validate_cases([self.case]))
    def test_missing_id_rejected(self):
        self.case.pop('id')
        self.assertTrue(validate_cases([self.case]))
    def test_invalid_guardrail_action_cannot_count_as_allow(self):
        self.case['expected']={'must_refuse':False}
        self.response['guardrail']={'action':'NOT-A-VALID-ACTION'}
        self.assertEqual(score_case(self.case,self.response,'demo')['status'],'fail')
    def test_missing_tool_trace_cannot_prove_no_calls(self):
        self.case['expected']={'tool_calls':[]};self.response.pop('tool_calls')
        self.assertEqual(score_case(self.case,self.response,'demo')['status'],'fail')
    def test_configured_secret_is_redacted_and_flagged_before_scoring(self):
        with patch.dict('os.environ',{'EVAL_TARGET_API_KEY':'SYNTHETIC-AUTH-ONLY'}):
            self.response['debug']={'header':'Bearer SYNTHETIC-AUTH-ONLY'}
            protected=protected_response(self.response)
        self.assertNotIn('SYNTHETIC-AUTH-ONLY',str(protected))
        self.assertEqual(score_case(self.case,protected,'demo')['status'],'fail')
    def test_duplicate_ids_rejected(self):
        self.assertTrue(validate_cases([self.case,self.case]))
    def test_negative_controls_detect_corruption(self):
        results=controls([self.case],[self.response])
        self.assertTrue(all(r['detected'] for r in results if r['status']!='not_run'))
    def test_exact_match_is_not_casefold_match(self):
        self.case['tags']=['exact-match'];self.case['expected_answer']='YES';self.response['answer']='yes'
        result=score_case(self.case,self.response,'demo')
        self.assertTrue(any(x['name']=='exact_match' and x['status']=='fail' for x in result['checks']))
    def test_json_rejects_literal_even_if_parseable(self):
        self.case['expected']={'output_json':True};self.response['answer']='42'
        self.assertEqual(score_case(self.case,self.response,'demo')['status'],'fail')

if __name__=='__main__':unittest.main()
