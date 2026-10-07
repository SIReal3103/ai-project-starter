"""Provider diagnostics and transport configuration without paid calls."""

from pathlib import Path
import subprocess
import sys

import pytest

from ingestion import _worker_environment
from pipeline_worker import safe_error


@pytest.mark.parametrize("code", ["401", "403", "429", "503"])
def test_provider_status_is_actionable_without_echoing_bodies(code):
    result = safe_error(ValueError(f"AI_HTTP_{code}: request failed; provider body omitted"))
    assert f"AI_HTTP_{code}" in result
    assert "Kiểm tra" in result


def test_unknown_provider_messages_are_not_persisted():
    secret = "private-request-body-and-key"
    for value in [secret, "AI_HTTP_401: " + secret, "AI_NETWORK_ERROR: " + secret]:
        assert secret not in safe_error(ValueError(value))
    assert "HTTPS" in safe_error(ValueError("AI_NETWORK_ERROR: request failed"))


def test_ai_adapter_keeps_certificate_verification_and_redirect_blocking():
    program = """import sys,ssl,urllib.request
sys.path.insert(0,sys.argv[1])
from ingestion import _require_upstream
sys.path.insert(0,_require_upstream()['path'])
from pipeline_worker import configure_ai_transport
import ai_http
configure_ai_transport()
https=next(h for h in ai_http.AI_OPENER.handlers if isinstance(h,urllib.request.HTTPSHandler))
assert https._context.verify_mode == ssl.CERT_REQUIRED
assert https._context.check_hostname
redirect=next(h for h in ai_http.AI_OPENER.handlers if isinstance(h,ai_http.NoAIRedirect))
try: redirect.redirect_request(None,None,302,'',{},'https://example.com/')
except ValueError: pass
else: raise AssertionError('AI redirects must remain blocked')
try: ai_http.post('https://example.com/embeddings',{},'test-only')
except ValueError as e: assert 'allowlist' in str(e)
else: raise AssertionError('Destination must remain restricted')
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", program, str(Path(__file__).resolve().parents[1])],
        capture_output=True,
        text=True,
        env=_worker_environment(),
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
