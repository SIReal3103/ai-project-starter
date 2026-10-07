# Bộ eval cho dự án mới

Kit này có runner, adapter HTTP/chat, kiểm tra xác định và tích hợp Ragas/DeepEval tùy chọn. Dataset demo và assistant dùng luật chỉ minh họa cách đánh giá, chưa chứng minh chất lượng sản phẩm của bạn. Bản khởi tạo này chưa có kết quả chạy; hãy tạo bằng chứng mới.

## Chạy core không cần key hoặc mạng

Cần Python 3.12 trở lên. Từ thư mục dự án, chuyển vào bộ kit; dấu ngoặc kép giữ lệnh hợp lệ khi working directory có khoảng trắng:

```bash
cd "tools/evals"
python3 main.py validate
python3 main.py self-test
python3 main.py demo --out runs/demo-01 --frameworks off
python3 report.py --input runs/demo-01/results.json --output reports/demo-01.html
```

Mỗi lượt dùng một thư mục `--out` mới. Core và HTML dùng thư viện chuẩn. Trên Windows dùng `python` hoặc `py -3.12` nếu đó là interpreter Python của bạn. Dataset/template mặc định được tìm trong kit; đường dẫn CLI tùy chỉnh tương đối tính từ nơi gọi lệnh.

## Nối sản phẩm

Đọc [hướng dẫn agent](agent-guide.md), [schema dataset](datasets/dataset-guide.md) và [mẫu ca](templates/case-template.json). Tạo dataset thực đã kiểm expected; không đưa expected hoặc gold vào target. Chọn [adapter HTTP](adapters/http-product.py), [adapter chat](adapters/openai-chat.py) hoặc adapter stdin/stdout riêng.

HTTP dùng `EVAL_TARGET_URL` và `EVAL_TARGET_API_KEY` nếu cần. Chat dùng `EVAL_TARGET_BASE_URL`, `EVAL_TARGET_MODEL`, `EVAL_TARGET_API_KEY`; chỉ có text/usage nên không tạo trace RAG/agent giả. Nạp key từ môi trường/kho bí mật, không ghi vào lệnh hay báo cáo.

```bash
python3 main.py evaluate --dataset datasets/product-cases.jsonl \
  --adapter "python3 adapters/http-product.py" --product-name "Sản phẩm của bạn" \
  --out runs/product-01 --frameworks auto
python3 report.py --input runs/product-01/results.json --output reports/product-01.html
```

Lệnh evaluate chỉ dùng sau khi dataset và endpoint sản phẩm đã được chuẩn bị. Runtime/transport lỗi phải giữ lỗi; không coi demo hoặc output tự dựng là phản hồi sản phẩm.

## Framework và judge tùy chọn

Đọc [hướng dẫn cài và khóa dependency](integrations/README.md). Trên macOS/Linux, từ thư mục kit, `sh setup-tools.sh` tạo môi trường cục bộ khi bạn chủ động cài; generator không chạy lệnh này. `--frameworks auto` tìm môi trường trong kit hoặc interpreter được khai báo qua `EVAL_RAGAS_PYTHON` / `EVAL_DEEPEVAL_PYTHON`, không phụ thuộc runtime ở repo nguồn.

Judge cần `EVAL_JUDGE_API_KEY`, `EVAL_JUDGE_BASE_URL`, `EVAL_JUDGE_MODEL`, framework đã sẵn sàng và ngân sách được phép. Replay response đã có để chấm riêng:

```bash
python3 main.py replay --dataset datasets/product-cases.jsonl \
  --responses runs/product-01/responses.json --out runs/product-judge-01 \
  --judge --judge-max-cases 4 --frameworks auto
```

`scored` nghĩa là đã đo metric, chưa tự thành release gate. Judge chưa chạy/lỗi ghi riêng; không tạo điểm thay thế. Đối chứng âm chỉ kiểm bộ chấm, không cộng vào chất lượng sản phẩm.

## Báo cáo và PDF

Report dùng [template HTML](templates/report-template.html) có bảng từng ca và biểu đồ. In HTML thành PDF A4 hoặc dùng script `render-pdf.mjs` sau khi chủ động chuẩn bị Node/dependency/browser:

```bash
npm ci --no-audit --no-fund
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright-browsers"
npx playwright install chromium
node render-pdf.mjs --input reports/product-01.html --output reports/product-01.pdf
```

Node/Playwright chỉ cần cho cách xuất PDF bằng script, không cần để chạy core. Kiểm layout từng trang sau khi xuất. Các thư mục runs/reports là bằng chứng cục bộ, không được tạo sẵn hoặc copy từ dự án khác.

Exit code runner: `0` khi các gate đã chạy đạt; `1` khi ca/đối chứng không đạt; `2` khi lỗi, ca chưa chạy hoặc framework lỗi. Đọc cả phạm vi và trạng thái metric, không kết luận mọi phép đo đã chạy từ exit code.
