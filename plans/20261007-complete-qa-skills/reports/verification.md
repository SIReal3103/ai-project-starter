# Xác minh bộ skill QA mở rộng

Ngày: 2026-10-07. Phạm vi: tài liệu và gói skill, không phải kết quả nghiệm thu sản phẩm.

## Nội dung

- `ai-qa-evals`: điều phối bốn nhóm test phần mềm, AI eval, hiệu năng và bảo mật/quyền riêng tư; bốn reference có cách chạy, evidence, cách đọc kết quả và giới hạn.
- `ai-qa-metrics`: M01–M34, giữ bảng QA 7 cột và trạng thái riêng; phân biệt chưa chạy, lỗi thực thi, N/A và dữ liệu mock.
- Manifest trống để ghi run, target, ngân sách, scope, công cụ, phép đo và evidence; không dùng làm input renderer.
- README và mô tả hiển thị skill giúp tìm đúng nhóm; toàn bộ gói được đồng bộ vào bản cài cá nhân.

## Kiểm tra đã thực hiện

- Validator của skill-creator: hai gói hợp lệ; kiểm thêm bản copy trong thư mục tạm.
- Đường dẫn Markdown nội bộ của hai gói tồn tại sau khi copy; không có đường dẫn máy tác giả trong hướng dẫn.
- JSON manifest parse được, không chứa kết quả giả; 34 mã metric duy nhất và liên tục.
- Ví dụ shell qua `sh -n`; JavaScript qua `node --check`. Đây là kiểm cú pháp, không phải chạy công cụ trên sản phẩm.
- Đối chiếu lệnh validate/evaluate/replay với `--help` của runner hiện có; hướng dẫn công cụ tham chiếu tài liệu chính thức ngay trong từng reference.
- Review độc lập các hướng dẫn; sửa Playwright để artifact có thư mục theo run và không tự mở báo cáo gây treo luồng tự động.
- `python3 scripts/sync-skills.py --check`: 72 reference sinh tự động khớp nguồn; tài liệu QA viết tay không làm thay đổi nhóm này.
- `git diff --check`: không có lỗi khoảng trắng.

## Giới hạn

Task này không chạy test sản phẩm, inference, LLM judge, load test hoặc security scan, cũng không cài tất cả công cụ. Các lệnh yêu cầu đúng stack, môi trường, dataset, quyền và ngân sách khi thực thi. Những thay đổi renderer, HTML/PDF và ZIP còn tồn tại từ tác vụ khác không thuộc commit này.
