# Cập nhật hướng dẫn và skill lập kế hoạch

Ngày: 07/10/2026. Trạng thái: hoàn tất. Phạm vi: repo `ai-project-starter`, nhánh `main`; không sửa repo dự thi của đội.

Mục tiêu: từ một đề bài, sinh kế hoạch đủ dữ kiện để agent không có lịch sử chat tiếp tục đúng phạm vi; đóng gói thành skill Codex độc lập.

- [Thực hiện và kiểm chứng](phase-01-planning-contract.md): bổ sung hợp đồng kế hoạch vào tài liệu gốc, đóng gói skill và thử với agent mới.
- Phụ thuộc: tài liệu techstack hiện có, skill-creator; không gọi inference BTC hoặc sửa ứng dụng.
- Nghiệm thu: tài liệu và skill nhất quán; mỗi yêu cầu truy được tới cách kiểm; thiếu dữ liệu/quyền không bị biến thành giả định đã xác nhận; gói skill không phụ thuộc đường dẫn máy tác giả; forward-test tạo được kế hoạch có hành động tiếp theo rõ ràng.
- [Kiểm chứng](reports/validation.md): validator, sync và link checks đạt; review độc lập đã xử lý finding; hai agent không có lịch sử chat tạo được gói kế hoạch trong workspace tạm, controller đã đọc đầu ra. Đã cài skill cá nhân và so byte với gói repo. Không commit/push/deploy trong task này.
