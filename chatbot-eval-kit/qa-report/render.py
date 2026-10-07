#!/usr/bin/env python3
"""Render a portable QA acceptance report; never run tests or invent verdicts."""
import argparse
from collections import Counter
from html import escape
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATUSES = {'pass': 'Đạt', 'fail': 'Chưa đạt', 'not_run': 'Chưa chạy', 'blocked': 'Bị chặn', 'na': 'Không áp dụng'}
GROUPS = {'product': 'QA sản phẩm', 'llm': 'Chất lượng LLM', 'rag': 'RAG và nguồn', 'agent': 'Hành động agent', 'guardrail': 'Guardrails', 'operations': 'Vận hành'}


def validate(data):
    errors = []
    if not isinstance(data, dict):
        raise ValueError('Dữ liệu gốc phải là JSON object.')
    if data.get('schema_version') != 1:
        errors.append('schema_version phải là 1.')
    if data.get('mode') not in ('template', 'evidence'):
        errors.append('mode phải là template hoặc evidence.')
    for name in ('product', 'decision'):
        if not isinstance(data.get(name), dict):
            errors.append(f'{name} cần là object.')
    for name in ('gates', 'metrics', 'cases', 'defects'):
        rows = data.get(name)
        if not isinstance(rows, list):
            errors.append(f'{name} cần là list.'); continue
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                errors.append(f'{name}: cần object.'); continue
            ident = row.get('id')
            if not isinstance(ident, str) or not ident or ident in seen:
                errors.append(f'{name}: ID trống/trùng.'); continue
            seen.add(ident)
            if name == 'defects':
                continue
            if row.get('status') not in STATUSES:
                errors.append(f'{ident}: trạng thái không hợp lệ.')
            if name in ('cases', 'metrics') and row.get('group') not in GROUPS:
                errors.append(f'{ident}: nhóm không hợp lệ.')
            if name in ('gates', 'metrics'):
                if type(row.get('threshold_approved')) is not bool:
                    errors.append(f'{ident}: threshold_approved phải là bool.')
                if row.get('status') in ('pass', 'fail') and not row.get('threshold_approved'):
                    errors.append(f'{ident}: chưa chốt ngưỡng nên chỉ được hiển thị đã đo/chưa kết luận.')
            if name == 'metrics':
                n = row.get('sample_size')
                if n is not None and (type(n) is not int or n < 0):
                    errors.append(f'{ident}: sample_size phải là số nguyên không âm hoặc null.')
                if row.get('value') is not None and not row.get('evidence'):
                    errors.append(f'{ident}: số đo cần bằng chứng.')
                if row.get('status') in ('pass', 'fail') and (row.get('value') is None or not n):
                    errors.append(f'{ident}: kết luận cần số đo và mẫu số lớn hơn 0.')
            if name == 'gates' and row.get('status') in ('pass', 'fail') and not row.get('evidence'):
                errors.append(f'{ident}: kết luận gate cần bằng chứng.')
            if name == 'cases':
                for key in ('preconditions', 'steps', 'checks', 'evidence'):
                    if not isinstance(row.get(key), list):
                        errors.append(f'{ident}: {key} cần là list.')
                if not row.get('expected') or not row.get('steps'):
                    errors.append(f'{ident}: cần bước thực hiện và mong đợi.')
                if row.get('status') in ('pass', 'fail') and (not row.get('actual') or not row.get('evidence')):
                    errors.append(f'{ident}: kết quả cần actual và evidence.')
                for check in row.get('checks', []):
                    if not isinstance(check, dict) or check.get('status') not in STATUSES:
                        errors.append(f'{ident}: check không hợp lệ.')
                    elif data.get('mode') == 'template' and (check.get('status') in ('pass', 'fail') or check.get('actual')):
                        errors.append(f'{ident}: template không được chứa kết quả check.')
                if row.get('status') == 'pass' and (not row.get('checks') or any(not isinstance(c, dict) or c.get('status') not in ('pass', 'na') for c in row.get('checks', []))):
                    errors.append(f'{ident}: không thể đạt khi còn kiểm tra chưa đạt/chưa chạy/bị chặn.')
            if data.get('mode') == 'template' and (row.get('status') in ('pass', 'fail') or (name == 'metrics' and row.get('value') is not None) or (name == 'cases' and (row.get('actual') or row.get('evidence')))):
                errors.append(f'{ident}: bản template không được có kết quả mẫu giả.')
    if errors:
        raise ValueError('\n'.join(errors))


