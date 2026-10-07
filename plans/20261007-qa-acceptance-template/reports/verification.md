# Kiểm chứng mẫu nghiệm thu QA

Ngày: 07/10/2026. Phạm vi thay đổi: `chatbot-eval-kit/qa-report/` và liên kết trong hai hướng dẫn của kit. Không thay runner cũ, không chạy lại model, không commit/push.

## Kết quả bàn giao

- Template: 20 ca đề xuất, 14 chỉ số, 5 điều kiện nghiệm thu; chưa có output, kết quả hoặc ngưỡng đã phê duyệt.
- Ví dụ: giữ nguyên 24 output và kết luận LLM sau audit, thêm 5 lifecycle checks và 1 crawl đã lưu. Tổng 32 mục gồm 30 đã chạy (12 đạt, 18 chưa đạt), 1 agent chưa chạy và 1 semantic judge bị chặn. 6/24 là kết quả LLM; 12/30 không phải điểm AI tổng hợp.
- HTML độc lập, đầy đủ mọi phiếu, có tìm kiếm/lọc/biểu đồ từ dữ liệu.
- PDF tổng hợp: template 17 trang, ví dụ 20 trang; có tất cả mã ca và chỉ số, chọn một phiếu chi tiết mỗi phạm vi và công bố rõ cách chọn. `--all-cases` xuất mọi phiếu; HTML/JSON luôn giữ đầy đủ.
- Font DejaVu và giấy phép đi cùng renderer. Gói ZIP chứa kit, hướng dẫn, input, renderer, font, báo cáo và bằng chứng; không chứa môi trường, model, cache hoặc khóa.

## Xác minh

- 9 kiểm tra tự động đạt, gồm mẫu số, bằng chứng bắt buộc, kết luận ngưỡng, output không tin cậy, mẫu chưa chạy và bảo toàn audit R04.
- Đối chiếu dữ liệu ví dụ với archived responses/audit; không biến exact-match hoặc text retrieval thành đánh giá ngữ nghĩa.
- HTML xem ở 1280px và 390px: không tràn ngang. Lọc agent được 4/20 ca của template; lọc R04 + Chưa đạt được đúng 1/32 ca của ví dụ. Mở chi tiết hiển thị điều kiện, bước kiểm, kỳ vọng/thực tế và checks.
- Render tất cả trang PDF thành ảnh và kiểm bố cục, tiếng Việt, bảng và phân trang. Kiểm lại các trang chỉ mục sau chỉnh cuối. Kiểm máy xác nhận mọi mã ca/chỉ số xuất hiện, không có trang trắng hoặc chữ vượt khung.
- Giải nén ZIP sang thư mục tạm có khoảng trắng; chạy cả hai HTML/PDF từ đó thành công. HTML trùng bản bàn giao từng byte; font lấy trong gói. Chạy lại 9 kiểm tra trong gói đều đạt.
- Không có phụ thuộc `/Users/` hoặc `/Volumes/` trong mẫu mới. Script trong `example-evidence` chỉ là snapshot tham chiếu có README giới hạn phạm vi, không được giới thiệu như sản phẩm có thể chạy sẵn.

## Giới hạn

Đây là thay đổi cách trình bày và hợp đồng dữ liệu báo cáo. Ví dụ dùng bằng chứng cũ: inference model thật trên corpus tổng hợp nhỏ, kiểm pipeline và crawl riêng. Không có kết quả agent tác động công cụ hoặc semantic judge mới; chưa đủ căn cứ ký nghiệm thu một chatbot tích hợp.
