# Bảng QA, biểu đồ và báo cáo mock

Đọc khi dựng báo cáo mới, sửa thiết kế hoặc người dùng yêu cầu mock. Giữ dữ liệu thật nguyên vẹn khi chỉ thay bố cục. Mock là một chế độ được yêu cầu rõ, không phải cách thay thế một lượt eval bị lỗi.

## Ví dụ đóng gói và chạy từ máy mới

Repo: https://github.com/SIReal3103/ai-project-starter

Mở terminal tại nơi muốn lưu repo. Chỉ clone nếu chưa có checkout; nếu có, dùng checkout đã xác minh và ghi phiên bản:

```sh
git clone https://github.com/SIReal3103/ai-project-starter.git qa-resources
cd qa-resources/chatbot-eval-kit
python3 qa-report/examples/mock-acceptance-report-v2/build-report.py
```

Mở `qa-report/examples/mock-acceptance-report-v2/report.html` trực tiếp bằng trình duyệt, không cần server. Ví dụ có 24 ca, 21 chỉ số và PDF 13 trang; đây là nội dung minh họa, không là cỡ mẫu hoặc số trang bắt buộc.

Sau khi xem HTML, từ cùng thư mục `chatbot-eval-kit`:

```sh
npm ci
npx playwright install chromium
node render-pdf.mjs \
  --input qa-report/examples/mock-acceptance-report-v2/report.html \
  --output qa-report/examples/mock-acceptance-report-v2/report.pdf
```

Cần Python 3.12+ và Node tương thích `package-lock.json`; Linux có thể cần dependencies Chromium. File PDF và HTML đã có sẵn để xem trước khi cài. Đọc README cạnh ví dụ nếu muốn thay dữ liệu.

`build-report.py` dùng Python stdlib và dữ liệu tổng hợp trong script, ghi lại fixture/JSON/HTML. Sửa JSON sinh ra rồi chạy script sẽ bị ghi đè. Schema `mode=mock` của ví dụ là riêng; không truyền vào renderer chung `qa-report/render.py` chỉ nhận template/evidence. Khi dùng dữ liệu thật, chọn hoặc điều chỉnh renderer theo hợp đồng thực, không đổi nhãn mock thành evidence rồi giữ số liệu mẫu.

## Hợp đồng trình bày

Bảng QA luôn có 7 cột: **Mã ca | Tình huống & đầu vào | Kết quả mong đợi | Kết quả thực tế hoặc giả lập | Kết quả Pass/Fail | Nhận xét QA | Bằng chứng / Mã lỗi**.

- Tách Đạt/Chưa đạt khỏi mã ca. Hiển thị chữ cùng màu; giữ Chưa chạy, Bị chặn, Không áp dụng khi phù hợp. Một tiêu chí bắt buộc sai làm ca chưa đạt; thiếu bằng chứng bắt buộc không được pass.
- Kỳ vọng nêu điều kiện quan sát được. Actual giữ nguyên output/state. Nhận xét giải thích chênh lệch và ảnh hưởng; tránh lặp mỗi chữ “sai”.
- Điều kiện trước, bước tái hiện, severity, priority và retest ở chi tiết/phụ lục hoặc fixture có liên kết mã ca. Không gộp severity và priority thành một giá trị.
- Mỗi metric có đơn vị, mẫu số, công thức/rubric, nguồn dữ liệu, giới hạn và trạng thái phê duyệt ngưỡng. Cột đánh giá mô phỏng không được hiểu là nghiệm thu thật.
- Bảng lỗi nối case ID với defect ID, tác động, hướng sửa và điều kiện retest. Mã dòng metric của báo cáo cần phân biệt với mã danh mục M01–M34 nếu đánh lại số.

## Tính trung thực khi dùng mock

- Ghi MOCK/DỮ LIỆU GIẢ LẬP ở tổng quan và mỗi trang in; cột output mang tên Kết quả giả lập. Nêu rõ tool/model nào chưa chạy. Không tạo credential hoặc dữ liệu cá nhân thật.
- Lưu một nguồn dữ liệu thống nhất cho bảng, tổng số và biểu đồ; tính tỷ lệ/percentile từ fixture. Nhãn mock không cho phép số đếm sai nhau.
- Mẫu có thể có đủ pass/fail/blocked/not_run để minh họa. Không dựng 0 lỗ hổng hoặc 100% pass cho phần chưa có dữ liệu. Ngưỡng đề xuất giữ chưa phê duyệt, không thêm chữ ký giả.
- Mẫu số các tập con phải riêng: số ca QA, số query retrieval, số mệnh đề, số request và số stream không được cộng tùy tiện. E2E thành công và timeout báo riêng; không gọi TTFB là TTFT.

## Thiết kế và kiểm tra

Dùng nền trắng/xám nhẹ, chữ hệ thống hỗ trợ tiếng Việt, xanh #0066cc cho điều hướng, đường phân cách mảnh. Bảng là nội dung chính; không biến ca thành thẻ dài. Cột trạng thái đủ rộng để chữ không bị vỡ vụn. Màn hình nhỏ cuộn trong bảng, không tràn toàn trang.

Biểu đồ hữu ích: số ca theo nhóm/trạng thái; phân bố thời gian kèm n, ranh giới đo và timeout. Không thêm “điểm AI tổng hợp” hoặc vẽ số liệu chưa có. Với mock, ghi rõ nguồn giả lập ngay cạnh biểu đồ.

Xuất PDF trực tiếp từ HTML đã kiểm, ưu tiên A4 ngang cho bảng 7 cột. Chia bảng theo nhóm khi cần, lặp đầu bảng, mở mọi chi tiết và bỏ bộ lọc khi in; không cắt output hay chỉ lấy ca đại diện để giảm trang. Khoảng trắng có chủ đích, tránh trang chỉ có footer.

Kiểm số ca và tổng trạng thái; đối chiếu tử/mẫu và công thức; kiểm actual giữa JSON/HTML/PDF. `pdftotext -layout` có thể xen kẽ nội dung giữa các cột; dùng `-raw` hoặc trích từng vùng khi so nguyên văn, rồi xem ảnh render tất cả trang để phát hiện cắt chữ/hàng và lỗi dấu. Kiểm metadata PDF không có thông tin riêng không cần công bố. Kiểm artifact thành công không đồng nghĩa sản phẩm đã được test.

Bàn giao HTML, PDF, dữ liệu và script/README dựng lại. Đường dẫn chạy phải tính từ checkout, không phụ thuộc môi trường cài cá nhân. Không ghi đè lượt đã có bằng chứng thật khi tạo ví dụ mới.
