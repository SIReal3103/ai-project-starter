#!/usr/bin/env python3
"""Render an offline, printable Vietnamese report from the eval runner JSON."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from html import escape
import json
import math
from pathlib import Path
import re
import sys
from typing import Any


STATUSES = ("pass", "fail", "error", "not_run")
LABELS = {"pass": "Đạt", "fail": "Không đạt", "error": "Lỗi chạy", "not_run": "Chưa chạy"}
COLORS = {"pass": "#1c7967", "fail": "#bd433d", "error": "#bd741e", "not_run": "#b1b7c1"}
CATEGORY_NAMES = {
    "chatbot": "Chatbot · Hội thoại và đầu ra",
    "rag": "RAG · Truy hồi và dẫn nguồn",
    "agent": "Agent · Công cụ và quy trình",
    "guardrail": "Guardrail · An toàn và phạm vi",
}
CHECK_NAMES = {
    "output_nonempty": "Đầu ra có nội dung",
    "exact_match": "Khớp đáp án nguyên văn",
    "answer_required_facts": "Dữ kiện bắt buộc",
    "answer_alternatives": "Cách diễn đạt hợp lệ",
    "output_forbidden_content": "Nội dung bị cấm",
    "guardrail_action": "Quyết định guardrail",
    "refusal_policy": "Chính sách từ chối",
    "json_output": "Định dạng JSON",
    "retrieval_schema": "Cấu trúc nguồn truy hồi",
    "retrieval_unique_ids": "Mã nguồn không trùng",
    "retrieval_recall_at_k": "Độ phủ nguồn chuẩn tại k",
    "citation_schema": "Cấu trúc trích dẫn",
    "citation_completeness": "Đủ nguồn trích dẫn",
    "citation_validity": "Mã trích dẫn hợp lệ",
    "tool_trace_schema": "Cấu trúc trace công cụ",
    "tool_sequence_and_arguments": "Thứ tự và đối số công cụ",
    "tool_call_budget": "Ngân sách gọi công cụ",
    "tool_allowlist": "Phạm vi công cụ được phép",
    "latency_budget": "Ngưỡng độ trễ",
}
METRIC_NAMES = {
    "non_llm_context_recall": "Độ phủ nguồn · khớp văn bản",
    "non_llm_context_precision_with_reference": "Độ chính xác nguồn · khớp văn bản",
    "faithfulness": "Độ bám nguồn · LLM judge",
    "factual_correctness": "Độ đúng dữ kiện · LLM judge",
    "llm_context_recall": "Độ phủ thông tin nguồn · LLM judge",
    "exact_match": "Khớp nguyên văn · đáp án đóng",
    "geval_correctness": "Độ đúng theo rubric · G-Eval",
}


def text(value: Any, default: str = "—") -> str:
    """Escape every value received from the product, dataset, or a judge."""
    if value is None or value == "":
        return default
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, indent=2)
    return (escape(str(value), quote=True)
            .replace("\r", "&#13;").replace("\n", "&#10;").replace("\t", "&#9;"))


def status(value: Any) -> str:
    return value if value in STATUSES else "not_run"


def badge(value: Any) -> str:
    kind = status(value)
    return f'<span class="badge {kind}">{LABELS[kind]}</span>'


def score(value: Any) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return "—"


def timestamp(value: Any) -> str:
    if not value:
        return "Không ghi thời gian"
    try:
        instant = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if instant.tzinfo is None:
            return text(value)
        return instant.astimezone(timezone(timedelta(hours=7))).strftime("%d/%m/%Y · %H:%M (giờ Việt Nam)")
    except ValueError:
        return text(value)


def load_results(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise ValueError("Kết quả phải là object JSON có trường cases là một mảng.")
    seen: set[str] = set()
    for index, case in enumerate(data["cases"]):
        if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"]:
            raise ValueError(f"cases[{index}] phải là object có id dạng chuỗi, không rỗng.")
        if case["id"] in seen:
            raise ValueError(f"Trùng mã ca kiểm thử: {case['id']}")
        seen.add(case["id"])
        if case.get("status") not in STATUSES:
            raise ValueError(f"Ca {case['id']} có status không hợp lệ.")
    for name in ("frameworks", "controls", "capability_coverage"):
        if name in data and not isinstance(data[name], list):
            raise ValueError(f"{name} phải là một mảng.")
    return data


def counts(cases: list[dict[str, Any]]) -> Counter:
    return Counter(status(case.get("status")) for case in cases)


def category_chart(groups: dict[str, list[dict[str, Any]]]) -> str:
    """One independent SVG per category stays readable across print page breaks."""
    if not groups:
        return '<p class="muted">Chưa có ca kiểm thử để vẽ biểu đồ.</p>'
    max_count = max(len(items) for items in groups.values())
    rows = []
    for name, items in groups.items():
        tally = counts(items)
        description = ", ".join(f"{LABELS[kind]}: {tally[kind]}" for kind in STATUSES)
        segments = []
        offset = 0.0
        for kind in STATUSES:
            width = tally[kind] / max_count * 680
            if width:
                segments.append(f'<rect x="{offset:.2f}" y="3" width="{width:.2f}" height="18" fill="{COLORS[kind]}"/>')
                offset += width
        rows.append(
            '<div class="chart-row">'
            f'<div class="chart-label">{text(name)} <span>{len(items)} ca</span></div>'
            f'<svg viewBox="0 0 680 24" role="img" aria-label="{text(name)}: {text(description)}">'
            f'<title>{text(description)}</title><rect width="680" height="18" y="3" fill="#eef0f4"/>'
            + "".join(segments)
            + f'</svg><div class="chart-counts">{text(description)}</div></div>'
        )
    legend = "".join(f'<span><i style="background:{COLORS[kind]}"></i>{LABELS[kind]}</span>' for kind in STATUSES)
    return f'<div class="legend">{legend}</div><div class="chart">{"".join(rows)}</div>'


def reason_html(case: dict[str, Any]) -> str:
    checks = case.get("checks") or []
    if not checks:
        return f'<p>{text(case.get("reason"), "Không có lý do chi tiết được ghi trong kết quả.")}</p>'
    items = []
    problems=[check for check in checks if isinstance(check,dict) and check.get('status')!='pass']
    displayed=problems if problems else []
    for check in displayed:
        if not isinstance(check, dict):
            continue
        kind = status(check.get("status"))
        name = text(CHECK_NAMES.get(check.get("name"), check.get("name")), "Kiểm tra")
        reason = text(check.get("reason"), "Không ghi lý do.")
        value = score(check.get("score"))
        suffix = f" · điểm {value}" if value != "—" else ""
        items.append(f'<li><b class="check-{kind}">{name} · {LABELS[kind]}{suffix}</b><span>{reason}</span></li>')
    diagnostics = case.get("retrieval_metrics") or {}
    metric_labels = {"recall_at_k": "Recall@k", "precision_at_k": "Precision@k", "mrr": "MRR", "ndcg_at_k": "nDCG@k", "k": "k"}
    metrics = " · ".join(f"{label}: {score(diagnostics[name])}" for name, label in metric_labels.items() if name in diagnostics)
    diagnostic_note = f'<p class="diagnostics">Chẩn đoán truy hồi: {metrics}. Chỉ các ngưỡng đã khai báo mới quyết định đạt/không đạt.</p>' if metrics else ""
    if not problems:
        relevant=[CHECK_NAMES.get(check.get('name'),check.get('name')) for check in checks if check.get('name') in ('answer_required_facts','exact_match','citation_validity','tool_sequence_and_arguments','output_forbidden_content','guardrail_action','json_output')]
        return f'<p class="diagnostics">Đạt {len(checks)} điều kiện: {text("; ".join(relevant[:3]))}.</p>'+diagnostic_note
    return '<ul class="checks">' + "".join(items) + "</ul>" + diagnostic_note


def case_sections(groups: dict[str, list[dict[str, Any]]]) -> str:
    sections = []
    for number, (name, cases) in enumerate(groups.items(), start=1):
        tally = counts(cases)
        rows = []
        for case in cases:
            latency = case.get("latency_ms")
            meta = f'{score(latency)} ms' if score(latency) != "—" else "Không ghi độ trễ"
            rows.append(
                '<tbody class="case-block"><tr class="case-primary">'
                f'<td class="case-id"><strong>{text(case["id"])}</strong><small>{text(meta)}</small></td>'
                f'<td class="question">{text(case.get("question"), "(Đầu vào trống)")}</td>'
                f'<td>{text(case.get("expected_answer"), "Không ghi đáp án tham chiếu.")}</td>'
                f'<td>{text(case.get("answer"), "Không có câu trả lời.")}</td>'
                f'<td class="case-verdict">{badge(case.get("status"))}</td></tr>'
                f'<tr class="case-reasons"><td colspan="5"><b class="reason-title">Căn cứ kết luận</b>{reason_html(case)}</td></tr></tbody>'
            )
        sections.append(
            f'<section class="category-section"><div class="section-heading"><span class="eyebrow">Nhóm {number:02d}</span>'
            f'<h2>{text(name)}</h2><p>{len(cases)} ca · {tally["pass"]} đạt · {tally["fail"]} không đạt · '
            f'{tally["error"]} lỗi · {tally["not_run"]} chưa chạy</p></div>'
            '<table class="cases-table"><colgroup><col class="col-id"><col class="col-question">'
            '<col class="col-expected"><col class="col-answer"><col class="col-verdict"></colgroup>'
            '<thead><tr><th>Ca</th><th>Câu hỏi / yêu cầu</th><th>Đáp án / hành vi mong đợi</th>'
            '<th>Câu trả lời thực tế</th><th>Kết luận</th></tr></thead>'
            + "".join(rows)
            + '</table></section>'
        )
    return "".join(sections) or '<section><h2>Chi tiết kiểm thử</h2><p>Không có ca nào được ghi nhận.</p></section>'


def framework_section(frameworks: list[dict[str, Any]], control_ids: set[str]) -> str:
    if not frameworks:
        return '<p>Không có kết quả framework bổ sung trong lượt chạy này.</p>'
    tables = []
    for framework in frameworks:
        if not isinstance(framework, dict):
            continue
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for result in framework.get("results") or []:
            if isinstance(result, dict) and result.get("case_id") not in control_ids:
                grouped[str(result.get("metric") or "Không ghi metric")].append(result)
        rows = []
        pending = []
        for metric, results in grouped.items():
            label = METRIC_NAMES.get(metric, metric)
            if all(item.get("status") == "not_run" and str(item.get("reason", "")).startswith("LLM judge disabled") for item in results):
                pending.append(label)
                continue
            results = [item for item in results if not (item.get("status") == "not_run" and str(item.get("reason", "")).startswith("Not applicable"))]
            if not results:
                continue
            metric_statuses = ("scored", "pass", "fail", "error", "not_run")
            tally = Counter(item.get("status") if item.get("status") in metric_statuses else "not_run" for item in results)
            scores = [item["score"] for item in results if item.get("status") in ("scored", "pass", "fail") and score(item.get("score")) != "—"]
            mean = score(sum(scores) / len(scores)) if scores else "—"
            rows.append(f'<tr><th scope="row">{text(label)}</th><td>{tally["scored"]}</td><td>{mean}</td><td>{tally["pass"]} / {tally["fail"]}</td><td>{tally["error"]}</td><td>{tally["not_run"]}</td></tr>')
        table = (
            '<table class="compact-table"><thead><tr><th>Phép đo</th><th>Đã đo</th><th>Điểm TB</th><th>Đạt / không đạt</th>'
            '<th>Lỗi</th><th>Chưa chạy</th></tr></thead><tbody>'
            + "".join(rows)
            + '</tbody></table>'
        ) if rows else f'<p class="muted">{text(framework.get("reason"), "Không có metric đã ghi nhận.")}</p>'
        if pending:
            table += '<p class="reading-note"><strong>Chưa bật judge:</strong> ' + '; '.join(text(name) for name in pending) + '.</p>'
        if any(str(item.get("reason", "")).startswith("Not applicable") for values in grouped.values() for item in values):
            table += '<p class="reading-note">Chỉ tổng hợp các ca đủ điều kiện áp dụng; bỏ các cặp ca–metric không phù hợp khỏi bảng.</p>'
        mode_label = {"offline": "Không gọi LLM", "judge": "Có yêu cầu LLM judge"}.get(framework.get("mode"), framework.get("mode"))
        tables.append(
            '<div class="framework-block">'
            f'<h3>{text(framework.get("framework"), "Framework")}</h3>'
            f'<p class="metadata">Phiên bản: {text(framework.get("version"), "Không ghi")} · Chế độ: '
            f'{text(mode_label, "Không ghi")}</p>{table}</div>'
        )
    return "".join(tables)


def judge_section(data: dict[str, Any]) -> str:
    judged = []
    for framework in data.get("frameworks") or []:
        if not isinstance(framework, dict):
            continue
        mode = str(framework.get("mode", "")).lower()
        name = str(framework.get("framework", "")).lower()
        is_judge = "judge" in mode or "judge" in name or ("llm" in mode and not any(marker in mode for marker in ("non_llm", "non-llm", "nonllm")))
        if is_judge and "smoke" not in mode:
            judged.extend(
                item for item in framework.get("results", [])
                if isinstance(item, dict)
                and not str(item.get("metric", "")).startswith("non_llm_")
                and item.get("metric") != "exact_match"
            )
    for case in data["cases"]:
        for check in case.get("checks") or []:
            if isinstance(check, dict) and ("judge" in str(check.get("name", "")).lower() or "llm" in str(check.get("name", "")).lower()):
                judged.append(check)
    executed = [item for item in judged if item.get("status") in ("scored", "pass", "fail")]
    if not executed:
        errors = sum(item.get("status") == "error" for item in judged)
        error_note = f" Có {errors} kết quả judge lỗi; không tính là đã chấm thành công." if errors else ""
        return '<div class="judge pending"><span class="eyebrow">LLM-as-a-judge · Chưa có kết quả hợp lệ</span><h3>Đánh giá ngữ nghĩa còn chờ chạy</h3><p>Chưa thể kết luận độ đúng, đầy đủ hoặc bám nguồn bằng LLM judge từ lượt này. Cần cấu hình judge, rubric và tập tham chiếu phù hợp rồi chạy riêng.' + error_note + '</p></div>'
    return '<div class="judge"><span class="eyebrow">LLM-as-a-judge · Có kết quả</span><h3>Đã ghi nhận đánh giá bằng mô hình</h3><p>Kết quả judge được trình bày theo metric ở phần framework. Judge là một nguồn nhận xét cần kiểm tra bằng rubric và mẫu do người đánh giá; không thay thế kiểm chứng nguồn hoặc đánh giá của chuyên gia.</p></div>'


def coverage_section(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<p>Chưa khai báo bản đồ phạm vi. Chỉ các ca và kiểm tra được liệt kê trong báo cáo là có bằng chứng; không suy ra đã phủ toàn bộ khả năng của sản phẩm.</p>'
    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue
        raw_status = item.get("status")
        scope_labels = {"available": "Có bộ kiểm", "configured": "Đã yêu cầu judge", "covered": "Có ca đo", "partial": "Một phần"}
        display = badge(raw_status) if raw_status in STATUSES else text(scope_labels.get(raw_status, raw_status), "Chưa xác định")
        rows.append(f'<tr><td><strong>{text(item.get("name"))}</strong></td><td>{display}</td><td>{text(item.get("note"))}</td></tr>')
    return '<table class="compact-table coverage-table"><thead><tr><th>Năng lực</th><th>Trạng thái phạm vi</th><th>Bằng chứng / phần còn thiếu</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table>'


def control_section(controls: list[dict[str, Any]]) -> str:
    if not controls:
        return '<p>Không có đối chứng âm trong kết quả. Chưa có bằng chứng ở lượt này rằng bộ chấm nhận ra câu trả lời hoặc hành vi sai có chủ đích.</p>'
    rows = []
    for item in controls:
        if not isinstance(item, dict):
            continue
        detected = item.get("detected")
        display = '<span class="badge pass">Phát hiện đúng</span>' if detected is True else ('<span class="badge fail">Không phát hiện</span>' if detected is False else '<span class="badge not_run">Chưa xác định</span>')
        rows.append(f'<tr><th scope="row">{text(item.get("id"))}</th><td>{text(item.get("description"))}</td><td>{display}</td></tr>')
    table = '<table class="compact-table"><thead><tr><th>Đối chứng</th><th>Sai lệch có chủ đích</th><th>Bộ chấm có phát hiện?</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table>'
    eligible = [item for item in controls if isinstance(item, dict) and "question" in item and "answer" in item]
    preferred = {"empty-answer": 0, "wrong-fact": 1, "forbidden-disclosure": 2}
    samples = sorted(eligible, key=lambda item: preferred.get(item.get("id"), 10))[:3]
    if not samples:
        return table
    cards = []
    for item in samples:
        verdict = '<span class="badge fail">Đầu ra không đạt</span>' if item.get("detected") is True else '<span class="badge error">Chưa phát hiện sai lệch</span>'
        cards.append(
            '<article class="control-sample">'
            f'<h3>{text(item.get("description"))}</h3><p class="metadata">{text(item.get("id"))} · Đầu ra được sửa sai có chủ đích</p>'
            '<table class="compact-table"><tbody>'
            f'<tr><th>Câu hỏi</th><td>{text(item.get("question"))}</td></tr>'
            f'<tr><th>Mong đợi</th><td>{text(item.get("expected_answer"))}</td></tr>'
            f'<tr><th>Đầu ra sai</th><td>{text(item.get("answer"), "(Câu trả lời rỗng)")}</td></tr>'
            f'<tr><th>Kết luận bộ chấm</th><td>{verdict}{reason_html(item)}</td></tr>'
            '</tbody></table></article>'
        )
    return table + '<h3 class="control-samples-title">Ví dụ phản hồi không đạt để thử bộ chấm</h3><p class="reading-note">Các ví dụ dưới đây là phản hồi đã bị sửa sai, không phải câu trả lời nguyên bản của sản phẩm và không tham gia tỷ lệ đạt.</p>' + ''.join(cards)


def render(data: dict[str, Any], template: str) -> str:
    run = data.get("run") or {}
    controls = data.get("controls") or []
    control_ids = {item["id"] for item in controls if isinstance(item, dict) and isinstance(item.get("id"), str)}
    cases = [case for case in data["cases"] if case["id"] not in control_ids and not case.get("is_control", False)]
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        category = str(case.get("category") or "Chưa phân nhóm")
        groups[CATEGORY_NAMES.get(category, category)].append(case)
    tally = counts(cases)
    total = len(cases)
    completed = tally["pass"] + tally["fail"]
    mode = str(run.get("mode") or "unknown")
    mode_labels = {"demo": "DEMO · ASSISTANT MẪU", "product": "KẾT QUẢ ADAPTER SẢN PHẨM", "replay": "REPLAY · CÂU TRẢ LỜI ĐÃ LƯU"}
    scope_notes = {
        "demo": "Đây là dữ liệu tham chiếu được viết thủ công và assistant ví dụ chạy xác định theo quy tắc. Kết quả minh họa cách vận hành bộ eval; chưa đánh giá LLM hay chatbot production.",
        "product": "Kết quả được tạo từ câu trả lời qua adapter sản phẩm. Mỗi kết luận chỉ áp dụng cho ca, dữ liệu và kiểm tra thực sự đã chạy; cần xem riêng trạng thái LLM judge.",
        "replay": "Bộ chấm chạy lại trên câu trả lời đã lưu. Lượt này không xác nhận API, mô hình hoặc công cụ của sản phẩm đang hoạt động trực tiếp; kết quả phụ thuộc snapshot đầu vào.",
    }
    product = text(run.get("product_name"), "Bộ eval chatbot, agent & guardrail")
    metrics = [('Tổng ca', total, 'Không gồm đối chứng âm', 'total'), ('Đạt', tally['pass'], 'Theo kiểm tra đã chạy', 'pass'), ('Không đạt', tally['fail'], 'Cần xem nguyên nhân', 'fail'), ('Lỗi / chưa chạy', f'{tally["error"]} / {tally["not_run"]}', 'Không tính thành đạt', 'not_run')]
    cards = "".join(f'<div class="metric {kind}"><span>{label}</span><strong>{value}</strong><small>{note}</small></div>' for label, value, note, kind in metrics)
    ratio = f"{tally['pass'] / completed * 100:.1f}%".replace('.', ',') if completed else "Chưa có"
    supplied = data.get("summary") or {}
    expected_summary = {"total": total, "passed": tally["pass"], "failed": tally["fail"], "errors": tally["error"], "not_run": tally["not_run"]}
    mismatch = any(key in supplied and supplied[key] != value for key, value in expected_summary.items())
    integrity = '<p class="integrity-note">Lưu ý dữ liệu: summary nguồn khác bảng ca. Báo cáo tính lại toàn bộ số đếm từ cases, sau khi loại đối chứng âm.</p>' if mismatch else ''
    failures = [case for case in cases if case["status"] in ("fail", "error")]
    finding_rows = ''.join(f'<li><strong>{text(case["id"])} · {text(case.get("category"))}</strong> — {text(case.get("question"))}</li>' for case in failures[:6])
    if failures:
        extra = f'<p class="muted">Còn {len(failures) - 6} ca cần xem trong bảng chi tiết.</p>' if len(failures) > 6 else ''
        findings = f'<h3>Ca cần xem trước</h3><ul class="priority-list">{finding_rows}</ul>{extra}'
    elif total:
        findings = '<p class="finding-note">Không ghi nhận ca không đạt hoặc lỗi trong các kiểm tra đã chạy. Điều này không chứng minh các khả năng chưa được đo hoặc chất lượng ngoài tập ca.</p>'
    else:
        findings = '<p class="finding-note">Chưa có dữ liệu để kết luận.</p>'
    replacements = {
        "PAGE_TITLE": f"Báo cáo eval · {product}",
        "PRODUCT_NAME": product,
        "MODE_LABEL": text(mode_labels.get(mode, 'CHƯA XÁC ĐỊNH CHẾ ĐỘ')),
        "RUN_METADATA": f'Lượt {text(run.get("id"), "Không ghi mã")} · {timestamp(run.get("started_at"))}',
        "DATASET_LABEL": text(run.get("dataset_label"), "Không ghi tên bộ ca"),
        "SCOPE_NOTE": text(scope_notes.get(mode, 'Chưa ghi chế độ chạy. Không thể xác định đây là kết quả demo, replay hay sản phẩm.')),
        "METRIC_CARDS": cards,
        "RATE_NOTE": f'{ratio} đạt trên {completed} ca có kết luận đạt/không đạt; {tally["error"]} ca lỗi và {tally["not_run"]} ca chưa chạy được báo riêng. Đây là tỷ lệ ca đạt theo bộ kiểm tra, không phải điểm chất lượng ngữ nghĩa tổng hợp.',
        "INTEGRITY_NOTE": integrity,
        "CATEGORY_CHART": category_chart(groups),
        "FINDINGS": findings,
        "JUDGE_SECTION": judge_section(data),
        "CASE_SECTIONS": case_sections(groups),
        "FRAMEWORK_SECTION": framework_section(data.get("frameworks") or [], control_ids),
        "CONTROL_SECTION": control_section(controls),
        "COVERAGE_SECTION": coverage_section(data.get("capability_coverage") or []),
    }
    required = set(re.findall(r"\{\{([A-Z_]+)\}\}", template))
    unknown = required - replacements.keys()
    if unknown:
        raise ValueError(f"Placeholder chưa được hỗ trợ: {', '.join(sorted(unknown))}")
    rendered = re.sub(r"\{\{([A-Z_]+)\}\}", lambda match: replacements[match.group(1)], template)
    return "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="results.json của lượt eval")
    parser.add_argument("--output", type=Path, required=True, help="Báo cáo HTML đích")
    parser.add_argument("--template", type=Path, default=Path(__file__).parent / "templates" / "report-template.html")
    args = parser.parse_args()
    try:
        result = render(load_results(args.input), args.template.read_text(encoding="utf-8"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    except (OSError, ValueError, TypeError) as error:
        print(f"Không tạo được báo cáo: {error}", file=sys.stderr)
        return 2
    print(f"Đã tạo báo cáo: {args.output.name}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
