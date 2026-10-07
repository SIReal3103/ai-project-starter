# Quyết định kiến trúc

Trạng thái: **chưa có kiến trúc được triển khai**. Định hướng stack ban đầu: `{{STACK}}`; đọc [hướng dẫn stack](stack-guide.md), chốt theo [contract](acceptance-contract.md).

## Sơ đồ trách nhiệm cần xác định

Đầu vào → validation → logic nghiệp vụ → dữ liệu/tool/model khi cần → đầu ra/trạng thái. Điền thành phần thực, ranh giới tin cậy, dữ liệu qua mỗi bước và nơi xử lý lỗi. Không mặc định mọi sản phẩm cần LLM, DB, queue hoặc microservice.

## Mẫu một quyết định

- Ngày và trạng thái: [Đề xuất/chấp nhận/thay thế; ngày].
- Vấn đề cần giải quyết: [Cần điền].
- Yêu cầu và ràng buộc liên quan: [Cần điền liên kết contract].
- Phương án đã xem: [Cần điền các lựa chọn thực].
- Quyết định, lý do và trade-off: [Cần điền].
- Dữ liệu, API và hợp đồng bị ảnh hưởng: [Cần điền].
- Kiểm chứng và giới hạn: [Cần điền kết quả spike/test; chưa chạy ghi chưa chạy].
- Khả năng đổi/rollback: [Cần điền].

Ghi quyết định đủ để người tiếp theo hiểu vì sao; không ghi benchmark hoặc xác nhận bảo mật chưa đo. Nếu có model/provider, ghi endpoint được phép, model, prompt version và cơ chế giữ bí mật; không ghi key.
