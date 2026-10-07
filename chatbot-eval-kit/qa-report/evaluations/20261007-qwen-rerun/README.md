# Chạy lại Qwen2.5-0.5B ngày 07/10/2026

Inference mới kết thúc lúc 16:57:47 +07:00. Model/revision và runtime trong `evidence/model-manifest.json`; dataset/prompt hash được ghi trước inference. **6/24 đạt sau audit**, 18 ca chưa đạt; 24/24 raw answers giống baseline. Đây là input tổng hợp và context snapshot cũ, không phải dữ liệu khách hàng hay lượt crawl/retrieval mới.

Xem [báo cáo HTML đầy đủ](report.html), [PDF tổng hợp](report.pdf) và [JSON báo cáo](report-data.json). Ragas 0.4.3 chạy 12 phép đo offline; DeepEval 4.2.8 chạy 18 exact-match, không có lỗi framework. Semantic judge và agent executor chưa chạy; không có điểm nghiệm thu giả cho hai phần này.

## Bằng chứng và cách đọc

- `responses.json`, `evidence/generation-traces.json`: raw output mới, token và độ trễ thật.
- `eval/results.json`, `eval/ragas.json`, `eval/deepeval.json`: chấm mới, chỉ sử dụng response/context đã ghi.
- `audited-results.json`: audit tách citation khỏi đáp án số; R04 raw pass bị sửa thành fail. File thô được giữ nguyên.
- `comparison.json`: đối chiếu câu trả lời với baseline. Không đổi model/prompt, nên chưa có căn cứ nói sản phẩm đã cải thiện.
- `audit-run.py` chỉ phục vụ fixture này: kiểm toàn bộ output giống baseline trước khi dùng lại nhận xét nội dung. Nếu output đổi, script dừng để yêu cầu review mới; không dùng làm judge cho sản phẩm khác.

Gốc đường dẫn evidence trong HTML/PDF là thư mục `chatbot-eval-kit/qa-report/` của repo. HTML chứa mọi phiếu; PDF hiện là bản tổng hợp theo mẫu, chỉ mục đủ 26 mục (24 đã chạy, 1 agent chưa chạy, 1 semantic judge bị chặn).

## Clone và chấm lại output có sẵn

Cần Git và Python 3.12+. Chạy từ nơi muốn lưu repo:

```sh
git clone https://github.com/SIReal3103/ai-project-starter.git
cd ai-project-starter/chatbot-eval-kit
sh setup-tools.sh
python3 main.py replay \
  --dataset qa-report/evaluations/20261007-qwen-rerun/cases.jsonl \
  --responses qa-report/evaluations/20261007-qwen-rerun/responses.json \
  --out runs/qwen-score-01 --frameworks auto
```

Đây là replay, không gọi model. Exit 1 vì có ca fail là kết quả eval; đọc `runs/qwen-score-01/results.json`. Không áp dụng trực tiếp `audit-run.py` cho đường dẫn khác vì script fixture đọc `eval/results.json` cạnh nó. Với lượt khác, làm audit riêng theo `../../agent-guide.md` và lưu cả raw/audit; không chép kết quả audit cũ.

## Chạy inference mới trên máy khác

Chỉ MLX inference yêu cầu **macOS Apple Silicon**; core replay và HTML không yêu cầu MLX. Từ thư mục `chatbot-eval-kit`, tạo một thư mục chưa tồn tại:

```sh
mkdir -p runs
mkdir runs/qwen-inference-02
cp qa-report/evaluations/20261007-qwen-rerun/cases.jsonl runs/qwen-inference-02/
cp qa-report/evaluations/20261007-qwen-rerun/requests.json runs/qwen-inference-02/
cp qa-report/evaluations/20261007-qwen-rerun/run-llm.py runs/qwen-inference-02/
cp qa-report/evaluations/20261007-qwen-rerun/requirements-llm.lock.txt runs/qwen-inference-02/
cd runs/qwen-inference-02
mkdir evidence
python3 -m venv .venv-llm
.venv-llm/bin/python -m pip install -r requirements-llm.lock.txt
.venv-llm/bin/python -c 'from huggingface_hub import snapshot_download; snapshot_download("mlx-community/Qwen2.5-0.5B-Instruct-4bit", revision="53a32aee5e9447773fd2b85988395066aef3700a", local_dir="model")'
.venv-llm/bin/python run-llm.py
cd ../..
python3 main.py replay --dataset runs/qwen-inference-02/cases.jsonl \
  --responses runs/qwen-inference-02/responses.json \
  --out runs/qwen-score-02 --frameworks auto
```

Không chạy inference trực tiếp trong thư mục evidence đã công bố vì script ghi `responses.json` cạnh nó. Chọn tên thư mục mới cho mỗi lượt; lưu hash inputs trước inference theo guide khi làm nghiệm thu chính thức. Không cần API key; model tải từ Hugging Face, tốn dung lượng và mạng riêng. Model/runtime giữ nguyên không cam kết bit-for-bit giữa các máy.

## Dựng báo cáo đã lưu

Từ `chatbot-eval-kit`:

```sh
python3 qa-report/render.py \
  --input qa-report/evaluations/20261007-qwen-rerun/report-data.json \
  --output reports/qwen-rerun.html
```

PDF: cài venv và `qa-report/requirements.txt` theo `../../README.md`, dùng cùng lệnh với `--pdf reports/qwen-rerun.pdf`; thêm `--all-cases` để có mọi phiếu. Đây chỉ dựng lại báo cáo. Với output mới, tạo report-data mới theo `../../agent-guide.md`, không ghi đè số đo/nhận xét trong báo cáo cũ rồi coi đó là test.
