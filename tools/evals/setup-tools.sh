#!/bin/sh
# Install optional frameworks into separate, kit-local environments.
set -eu
kit_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
selection=${1:-all}
case "$selection" in
  all|ragas|deepeval) ;;
  -h|--help)
    printf '%s\n' 'Usage: sh setup-tools.sh [all|ragas|deepeval]' 'Optional EVAL_SETUP_PYTHON selects Python >=3.12; defaults to python3.12 or python3.'
    exit 0 ;;
  *) printf '%s\n' 'Expected all, ragas, or deepeval.' >&2; exit 2 ;;
esac
if [ -n "${EVAL_SETUP_PYTHON:-}" ]; then
  setup_python=$EVAL_SETUP_PYTHON
elif command -v python3.12 >/dev/null 2>&1; then
  setup_python=python3.12
else
  setup_python=python3
fi
# Prevent unrelated Python environments from injecting packages into this install.
unset PYTHONPATH PYTHONHOME VIRTUAL_ENV CONDA_PREFIX
export PYTHONNOUSERSITE=1
"$setup_python" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else "Python >=3.12 is required")'
for framework in ragas deepeval; do
  if [ "$selection" != all ] && [ "$selection" != "$framework" ]; then continue; fi
  runtime_dir="$kit_dir/.venv-$framework"
  if [ ! -x "$runtime_dir/bin/python" ]; then
    "$setup_python" -m venv "$runtime_dir"
  fi
  "$runtime_dir/bin/python" -m pip install --disable-pip-version-check --requirement "$kit_dir/integrations/requirements-$framework.lock.txt"
  printf 'Ready: %s (auto-discovered by this kit only).\n' "$runtime_dir"
done