def summarize(cases):
    count = Counter(c['status'] for c in cases)
    planned = len(cases) - count['na']
    executed = count['pass'] + count['fail']
    return {'planned': planned, 'executed': executed, 'passed': count['pass'], 'failed': count['fail'], 'pending': count['not_run'] + count['blocked'], 'blocked': count['blocked'], 'na': count['na'], 'pass_rate': count['pass'] / executed if executed else None}


def e(value):
    return escape(str(value if value is not None else ''))


def content(value, placeholder='Chưa ghi nhận'):
    return e(value).replace('\n', '<br>') if value is not None and value != '' else f'<span class="empty">{e(placeholder)}</span>'


def pill(status):
    return f'<span class="pill {e(status)}">{STATUSES[status]}</span>'


def metric_status(row):
    if row.get('value') is not None and not row['threshold_approved']:
        return 'Đã đo · Chưa chốt ngưỡng'
    return STATUSES[row['status']]


def items(values, ordered=False):
    if ordered:
        values = [re.sub(r'^\s*\d+[a-zA-Z]?[.)]\s*', '', str(v)) for v in values]
    tag = 'ol' if ordered else 'ul'
    return f'<{tag} class="steps">'+''.join(f'<li>{content(v)}</li>' for v in values)+f'</{tag}>' if values else '<p class="empty">Chưa ghi nhận</p>'


