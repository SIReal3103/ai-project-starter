# Báo cáo QA mock: An Tâm Support AI

Ví dụ tiếng Việt theo `ai-qa-evals` và `ai-qa-metrics`. Mọi input, output, trace, nhãn, latency và số đếm đều tổng hợp. Không gọi sản phẩm/model, không chạy Ragas judge hay security scanner để tạo số liệu này.

- 24 ca QA: 14 Đạt, 8 Chưa đạt, 1 Bị chặn, 1 Chưa chạy.
- 21 chỉ số: định nghĩa, mẫu số, cách tính, diễn giải và mốc đề xuất chưa phê duyệt. M01–M21 là mã dòng cục bộ của báo cáo, không là số thứ tự danh mục chỉ số của skill.
- 8 lỗi minh họa với ảnh hưởng, hướng sửa và điều kiện retest.
- HTML tự chứa và PDF 13 trang A4 ngang; biểu đồ nhóm QA và phân bố E2E.

## Xem và dựng lại

Mở `report.html` bằng trình duyệt hoặc `report.pdf`. Không cần localhost.

Từ thư mục này:

```sh
python3 build-report.py
```

Script tự chứa bằng Python stdlib; dựng lại `fixture.json`, `report-data.json` và HTML. Muốn thay dữ liệu mẫu, chỉnh ROWS và các tập dữ liệu trong script; không chỉnh JSON sinh ra rồi chạy script vì sẽ bị ghi đè. Schema `mode=mock` của ví dụ này thuộc renderer riêng, không đưa vào `qa-report/render.py` chỉ nhận template/evidence.

Để xuất PDF, từ thư mục `chatbot-eval-kit` của repo:

```sh
npm ci
npx playwright install chromium
node render-pdf.mjs --input qa-report/examples/mock-acceptance-report-v2/report.html --output qa-report/examples/mock-acceptance-report-v2/report.pdf
```

Kiểm HTML trước khi in. PDF được in trực tiếp từ HTML bằng Chromium; không có renderer PDF riêng. Ngưỡng là đề xuất; nhãn Pass/Fail trong bảng QA chỉ thuộc kịch bản minh họa.

## Bảng QA 7 cột

Mã ca | Tình huống & đầu vào | Kết quả mong đợi | Kết quả giả lập | Kết quả Pass/Fail | Nhận xét QA | Bằng chứng / Mã lỗi.

Các tham chiếu `fixture.json#cases/P01` là ký hiệu tra theo trường `id`, không phải JSON Pointer chuẩn hoặc link trình duyệt tự cuộn. Mỗi record chứa điều kiện trước và bước đối chiếu. Dữ liệu latency, retrieval và claim là các tập phụ độc lập được nêu mẫu số riêng; không cộng chúng thành số ca QA.

## Thiết kế và kiểm tra

Tham chiếu Apple: https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/apple/DESIGN.md. Áp dụng trắng/xám nhẹ, chữ hệ thống, xanh #0066cc, đường kẻ mảnh, khoảng trắng; không dùng logo thương hiệu. Bảng là nội dung chính. Màn hình hẹp cuộn bên trong bảng, không tràn toàn trang.

Đã kiểm 13 trang render PNG, số ca/metric, nhãn MOCK từng trang và toàn bộ actual bằng `pdftotext -raw`; cách trích `-layout` xen kẽ các cột nên không dùng để so nguyên văn từng ô. `verification.json` chỉ ghi kiểm artifact, không phải test sản phẩm. Mốc E2E p95=9,5 s, TTFT p95=1,7 s và các tỷ lệ được kiểm từ mock gốc.
