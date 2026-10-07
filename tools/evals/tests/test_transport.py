"""Real loopback transport checks; not product or model quality evaluations."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import shlex
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]

class TransportTests(unittest.TestCase):
    def setUp(self):
        self.received=[]
        received=self.received
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                received.append(body)
                if self.path=='/redirect':
                    self.send_response(302);self.send_header('Location','/unexpected');self.end_headers();return
                self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers()
                self.wfile.write(json.dumps({'case_id':body['id'],'answer':body['question'].upper()}).encode())
            def do_GET(self):
                received.append({'redirect_followed':True});self.send_response(200);self.end_headers()
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
    def env(self,path='/eval'):
        return dict(os.environ,EVAL_TARGET_URL=f'http://127.0.0.1:{self.server.server_port}{path}',EVAL_TARGET_API_KEY='SYNTHETIC-TRANSPORT-CREDENTIAL')
    def test_product_evaluate_strips_reference_before_real_http_request(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);dataset=root/'cases.jsonl'
            dataset.write_text(json.dumps({'id':'local','category':'chatbot','question':'Xin chào','expected_answer':'XIN CHÀO','contexts':[{'id':'gold','text':'DO NOT SEND THIS REFERENCE'}],'expected':{'answer_contains_all':['XIN CHÀO']}})+'\n')
            result=subprocess.run([sys.executable,str(ROOT/'main.py'),'evaluate','--dataset',str(dataset),'--adapter',shlex.join([sys.executable, 'adapters/http-product.py']),'--out',str(root/'run'),'--frameworks','off'],cwd=ROOT,env=self.env(),capture_output=True,text=True,encoding='utf-8',timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(len(self.received),1)
            self.assertEqual(set(self.received[0]),{'id','question','history'})
            report=json.loads((root/'run/results.json').read_text(encoding='utf-8'))
            self.assertEqual(report['summary']['passed'],1)
            self.assertNotIn('SYNTHETIC-TRANSPORT-CREDENTIAL',(root/'run/results.json').read_text(encoding='utf-8'))
    def test_http_adapter_does_not_follow_redirect(self):
        result=subprocess.run([sys.executable,str(ROOT/'adapters/http-product.py')],input=json.dumps({'id':'local','question':'Hello'}),capture_output=True,text=True,encoding='utf-8',env=self.env('/redirect'),timeout=10)
        response=json.loads(result.stdout)
        self.assertIn('HTTP 302',response['error'])
        self.assertEqual(len(self.received),1)

if __name__=='__main__':unittest.main()
