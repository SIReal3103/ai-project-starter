#!/usr/bin/env python3
"""Readiness probe: executable versions only, never a product test."""

import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

root = Path(
    os.environ.get("QA_TOOLS_ROOT", str(Path.home() / ".local/share/ai-qa-tools"))
)
node = root / "node/node_modules/.bin"
local = Path.home() / ".local/bin"
commands = {
    "pytest": [str(root / "bin/qa-pytest"), "--version"],
    "coverage.py": [str(root / "bin/qa-coverage"), "--version"],
    "ruff": [str(root / "bin/ruff"), "--version"],
    "vitest": [str(node / "vitest"), "--version"],
    "playwright": [str(node / "playwright"), "--version"],
    "promptfoo": [str(root / "bin/promptfoo"), "--version"],
    "semgrep": [str(local / "semgrep"), "--version"],
    "bandit": [str(local / "bandit"), "--version"],
    "pip-audit": [str(local / "pip-audit"), "--version"],
    "gitleaks": [shutil.which("gitleaks") or "gitleaks", "version"],
    "k6": [shutil.which("k6") or "k6", "version"],
    "trivy": [shutil.which("trivy") or "trivy", "--version"],
    "zap": [str(root / "bin/qa-zap"), "-version"],
    "ffmpeg": [shutil.which("ffmpeg") or "ffmpeg", "-version"],
    "ffprobe": [shutil.which("ffprobe") or "ffprobe", "-version"],
}
for name, runtime in [("ragas", "python"), ("deepeval", "extended-python")]:
    commands[name] = [
        os.environ.get(
            "EVAL_" + name.upper() + "_PYTHON",
            str(
                Path.home()
                / ".local/share/scope-data-bot-eval"
                / runtime
                / "bin/python"
            ),
        ),
        "-I",
        "-c",
        f"from importlib.metadata import version; print(version({name!r}))",
    ]
env = os.environ.copy()
env.update(
    {
        "SEMGREP_SEND_METRICS": "off",
        "SEMGREP_ENABLE_VERSION_CHECK": "0",
        "PROMPTFOO_DISABLE_TELEMETRY": "1",
        "PROMPTFOO_DISABLE_UPDATE": "1",
    }
)


def probe(item):
    name, args = item
    try:
        p = subprocess.run(
            args,
            check=False,
            env=env,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=45,
        )
        lines = (p.stdout or p.stderr).strip().splitlines()
        return {
            "tool": name,
            "ready": p.returncode == 0,
            "exit_code": p.returncode,
            "version_output": lines[:3],
        }
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {"tool": name, "ready": False, "error": str(e)}


with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(probe, commands.items()))
print(
    json.dumps(
        {
            "scope": "version/launcher readiness, not product acceptance",
            "results": results,
        },
        ensure_ascii=False,
        indent=2,
    )
)
sys.exit(0 if all(r["ready"] for r in results) else 1)
