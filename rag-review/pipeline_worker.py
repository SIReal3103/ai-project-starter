"""Isolated upstream execution. Credentials arrive through stdin, never artifacts."""

import hashlib
import json
import os
from pathlib import Path
import re
import ssl
import sys
import urllib.request

import certifi

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingestion import _require_upstream


def configure_ai_transport():
    import ai_http

    # Some local Python installs lack system CA roots. Keep verification and
    # upstream's fixed destinations / no-redirect policy while adding certifi.
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=certifi.where())
    ai_http.AI_OPENER = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        ai_http.NoAIRedirect(),
        urllib.request.HTTPSHandler(context=context),
    )


def safe_error(error):
    message = str(error)
    http = re.fullmatch(r"AI_HTTP_(\d{3}): request failed; provider body omitted", message)
    if http:
        code = http[1]
        hint = {
            "401": "Key không được chấp nhận. Kiểm tra key của provider đã chọn trong Cấu hình API key.",
            "403": "Provider từ chối quyền truy cập. Kiểm tra quyền tài khoản và model.",
            "429": "Provider giới hạn lượt gọi hoặc hạn mức thanh toán. Kiểm tra quota/billing trước khi thử lại.",
        }.get(code, "Kiểm tra trạng thái dịch vụ và quyền sử dụng model trước khi thử lại.")
        return f"AI_HTTP_{code}: {hint}"
    if message == "AI_NETWORK_ERROR: request failed":
        return "AI_NETWORK_ERROR: Không kết nối được provider. Kiểm tra mạng và chứng chỉ HTTPS của Python."
    if message == "Embedding response contract mismatch":
        return "Phản hồi embedding không khớp model hoặc số lượng yêu cầu. Index chưa được tạo."
    return f"Pipeline không hoàn tất ({type(error).__name__}). Kiểm tra trace, nguồn và cấu hình phiên."


def embeddings(texts, model, dimensions):
    from ai_http import post
    from gateway import endpoint, gateway_key
    from data_pipeline import valid_vector

    vectors, receipts = [], []
    for text in texts:
        raw = post(
            endpoint("embeddings"),
            {"model": model, "input": text},
            gateway_key(),
            max_bytes=8_000_000,
        )
        payload = json.loads(raw)
        data = payload.get("data", [])
        if payload.get("model") != model or len(data) != 1 or data[0].get("index") != 0:
            raise ValueError("Embedding response contract mismatch")
        vectors.append(valid_vector(data[0].get("embedding"), dimensions))
        receipts.append(hashlib.sha256(raw).hexdigest())
    return vectors, {
        "model": model,
        "dimensions": dimensions,
        "inputs": len(texts),
        "response_sha256": receipts,
    }


def prepare_snapshot(folder, scope):
    from trace import TraceStore

    snapshot = json.loads((folder / "approved.json").read_text())
    run = folder / "published"
    (run / "parsed").mkdir(parents=True)
    (run / "raw").mkdir()
    trace = TraceStore(run)
    (run / "approval.json").write_text(json.dumps(snapshot, ensure_ascii=False))
    root = trace.artifact("approval.json", parents=[], stage="human-review")
    for doc in snapshot["documents"]:
        if doc["status"] != "approved":
            raise ValueError("Unapproved snapshot")
        raw = (folder / "originals" / doc["id"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != doc["source_sha256"]:
            raise ValueError("Original integrity failure")
        raw_path = "raw/" + doc["id"]
        (run / raw_path).write_bytes(raw)
        raw_node = trace.artifact(raw_path, parents=[root["id"]], stage="human-review")
        parsed = {
            "title": doc["title"],
            "text": doc["text"],
            "url": doc["source_url"],
            "parser": doc["parser"],
            "raw_sha256": doc["source_sha256"],
            "raw_path": raw_path,
            "status": "review",
            "trace_id": root["id"],
            "parse_warnings": doc["parser_warnings"],
            "parse_partial": doc["partial"],
            "assessment": {
                "human_approval": {
                    "document_id": doc["id"],
                    "revision": doc["revision"],
                    "audit": doc["audit"],
                },
                "factual_confidence": "unverified",
            },
        }
        name = "parsed/" + doc["id"] + ".json"
        (run / name).write_text(json.dumps(parsed, ensure_ascii=False))
        if (
            not doc["edited"]
            and doc.get("segments")
            and all(s.get("locator", {}).get("kind") == "page" for s in doc["segments"])
        ):
            parsed["pages"] = [
                {"page": s["locator"]["page"], "text": s["text"]} for s in doc["segments"]
            ]
            (run / name).write_text(json.dumps(parsed, ensure_ascii=False))
        trace.artifact(name, parents=[raw_node["id"]], stage="save")
    (run / "scope.json").write_text(
        json.dumps({"brief": scope, "planner": "human-review", "ambiguities": []})
    )
    (run / "report.json").write_text(
        json.dumps(
            {
                "status": "human_approved",
                "counts": {"human_approved": len(snapshot["documents"])},
            }
        )
    )
    return run


def execute(request):
    sys.path.insert(0, _require_upstream()["path"])
    provider = request.get("provider", "btc")
    os.environ["AI_PROVIDER"] = provider
    os.environ["BTC_API_KEY" if provider == "btc" else "OPENAI_API_KEY"] = request.pop("key", "")
    folder = Path(request["folder"])
    if request["action"] == "crawl":
        from bot import run_bot, PublicHTTP
        from crawl_transport import CrawlTransport

        original_init = PublicHTTP.__init__

        def initialize(http, *args, **kwargs):
            original_init(http, *args, **kwargs)
            http.opener = CrawlTransport(http)

        PublicHTTP.__init__ = initialize
        if request.get("seed_urls"):
            import bot

            def seeded_discovery(http, plan, search_provider):
                candidates = []
                for url in request["seed_urls"]:
                    node = http.trace.node(
                        "discovery",
                        "Nguồn do người dùng chỉ định",
                        parents=[http.trace_parent],
                        refs={"url": url},
                    )
                    candidates.append(
                        {
                            "url": url,
                            "title": url,
                            "decision": "candidate",
                            "reason": "Nguồn do người dùng chỉ định; chưa xác minh",
                            "lineage_ids": [node["id"]],
                        }
                    )
                return candidates, [
                    {"provider": "user-supplied", "status": "success", "query": plan["brief"]}
                ]

            bot.discover = seeded_discovery

        report, run = run_bot(
            request["scope"],
            folder / "crawl",
            request["max_sources"],
            request["max_pages"],
            request["max_depth"],
            search_provider="duckduckgo",
            planner="rules",
        )
        return {"run": str(run), "summary": report.get("summary"), "status": report["status"]}
    configure_ai_transport()
    from data_pipeline import build, retrieve

    if request["action"] == "build":
        run = prepare_snapshot(folder, request["scope"])
        return build(
            run,
            request["model"],
            request["dimensions"],
            request["max_chunks"],
            request_fn=embeddings,
        )
    return retrieve(folder / "published", request["question"], rerank=False, request_fn=embeddings)


if __name__ == "__main__":
    request = json.load(sys.stdin)
    output = Path(request.pop("result"))
    try:
        result = {"ok": True, "result": execute(request)}
    except Exception as error:
        # Provider exceptions can contain response text. Do not persist it or credentials.
        result = {
            "ok": False,
            "error": safe_error(error),
        }
    output.write_text(json.dumps(result, ensure_ascii=False))
