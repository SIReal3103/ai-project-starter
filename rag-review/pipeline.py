"""Persisted local jobs bridging upstream crawls and human-approved snapshots."""

import hashlib
import json
import mimetypes
from pathlib import Path
import subprocess
import sys
from threading import Lock, Thread
from uuid import uuid4

from ingestion import _worker_environment, _require_upstream, MAX_BYTES, MAX_TEXT
from ingestion import _public_target
from store import Conflict, now, today, canonical_date

MODELS = {
    "btc": ("text-multilingual-embedding-002", 768),
    "openai": ("text-embedding-3-small", 1536),
}


def fingerprint(documents):
    return sorted(
        (d["id"], d["revision"], hashlib.sha256(d["text"].encode()).hexdigest()) for d in documents
    )


class Pipeline:
    def __init__(self, store, credentials):
        self.store, self.credentials = store, credentials
        self.folder = store.folder / "pipeline"
        self.folder.mkdir(exist_ok=True)
        self.lock = Lock()
        self.busy = False
        for path in self.folder.glob("*/job.json"):
            job = json.loads(path.read_text())
            if job["status"] == "running":
                job.update(
                    status="interrupted",
                    error="Server khởi động lại. Tạo phiên mới; tài liệu đã nhập vẫn được giữ.",
                )
                self.save(job)

    def save(self, job):
        folder = self.folder / job["id"]
        folder.mkdir(exist_ok=True)
        path = folder / "job.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(job, ensure_ascii=False))
        temporary.replace(path)

    def get(self, identifier):
        if (
            not isinstance(identifier, str)
            or len(identifier) != 32
            or any(c not in "0123456789abcdef" for c in identifier)
        ):
            raise ValueError("Mã phiên không hợp lệ.")
        path = self.folder / identifier / "job.json"
        if not path.exists():
            raise KeyError(identifier)
        return json.loads(path.read_text())

    def list(self):
        return sorted(
            (json.loads(p.read_text()) for p in self.folder.glob("*/job.json")),
            key=lambda j: j["created_at"],
            reverse=True,
        )

    def eligible(self, job):
        return self.store.export(job["collection"], job["as_of"])["documents"]

    def assert_current(self, job):
        if job["as_of"] != today() or fingerprint(self.eligible(job)) != [
            tuple(x) for x in job["approved_versions"]
        ]:
            raise Conflict(
                "Index đã cũ do thay đổi tài liệu/hiệu lực. Tạo lại index trước khi lấy evidence."
            )

    def worker(self, request, key=""):
        folder = Path(request["folder"])
        result = folder / ("result-" + uuid4().hex + ".json")
        payload = {**request, "key": key, "result": str(result)}
        try:
            subprocess.run(
                [sys.executable, "-I", str(Path(__file__).with_name("pipeline_worker.py"))],
                input=json.dumps(payload),
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=_worker_environment(),
                timeout=1800,
                check=True,
            )
            response = json.loads(result.read_text())
            if not response["ok"]:
                raise ValueError(response["error"])
            return response["result"]
        except (subprocess.SubprocessError, OSError):
            raise ValueError(
                "Pipeline hết thời gian hoặc worker dừng. Tạo phiên mới để thử lại."
            ) from None
        finally:
            result.unlink(missing_ok=True)

    def start(self, payload):
        _require_upstream()
        action = payload.get("action")
        collection = payload.get("collection", "")
        scope = payload.get("scope", "")
        if (
            action not in ("crawl", "build")
            or not isinstance(collection, str)
            or not 1 <= len(collection.strip()) <= 100
            or not isinstance(scope, str)
            or not 12 <= len(scope.strip()) <= 8000
        ):
            raise ValueError("Cần tác vụ crawl/build, bộ tài liệu và phạm vi 12–8.000 ký tự.")
        job = {
            "id": uuid4().hex,
            "action": action,
            "collection": collection.strip(),
            "scope": scope.strip(),
            "created_at": now(),
            "status": "running",
            "document_ids": [],
            "errors": [],
        }
        key = ""
        if action == "crawl":
            seeds = payload.get("seed_urls", [])
            if not isinstance(seeds, list) or len(seeds) > 10:
                raise ValueError("Tối đa 10 URL nguồn.")
            for url in seeds:
                if not isinstance(url, str) or len(url) > 2048:
                    raise ValueError("URL nguồn không hợp lệ.")
                _public_target(url)
            job["seed_urls"] = list(dict.fromkeys(seeds))
            for name, default, high in (
                ("max_sources", 3, 10),
                ("max_pages", 10, 30),
                ("max_depth", 1, 2),
            ):
                value = payload.get(name, default)
                if type(value) is not int or not (0 if name == "max_depth" else 1) <= value <= high:
                    raise ValueError("Giới hạn crawl không hợp lệ.")
                job[name] = value
        else:
            provider = payload.get("provider", "btc")
            if provider not in MODELS:
                raise ValueError("Chọn BTC hoặc OpenAI; không tự chuyển provider.")
            job.update(
                provider=provider,
                model=MODELS[provider][0],
                dimensions=MODELS[provider][1],
                max_chunks=400,
                as_of=today(),
            )
            canonical_date(job["as_of"])
            key = self.credentials.secret(provider)
            docs = self.eligible(job)
            if not docs:
                raise ValueError("Chưa có tài liệu đã duyệt còn hiệu lực trong bộ này.")
            job["approved_versions"] = fingerprint(docs)
        with self.lock:
            if self.busy:
                raise Conflict("Một tác vụ pipeline đang chạy. Đợi hoàn tất rồi thử lại.")
            self.busy = True
            try:
                self.save(job)
                if action == "build":
                    originals = self.folder / job["id"] / "originals"
                    originals.mkdir()
                    for doc in docs:
                        raw = (self.store.raw / doc["id"]).read_bytes()
                        if hashlib.sha256(raw).hexdigest() != doc["source_sha256"]:
                            raise ValueError("Bản gốc thay đổi; dừng xuất index.")
                        (originals / doc["id"]).write_bytes(raw)
                    (self.folder / job["id"] / "approved.json").write_text(
                        json.dumps({"documents": docs}, ensure_ascii=False)
                    )
                Thread(target=self.run, args=(job, key), daemon=True).start()
            except BaseException:
                job.update(
                    status="failed",
                    error="Không tạo được snapshot; kiểm tra bản gốc và dung lượng lưu trữ.",
                )
                self.save(job)
                self.busy = False
                raise
        return job

    def import_run(self, job, run):
        run = Path(run).resolve()
        if not run.is_relative_to((self.folder / job["id"] / "crawl").resolve()):
            raise ValueError("Thư mục crawl ngoài phiên.")
        report = json.loads((run / "report.json").read_text())
        fetch_path = run / "fetch-manifest.json"
        fetches = json.loads(fetch_path.read_text()) if fetch_path.exists() else []
        entries = list(report.get("documents", []))
        entries.extend(
            {"parsed_path": str(p.relative_to(run))}
            for p in sorted((run / "parsed").glob("series-*.json"))
        )
        for entry in entries:
            relative = entry.get("parsed_path") or entry.get("unassessed_path")
            if entry.get("status") == "out_of_scope" or (
                not relative and not entry.get("raw_path")
            ):
                continue
            try:
                if relative:
                    path = (run / relative).resolve()
                    if not path.is_relative_to(run) or path.stat().st_size > 20_000_000:
                        raise ValueError("Parsed artifact không hợp lệ")
                    parsed = json.loads(path.read_text())
                else:
                    record = next(
                        r
                        for r in fetches
                        if r.get("raw_path") == entry["raw_path"] and r.get("status") == "success"
                    )
                    parsed = {
                        "text": "",
                        "parser": "extraction-failed",
                        "raw_path": record["raw_path"],
                        "raw_sha256": record["sha256"],
                        "url": record.get("final_url", entry.get("url")),
                        "status": "failed",
                        "parse_warnings": [
                            "Không trích được nội dung; đối chiếu bản gốc và bổ sung văn bản trước khi duyệt."
                        ],
                    }
                rows = parsed.get("rows") or []
                if rows and not parsed.get("raw_path"):
                    parsed["raw_path"] = rows[0]["raw_path"]
                    parsed["raw_sha256"] = rows[0]["raw_sha256"]
                    parsed["title"] = parsed.get("indicator", {}).get("name", "Bảng số liệu")
                raw = (run / parsed["raw_path"]).resolve()
                if not raw.is_relative_to(run) or raw.stat().st_size > MAX_BYTES:
                    raise ValueError("Raw artifact không hợp lệ")
                body = raw.read_bytes()
                if hashlib.sha256(body).hexdigest() != parsed["raw_sha256"]:
                    raise ValueError("Source hash mismatch")
                text = parsed.get("text") or (json.dumps(rows, ensure_ascii=False) if rows else "")
                if len(text) > MAX_TEXT:
                    raise ValueError("Text quá lớn")
                if parsed.get("tables") and not parsed.get("pages"):
                    text += "\n\nBảng trích xuất (cần đối chiếu bản gốc):\n" + json.dumps(
                        parsed["tables"], ensure_ascii=False
                    )
                if len(text) > MAX_TEXT:
                    raise ValueError("Text và bảng quá lớn")
                segments = [
                    {"text": p["text"], "locator": {"kind": "page", "page": p["page"]}}
                    for p in parsed.get("pages", [])
                    if p.get("text")
                ]
                if text and not segments:
                    segments = [{"text": text, "locator": {"kind": "document_text"}}]
                doc = self.store.create(
                    body,
                    {
                        "text": text,
                        "parser": parsed.get("parser", "scope-data-bot"),
                        "segments": segments,
                        "warnings": [str(w) for w in parsed.get("parse_warnings", [])],
                        "partial": parsed.get("parse_partial", False),
                    },
                    {
                        "title": str(parsed.get("title") or entry.get("title") or "Tài liệu crawl")[
                            :300
                        ],
                        "collection": job["collection"],
                        "source_id": "url-"
                        + hashlib.sha256(str(parsed.get("url", "")).encode()).hexdigest()[:24],
                        "document_version": job["id"],
                    },
                    source_kind="web",
                    filename=raw.name,
                    mime="application/pdf"
                    if body.startswith(b"%PDF-")
                    else (mimetypes.guess_type(raw.name)[0] or "text/plain"),
                    source_url=parsed.get("url"),
                    crawl={
                        "job_id": job["id"],
                        "upstream_status": parsed.get("status"),
                        "assessment": parsed.get("assessment"),
                        "parsed_path": relative,
                    },
                )
                job["document_ids"].append(doc["id"])
            except (ValueError, KeyError, OSError, TypeError, StopIteration):
                job["errors"].append(
                    "Không nhập được một tài liệu: kiểm tra cấu trúc, kích thước hoặc hash nguồn."
                )
            self.save(job)
        job["crawl_summary"] = report.get("summary", "")
        job["crawl_counts"] = report.get("counts", {})

    def run(self, job, key):
        try:
            result = self.worker({**job, "folder": str(self.folder / job["id"])}, key)
            if job["action"] == "crawl":
                self.import_run(job, result["run"])
                job["status"] = "needs_review" if job["document_ids"] else "no_documents"
            else:
                self.assert_current(job)
                job["manifest"] = result
                job["status"] = "ready"
        except Exception as error:
            job.update(
                status="failed",
                error=str(error)
                if isinstance(error, (ValueError, Conflict))
                else "Lỗi pipeline nội bộ.",
            )
        finally:
            job["finished_at"] = now()
            self.save(job)
            with self.lock:
                self.busy = False

    def evidence(self, identifier, question):
        job = self.get(identifier)
        if job["action"] != "build" or job["status"] != "ready":
            raise Conflict("Index chưa sẵn sàng.")
        if not isinstance(question, str) or not 1 <= len(question.strip()) <= 8000:
            raise ValueError("Câu hỏi cần 1–8.000 ký tự.")
        self.assert_current(job)
        result = self.worker(
            {
                **job,
                "action": "retrieve",
                "question": question,
                "folder": str(self.folder / identifier),
            },
            self.credentials.secret(job["provider"]),
        )
        self.assert_current(job)
        path = self.folder / identifier / "last-evidence.json"
        temporary = path.with_name("last-evidence-" + uuid4().hex + ".tmp")
        temporary.write_text(
            json.dumps(
                {"question": question, "created_at": now(), "bundle": result}, ensure_ascii=False
            )
        )
        temporary.replace(path)
        return result

    def last_evidence(self, identifier):
        job = self.get(identifier)
        if job["action"] != "build" or job["status"] != "ready":
            raise Conflict("Index chưa sẵn sàng.")
        # Saved context has the same withdrawal/expiry gate as a new query.
        self.assert_current(job)
        path = self.folder / identifier / "last-evidence.json"
        result = json.loads(path.read_text()) if path.exists() else None
        self.assert_current(job)
        return result
