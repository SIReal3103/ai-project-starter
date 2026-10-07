# Bộ eval chatbot, RAG, agent và guardrails

**Mẫu tổng hợp kèm theo:** [báo cáo HTML tiếng Việt](reports/bao-cao-evals.html), [hướng dẫn agent](agent-guide.md), [dataset 40 ca](datasets/demo-cases.jsonl).

Kit có runner chạy được, adapter API/chat, bộ chấm theo điều kiện, Ragas/DeepEval, LLM judge tùy chọn, bảng câu hỏi/đáp án/kết quả và biểu đồ. Đây là template thực hành; dữ liệu mẫu và trợ lý dùng luật không chứng minh chất lượng LLM của sản phẩm thật.

## Chạy ngay

Cần Python **3.12 trở lên**. Từ root repo, chạy `cd chatbot-eval-kit`; nếu sao chép riêng bộ kit, mở terminal ngay trong thư mục chứa `main.py`. Các lệnh bên dưới đều chạy tại thư mục đó. Trên Windows có thể dùng `python` hoặc `py -3.12` thay cho `python3`.

```sh
python3 main.py validate
python3 main.py self-test
python3 main.py demo --out runs/my-demo-01 --frameworks auto
python3 report.py --input runs/my-demo-01/results.json --output reports/my-demo-01.html
```

Core và HTML chỉ dùng thư viện chuẩn Python, không cần cài package, key hay kết nối mạng. Nếu chưa cài framework, runner vẫn chạy các contract checks và ghi rõ Ragas/DeepEval `not_run`. Các đường dẫn `--dataset`, `--out`, `--responses`, `--input`, `--output` tương đối tính từ thư mục gọi lệnh; dataset/template mặc định và adapter con luôn tìm trong kit. Mỗi lượt dùng một `--out` mới.

Để cài hai framework tùy chọn, dùng Python 3.12 và shell POSIX (macOS/Linux):

```sh
sh setup-tools.sh
# Hoặc chỉ một framework: sh setup-tools.sh ragas
python3 main.py demo --out runs/framework-demo-01 --frameworks auto
```

`setup-tools.sh` dùng `venv` và `pip` có sẵn trong Python, cài từ các lock đã pin đầy đủ; không cần `uv`. Chạy lại an toàn. Hai môi trường `.venv-ragas` và `.venv-deepeval` nằm ngay trong kit và được `--frameworks auto` tìm thấy. Runner chỉ dùng hai môi trường này hoặc đường dẫn Python được chỉ định rõ qua `EVAL_RAGAS_PYTHON` / `EVAL_DEEPEVAL_PYTHON`; không tìm runtime ở home, repo khác hay môi trường đang activate. Đường dẫn trong hai biến có thể chứa khoảng trắng; đường dẫn tương đối tính từ nơi gọi runner. Dùng `EVAL_SETUP_PYTHON` để chọn Python lúc cài. Xem [tích hợp framework](integrations/README.md) để cài thủ công trên Windows hoặc nâng dependency.

## Nối sản phẩm mới

1. Tạo dataset từ yêu cầu/nguồn chuẩn của sản phẩm, theo [mẫu ca](templates/case-template.json). Thay tất cả giá trị trống; validate phải đạt trước khi chấm.
2. Chọn adapter [HTTP sản phẩm](adapters/http-product.py), [chat-completions](adapters/openai-chat.py) hoặc viết adapter stdin/stdout theo guide. Endpoint chỉ dùng HTTPS hoặc HTTP loopback; không tự theo redirect hoặc proxy môi trường.
3. Đặt `EVAL_TARGET_URL` và key nếu API cần. Chat adapter dùng `EVAL_TARGET_BASE_URL`, `EVAL_TARGET_MODEL`, `EVAL_TARGET_API_KEY`. Các key chỉ nằm trong môi trường; đừng chép key vào câu lệnh lưu trong lịch sử shell.
4. Chạy với thư mục mới:

```sh
python3 main.py evaluate --dataset datasets/product-cases.jsonl \
  --adapter "python3 adapters/http-product.py" --product-name "Sản phẩm của bạn" \
  --out runs/product-01 --frameworks auto
python3 report.py --input runs/product-01/results.json --output reports/product-01.html
```

Runner không gửi đáp án chuẩn, oracle hoặc gold context cho adapter sản phẩm. Adapter phải trả trace retrieval/tool/guardrail thật; thiếu trace không được suy ra là không có hành động. Chat adapter chỉ trả text/usage, nên cần chọn ca phù hợp hoặc bổ sung adapter để đo agent/RAG.

## Chấm bằng LLM

Đặt riêng `EVAL_JUDGE_API_KEY`, `EVAL_JUDGE_BASE_URL`, `EVAL_JUDGE_MODEL`, sau đó replay response có sẵn với `--judge`. Judge dùng model thật, không dùng giá trị giả khi thiếu cấu hình:

```sh
python3 main.py replay --dataset datasets/product-cases.jsonl \
  --responses runs/product-01/responses.json --out runs/product-judge-01 \
  --judge --judge-max-cases 4 --frameworks auto
```

Tối đa mặc định 4 ca và 12 request mỗi framework; hai framework có thể cần tới 24 request. Lỗi/quá budget hiện riêng. Model phải hỗ trợ chat-completions, JSON response và các tham số của adapter; kiểm một ca trước. Chưa có lượt judge live thành công được đóng gói trong bản mẫu này.

## Xuất PDF

Mở HTML → In → A4 → bật màu nền. Hoặc cài dependency PDF tùy chọn:

```sh
# Cần Node.js >=18; dependency Playwright đã pin trong package-lock.json.
npm ci --no-audit --no-fund
# Giữ browser cài đặt trong kit (POSIX shell):
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright-browsers"
npx playwright install chromium
node render-pdf.mjs --input reports/product-01.html --output reports/product-01.pdf
```

Sau xuất cần xem từng trang để bắt lỗi bảng bị cắt và chữ tràn. File HTML là template đã điền; cấu trúc gốc tại [templates/report-template.html](templates/report-template.html).

## Kết quả mẫu kèm theo

- 40 ca: 12 chatbot, 8 RAG, 8 agent, 12 guardrail; 40/40 đạt trong demo dùng luật.
- 24 phép đo Ragas offline trên 12 ca; 7 phép đo DeepEval ExactMatch.
- 8 output cố ý sai đều bị bộ chấm bắt; tách khỏi điểm demo.
- Bộ mã portable có 25 kiểm tra evaluator/transport/portability; API transport thử trên server loopback, không phải API sản phẩm thật.
- Snapshot minh họa tổng hợp: [example-results/results.json](example-results/results.json); không phải kết quả sản phẩm mới. Thư mục `runs/` dành cho lượt mới và không được đóng gói sẵn để lệnh demo không va chạm.

Exit code: 0 = các gate đã chạy đạt; 1 = có ca/đối chứng không đạt; 2 = lỗi, ca chưa chạy hoặc framework lỗi. Metric thư viện “đã đo” chưa tự là release gate. Không tuyên bố bao phủ mọi loại tấn công từ 40 ca mẫu.

## Báo cáo gốc được giữ nguyên

[HTML](reports/bao-cao-evals.html) và [PDF](reports/bao-cao-evals.pdf) cùng bốn JSON trong `example-results/` được giữ nguyên từ gói báo cáo đã cung cấp. Đây là kết quả mẫu của lượt cũ, không phải một lượt đánh giá sản phẩm mới. Mã runner/setup giữ các sửa lỗi đường dẫn và runtime độc lập; chạy lại bằng các lệnh ở trên vào tên output mới.
