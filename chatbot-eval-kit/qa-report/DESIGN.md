# Thiết kế báo cáo QA

Tham chiếu: [Apple DESIGN.md của VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/apple/DESIGN.md).

Điều chỉnh cho tác vụ đọc báo cáo: nền trắng/xám #f5f5f7, chữ #1d1d1f, hành động xanh #0066cc, đường phân cách mảnh, thẻ bo 18px, không gradient hoặc bóng trang trí. Font hệ thống, cỡ thân bài 17px và dòng 1.5; khoảng trắng làm rõ thứ tự đọc. Xanh lá/đỏ/vàng chỉ thể hiện trạng thái và luôn có nhãn chữ.

Bố cục: kết luận đề xuất → độ phủ kiểm thử → điều kiện nghiệm thu → chỉ số được giải thích → phiếu kiểm thử → lỗi cần xử lý. Dùng thẻ thay cho bảng sáu cột hẹp. Mỗi phiếu đặt mong đợi/thực tế cạnh nhau; bước tái hiện, assertion và evidence ở dưới. Biểu đồ tính từ trạng thái, không dựng điểm hoặc trộn chất lượng sản phẩm và AI.

HTML độc lập, hỗ trợ bàn phím, tìm/lọc, mở/thu gọn và in toàn bộ. Trên điện thoại chuyển về một cột. PDF dùng font DejaVu được đóng gói để giữ tiếng Việt; bản in ưu tiên chữ đọc được hơn giảm số trang. Không dùng logo Apple hoặc ngụ ý Apple chứng nhận.
