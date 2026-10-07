import json, pathlib,time, re, platform, importlib.metadata
from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler
ROOT=pathlib.Path(__file__).resolve().parent
requests=json.loads((ROOT/'requests.json').read_text())
tick=time.perf_counter(); model,tokenizer=load(str(ROOT/'model')); load_seconds=time.perf_counter()-tick
responses=[]; traces=[]
for req in requests:
    prompt=tokenizer.apply_chat_template(req['messages'],tokenize=False,add_generation_prompt=True)
    tick=time.perf_counter(); answer=''; first=None; last=None
    for item in stream_generate(model,tokenizer,prompt=prompt,max_tokens=192,sampler=make_sampler(temp=0)):
        if first is None:first=time.perf_counter()-tick
        answer+=item.text; last=item
    elapsed=time.perf_counter()-tick
    response={'case_id':req['case_id'],'answer':answer,'latency_ms':round(elapsed*1000,2),'retrieved_contexts':req['retrieved_contexts'],'citations':re.findall(r'\[([^\[\]\n]+)\]',answer) if req['retrieved_contexts'] else []}
    responses.append(response)
    traces.append({'case_id':req['case_id'],'prompt':prompt,'answer':answer,'time_to_first_chunk_seconds':first,'latency_seconds':elapsed,'prompt_tokens':last.prompt_tokens,'generation_tokens':last.generation_tokens,'generation_tps':last.generation_tps,'finish_reason':last.finish_reason})
    (ROOT/'responses.json').write_text(json.dumps(responses,ensure_ascii=False,indent=2)); (ROOT/'evidence/generation-traces.json').write_text(json.dumps(traces,ensure_ascii=False,indent=2))
    print(req['case_id'],round(elapsed,2),repr(answer),flush=True)
manifest={'model':'mlx-community/Qwen2.5-0.5B-Instruct-4bit','model_revision':'53a32aee5e9447773fd2b85988395066aef3700a','temperature':0,'max_tokens':192,'load_seconds':load_seconds,'platform':platform.platform(),'machine':platform.machine(),'versions':{k:importlib.metadata.version(k) for k in ['mlx','mlx-lm','transformers','huggingface-hub']},'completed_at':time.strftime('%Y-%m-%dT%H:%M:%S%z')}
(ROOT/'evidence/model-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
