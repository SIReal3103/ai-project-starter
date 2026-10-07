# AI Project Starter

Hướng dẫn agent và template tiếng Việt để bắt đầu **một sản phẩm mới hoàn toàn**: chatbot, RAG, agent dùng công cụ, voicebot hoặc ứng dụng có AI. Repo có bộ eval chạy được để kiểm quy trình trước khi nối sản phẩm thật.

Đây là bộ khởi động phát triển, chưa phải ứng dụng đã triển khai. Bạn chọn bài toán, stack và provider; agent xây sản phẩm theo hợp đồng nghiệm thu. Không cần clone repo cũ, đọc file ngoài máy, có key hay cài model để chạy mẫu đầu tiên.

## Clone và kiểm ngay

Yêu cầu tối thiểu: Git và Python 3.12+. Repo private cần tài khoản GitHub được cấp quyền.

```sh
git clone https://github.com/SIReal3103/ai-project-starter.git
cd ai-project-starter
python3 scripts/check_repository.py
python3 tools/evals/main.py self-test
python3 tools/evals/main.py demo --frameworks off --out tools/evals/runs/first-demo
python3 tools/evals/report.py --input tools/evals/runs/first-demo/results.json --output tools/evals/reports/first-demo.html
```

Trên Windows dùng `python` thay `python3` nếu đó là tên executable đã cài. Core dùng thư viện chuẩn, không gọi mạng/model. Mỗi lượt eval cần thư mục output mới; lần sau đổi `first-demo` thành tên khác.

## Tạo dự án mới

```sh
python3 scripts/new_project.py --name "Trợ lý tài liệu" --destination ../my-new-project --stack python
cd ../my-new-project
```

Lệnh sao chép hướng dẫn, tài liệu cần điền và bộ eval vào dự án mới. Không ghi đè thư mục có dữ liệu; không tự cài package, khởi tạo Git hoặc tạo sản phẩm giả. Chọn `--stack web` hoặc `--stack undecided` nếu phù hợp hơn. Dự án sinh ra hoạt động độc lập với vị trí repo starter.

Sau đó mở thư mục mới bằng coding agent và gửi:

> Đọc AGENTS.md và README.md trong repo này. Tôi muốn xây [mô tả sản phẩm], cho [người dùng], trong [thời gian]. Hãy hoàn thiện brief và tiêu chí nghiệm thu từ thông tin có thể xác định; chỉ hỏi các quyết định chưa thể suy ra. Đề xuất một luồng cốt lõi, lập kế hoạch rồi triển khai thật. Viết test và dataset eval độc lập với câu trả lời của sản phẩm. Chạy kiểm, phân tích lỗi và xuất báo cáo tiếng Việt; không lấy kết quả demo làm chất lượng AI thực tế. Không tự triển khai công khai hay ghi đè dữ liệu ngoài scope được giao.

Chi tiết: [hướng dẫn tạo dự án](docs/new-project.md).

## Đọc theo công việc

| Cần làm | Tài liệu |
| --- | --- |
| Agent bắt đầu và quy tắc làm việc | [AGENTS.md](AGENTS.md) |
| Chọn bài toán, stack và kiến trúc | [Kiến trúc và hướng sản phẩm](docs/guides/architecture-and-use-cases.md) |
| Chatbot, RAG, tool-calling agent | [Chatbot, RAG và agent](docs/guides/chatbot-rag-and-agents.md) |
| Backend, quyền, dữ liệu và guardrails | [Backend, security và privacy](docs/guides/backend-security-and-privacy.md) |
| Voicebot, audio, video | [Voice và media](docs/guides/voice-and-media.md) |
| Test, eval, báo cáo và observability | [Eval và quan sát vận hành](docs/guides/evals-and-observability.md) |
| Làm bài 2 giờ, kiểm 10 phút cuối | [Quy trình 2 giờ](docs/guides/two-hour-workflow.md) |
| Chọn provider, kiểm capability; BTC tùy chọn | [Provider profiles](docs/guides/provider-profiles.md) |
| Chạy bộ eval thực tế | [Eval kit](tools/evals/README.md), [hướng dẫn agent eval](tools/evals/agent-guide.md) |
| Các tài liệu gốc đã rà và cách hợp nhất | [Source audit](docs/review/source-audit.md) |

## Trong repo có gì?

```text
AGENTS.md               Hướng dẫn agent tự chứa trong repo
docs/                   Playbook theo nhiệm vụ, không phụ thuộc file local bên ngoài
templates/              Tài liệu và skeleton cho dự án mới
scripts/new_project.py  Sinh thư mục dự án mới an toàn
scripts/check_repository.py  Kiểm portability, link và cú pháp
tools/evals/            Dataset, scorer, adapter, report HTML/PDF, test
tests/                  Kiểm scaffolder và repo
.github/workflows/      CI kiểm bản clone
```

## Phần có thể chạy và phần cần cấu hình

- **Có thể chạy sau clone:** kiểm repo, sinh dự án, 40 ca demo, scorer/transport tests và tạo HTML. Kết quả demo dùng dữ liệu tổng hợp và trợ lý theo luật.
- **Ragas/DeepEval:** cài dependency riêng bằng script trong eval kit; chạy metric offline không cần key. Không tìm runtime đã cài ở thư mục cá nhân.
- **Sản phẩm/LLM thật:** cần dataset, API hoặc adapter và credential do bạn cấp. Judge là cấu hình riêng; thiếu dữ liệu/cấu hình ghi chưa chạy hoặc lỗi, không tạo điểm giả.
- **PDF tự động:** cần Node và Playwright được cài trong eval kit. Hoặc in HTML bằng trình duyệt. Không phụ thuộc browser/tool ở repo khác.
- **Hạ tầng nâng cao:** database, OCR, tracing, load test hoặc deployment chỉ dựng khi bài toán cần. Hướng dẫn không có nghĩa các dịch vụ đó đã được triển khai.

Mẫu secret chỉ dùng biến môi trường. Không commit key, `.env`, raw dữ liệu riêng hoặc report sản phẩm chứa thông tin cá nhân. Repo không tự cấp quyền sử dụng dịch vụ/provider và không tự xác nhận tuân thủ quy định cuộc thi.
