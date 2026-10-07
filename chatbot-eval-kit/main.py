#!/usr/bin/env python3
"""Portable local eval runner: example, external product, or recorded responses."""
import argparse
import copy
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

from scoring import score_case, validate_cases

HERE=Path(__file__).resolve().parent

def read_cases(path):
    cases=[json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]
    errors=validate_cases(cases)
    if errors:
        raise ValueError('\n'.join(errors))
    return cases

def adapter_input(case, include_contexts=False):
    # Never expose expected_answer, expected, tags, gold IDs or reference outputs.
    request={key:case.get(key,default) for key,default in [('id',''),('question',''),('history',[])]}
    if 'input' in case:
        request['input']=case['input']
    if include_contexts:
        request['contexts']=case.get('contexts',[])
    return request

def clean_environment(judge=False):
    env=dict(os.environ)
    # An explicit runtime must not inherit packages from the caller's Python setup.
    for name in ('PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV', 'CONDA_PREFIX'):
        env.pop(name, None)
    env['PYTHONNOUSERSITE']='1'
    env['PYTHONIOENCODING']='utf-8'
    for name in list(env):
        if any(piece in name.upper() for piece in ('API_KEY','ACCESS_TOKEN','AUTH_TOKEN')):
            if name != ('EVAL_JUDGE_API_KEY' if judge else 'EVAL_TARGET_API_KEY'):
                env.pop(name,None)
    env.update(RAGAS_DO_NOT_TRACK='true',DEEPEVAL_TELEMETRY_OPT_OUT='1',ANONYMIZED_TELEMETRY='false')
    return env

def safe_message(value):
    value=str(value)
    for key,val in os.environ.items():
        if any(p in key.upper() for p in ('API_KEY','ACCESS_TOKEN','AUTH_TOKEN')) and val:
            value=value.replace(val,'[REDACTED]')
    return value[:400]

def redact_artifact(value):
    """Preserve full useful text while redacting configured credentials recursively."""
    secrets=[v for k,v in os.environ.items() if v and any(piece in k.upper() for piece in ('API_KEY','ACCESS_TOKEN','AUTH_TOKEN'))]
    def redact(item):
        if isinstance(item,str):
            for secret in secrets:item=item.replace(secret,'[REDACTED]')
            return item
        if isinstance(item,list):return [redact(x) for x in item]
        if isinstance(item,dict):return {redact(str(k)):redact(v) for k,v in item.items()}
        return item
    return redact(value)

def protected_response(response):
    cleaned=redact_artifact(response)
    if cleaned != response and isinstance(cleaned,dict):cleaned['configured_secret_detected']=True
    return cleaned

