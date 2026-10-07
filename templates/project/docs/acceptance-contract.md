# Hợp đồng nghiệm thu

Trạng thái: **chưa chốt**. Căn cứ: [đề bài](project-brief.md). Người xác nhận và phiên bản: [Cần điền].

| Nội dung | Quyết định cần điền |
| --- | --- |
| Đầu vào hợp lệ | Kiểu, field/file, ngôn ngữ, kích thước và giới hạn thực |
| Đầu ra đúng | Schema, trạng thái, dữ kiện, đơn vị, artifact hoặc tác động bắt buộc |
| Thiếu/sai dữ liệu | Hỏi lại, lỗi có thể sửa hoặc từ chối; không bịa kết quả |
| Phụ thuộc | API/model/DB; phân biệt đã thử thật và mới dự kiến |
| Hành động có tác động | Ghi/xóa/gửi/tạo có phí; quyền và lúc cần xác nhận |
| Giới hạn vận hành | Timeout, số vòng/request, ngân sách; chưa rõ thì ghi chưa rõ |
| Điều kiện chặn nghiệm thu | Lỗi ảnh hưởng kết quả cốt lõi, dữ liệu, quyền hoặc luồng bắt buộc |

## Ca bắt buộc

| ID | Tình huống | Input | Mong đợi và oracle độc lập | Critical? | Cách kiểm |
| --- | --- | --- | --- | --- | --- |
| [Cần điền] | Luồng hợp lệ | [Cần điền] | [Cần điền] | [Có/không] | [Test/eval/người] |
| [Cần điền] | Input thiếu/sai | [Cần điền] | [Cần điền] | [Có/không] | [Cần điền] |
| [Cần điền] | Phụ thuộc lỗi | [Cần điền] | [Cần điền] | [Có/không] | [Cần điền] |

Bổ sung quyền/ghi lặp/tool budget khi sản phẩm thực sự có; ghi lý do nếu không áp dụng. Không tự thêm auth/DB để làm đầy bảng.

## Quy tắc kết luận

Mỗi ngưỡng cần lý do nghiệp vụ, phạm vi đo và người chấp nhận. Mọi ca critical phải có kết quả; lỗi vận hành, timeout hoặc chưa chạy không được thành pass. Điểm trung bình không bù cho lỗi critical. Demo hoạt động không đồng nghĩa production-ready.

Thay đổi contract: ghi quyết định cũ, căn cứ mới, tác động và người chấp nhận trước khi sửa expected hoặc ngưỡng. Các placeholder chưa phải oracle dùng để chạy.
