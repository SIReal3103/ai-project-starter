"""Plain chat-completions adapter; no fictitious RAG or agent telemetry."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

request=json.load(sys.stdin.buffer)
base=os.environ.get('EVAL_TARGET_BASE_URL','').rstrip('/')
model=os.environ.get('EVAL_TARGET_MODEL')
key=os.environ.get('EVAL_TARGET_API_KEY')
parsed=urllib.parse.urlparse(base)
valid_url=bool(parsed.hostname) and not (parsed.username or parsed.password or parsed.query or parsed.fragment) and (parsed.scheme=='https' or (parsed.scheme=='http' and parsed.hostname in ('localhost','127.0.0.1','::1')))
if not (valid_url and key and model):
    print(json.dumps({'case_id':request['id'],'error':'Cần EVAL_TARGET_BASE_URL, EVAL_TARGET_MODEL, EVAL_TARGET_API_KEY; chưa gọi model.'}));sys.exit(0)
system=os.environ.get('EVAL_TARGET_SYSTEM_PROMPT','Bạn là trợ lý trả lời bằng tiếng Việt. Không bịa dữ liệu không được cung cấp. Hỏi lại nếu thiếu thông tin.')
messages=[{'role':'system','content':system}]
messages.extend({'role':m['role'],'content':m['content']} for m in request.get('history',[]) if m.get('role') in ('user','assistant') and isinstance(m.get('content'),str))
messages.append({'role':'user','content':request['question']})
payload={'model':model,'messages':messages,'max_tokens':int(os.environ.get('EVAL_TARGET_MAX_TOKENS','700'))}
class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirects())
try:
    req=urllib.request.Request(base+'/chat/completions',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
    with opener.open(req,timeout=25) as result:
        body=result.read(2_000_001)
        if len(body)>2_000_000:raise ValueError('Response too large')
        raw=json.loads(body)
    content=raw['choices'][0]['message'].get('content')
    if not isinstance(content,str):raise ValueError('No text output')
    print(json.dumps({'case_id':request['id'],'answer':content,'usage':raw.get('usage',{}),'provider_metadata':{'mode':'live-chat','model':model,'telemetry':'text-only; no retrieval/tool/guardrail trace supplied'}}))
except urllib.error.HTTPError as error:
    print(json.dumps({'case_id':request['id'],'error':f'Provider HTTP {error.code}; body omitted.'}))
except Exception as error:
    print(json.dumps({'case_id':request['id'],'error':f'Provider error {type(error).__name__}; detail omitted.'}))
