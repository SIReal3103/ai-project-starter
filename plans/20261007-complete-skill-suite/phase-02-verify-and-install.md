# Review và cài đặt

Điều kiện vào: entrypoint và references có đủ cho 24 skill. Review scope và bất biến theo từng miền; không thay lựa chọn user vì lo ngại trừu tượng. Dùng agent mới không có lịch sử chat thử lập brief/kế hoạch và review thiết kế, bao gồm quyết định triển khai, với dữ liệu thiếu và provider có/không thuộc BTC. Đây không phải kiểm triển khai ứng dụng. Chỉ viết artifact tạm; không gọi API, tạo media hoặc gửi tin.

Kiểm cấu trúc và metadata tất cả skill; scripts chạy từ CWD khác vẫn đúng; --check chỉ đọc, phát hiện stale/missing; references và local links có thật. Review output hành vi thực, sửa lỗi có bằng chứng rồi kiểm phần liên quan.

Cài toàn bộ gói vào thư mục skill cá nhân. Nếu gặp skill có sẵn không thuộc task, giữ nguyên và báo thay vì ghi đè. Skill planning của task trước được cập nhật cùng nguồn. So byte giữa gói repo và bản cài, không dùng symlink tới ổ dự án.

Đầu ra: catalog có cách chọn và ví dụ gọi, báo cáo nguồn/checks/ca thử/giới hạn, trạng thái từng gói. Rollback chỉ gói đã cài hoặc file task; không xóa skill khác. Không commit/push mặc định.