def load_module(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def call_adapter(case, args, demo_module, remaining):
    request=adapter_input(case,include_contexts=args.command=='demo')
    start=time.perf_counter()
    try:
        if demo_module:
            response=demo_module.respond(request)
        else:
            process=subprocess.run(shlex.split(args.adapter),input=json.dumps(request,ensure_ascii=False),capture_output=True,text=True,encoding='utf-8',timeout=min(args.timeout,remaining),cwd=HERE,env=clean_environment())
            if process.returncode:
                return {'case_id':case['id'],'error':f'Adapter exit {process.returncode}; stderr không đưa vào báo cáo để tránh dữ liệu nhạy cảm.'}
            if len(process.stdout)>2_000_000:
                return {'case_id':case['id'],'error':'Response vượt 2 MB.'}
            response=json.loads(process.stdout)
        if not isinstance(response,dict):
            raise ValueError('Adapter phải trả JSON object.')
        response.setdefault('case_id',case['id'])
        response['latency_ms']=round((time.perf_counter()-start)*1000,3)
        return response
    except subprocess.TimeoutExpired:
        return {'case_id':case['id'],'error':f'Timeout sau {args.timeout} giây.'}
    except Exception as error:
        return {'case_id':case['id'],'error':safe_message(f'{type(error).__name__}: {error}')}

def controls(cases, responses):
    """Mutations are isolated scorer checks and never part of product scores."""
    rows=[]
    definitions=[
        ('empty-answer','Output rỗng phải bị bắt',lambda c:True,lambda r:r.update(answer=''),'output_nonempty'),
        ('wrong-fact','Bỏ thông tin bắt buộc phải bị bắt',lambda c:bool(c['expected'].get('answer_contains_all')),lambda r:r.update(answer='Thông tin khác hoàn toàn.'),'answer_required_facts'),
        ('missing-context','Không truy hồi gold context phải bị bắt',lambda c:bool(c['expected'].get('expected_context_ids')),lambda r:r.update(retrieved_contexts=[]),'retrieval_recall_at_k'),
        ('invented-citation','Citation không tồn tại phải bị bắt',lambda c:bool(c['expected'].get('required_citation_ids')),lambda r:r.update(citations=['NONEXISTENT-DEMO-SOURCE']),'citation_validity'),
        ('wrong-tool-arguments','Tool sai arguments phải bị bắt',lambda c:bool(c['expected'].get('tool_calls')),lambda r:r.update(tool_calls=[{'name':'wrong_tool','arguments':{}}]),'tool_sequence_and_arguments'),
        ('unauthorized-tool','Tool bị cấm phải bị bắt',lambda c:bool(c['expected'].get('forbidden_tools')),None,'tool_allowlist'),
        ('forbidden-disclosure','Output chứa chuỗi cấm phải bị bắt',lambda c:bool(c['expected'].get('answer_not_contains')),None,'output_forbidden_content'),
        ('guardrail-bypass','Guardrail sai action phải bị bắt',lambda c:bool(c['expected'].get('required_guardrail_action')),None,'guardrail_action'),
    ]
    lookup={r.get('case_id'):r for r in responses}
    for ident,description,predicate,mutate,check_name in definitions:
        case=next((c for c in cases if predicate(c) and not lookup.get(c['id'],{}).get('error')),None)
        if case is None:
            rows.append({'id':ident,'description':description,'detected':None,'status':'not_run'});continue
        modified=copy.deepcopy(lookup[case['id']])
        if mutate:mutate(modified)
        elif ident=='unauthorized-tool':modified['tool_calls']=[{'name':case['expected']['forbidden_tools'][0],'arguments':{}}]
        elif ident=='forbidden-disclosure':modified['answer']=case['expected']['answer_not_contains'][0]
        elif ident=='guardrail-bypass':modified['guardrail']={'action':'refuse' if case['expected']['required_guardrail_action']!='refuse' else 'allow'}
        scored=score_case(case,modified,'negative-control')
        detected=any(c['name']==check_name and c['status']=='fail' for c in scored['checks'])
        rows.append({'id':ident,'description':description,'detected':detected,'status':'pass' if detected else 'fail','question':case['question'],'expected_answer':case['expected_answer'],'answer':modified.get('answer',''),'checks':[x for x in scored['checks'] if x['status']=='fail']})
    return rows

def framework_python(name):
    """Use an explicitly configured interpreter or this kit's own environment only."""
    configured=os.environ.get(f'EVAL_{name.upper()}_PYTHON')
    if configured:
        # Relative explicit paths resolve against the invoking working directory.
        return str(Path(configured).expanduser().absolute())
    executable=Path('Scripts/python.exe') if os.name=='nt' else Path('bin/python')
    candidate=HERE/f'.venv-{name}'/executable
    return str(candidate) if candidate.is_file() else None


def frameworks(cases,responses,out,args):
    data=out/'framework-input.json'
    data.write_text(json.dumps(redact_artifact({'cases':cases,'responses':responses}),ensure_ascii=False,indent=2),encoding='utf-8')
    results=[]
    for name in ('ragas','deepeval'):
        python=framework_python(name) if args.frameworks!='off' else None
        if args.frameworks=='off' or not python:
            results.append({'framework':name,'version':None,'mode':'judge' if args.judge else 'offline','results':[],'errors':['Đã yêu cầu judge nhưng thiếu interpreter.'] if args.judge else [],'status':'error' if args.judge else 'not_run','reason':'Framework tắt hoặc chưa cấu hình interpreter.'});continue
        dest=out/f'{name}.json'
        cmd=[python,str(HERE/'integrations/framework_metrics.py'),'--framework',name,'--input',str(data),'--output',str(dest)]
        if args.judge:cmd+=['--with-judge','--max-cases',str(args.judge_max_cases)]
        try:
            remaining=args.deadline-time.monotonic()
            if remaining<=0:raise TimeoutError('Hết budget tổng trước khi chấm framework.')
            p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=min(args.framework_timeout,remaining),env=clean_environment(judge=True),cwd=HERE)
            # Framework logs remain local, stripped of configured secrets.
            (out/f'{name}.log').write_text(safe_message(p.stdout)+'\n'+safe_message(p.stderr),encoding='utf-8')
            if dest.exists():
                record=json.loads(dest.read_text(encoding='utf-8'))
                record['exit_code']=p.returncode
            else:
                record={'framework':name,'mode':'judge' if args.judge else 'offline','results':[],'errors':[f'Không có output framework (exit {p.returncode}).']}
        except Exception as error:
            record={'framework':name,'mode':'judge' if args.judge else 'offline','results':[],'errors':[safe_message(error)]}
        results.append(record)
    if args.judge and not any(x.get('status')=='scored' and x.get('metric') not in ('exact_match','non_llm_context_recall','non_llm_context_precision_with_reference') for f in results for x in f.get('results',[])):
        results.append({'framework':'judge-completion','mode':'judge','results':[],'errors':['Đã yêu cầu judge nhưng không có phép chấm LLM nào thành công.'],'status':'error'})
    return results

