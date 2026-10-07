#!/bin/sh
# Optional QA packages on an already mounted APFS QA volume.
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(CDPATH= cd -- "$script_dir/.." && pwd)
selection=${1:-core}
case "$selection" in
  core|evals|security|zap|all) ;;
  *) echo 'Usage: sh setup-libraries.sh [core|evals|security|zap|all]' >&2; exit 2 ;;
esac
. "$script_dir/activate.sh"
test -f "$QA_RUNTIME_VOLUME/.qa-tools-volume-id" || { echo 'Mount the QA volume first.' >&2; exit 1; }
setup_python=${QA_SETUP_PYTHON:-python3}
unset PYTHONPATH PYTHONHOME VIRTUAL_ENV CONDA_PREFIX
export PYTHONNOUSERSITE=1
"$setup_python" -c 'import sys; assert sys.version_info >= (3,12), "Python >=3.12 required"'
if [ "$selection" = core ] || [ "$selection" = all ]; then
  node -e 'if(Number(process.versions.node.split(".")[0])<24)process.exit(1)'
  mkdir -p "$QA_TOOLS_ROOT/node/promptfoo" "$QA_TOOLS_ROOT/bin"
  if [ ! -x "$QA_PYTHON" ]; then "$setup_python" -m venv "$QA_TOOLS_ROOT/python"; fi
  "$QA_PYTHON" -m pip install --cache-dir "$QA_RUNTIME_VOLUME/caches/pip" -r "$script_dir/requirements-qa.lock.txt"
  # Never overwrite an existing Node package/lock from a different installation.
  if [ ! -f "$QA_NODE_ROOT/package.json" ]; then cp "$script_dir/node-package.json" "$QA_NODE_ROOT/package.json"; fi
  npm --prefix "$QA_NODE_ROOT" install
  "$QA_NODE_ROOT/node_modules/.bin/playwright" install chromium
  if [ ! -f "$QA_NODE_ROOT/promptfoo/package.json" ]; then cp "$script_dir/promptfoo-package.json" "$QA_NODE_ROOT/promptfoo/package.json"; fi
  npm --prefix "$QA_NODE_ROOT/promptfoo" install
  for tool in python pytest coverage ruff; do
    case "$tool" in python) executable=python; wrapper=qa-python ;; pytest) executable=pytest; wrapper=qa-pytest ;; coverage) executable=coverage; wrapper=qa-coverage ;; *) executable=ruff; wrapper=ruff ;; esac
    printf '#!/bin/sh\nexec "%s/python/bin/%s" "$@"\n' "$QA_TOOLS_ROOT" "$executable" > "$QA_TOOLS_ROOT/bin/$wrapper"
    chmod +x "$QA_TOOLS_ROOT/bin/$wrapper"
  done
  printf '#!/bin/sh\nexec "%s/node/promptfoo/node_modules/.bin/promptfoo" "$@"\n' "$QA_TOOLS_ROOT" > "$QA_TOOLS_ROOT/bin/promptfoo"
  chmod +x "$QA_TOOLS_ROOT/bin/promptfoo"
fi
if [ "$selection" = evals ] || [ "$selection" = all ]; then
  for framework in ragas deepeval; do
    case "$framework" in ragas) runtime=python ;; *) runtime=extended-python ;; esac
    interpreter="$QA_RUNTIME_VOLUME/runtime/scope-data-bot-eval/$runtime/bin/python"
    if [ ! -x "$interpreter" ]; then "$setup_python" -m venv "$(dirname "$(dirname "$interpreter")")"; fi
    "$interpreter" -m pip install --cache-dir "$QA_RUNTIME_VOLUME/caches/pip" -r "$repo_dir/chatbot-eval-kit/integrations/requirements-$framework.lock.txt"
  done
fi
if [ "$selection" = security ] || [ "$selection" = all ]; then
  uv tool install 'semgrep==1.179.0'
  uv tool install 'bandit==1.9.4'
  uv tool install 'pip-audit==2.10.1'
fi
if [ "$selection" = zap ] || [ "$selection" = all ]; then
  mkdir -p "$QA_TOOLS_ROOT/zap" "$QA_TOOLS_ROOT/bin"
  archive="$QA_TOOLS_ROOT/zap/ZAP_2.17.0_Crossplatform.zip"
  if [ ! -f "$archive" ]; then
    curl --fail --location --output "$archive.part" https://github.com/zaproxy/zaproxy/releases/download/v2.17.0/ZAP_2.17.0_Crossplatform.zip
    mv "$archive.part" "$archive"
  fi
  "$setup_python" - "$archive" <<'PY'
import hashlib, sys
from pathlib import Path
assert hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest() == '94c8f767b1c2e94f0db66b3ae56514d5e3f5a728ee1b6c798e0c8fe2d61fbff0', 'ZAP checksum mismatch; do not execute'
PY
  if [ ! -f "$QA_TOOLS_ROOT/zap/ZAP_2.17.0/zap-2.17.0.jar" ]; then
    unzip -q "$archive" -d "$QA_TOOLS_ROOT/zap"
  fi
  cp "$script_dir/zap-launcher.sh" "$QA_TOOLS_ROOT/bin/qa-zap"
  chmod +x "$QA_TOOLS_ROOT/bin/qa-zap"
fi
echo 'Selected packages installed. Run doctor and the product-specific checks in README.'
