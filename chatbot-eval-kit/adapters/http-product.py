"""Send only public eval input to a user-configured product endpoint."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

request=json.load(sys.stdin.buffer)
url=os.environ.get('EVAL_TARGET_URL','')
parsed=urllib.parse.urlparse(url)
if parsed.username or parsed.password or parsed.fragment or not parsed.hostname or (parsed.scheme!='https' and not (parsed.scheme=='http' and parsed.hostname in ('127.0.0.1','localhost','::1'))):
    print(json.dumps({'case_id':request['id'],'error':'EVAL_TARGET_URL cần HTTPS hoặc HTTP loopback.'}));sys.exit(0)
headers={'Content-Type':'application/json'}
class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirects())
if os.environ.get('EVAL_TARGET_API_KEY'):
    headers['Authorization']='Bearer '+os.environ['EVAL_TARGET_API_KEY']
try:
    payload=json.dumps(request,ensure_ascii=False).encode()
    req=urllib.request.Request(url,data=payload,headers=headers,method='POST')
    with opener.open(req,timeout=float(os.environ.get('EVAL_TARGET_TIMEOUT','25'))) as result:
        body=result.read(2_000_001)
        if len(body)>2_000_000:raise ValueError('Response lớn hơn 2 MB.')
        response=json.loads(body)
    if not isinstance(response,dict):raise ValueError('Cần JSON object theo response schema.')
    response.setdefault('case_id',request['id'])
    print(json.dumps(response))
except urllib.error.HTTPError as error:
    print(json.dumps({'case_id':request['id'],'error':f'Product HTTP {error.code}; body omitted.'}))
except Exception as error:
    print(json.dumps({'case_id':request['id'],'error':f'Product request failed ({type(error).__name__}); detail omitted.'}))
