# Hướng dẫn phát triển dự án

## Đọc trước khi làm

- [README](README.md): trạng thái và các lệnh đã được xác nhận.
- [Đề bài](docs/project-brief.md), [nghiệm thu](docs/acceptance-contract.md), [kiến trúc](docs/architecture-decisions.md).
- [Kế hoạch triển khai](docs/implementation-plan.md), [eval](docs/eval-plan.md), [dữ liệu](docs/data-handling.md), [bàn giao](docs/handoff.md).
- [Cấu hình](docs/configuration.md): chỉ tên biến và mục đích, không lưu dotenv hoặc credential trong repo.
- [Hướng dẫn stack](docs/stack-guide.md) và [hướng dẫn bộ eval](tools/evals/agent-guide.md).
- [Danh mục hướng dẫn sản phẩm/kiến trúc](docs/guides/architecture-and-use-cases.md): chọn nhánh liên quan, không áp dụng mọi nhánh cùng lúc.

## Thực hiện

Đây là bộ tài liệu và công cụ khởi đầu, chưa phải sản phẩm hoàn chỉnh. Khảo sát code và tài liệu hiện có trước; các mục chưa điền không được coi là quyết định của chủ sản phẩm. Hỏi về mục tiêu, quyền, ngân sách hoặc trade-off không thể suy ra từ bằng chứng; tự xử lý lựa chọn kỹ thuật thông thường trong phạm vi đã giao.

Ưu tiên YAGNI, KISS, DRY theo thứ tự. Làm một luồng thật từ đầu vào đến đầu ra trước, rồi mở rộng. Không tạo output giả, telemetry giả hoặc mock toàn bộ luồng để trình bày như sản phẩm hoạt động. Không tự đổi scope, ngưỡng nghiệm thu hay provider đã chọn để làm xanh báo cáo.

Giữ sửa đổi đúng phạm vi. Không hoàn tác thay đổi của người khác. Khi chia việc, nêu rõ quyền sửa file, hợp đồng tích hợp và tiêu chí hoàn tất. Kế hoạch mới lưu dưới `plans/<timestamp>-<slug>/`; chỉ tạo khi công việc thực sự cần kế hoạch chi tiết.

## Kiểm chứng

Viết test có giá trị cho logic cốt lõi, input sai/thiếu và lỗi phụ thuộc. Chạy kiểm tra hẹp trước; mở rộng khi sửa contract hoặc logic dùng chung. Không giấu fail, error, timeout, skipped hoặc not-run. Không coi test phần mềm pass là bằng chứng model đúng.

Chọn công cụ theo stack và tác vụ thật; không cài tất cả công cụ có trong danh mục. Bộ eval kèm theo hỗ trợ câu trả lời/nguồn/trace của chatbot, RAG, agent và guardrail. Đọc hướng dẫn trước khi cấu hình; chỉ đưa input hợp lệ cho target, giữ expected và gold ngoài prompt. Đối chứng âm kiểm bộ chấm, không cộng vào điểm sản phẩm.

## Dữ liệu và tác động

Không commit hoặc in secret, token, `.env`, dữ liệu cá nhân. Nạp credential từ môi trường hoặc kho bí mật phù hợp. Ghi rõ provider/model, quyền, số lần gọi và ngân sách; không tự fallback sang nhà cung cấp khác. Với hành động gửi, ghi, xóa hoặc tính phí, tuân thủ quyền và bước xác nhận đã xác định trong contract.

## Bàn giao

Cập nhật tài liệu khi thay đổi hành vi, setup, lệnh, kiến trúc hoặc contract. Nêu kết quả thực, cách chạy lại, lỗi còn lại và phần chưa kiểm; không tuyên bố production-ready chỉ từ demo. Không tự commit/push khi người dùng chưa yêu cầu. Khi được yêu cầu commit, chỉ lấy đúng thay đổi được giao và dùng conventional commit không có tham chiếu AI.
