# Hướng dẫn khi chọn Python

Đây là hướng dẫn, chưa có package ứng dụng hoặc dependency đã cài.

Chọn cấu trúc theo tác vụ: CLI nhỏ có thể bắt đầu từ một module; API chỉ thêm framework khi contract cần HTTP. Dùng thư viện chuẩn khi đủ; thêm thư viện có lý do và khóa dependency bằng cách phù hợp với công cụ quản lý được chọn. Ghi phiên bản Python sau khi thử trên môi trường mục tiêu.

Triển khai một luồng thật và test hẹp bằng runner phù hợp. `unittest` dùng được không cần cài thêm; pytest/Ruff/type checker là lựa chọn khi chúng giúp dự án và đã được cấu hình. Không ghi lệnh kiểm chưa tồn tại vào mục “đã chạy”.

Với I/O, kiểm input, timeout/lỗi phụ thuộc và output schema. Với tính toán, dùng oracle độc lập và đơn vị/làm tròn theo nghiệp vụ. Với service, cô lập storage test và kiểm quyền khi thực sự có nhiều người dùng.

Nối AI qua adapter/service của sản phẩm nếu cần; không biến lời gọi trực tiếp model khác thành bằng chứng cho luồng ứng dụng. Cập nhật README bằng lệnh ứng dụng, cài đặt và test thực sau khi triển khai.
