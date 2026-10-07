# Hướng dẫn BTC và bộ báo cáo/eval

Repo để chung các hướng dẫn được cung cấp, script thử gateway, trọn bộ báo cáo/template eval và ứng dụng Crawl & RAG pipeline. Không có scaffolder hoặc bộ hướng dẫn khởi tạo dự án được viết lại.

## Tài liệu

| Nội dung | File |
| --- | --- |
| Hướng dẫn chatbot và agent BTC — bản gốc | [agent-chatbot-btc-guide.md](agent-chatbot-btc-guide.md) |
| Hướng dẫn voicebot BTC — bản gốc | [agent-voice-bot-btc-guide.md](agent-voice-bot-btc-guide.md) |
| Các hướng phát triển sản phẩm — bản gốc | [cac-huong-phat-trien-san-pham-dua-vao-techstack.md](cac-huong-phat-trien-san-pham-dua-vao-techstack.md) |
| Script thử gateway — bản gốc | [gateway-test.sh](gateway-test.sh) |
| **Hướng dẫn agent và prompt giao việc cho eval** | [chatbot-eval-kit/agent-guide.md](chatbot-eval-kit/agent-guide.md) |
| **Báo cáo mẫu HTML** | [bao-cao-evals.html](chatbot-eval-kit/reports/bao-cao-evals.html) |
| **Báo cáo mẫu PDF** | [bao-cao-evals.pdf](chatbot-eval-kit/reports/bao-cao-evals.pdf) |
| Template HTML và ca đánh giá | [report-template.html](chatbot-eval-kit/templates/report-template.html), [case-template.json](chatbot-eval-kit/templates/case-template.json) |
| Toàn bộ bộ eval, dataset, adapter, Ragas/DeepEval và cách chạy | [chatbot-eval-kit/README.md](chatbot-eval-kit/README.md) |
| Gói ZIP bộ eval để giao cho agent | [chatbot-agent-guardrail-eval-template.zip](chatbot-agent-guardrail-eval-template.zip) |
| **Ứng dụng Crawl & RAG pipeline** | [rag-review/README.md](rag-review/README.md) |
| **Hướng dẫn trang Crawl & RAG pipeline** | [huong-dan-crawl-rag-pipeline.md](huong-dan-crawl-rag-pipeline.md) |

Ba hướng dẫn BTC/techstack, script gateway và guide giao việc eval giữ nguyên nội dung nguồn. HTML/PDF và bốn JSON kết quả mẫu cũng giữ nguyên từ gói báo cáo đã cung cấp. Mã eval/setup giữ các sửa lỗi portability để chạy độc lập; ZIP chứa cùng bộ kit đang có trong repo.

## Chạy lại bộ eval

Core cần Python 3.12+, không cần key hay package bên ngoài:

```sh
cd chatbot-eval-kit
python3 main.py validate
python3 main.py self-test
python3 main.py demo --frameworks off --out runs/demo-01
python3 report.py --input runs/demo-01/results.json --output reports/demo-01.html
```

Đổi tên thư mục output ở lượt tiếp theo. Trên Windows dùng `python` nếu không có lệnh `python3`. Ragas/DeepEval và xuất PDF tự động cần cài dependency theo README của kit. LLM judge live cần endpoint/model/key và ngân sách riêng.

Báo cáo có sẵn là **mẫu tổng hợp**, không phải kết luận chất lượng của sản phẩm mới. Cấu hình model, endpoint và quota trong hướng dẫn gốc cần được xác nhận tại thời điểm sử dụng; lượt đóng gói này không gọi gateway hay provider.

## Chạy ứng dụng Crawl & RAG pipeline

Cần Python 3.12, Git và shell Bash (macOS/Linux hoặc WSL). Từ root repo:

```sh
cd rag-review
bash setup.sh
bash run.sh
```

Mở **http://localhost:8765/#pipeline**. Nếu cổng 8765 đang được ứng dụng khác dùng, chạy `RAG_REVIEW_PORT=8766 bash run.sh` rồi mở cổng 8766. Setup tải dependency/upstream vào thư mục riêng của ứng dụng, không cần checkout trên máy cũ. Kho tài liệu, key và lịch sử phiên của máy nguồn không được sao chép; bản mới bắt đầu với dữ liệu riêng. Chi tiết tại [README ứng dụng](rag-review/README.md).

Dùng **Code → Download ZIP** trên GitHub để lấy cả hướng dẫn, ứng dụng pipeline và bộ eval. File `chatbot-agent-guardrail-eval-template.zip` riêng chỉ chứa bộ eval.
