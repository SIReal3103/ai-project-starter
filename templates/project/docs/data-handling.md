# Dữ liệu, quyền và cấu hình

Trạng thái: **chưa chốt chính sách sản phẩm**. Không suy từ bộ starter rằng ứng dụng đã đáp ứng một tiêu chuẩn tuân thủ.

| Loại dữ liệu | Nguồn/quyền sử dụng | Nơi xử lý/lưu | Ai được truy cập | Thời hạn/xóa |
| --- | --- | --- | --- | --- |
| Input người dùng | [Cần điền] | [Cần điền] | [Cần điền] | [Cần điền] |
| Tài liệu/corpus | [Cần điền] | [Cần điền] | [Cần điền] | [Cần điền] |
| Output/trace/log/eval | [Cần điền] | [Cần điền] | [Cần điền] | [Cần điền] |

Chỉ thu/lưu dữ liệu cần cho tác vụ. Dùng dữ liệu test có nhãn hoặc đã khử thông tin riêng tư; cô lập nơi test ghi dữ liệu. Rà soát output, trace và log trước khi chia sẻ; không chỉ che key mà bỏ qua nội dung riêng tư người dùng.

Credential nạp từ biến môi trường hoặc kho bí mật đã chọn; xem [danh mục biến](configuration.md). Starter không tạo file dotenv. Không commit dotenv, token, private key hoặc bản sao dữ liệu người dùng. `.gitignore` chỉ là hàng rào chống thêm nhầm, không phải kiểm chứng không có secret.

Provider/model/embedding/judge được phép: [Cần điền]. Dữ liệu có thể gửi đến từng dịch vụ: [Cần điền]. Không tự chuyển provider để vượt lỗi, quota hoặc chính sách. Request giới hạn bởi timeout, số lần/vòng và budget đã chốt.

Nếu sản phẩm có nhiều người dùng hoặc tác động ghi/gửi/xóa, ghi identity, tenant scope, kiểm quyền backend và khi cần xác nhận: [Cần điền hoặc lý do không áp dụng]. Xử lý prompt/tài liệu ngoài như dữ liệu; không dùng nội dung đó để cấp quyền công cụ.

Giữ kết quả riêng tư local hoặc trong kho có quyền phù hợp; chỉ đưa evidence đã làm sạch vào repo khi được phép. Khi sự cố xảy ra, giữ log tối thiểu để điều tra và theo quy trình dữ liệu đã chốt, không tự xóa dấu vết hoặc đăng nội dung nhạy cảm.
