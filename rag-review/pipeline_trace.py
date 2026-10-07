"""Bounded read-only projection of upstream lineage for the operator UI."""

import json
import re
from urllib.parse import parse_qsl, quote, quote_plus, urlencode, urlsplit, urlunsplit

from store import now

STAGES = {
    "scope": "Xác định phạm vi",
    "search": "Tìm nguồn",
    "discovery": "Chọn nguồn",
    "crawl": "Tải nguồn",
    "parse": "Trích xuất",
    "check": "Kiểm sơ bộ",
    "save": "Lưu dữ liệu",
    "human-review": "Người duyệt",
    "chunk": "Chia đoạn",
    "embedding": "Tạo embedding",
    "index": "Lập chỉ mục",
    "context": "Gói evidence",
    "retrieval": "Chọn đoạn liên quan",
}


def read_json(path):
    try:
        if path.stat().st_size > 20_000_000:
            return None
        return json.loads(path.read_text())
    except (OSError, ValueError):
        # Upstream writes can be observed between truncate and completion.
        return None


def clean(value, secrets):
    text = str(value or "")
    for secret in secrets:
        if secret:
            for representation in (secret, quote(secret, safe=""), quote_plus(secret)):
                text = text.replace(representation, "[KEY ĐÃ ẨN]")
    text = re.sub(
        r"(?i)(bearer\s+|(?:api[_-]?key|token|password|secret)\s*[=:]\s*)[^\s&,;]+",
        r"\1[ĐÃ ẨN]",
        text,
    )
    return text[:1200]


def safe_url(value, secrets):
    if not value:
        return ""
    try:
        p = urlsplit(str(value))
        if p.scheme not in ("http", "https") or not p.hostname:
            return ""
        query = [
            (
                k,
                "[ĐÃ ẨN]"
                if re.search("key|token|secret|password|signature|credential", k, re.I)
                else v,
            )
            for k, v in parse_qsl(p.query, keep_blank_values=True)
        ]
        return clean(urlunsplit((p.scheme, p.hostname, p.path, urlencode(query), "")), secrets)
    except ValueError:
        return ""


def discovery_diagnosis(job, events, issues):
    if (
        job["action"] != "crawl"
        or job["status"] != "no_documents"
        or job.get("seed_urls")
        or job.get("document_ids")
    ):
        return None
    codes = {issue["id"]: issue["code"] for issue in issues}
    blocked = set()
    for event in events:
        try:
            host = urlsplit(event.get("url") or "").hostname or ""
        except ValueError:
            continue
        if (
            host in ("duckduckgo.com", "lite.duckduckgo.com", "html.duckduckgo.com")
            and event["status"] == "failed"
            and codes.get(event.get("issue_id")) == "202"
        ):
            blocked.add(event["issue_id"])
    searches = [event for event in events if event["stage"] == "search"]
    if searches and all(
        event["status"] == "failed" and event.get("issue_id") in blocked for event in searches
    ):
        return {
            "code": "discovery_http_202",
            "stage": "search",
            "title": "Không tìm được nguồn: DuckDuckGo trả HTTP 202",
            "detail": "Các truy vấn tìm kiếm không nhận được kết quả để chọn URL. Chọn Nhập URL nguồn để thử lại, dán link bài viết/PDF rồi crawl. Bước này không dùng key AI; đổi key không xử lý lỗi tìm nguồn.",
        }
    return None


def trace_view(pipeline, identifier):
    job = pipeline.get(identifier)
    with pipeline.credentials.lock:
        try:
            secrets = [v["api_key"] for v in pipeline.credentials._read().values()]
        except ValueError:
            return {
                "job_id": identifier,
                "status": job["status"],
                "events": [],
                "issues": [],
                "message": "Tạm ẩn trace vì không đọc được kho key để lọc dữ liệu nhạy cảm.",
                "updated_at": now(),
                "incomplete": True,
            }
    folder = pipeline.folder / identifier
    runs = (
        sorted((folder / "crawl").glob("*/lineage.json"))
        if job["action"] == "crawl"
        else [folder / "published/lineage.json"]
    )
    lineage = read_json(runs[-1]) if runs else None
    events, issues = [], []
    for node in (lineage or {}).get("nodes", [])[-500:]:
        refs = node.get("refs") or {}
        events.append(
            {
                "id": clean(node.get("id"), secrets),
                "parents": node.get("parents", []),
                "stage": node.get("stage"),
                "stage_label": STAGES.get(node.get("stage"), node.get("stage")),
                "label": clean(node.get("label"), secrets),
                "status": node.get("status"),
                "at": node.get("at"),
                "url": safe_url(refs.get("url"), secrets),
                "path": clean(refs.get("path"), secrets),
                "issue_id": node.get("issue_id"),
            }
        )
    for issue in (lineage or {}).get("issues", [])[-100:]:
        code = clean(issue.get("code"), secrets)
        # Crawl errors describe public fetches. Provider errors may echo request/response bodies.
        message = (
            clean(issue.get("message"), secrets)
            if job["action"] == "crawl"
            else "Bước xử lý thất bại; nội dung phản hồi provider được ẩn để bảo vệ dữ liệu."
        )
        hint = "Kiểm tra URL và nguồn gốc; có thể thử URL bài viết/PDF cụ thể."
        if job["action"] != "crawl":
            hint = clean(job.get("error"), secrets) or "Kiểm tra provider, key và model đã chọn."
        if code == "202":
            hint = "Nguồn trả HTTP 202, chưa có trang nội dung mà crawler chấp nhận. Có thể nhập URL nguồn trực tiếp; không tự vượt trang chặn."
        issues.append(
            {
                "id": clean(issue.get("id"), secrets),
                "node_id": issue.get("detected_at"),
                "stage": STAGES.get(issue.get("detected_stage"), issue.get("detected_stage")),
                "code": code,
                "message": message,
                "hint": hint,
            }
        )
    for i, doc_id in enumerate(job.get("document_ids", [])):
        try:
            doc = pipeline.store.get(doc_id)
        except KeyError:
            continue
        events.append(
            {
                "id": f"import-{i + 1}",
                "parents": [],
                "stage": "human-review",
                "stage_label": "Đưa vào hàng chờ",
                "label": clean(doc["title"], secrets),
                "status": "success",
                "at": doc["created_at"],
                "url": safe_url(doc.get("source_url"), secrets),
                "document_id": doc_id,
                "document_status": doc["status"],
            }
        )
    running = [e for e in events if e["status"] == "running"]
    current = running[-1] if running and job["status"] == "running" else None
    return {
        "job_id": identifier,
        "status": job["status"],
        "updated_at": now(),
        "incomplete": lineage is None,
        "current": current,
        "events": events,
        "issues": issues,
        "diagnosis": discovery_diagnosis(job, events, issues),
        "total_nodes": len((lineage or {}).get("nodes", [])),
        "message": (
            "Chưa có trace hoàn chỉnh; worker đang khởi tạo hoặc ghi dữ liệu."
            if job["status"] == "running"
            else "Không có trace đọc được cho phiên này."
        )
        if lineage is None
        else "Trace từ lần ghi gần nhất; thời gian mỗi bước là thời điểm bắt đầu. Chỉ hiển thị tối đa 500 bước gần nhất.",
    }
