# Hướng dẫn BTC và bộ báo cáo/eval

Repo chứa hướng dẫn BTC, script thử gateway và bộ báo cáo/template eval. Ứng dụng Crawl & RAG pipeline được phát triển trong [repo riêng](https://github.com/SIReal3103/crawl-rag-pipeline); thư mục `rag-review/` ở đây là bản mã lưu trước khi tách.

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
| **Ứng dụng Crawl & RAG pipeline** | [Repo crawl-rag-pipeline](https://github.com/SIReal3103/crawl-rag-pipeline) |
| **Hướng dẫn trang Crawl & RAG pipeline** | [huong-dan-crawl-rag-pipeline.md](huong-dan-crawl-rag-pipeline.md) |

Ba hướng dẫn BTC/techstack, script gateway và guide giao việc eval giữ nguyên nội dung nguồn. HTML/PDF và bốn JSON kết quả mẫu cũng giữ nguyên từ gói báo cáo đã cung cấp. Mã eval/setup giữ các sửa lỗi portability để chạy độc lập; ZIP chứa cùng bộ kit đang có trong repo.

## Chạy lại bộ eval

Core cần Python 3.12+, không cần key hay package bên ngoài. Lần đầu, mở terminal tại nơi muốn lưu repo và chạy:

```sh
git clone https://github.com/SIReal3103/ai-project-starter.git
cd ai-project-starter/chatbot-eval-kit
python3 main.py validate
python3 main.py self-test
python3 main.py demo --frameworks off --out runs/demo-01
python3 report.py --input runs/demo-01/results.json --output reports/demo-01.html
```

Nếu đã clone, mở terminal trong `ai-project-starter/chatbot-eval-kit` và bắt đầu từ lệnh `python3 main.py validate`. Đổi tên thư mục output ở lượt tiếp theo. Trên Windows dùng `python` nếu không có lệnh `python3`. Ragas/DeepEval và xuất PDF tự động cần cài dependency theo README của kit. LLM judge live cần endpoint/model/key và ngân sách riêng.

Báo cáo có sẵn là **mẫu tổng hợp**, không phải kết luận chất lượng của sản phẩm mới. Cấu hình model, endpoint và quota trong hướng dẫn gốc cần được xác nhận tại thời điểm sử dụng; lượt đóng gói này không gọi gateway hay provider.

## Clone và chạy ứng dụng Crawl & RAG pipeline

Ứng dụng có [repo GitHub riêng](https://github.com/SIReal3103/crawl-rag-pipeline). Cần Git, Python 3.12 và Bash (macOS/Linux hoặc WSL trên Windows). Mở terminal tại nơi muốn lưu project:

```bash
git clone https://github.com/SIReal3103/crawl-rag-pipeline.git
cd crawl-rag-pipeline
bash setup.sh
bash run.sh
```

Giữ terminal mở và truy cập **http://127.0.0.1:8765/#pipeline** trên cùng máy. Xem [README ứng dụng](https://github.com/SIReal3103/crawl-rag-pipeline#readme) để cài điều kiện cần, đổi cổng, cập nhật và xử lý lỗi.

Thư mục `rag-review/` ở repo tài liệu là bản mã đi kèm trước khi tách. Để cài mới hoặc cập nhật ứng dụng, dùng repo `crawl-rag-pipeline` ở trên. Bộ báo cáo/eval tiếp tục nằm trong repo tài liệu này.

Hướng dẫn từng bước, bao gồm kiểm công cụ, dừng/mở lại, cập nhật và kiểm lần đầu: [Cài và sử dụng pipeline](huong-dan-crawl-rag-pipeline.md#0-clone-cài-đặt-và-mở-ứng-dụng).
