"""Local operator credentials, separate from documents and never returned to the UI."""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

PROVIDERS = (
    {
        "id": "btc",
        "group": "btc",
        "name": "BTC · Thực Chiến",
        "variable": "BTC_API_KEY",
        "description": "Key riêng cho gateway api.thucchien.ai. Không dùng key nhà cung cấp thay thế.",
    },
    {
        "id": "openai",
        "group": "external",
        "name": "OpenAI",
        "variable": "OPENAI_API_KEY",
        "description": "Key OpenAI riêng, tách biệt hoàn toàn với BTC.",
    },
    {
        "id": "google",
        "group": "external",
        "name": "Google · Gemini / Veo",
        "variable": "GOOGLE_API_KEY",
        "description": "Key Google riêng. Quyền dùng Gemini/Veo phụ thuộc tài khoản và dịch vụ; chưa kiểm chứng.",
    },
    {
        "id": "anthropic",
        "group": "external",
        "name": "Anthropic · Claude",
        "variable": "ANTHROPIC_API_KEY",
        "description": "Key Anthropic riêng cho Claude.",
    },
    {
        "id": "deepseek",
        "group": "external",
        "name": "DeepSeek",
        "variable": "DEEPSEEK_API_KEY",
        "description": "Key DeepSeek riêng; khác với truy cập DeepSeek qua BTC.",
    },
)
PROVIDER_IDS = {provider["id"] for provider in PROVIDERS}


class CredentialStore:
    def __init__(self, data_dir):
        self.directory = Path(data_dir) / "credentials"
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.directory.chmod(0o700)
        self.path = self.directory / "providers.json"
        self.lock = RLock()

    def _read(self):
        if not self.path.exists():
            return {}
        try:
            self.path.chmod(0o600)
            record = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(record, dict) or any(
                provider not in PROVIDER_IDS
                or not isinstance(value, dict)
                or not isinstance(value.get("api_key"), str)
                or not isinstance(value.get("updated_at"), str)
                for provider, value in record.items()
            ):
                raise ValueError
            return record
        except (OSError, ValueError):
            raise ValueError(
                "Không đọc được kho key local. Giữ nguyên file để kiểm tra/khôi phục."
            ) from None

    def _write(self, record):
        descriptor, filename = tempfile.mkstemp(prefix=".providers-", dir=self.directory)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                os.fchmod(stream.fileno(), 0o600)
                json.dump(record, stream, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(filename, self.path)
        finally:
            Path(filename).unlink(missing_ok=True)

    def summary(self):
        with self.lock:
            record = self._read()
            return {
                "providers": [
                    {
                        **provider,
                        "configured": provider["id"] in record,
                        "updated_at": record.get(provider["id"], {}).get("updated_at"),
                        "connection_status": "not_tested",
                    }
                    for provider in PROVIDERS
                ],
                "storage": "local-file-0600",
                "ai_enabled": False,
            }

    def put(self, provider, key):
        if provider not in PROVIDER_IDS:
            raise ValueError("Nhà cung cấp không được hỗ trợ.")
        if not isinstance(key, str):
            raise ValueError("Key phải là chuỗi văn bản.")
        key = key.strip()
        if not 8 <= len(key) <= 4096 or any(c.isspace() or ord(c) < 32 for c in key):
            raise ValueError("Key cần 8–4.096 ký tự, không có khoảng trắng hoặc ký tự điều khiển.")
        with self.lock:
            record = self._read()
            record[provider] = {
                "api_key": key,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            self._write(record)
            return self.summary()

    def secret(self, provider):
        with self.lock:
            key = self._read().get(provider, {}).get("api_key")
            if not key:
                raise ValueError("Chưa lưu key cho " + provider + ". Mở Cấu hình API key.")
            return key

    def reset(self):
        with self.lock:
            self._write({})
            return self.summary()

    def remove(self, provider):
        if provider not in PROVIDER_IDS:
            raise ValueError("Nhà cung cấp không được hỗ trợ.")
        with self.lock:
            record = self._read()
            record.pop(provider, None)
            self._write(record)
            return self.summary()