def render_html(data):
    s = summarize(data['cases']); p = data['product']; d = data['decision']
    css = (HERE/'assets/report.css').read_text()
    js = (HERE/'assets/report.js').read_text()
    mode = 'Mẫu trống · Chưa thực hiện kiểm thử' if data['mode'] == 'template' else 'Báo cáo từ bằng chứng kiểm thử'
    groups = []
    for key, label in GROUPS.items():
        rows = [c for c in data['cases'] if c['group'] == key]
        if not rows:
            continue
        count = Counter(c['status'] for c in rows)
        segments = ''.join(f'<span class="{status}-seg" style="width:{100*count[status]/len(rows):.3f}%" title="{STATUSES[status]}: {count[status]}"></span>' for status in STATUSES if count[status])
        verbal = '; '.join(f'{STATUSES[k]} {count[k]}' for k in STATUSES if count[k])
        groups.append(f'<div class="chart-row"><span class="chart-name">{label}</span><div class="chart-track" role="img" aria-label="{e(label+": "+verbal)}">{segments}</div><span class="chart-count">{e(verbal)}</span></div>')
    gates = []
    for g in data['gates']:
        gates.append(f'<article class="card gate"><div class="top"><h3>{e(g["name"])}</h3>{pill(g["status"])}</div><p>{content(g["rule"])}</p><div class="subtle"><span class="label">Điều kiện nghiệm thu</span>{"Đã thống nhất cho lượt này" if g["threshold_approved"] else "Đề xuất · cần chủ sản phẩm xác nhận"}</div><p class="evidence">Bằng chứng: {content(g["evidence"])}</p></article>')
    metrics = []
    for m in data['metrics']:
        status_label = metric_status(m)
        metrics.append(f'''<article class="card metric"><div class="top"><div><span class="eyebrow">{GROUPS[m['group']]}</span><h3>{e(m['name'])}</h3></div></div><p class="question">{e(m['question'])}</p><div class="metric-value">{content(m['value'],'Chưa đo')}</div><span class="pill {m['status']}">{e(status_label)}</span><p class="hint">Mẫu đánh giá: {m['sample_size'] if m['sample_size'] is not None else 'chưa có'} · {content(m['interpretation'],'Chưa có kết quả để diễn giải.')}</p><dl><div><dt>Đo điều gì?</dt><dd>{e(m['definition'])}</dd></div><div><dt>Khi nào được coi là đạt?</dt><dd>{e(m['threshold'])}<br><b>{'Ngưỡng đã thống nhất.' if m['threshold_approved'] else 'Ngưỡng đề xuất, chưa được phê duyệt.'}</b></dd></div></dl><details><summary>Cách chấm và bằng chứng</summary><dl><div><dt>Cách đo</dt><dd>{content(m['method'])}</dd></div><div><dt>Bằng chứng</dt><dd>{content(m['evidence'])}</dd></div><div><dt>Giới hạn của kết luận</dt><dd>{content(m['limitation'])}</dd></div></dl></details></article>''')
    cards = []
    for i, c in enumerate(data['cases']):
        checks = ''.join(f'<tr><td>{e(x["criterion"])}</td><td>{content(x["expected"])}</td><td>{content(x["actual"])}</td><td>{pill(x["status"])}</td></tr>' for x in c['checks'])
        evidence = '<br>'.join(f'<code>{e(x)}</code>' for x in c['evidence']) or 'Chưa có bằng chứng thực thi.'
        cards.append(f'''<details class="card case-card" data-group="{c['group']}" data-status="{c['status']}" {'open' if i == 0 else ''}><summary><span class="case-id">{e(c['id'])}</span><div><h3>{e(c['title'])}</h3><span class="case-sub">{GROUPS[c['group']]} · {e(c['priority'])} · {e(c['data_type'])}</span></div>{pill(c['status'])}</summary><div class="case-body"><div class="case-context"><div><span class="label">Yêu cầu cần nghiệm thu</span><p>{content(c['requirement'])}</p></div><div><span class="label">Điều kiện trước khi kiểm</span>{items(c['preconditions'])}</div></div><span class="label">Các bước thực hiện</span>{items(c['steps'],True)}<div class="input"><span class="label">Đầu vào / yêu cầu của người dùng</span>{content(c['input'],'Không cần nhập thêm dữ liệu.')}</div><div class="comparison"><div class="expected"><span class="label">Kết quả mong đợi</span><p>{content(c['expected'])}</p></div><div class="actual"><span class="label">Kết quả thực tế</span><p>{content(c['actual'],'Chưa chạy. Điền kết quả quan sát được sau khi thực hiện.')}</p></div></div><table class="checks"><thead><tr><th scope="col">Tiêu chí</th><th scope="col">Mong đợi</th><th scope="col">Thực tế</th><th scope="col">Kết luận</th></tr></thead><tbody>{checks}</tbody></table><div class="evidence"><span class="label">Bằng chứng để kiểm lại</span>{evidence}</div><div class="followup"><div><span class="label">Lỗi / việc cần xử lý</span>{content(c['defect'],'Chưa ghi nhận lỗi.')}<br>{content(c['follow_up'],'Chưa có hành động bổ sung.')}</div><div><span class="label">Kiểm lại sau sửa</span>{content(c['retest'],'Chưa kiểm lại.')}</div></div></div></details>''')
    defects = []
    for x in data['defects']:
        defects.append(f'''<article class="card issue"><div class="issue-head"><div><span class="eyebrow">{e(x['id'])} · {e(x['severity'])}</span><h3>{e(x['title'])}</h3></div><span class="pill">{e(x['status'])}</span></div><p>{content(x['impact'])}</p><p class="small">Liên quan: {e(', '.join(x['case_ids']))}</p><details><summary>Cách tái hiện và kiểm lại</summary>{items(x['reproduce'],True)}<dl><dt>Mong đợi</dt><dd>{content(x['expected'])}</dd><dt>Thực tế</dt><dd>{content(x['actual'])}</dd><dt>Cần sửa</dt><dd>{content(x['fix'])}</dd><dt>Điều kiện đóng lỗi</dt><dd>{content(x['retest'])}</dd></dl></details></article>''')
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(p['name'])} · Nghiệm thu QA</title><style>{css}</style></head><body><a class="skip" href="#main">Đến nội dung chính</a><header class="topbar"><div class="topinner"><span class="brand">QA / AI Acceptance</span><nav class="topnav" aria-label="Nội dung báo cáo"><a href="#criteria">Nghiệm thu</a><a href="#metrics">Evals</a><a href="#cases">Phiếu QA</a><a href="#issues">Lỗi cần sửa</a></nav></div></header><main id="main" class="wrap"><span class="eyebrow">{e(mode)}</span><h1>{e(p['name'])}<br><span style="color:var(--muted)">Báo cáo nghiệm thu QA.</span></h1><p class="lead">{e(p['scope'])}</p><div class="meta"><span><b>Phiên bản</b> {content(p['version'],'Chưa điền')}</span><span><b>Môi trường</b> {content(p['environment'],'Chưa điền')}</span><span><b>Ngày kiểm</b> {content(p['run_date'],'Chưa điền')}</span></div><section class="card decision" aria-label="Đề xuất nghiệm thu"><div><span class="label">Đề xuất QA</span><strong>{content(d['recommendation'],'Chưa đủ bằng chứng')}</strong></div><div><p>{content(d['rationale'])}</p><p class="small">Phê duyệt của chủ sản phẩm: {content(d['approved_by'],'Chưa xác nhận')} · {content(d['approved_at'],'Chưa có ngày phê duyệt')}</p></div></section><section aria-label="Tình trạng kiểm thử"><div class="kpis"><div class="card kpi"><span class="label">Ca đã chạy</span><b>{s['executed']}/{s['planned']}</b><span class="small">Loại {s['na']} ca không áp dụng</span></div><div class="card kpi"><span class="label">Đạt yêu cầu ca</span><b>{s['passed']}</b><span class="small">Trong {s['executed']} ca đã chạy</span></div><div class="card kpi"><span class="label">Chưa đạt</span><b>{s['failed']}</b><span class="small">Cần sửa hoặc đối chiếu</span></div><div class="card kpi"><span class="label">Chưa có kết quả</span><b>{s['pending']}</b><span class="small">Gồm {s['blocked']} ca bị chặn</span></div></div><div class="card"><h3>Phạm vi nào đã có bằng chứng?</h3><p class="small">Đạt/Chưa đạt chỉ dành cho ca đã chạy. Chưa chạy và bị chặn không được tính thành đạt hoặc điểm chất lượng bằng 0.</p>{''.join(groups)}<div class="legend">{''.join(f'<span><i class="dot {k}-seg"></i>{v}</span>' for k,v in STATUSES.items())}</div></div></section><section class="section" id="criteria"><div class="section-head"><div><h2>Điều kiện nghiệm thu.</h2><p>Kiểm từng yêu cầu bắt buộc. Điểm trung bình tốt không bù cho lỗi chặn phát hành.</p></div></div><div class="gate-grid">{''.join(gates)}</div></section><section class="section" id="metrics"><div class="section-head"><div><h2>AI được đánh giá như thế nào?</h2><p>Mỗi chỉ số nêu rõ điều cần biết, cách đo, ngưỡng và bằng chứng. Có số đo chưa đồng nghĩa đạt nghiệm thu.</p></div></div><div class="metric-grid">{''.join(metrics)}</div></section><section class="section" id="cases"><div class="section-head"><div><h2>Phiếu kiểm thử QA.</h2><p>Mỗi phiếu mô tả một tình huống có thể thực hiện và kiểm lại. Mở phiếu để xem các bước, đối chiếu và bằng chứng.</p></div></div><div class="toolbar screen-only"><div class="control"><label for="query">Tìm tình huống hoặc mã ca</label><input id="query" type="search" placeholder="Ví dụ: nguồn, phê duyệt, R04"></div><div class="control"><label for="group">Phạm vi</label><select id="group"><option value="all">Tất cả phạm vi</option>{''.join(f'<option value="{k}">{v}</option>' for k,v in GROUPS.items())}</select></div><div class="control"><label for="status">Kết quả</label><select id="status"><option value="all">Tất cả kết quả</option>{''.join(f'<option value="{k}">{v}</option>' for k,v in STATUSES.items())}</select></div><button id="expand" class="button secondary">Mở toàn bộ phiếu</button></div><p id="visible-count" class="small screen-only" aria-live="polite"></p><div class="case-list">{''.join(cards)}</div><p id="no-results" class="no-results" hidden>Không có ca phù hợp. Đổi từ khóa hoặc bộ lọc.</p></section><section id="issues" class="section"><div class="section-head"><div><h2>Việc cần hoàn tất.</h2><p>Gắn lỗi với ca kiểm thử, ảnh hưởng đến người dùng và điều kiện kiểm lại.</p></div></div>{''.join(defects) or '<div class="card"><p>Chưa ghi nhận lỗi. Nếu chưa chạy các ca, trạng thái này không có nghĩa sản phẩm không có lỗi.</p></div>'}</section><section class="section card"><h3>Bối cảnh và giới hạn của báo cáo</h3><p class="small"><b>Nguồn dữ liệu:</b> {content(p['data_origin'])}<br><b>Model:</b> {content(p['model'])}<br><b>Dataset:</b> {content(p['dataset'])}<br><b>Người phụ trách:</b> {content(p['owner'],'Chưa phân công')}</p>{items(p['limitations'])}</section><footer class="foot"><span>Đề xuất QA không thay cho phê duyệt của chủ sản phẩm.<br>Không có bằng chứng thì không suy ra kết quả.</span><button id="print" class="button screen-only">In toàn bộ báo cáo</button></footer></main><script>{js}</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pdf', type=Path)
    parser.add_argument('--all-cases', action='store_true', help='PDF kèm mọi phiếu chi tiết; mặc định chỉ mục đầy đủ và phiếu đại diện theo nhóm.')
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding='utf-8'))
        validate(data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render_html(data), encoding='utf-8')
        if args.pdf:
            from pdf_report import render_pdf
            args.pdf.parent.mkdir(parents=True, exist_ok=True)
            render_pdf(data, args.pdf, all_cases=args.all_cases)
        print(json.dumps({'html': str(args.output), 'pdf': str(args.pdf) if args.pdf else None, 'counts': summarize(data['cases'])}, ensure_ascii=False))
    except (ValueError, KeyError, TypeError, OSError, ImportError) as exc:
        parser.exit(2, f'Lỗi dữ liệu/render: {exc}\n')


if __name__ == '__main__':
    main()
