# Hợp đồng kế hoạch và skill

## Nguồn và yêu cầu

Đọc [tài liệu gốc](../../cac-huong-phat-trien-san-pham-dua-vao-techstack.md), nhất là phần 18–21. Người dùng yêu cầu cập nhật cả tài liệu lẫn skill để bàn giao cho agent chưa có context. Không biến ví dụ đổi trả thành yêu cầu chung của mọi dự án.

## File và các bước

1. Cập nhật tài liệu gốc: chế độ lập kế hoạch, brief tự đủ, inventory có evidence, requirement/acceptance mapping, phase contracts, trạng thái sẵn sàng và tự kiểm khi bỏ lịch sử chat.
2. Tạo `skills/ai-product-planning/SKILL.md`, metadata và reference đóng gói từ nguồn; thêm `scripts/sync-planning-skill.py` để kiểm lệch bản.
3. Cập nhật README về phạm vi mới và cách dùng. Cài bản skill đầy đủ vào thư mục skill cá nhân nếu chưa có bản khác.
4. Chạy validator, kiểm link và đồng bộ. Agent độc lập thử một đề thiếu dữ liệu và một đề không thuộc BTC trong thư mục tạm; đọc kết quả thực tế trước khi sửa.

## Kiểm chứng và giới hạn

Không thay model/ngân sách của đề thành dữ kiện đã xác minh. Kế hoạch chưa đủ đầu vào vẫn phải có phần làm được và câu hỏi có owner; chỉ nhánh phụ thuộc bị chặn. Lệnh/file chưa tồn tại phải được đánh dấu dự kiến. Mỗi phase có điều kiện vào/ra, file, thứ tự, oracle và hành động khi lỗi.

Rollback: hoàn tác đúng thay đổi tài liệu/skill/script của task; giữ các file khác. Gói cài cá nhân là bản sao của gói trong repo, không tạo phụ thuộc tới đường dẫn repo gốc.