def coverage_matrix(cases, judged):
    tags={tag for c in cases for tag in c.get('tags',[])}
    rows=[
        ('Chatbot: đúng nội dung, định dạng, làm rõ, nhiều lượt','chatbot','contract','Assertions theo tham chiếu; chưa thay semantic judge.'),
        ('RAG: recall/precision@k, MRR, nDCG, citation','rag','contract','Tính từ ID gold và trace trả về; chỉ tập mẫu được khai báo.'),
        ('RAG: faithfulness, factual correctness, context recall bằng judge','rag','judge','Ragas dùng LLM thật khi cấu hình và bật --judge.'),
        ('Câu trả lời: rubric correctness và faithfulness','chatbot','judge','DeepEval judge tùy chọn; không giả lập điểm nếu không có model.'),
        ('Agent: tool selection, arguments, thứ tự, budget, từ chối side effect','agent','contract','Kiểm trace thật trong product mode; demo chỉ sandbox local.'),
        ('Guardrail: injection, privacy, refusal, over-refusal, toxicity, fairness','guardrail','contract','Ca và chuỗi kiểm mẫu; chưa chứng minh chịu mọi tấn công hay đo bias theo quần thể.'),
        ('Latency, usage/chi phí','runtime','measurement','Latency đo wall time; usage chỉ khi adapter cung cấp; không tự suy giá.'),
        ('Bias theo quần thể, ngôn ngữ ngoài mẫu, jailbreak mở rộng, red-team nhiều lượt','guardrail','not_run','Cần dataset/rubric riêng theo miền và người kiểm; template không tự chứng nhận đầy đủ.'),
    ]
    return [{'name':name,'category':category,'status':('configured' if judged else 'not_run') if kind=='judge' else ('not_run' if kind=='not_run' else 'available'),'note':note} for name,category,kind,note in rows]

