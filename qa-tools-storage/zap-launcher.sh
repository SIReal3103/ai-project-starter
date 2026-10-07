#!/bin/sh
set -eu
umask 077
QA_TOOLS_ROOT=${QA_TOOLS_ROOT:-${QA_RUNTIME_VOLUME:-/Volumes/AI-QA-Tools}/runtime/ai-qa-tools}
zap_root="$QA_TOOLS_ROOT/zap"
if [ -n "${JAVA_HOME:-}" ]; then
  zap_java="$JAVA_HOME/bin/java"
elif command -v brew >/dev/null 2>&1; then
  zap_java="$(brew --prefix openjdk@17)/bin/java"
else
  zap_java=java
fi
if [ "$#" -eq 0 ]; then set -- -help; fi
exec "$zap_java" -Djava.awt.headless=true \
  -Djava.util.prefs.userRoot="$zap_root/java-preferences" -Xmx1g \
  -jar "$zap_root/ZAP_2.17.0/zap-2.17.0.jar" \
  -installdir "$zap_root/ZAP_2.17.0" -dir "$zap_root/home" -silent \
  -config oast.callback.localaddr=127.0.0.1 \
  -config oast.callback.remoteaddr=127.0.0.1 "$@"
