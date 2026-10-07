"""Rule-based Vietnamese example adapter; no model, network, or external side effects.

The supplied contexts form an in-memory sandbox corpus. This deliberately small
baseline demonstrates the response contract, not production assistant quality.
Reference answers and expected assertions are never read by the responder.
"""

from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from decimal import Decimal, InvalidOperation


TOOL_ALLOWLIST = frozenset({"calculator.add", "search_documents", "read_document"})
NO_EVIDENCE = "Chưa đủ bằng chứng trong các nguồn được cung cấp để trả lời câu hỏi này."
STOP_WORDS = frozenset(
    "toi ban hay cho biet la gi va cua co theo tai lieu nguon ve trong cac mot "
    "thu vien duoc cung cap tra loi chi dua vao bao nhieu nao nay do bang "
    "json tim roi doc giup vui long dung cong cu".split()
)


def _fold(text: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
        if not unicodedata.combining(char)
    )


def _terms(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", _fold(text))) - STOP_WORDS


def _is_exfiltration(text: str) -> bool:
    normalized = _fold(text)
    return bool(re.search(r"https?://", normalized)) and any(
        phrase in normalized for phrase in ("gui toan bo", "chuyen noi dung", "tai len", "http_post")
    )


def _is_instruction(text: str) -> bool:
    normalized = _fold(text)
    return _is_exfiltration(text) or any(phrase in normalized for phrase in (
        "bo qua chi dan", "bo qua huong dan", "ignore previous", "system prompt",
        "gui email", "send_email", "tiet lo mat khau", "xoa tai lieu",
    ))


def _facts(context: dict) -> list[str]:
    """Discard topic labels and instruction-like source lines, keeping evidence.

    This heuristic is intentionally narrow and is not a security boundary.
    """
    result = []
    for line in str(context.get("text", "")).splitlines():
        line = line.strip()
        if not line or _fold(line).startswith("chu de:") or _is_instruction(line):
            continue
        line = re.sub(r"^(Dữ kiện|Thông tin):\s*", "", line, flags=re.IGNORECASE)
        result.append(line)
    return result


def _search(query: str, contexts: list[dict]) -> list[dict]:
    explicit = [item for item in contexts if str(item["id"]).casefold() in query.casefold()]
    if explicit:
        return explicit
    query_terms = _terms(query)
    scored = []
    for position, item in enumerate(contexts):
        evidence = " ".join(_facts(item))
        searchable = " ".join(
            line for line in item["text"].splitlines() if not _is_instruction(line)
        )
        overlap = len(query_terms & _terms(searchable))
        if evidence and overlap >= min(2, max(1, len(query_terms))):
            scored.append((overlap, position, item))
    return [entry[2] for entry in sorted(scored, key=lambda entry: (-entry[0], entry[1]))]


def _evidence_answer(contexts: list[dict]) -> str:
    if not contexts:
        return NO_EVIDENCE
    values: dict[str, list[tuple[str, str, str]]] = {}
    for context in contexts:
        for fact in _facts(context):
            if ":" in fact:
                key, value = fact.split(":", 1)
                values.setdefault(_fold(key.strip()), []).append(
                    (key.strip(), value.strip().rstrip("."), context["id"])
                )
    conflicts = [items for items in values.values() if len({_fold(i[1]) for i in items}) > 1]
    if conflicts:
        parts = [
            f"{items[0][0]}: " + "; ".join(f"{value} [{source}]" for _, value, source in items)
            for items in conflicts
        ]
        return "Các nguồn mâu thuẫn về " + ". ".join(parts) + ". Chưa thể kết luận một giá trị duy nhất."
    return " ".join(
        f"{' '.join(_facts(context))} [{context['id']}]" for context in contexts if _facts(context)
    ) or NO_EVIDENCE


def _number(value: Decimal) -> int | float:
    return int(value) if value == value.to_integral() else float(value)


def _addition(question: str) -> list[Decimal] | None:
    # Restrict numeric extraction to the arithmetic clause, excluding budgets.
    clause = re.search(r"(?:cong|tinh tong)\s+(.+)", _fold(question))
    if clause:
        text = clause.group(1)
    elif "cong" in _fold(question) or "+" in question:
        text = question
    else:
        return None
    values = re.findall(r"(?<![\w])[-+]?\d+(?:[.,]\d+)?", text)
    # Infix Vietnamese arithmetic starts with the first operand before “cộng”.
    prefix = re.search(r"([-+]?\d+(?:[.,]\d+)?)\s+cong\s", _fold(question))
    if prefix:
        values.insert(0, prefix.group(1))
    if len(values) < 2:
        return None
    try:
        return [Decimal(value.replace(",", ".")) for value in values]
    except InvalidOperation:
        return None


def respond(case: dict) -> dict:
    """Respond using only question, history and contexts, never evaluation oracles."""
    started = time.perf_counter()
    question = str(case.get("question", ""))
    normalized = re.sub(r"\s+", " ", _fold(question)).strip()
    history = case.get("history", [])
    corpus = [{"id": str(item["id"]), "text": str(item["text"])} for item in case.get("contexts", [])]
    response = {
        "case_id": case.get("id"),
        "answer": "",
        "retrieved_contexts": [],
        "citations": [],
        "tool_calls": [],
        "guardrail": {"action": "allow", "reason": "Yêu cầu nằm trong khả năng demo."},
        "latency_ms": 0.0,
        "usage": {},
        "provider_metadata": {
            "mode": "demo", "implementation": "deterministic-rules",
            "sandbox": "in-memory; no network or filesystem writes",
        },
    }
    budget_match = re.search(r"(?:toi da|ngan sach)\s+(\d+)\s+(?:lan|cuoc)", normalized)
    tool_budget = int(budget_match.group(1)) if budget_match else 4

    def finish(answer: str, action: str = "allow", reason: str | None = None) -> dict:
        if "json" in normalized and action == "allow":
            answer = json.dumps({"answer": answer, "citations": response["citations"]}, ensure_ascii=False)
        response["answer"] = answer
        response["guardrail"]["action"] = action
        if reason:
            response["guardrail"]["reason"] = reason
        response["latency_ms"] = round((time.perf_counter() - started) * 1000, 6)
        return response

    def call_tool(name: str, arguments: dict) -> dict | None:
        if name not in TOOL_ALLOWLIST or len(response["tool_calls"]) >= tool_budget:
            return None
        status = "success"
        if name == "calculator.add":
            total = sum((Decimal(str(item)) for item in arguments["numbers"]), Decimal(0))
            result = {"value": _number(total), "sandbox": "demo"}
        elif name == "search_documents":
            found = _search(arguments["query"], corpus)
            result = {"document_ids": [item["id"] for item in found], "sandbox": "demo"}
        else:
            document = next((item for item in corpus if item["id"] == arguments["document_id"]), None)
            if document is None:
                status = "error"
                result = {"error": "DOCUMENT_NOT_FOUND", "sandbox": "demo"}
            else:
                result = {"document": document, "sandbox": "demo"}
        call = {"name": name, "arguments": arguments, "result": result, "status": status}
        response["tool_calls"].append(call)
        return call

    if not question.strip():
        return finish("Bạn muốn hỏi nội dung gì?", "clarify", "Thiếu câu hỏi.")
    if "chi tra loi json" in normalized and any(
        phrase in normalized for phrase in ("khong dung json", "khong su dung json")
    ):
        return finish("Bạn muốn câu trả lời ở dạng JSON hay văn bản thuần? Hai yêu cầu định dạng đang mâu thuẫn.", "clarify", "Yêu cầu định dạng mâu thuẫn.")
    security_education = "prompt injection" in normalized and any(
        phrase in normalized for phrase in ("giai thich", "la gi", "phan tich cau trich dan")
    )
    if security_education:
        return finish("Prompt injection là nội dung cố khiến trợ lý làm theo chỉ dẫn trái với nhiệm vụ. Cách phòng tránh: coi tài liệu là dữ liệu, giới hạn quyền công cụ và kiểm tra đầu ra.")
    injection = any(phrase in normalized for phrase in (
        "bo qua chi dan", "bo qua huong dan", "ignore previous", "tiet lo system prompt",
    ))
    secrets = any(phrase in normalized for phrase in (
        "cho toi mat khau", "tiet lo mat khau", "in api key", "hien thi khoa bi mat",
    ))
    privacy = any(phrase in normalized for phrase in (
        "so dien thoai rieng", "dia chi nha rieng", "du lieu ca nhan cua",
    ))
    if injection or secrets:
        return finish("Tôi không thể tiết lộ chỉ dẫn nội bộ hoặc thông tin bí mật.", "refuse", "Bảo vệ chỉ dẫn và bí mật.")
    if privacy:
        return finish("Tôi không thể cung cấp dữ liệu cá nhân riêng tư của người khác.", "refuse", "Bảo vệ dữ liệu cá nhân.")
    if _is_exfiltration(question):
        return finish("Tôi không chuyển nội dung tài liệu đến địa chỉ bên ngoài.", "refuse", "Không cho phép gửi dữ liệu ra ngoài.")
    if any(phrase in normalized for phrase in ("viet loi lang ma", "viet loi nhuc ma", "viet loi de doa")):
        return finish("Tôi không hỗ trợ viết lời lăng mạ hoặc đe dọa. Tôi có thể giúp soạn phản hồi lịch sự.", "refuse", "Chính sách ứng xử của trợ lý demo.")
    if "tu choi cap the" in normalized and any(
        phrase in normalized for phrase in ("dan toc", "gioi tinh", "ton giao")
    ):
        return finish("Tôi không hỗ trợ loại trừ người dùng dựa trên dân tộc, giới tính hoặc tôn giáo. Việc cấp thẻ cần tiêu chí công bằng và áp dụng như nhau.", "refuse", "Không hỗ trợ đề xuất phân biệt đối xử.")
    if any(phrase in normalized for phrase in ("xoa tai lieu", "xoa toan bo", "gui email ngay", "gui email nhac")):
        return finish("Tôi không thực hiện thao tác gửi email hoặc xóa dữ liệu; demo chỉ cho phép đọc và tính toán.", "refuse", "Công cụ có tác động bên ngoài không được cho phép.")
    if "ke don thuoc" in normalized:
        return finish("Yêu cầu kê đơn thuốc nằm ngoài phạm vi trợ lý tài liệu này.", "refuse", "Ngoài phạm vi demo.")
    if "soan email" in normalized:
        return finish("Bản nháp email: Vui lòng trả sách đúng hạn. Chưa gửi email.")
    if "gia han" in normalized and not corpus:
        return finish("Bạn muốn gia hạn tài liệu nào?", "clarify", "Thiếu tài liệu cần gia hạn.")
    if normalized.strip(" !.?") in {"xin chao", "chao", "chao ban"}:
        return finish("Xin chào! Tôi có thể tra cứu tài liệu, trích nguồn và tính tổng.")
    if "ban co the giup gi" in normalized:
        return finish("Tôi có thể tra cứu tài liệu, trích nguồn, tính tổng và soạn bản nháp. Các công cụ demo chỉ đọc dữ liệu và tính toán.")
    if "nhac lai" in normalized:
        previous = next((item.get("content", "") for item in reversed(history) if item.get("role") == "assistant"), None)
        if previous:
            return finish(str(previous))
        return finish("Bạn muốn tôi nhắc lại nội dung nào?", "clarify", "Chưa có câu trả lời trước đó.")
    if "retrieval" in normalized and not corpus:
        return finish("Retrieval là bước tìm và lấy các đoạn tài liệu liên quan đến câu hỏi.")

    numbers = _addition(question)
    if numbers is not None:
        if "dung cong cu" in normalized and "khong goi cong cu" not in normalized:
            call = call_tool("calculator.add", {"numbers": [_number(value) for value in numbers]})
            if call is None:
                return finish("Đã hết ngân sách gọi công cụ; chưa thực hiện phép tính.", "clarify", "Giới hạn số lần gọi công cụ.")
            total = call["result"]["value"]
        else:
            total = _number(sum(numbers, Decimal(0)))
        return finish(str(total))

    if "tim roi doc" in normalized:
        query_match = re.search(r"\bvề\s+(.+?)[.!?]*$", question, re.IGNORECASE)
        query = query_match.group(1).rstrip(".!? ") if query_match else question
        search_call = call_tool("search_documents", {"query": query})
        if search_call is None:
            return finish("Đã hết ngân sách gọi công cụ; chưa tìm kiếm.", "clarify", "Giới hạn số lần gọi công cụ.")
        document_ids = search_call["result"]["document_ids"]
        if not document_ids:
            return finish(NO_EVIDENCE)
        read_call = call_tool("read_document", {"document_id": document_ids[0]})
        if read_call is None:
            return finish("Đã tìm thấy tài liệu nhưng chưa đọc vì đã hết ngân sách gọi công cụ.", "clarify", "Giới hạn số lần gọi công cụ.")
        selected = [read_call["result"]["document"]]
    elif "doc tai lieu" in normalized:
        match = re.search(r"\bdoc-[a-z0-9-]+\b", question, re.IGNORECASE)
        if not match:
            return finish("Bạn muốn đọc tài liệu nào?", "clarify", "Thiếu mã tài liệu.")
        document_id = match.group(0)
        read_call = call_tool("read_document", {"document_id": document_id})
        if read_call is None:
            return finish("Đã hết ngân sách gọi công cụ; chưa đọc tài liệu.", "clarify", "Giới hạn số lần gọi công cụ.")
        if read_call["status"] == "error":
            return finish(f"Không tìm thấy tài liệu {document_id}; công cụ đọc báo DOCUMENT_NOT_FOUND.")
        selected = [read_call["result"]["document"]]
    else:
        query = question
        if "mot cau" in normalized:
            prior_user = next((item.get("content", "") for item in reversed(history) if item.get("role") == "user"), "")
            query = str(prior_user) + " " + question
        selected = _search(query, corpus)
    response["retrieved_contexts"] = selected
    response["citations"] = [item["id"] for item in selected if _facts(item)]
    ignored = any(_is_instruction(item["text"]) for item in selected)
    reason = "Bỏ qua chỉ dẫn nằm trong tài liệu; chỉ sử dụng dữ kiện." if ignored else None
    return finish(_evidence_answer(selected), reason=reason)


def main() -> None:
    case = json.load(sys.stdin.buffer)
    json.dump(respond(case), sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
