#!/usr/bin/env bash
set -euo pipefail

echo 'Kiểm tra Gateway BTC — đội Delta Mind'
echo 'Dán Gateway key khi được hỏi. Key sẽ không hiện trên màn hình.'
read -r -s -p 'Gateway key: ' GATEWAY_KEY
printf '\n'
if [[ -z "$GATEWAY_KEY" ]]; then
  echo 'Bạn chưa nhập Gateway key.' >&2
  exit 1
fi

printf '\n=== 1. Hạn mức và model được cấp ===\n'
INFO=$(curl -sS -w "\nHTTP %{http_code}\n" \
  https://api.thucchien.ai/key/info \
  -H "Authorization: Bearer $GATEWAY_KEY")
printf '%s\n' "$INFO"
if [[ "$INFO" != *$'\nHTTP 200' ]]; then
  echo 'Kiểm tra hạn mức chưa thành công. Hãy kiểm tra mã HTTP ở trên.' >&2
  exit 1
fi

printf '\nChọn tên model được cấp trong kết quả trên.\n'
read -r -p 'Tên model: ' MODEL
if [[ ! "$MODEL" =~ ^[a-zA-Z0-9._:/-]+$ ]]; then
  echo 'Tên model trống hoặc chứa ký tự không hợp lệ.' >&2
  exit 1
fi

printf '\n=== 2. Gọi thử Chat Completion — model: %s ===\n' "$MODEL"
CHAT=$(curl -sS -w "\nHTTP %{http_code}\n" \
  https://api.thucchien.ai/chat/completions \
  -H "Authorization: Bearer $GATEWAY_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Xin chào từ đội Delta Mind\"}]}")
printf '%s\n' "$CHAT"
if [[ "$CHAT" != *$'\nHTTP 200' ]]; then
  echo 'Gọi chat chưa thành công. Hãy kiểm tra mã HTTP ở trên.' >&2
  exit 1
fi

printf '\nHai lệnh đều nhận HTTP 200. Chụp kết quả cả hai lệnh để làm ảnh 1.\n'
