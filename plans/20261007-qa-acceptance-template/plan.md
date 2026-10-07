# Mẫu nghiệm thu QA sản phẩm và AI

Trạng thái: hoàn tất ngày 07/10/2026; chưa commit/push.

## Phạm vi
- Mẫu JSON + HTML độc lập, có thể điền cho sản phẩm khác; mẫu chưa chạy không có điểm giả.
- Thẻ ca kiểm thử có mục tiêu, điều kiện, bước thao tác, mong đợi, thực tế, Đạt/Chưa đạt và bằng chứng.
- Tiêu chí sản phẩm, LLM/RAG, agent, guardrails, vận hành; nêu rõ cách đo và điều kiện nghiệm thu.
- Báo cáo ví dụ từ bằng chứng đã chạy; không tạo thêm kết quả test hoặc xác nhận đã test agent.
- Giao diện Apple-like; PDF dễ đọc; hướng dẫn agent và lệnh chạy từ clone.

## Phases
1. Hoàn tất hợp đồng dữ liệu, 20 ca đề xuất, 14 chỉ số và hướng dẫn.
2. Hoàn tất renderer HTML/PDF dùng chung dữ liệu; responsive, tìm/lọc và in.
3. Hoàn tất kiểm nội dung, dữ liệu và hiển thị; thử gói sau giải nén ở thư mục độc lập.

Kết quả kiểm chứng: [báo cáo bàn giao](reports/verification.md).

## Nghiệm thu
Không có local path trong template/guide. Tách tỷ lệ chạy, tỷ lệ đạt, giới hạn mẫu. Không coi thiếu bằng chứng là đạt. Biểu đồ sinh từ dữ liệu. Đọc được PDF và đủ dấu tiếng Việt. Không auto-commit/push.