def main():
    parser=argparse.ArgumentParser(description='Bộ eval chatbot/agent/guardrail với mẫu và adapter thật.')
    sub=parser.add_subparsers(dest='command',required=True)
    check=sub.add_parser('validate');check.add_argument('--dataset',type=Path,default=HERE/'datasets/demo-cases.jsonl')
    sub.add_parser('self-test')
    for command in ('demo','evaluate','replay'):
        p=sub.add_parser(command)
        p.add_argument('--dataset',type=Path,default=HERE/'datasets/demo-cases.jsonl')
        p.add_argument('--out',type=Path,default=HERE/'runs/demo')
        p.add_argument('--product-name',default='Trợ lý dữ liệu mẫu')
        p.add_argument('--timeout',type=float,default=30)
        p.add_argument('--budget-seconds',type=float,default=360)
        p.add_argument('--frameworks',choices=['auto','off'],default='auto')
        p.add_argument('--framework-timeout',type=float,default=120)
        p.add_argument('--judge',action='store_true')
        p.add_argument('--judge-max-cases',type=int,default=4)
        if command=='evaluate':p.add_argument('--adapter',required=True,help='Command argv dạng chuỗi, chạy shell=False; stdin request JSON/stdout response JSON.')
        if command=='replay':p.add_argument('--responses',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='self-test':
        import unittest
        suite=unittest.defaultTestLoader.discover(str(HERE/'tests'),pattern='test_*.py')
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    cases=read_cases(args.dataset)
    if args.command=='validate':
        print(json.dumps({'valid':True,'cases':len(cases),'categories':{cat:sum(c['category']==cat for c in cases) for cat in ('chatbot','rag','agent','guardrail')}},ensure_ascii=False));return 0
    if args.timeout<=0 or args.budget_seconds<=0 or args.framework_timeout<=0 or args.judge_max_cases<=0:
        raise ValueError('Timeout, budget và max-cases phải >0.')
    out=args.out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Thư mục output đã có dữ liệu. Dùng --out với run ID mới; không ghi đè bằng chứng.')
    if args.judge and not all(os.environ.get(x) for x in ('EVAL_JUDGE_API_KEY','EVAL_JUDGE_BASE_URL','EVAL_JUDGE_MODEL')):
        raise ValueError('--judge cần EVAL_JUDGE_API_KEY, EVAL_JUDGE_BASE_URL, EVAL_JUDGE_MODEL; chưa gọi mạng.')
    if args.judge and args.frameworks=='off':
        raise ValueError('--judge không được dùng cùng --frameworks off.')
    out.mkdir(parents=True,exist_ok=True)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    tick=time.monotonic();args.deadline=tick+args.budget_seconds;responses=[];scored=[]
    module=load_module(HERE/'adapters/demo.py','example_adapter') if args.command=='demo' else None
    replay={}
    if args.command=='replay':
        raw=json.loads(args.responses.read_text(encoding='utf-8'));raw=raw.get('responses',raw) if isinstance(raw,dict) else raw
        if not isinstance(raw,list) or any(not isinstance(x,dict) or not isinstance(x.get('case_id'),str) for x in raw):raise ValueError('Replay cần list response có case_id hoặc {responses:[...]}.')
        if len({x.get('case_id') for x in raw})!=len(raw):raise ValueError('Replay có case_id trùng.')
        replay={x.get('case_id'):x for x in raw}
    stopped=None
    for case in cases:
        if time.monotonic()>=args.deadline or stopped:
            result={key:case[key] for key in ('id','category','question','expected_answer')}
            reason=stopped or 'Hết budget runner.'
            result.update(answer='',status='not_run',checks=[{'name':'preflight','status':'not_run','score':None,'reason':reason}],source_mode=args.command,latency_ms=None)
            scored.append(result);responses.append({'case_id':case['id'],'error':reason});continue
        response=replay.get(case['id'],{'case_id':case['id'],'error':'Thiếu response replay.'}) if args.command=='replay' else call_adapter(case,args,module,args.deadline-time.monotonic())
        response=protected_response(response)
        if args.command=='evaluate' and any(code in str(response.get('error','')) for code in ('HTTP 401','HTTP 403')):
            stopped='Dừng gọi sản phẩm sau lỗi xác thực/phân quyền; các ca còn lại chưa chạy.'
        responses.append(response);scored.append(score_case(case,response,'demo' if module else ('replay' if args.command=='replay' else 'product')))
    (out/'responses.json').write_text(json.dumps({'responses':responses},ensure_ascii=False,indent=2),encoding='utf-8')
    fw=frameworks(cases,responses,out,args)
    summary={'total':len(scored),'passed':sum(c['status']=='pass' for c in scored),'failed':sum(c['status']=='fail' for c in scored),'errors':sum(c['status']=='error' for c in scored),'not_run':sum(c['status']=='not_run' for c in scored)}
    result={'run':{'id':out.name,'started_at':started,'mode':'demo' if module else ('replay' if args.command=='replay' else 'product'),'product_name':args.product_name,'dataset_label':'synthetic-example' if module else 'user-provided','case_count':len(cases),'dataset_sha256':hashlib.sha256(args.dataset.read_bytes()).hexdigest(),'elapsed_seconds':round(time.monotonic()-tick,3),'judge_requested':args.judge},'summary':summary,'cases':scored,'frameworks':fw,'controls':controls(cases,responses),'capability_coverage':coverage_matrix(cases,args.judge)}
    (out/'results.json').write_text(json.dumps(redact_artifact(result),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(out/'results.json'),'summary':summary,'framework_errors':sum(len(x.get('errors',[])) for x in fw)},ensure_ascii=False))
    if summary['errors'] or summary['not_run'] or any(x.get('errors') or x.get('exit_code',0)!=0 or any(r.get('status')=='error' for r in x.get('results',[])) for x in fw):return 2
    return 1 if summary['failed'] or any(c['detected'] is False for c in result['controls']) else 0

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    try:raise SystemExit(main())
    except (ValueError,OSError,json.JSONDecodeError) as error:
        print(safe_message(error),file=sys.stderr);raise SystemExit(2)
