# Cấu hình

Bộ khởi đầu không tạo dotenv và không chứa credential. Runner đọc biến môi trường của tiến trình; nạp giá trị từ shell hoặc kho bí mật phù hợp, tránh ghi key vào lệnh được lưu trong lịch sử. Chỉ dùng những biến cần cho adapter đã chọn.

| Tên biến | Mục đích | Khi nào cần |
| --- | --- | --- |
| `EVAL_TARGET_URL` | Endpoint sản phẩm nhận request eval | Adapter HTTP sản phẩm |
| `EVAL_TARGET_API_KEY` | Credential cho sản phẩm | API yêu cầu xác thực; adapter chat |
| `EVAL_TARGET_BASE_URL` | Base URL trước đường chat-completions | Adapter chat tương thích |
| `EVAL_TARGET_MODEL` | Model của target | Adapter chat |
| `EVAL_JUDGE_BASE_URL` | Endpoint judge riêng | Chủ động bật LLM judge |
| `EVAL_JUDGE_MODEL` | Model judge được phép | Chủ động bật LLM judge |
| `EVAL_JUDGE_API_KEY` | Credential của judge | Chủ động bật LLM judge |
| `EVAL_RAGAS_PYTHON` | Interpreter có Ragas | Chỉ định runtime tùy chọn ngoài môi trường cục bộ của kit |
| `EVAL_DEEPEVAL_PYTHON` | Interpreter có DeepEval | Chỉ định runtime tùy chọn ngoài môi trường cục bộ của kit |

Demo core không cần những biến trên. Các biến này phục vụ bộ eval, không mặc định là cấu hình của ứng dụng chưa được triển khai. Khi chọn runtime/product/provider, bổ sung tên biến, mục đích, quy tắc validation và giá trị không nhạy cảm phù hợp; không đưa giá trị credential vào tài liệu.

Đọc [hướng dẫn eval](../tools/evals/agent-guide.md) và [xử lý dữ liệu](data-handling.md) trước khi gửi dữ liệu đến dịch vụ ngoài. Thiếu cấu hình phải giữ trạng thái thiếu/lỗi, không tự fallback provider hoặc tạo output giả.
