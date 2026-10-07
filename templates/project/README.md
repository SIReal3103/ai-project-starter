# {{PROJECT_NAME}}

**Trạng thái: bộ khởi đầu để phát triển; chưa có sản phẩm được triển khai.** Stack định hướng: `{{STACK}}`. Việc chọn stack chỉ thêm hướng dẫn, không tạo ứng dụng giả, cài dependency, khởi tạo Git hay gọi dịch vụ.

Bộ này dùng độc lập sau khi copy hoặc chuyển thư mục. Mọi đường dẫn bên dưới là tương đối với dự án; không cần starter nguồn còn ở máy.

## Bắt đầu

1. Điền [đề bài](docs/project-brief.md) và chọn một luồng người dùng chính.
2. Chốt [hợp đồng nghiệm thu](docs/acceptance-contract.md), ca critical, nguồn chuẩn và hành động được phép.
3. Ghi [quyết định kiến trúc](docs/architecture-decisions.md), đọc [hướng dẫn stack](docs/stack-guide.md), rồi triển khai theo [kế hoạch](docs/implementation-plan.md).
4. Viết test hành vi khi xây tính năng. Nối bộ eval vào output thật theo [kế hoạch eval](docs/eval-plan.md).
5. Kiểm [xử lý dữ liệu](docs/data-handling.md) và hoàn thiện [bàn giao](docs/handoff.md) bằng bằng chứng thực.

Hướng dẫn agent ở [AGENTS.md](AGENTS.md). Các mục `[Cần điền]` là quyết định chưa có, không phải thông tin đã xác nhận.

Đọc [bộ hướng dẫn kiến trúc và các hướng sản phẩm](docs/guides/architecture-and-use-cases.md) để chọn phần cần dùng: chatbot/RAG/agent, backend/quyền/dữ liệu, voice/media, eval/vận hành, workflow hai giờ và cấu hình provider. Toàn bộ hướng dẫn được copy vào dự án để dùng độc lập.

## Kiểm bộ eval mẫu

Cần Python 3.12 trở lên. Từ thư mục dự án, chạy các lệnh dưới đây. Đường dẫn tương đối vẫn dùng được khi thư mục dự án có khoảng trắng:

```bash
python3 tools/evals/main.py validate --dataset tools/evals/datasets/demo-cases.jsonl
python3 tools/evals/main.py self-test
python3 tools/evals/main.py demo --out tools/evals/runs/demo --frameworks off
python3 tools/evals/report.py --input tools/evals/runs/demo/results.json --output tools/evals/reports/demo.html
```

Dùng `runs/demo-02` cho lượt tiếp theo; runner không ghi đè thư mục đã có kết quả. Những lệnh này chỉ kiểm assistant mẫu xác định và công cụ, **chưa kiểm sản phẩm của bạn**. Bộ eval giữ hướng dẫn đầy đủ tại [tools/evals/README.md](tools/evals/README.md) và [agent-guide.md](tools/evals/agent-guide.md).

Chưa có lệnh mở ứng dụng, build hoặc test sản phẩm. Khi đã triển khai và chạy thành công, ghi lệnh thực cùng môi trường cần thiết vào README và bàn giao. Không gọi `demo` là ứng dụng hoàn chỉnh.

## Cấu hình và bằng chứng

Đọc [cấu hình](docs/configuration.md) để biết tên biến và khi nào cần dùng; bộ khởi đầu không tạo file dotenv. Bộ eval đọc biến môi trường của tiến trình. Không commit key, dotenv, dữ liệu người dùng hoặc kết quả chứa thông tin riêng tư. Đọc phạm vi cụ thể trong tài liệu xử lý dữ liệu.

Kết quả eval được tạo mới tại `tools/evals/runs/` và `tools/evals/reports/`, được Git ignore. Bộ khởi đầu không chứa kết quả chạy cũ, môi trường ảo hay `node_modules`.
