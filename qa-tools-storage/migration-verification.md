# Hậu kiểm chuyển bộ công cụ QA — 07/10/2026

Báo cáo này xác minh bộ công cụ chạy được sau khi chuyển sang SSD. Dữ liệu smoke là fixture; không có lượt gọi LLM hoặc kết luận nghiệm thu sản phẩm trong lần chuyển này.

| Kiểm tra | Kết quả | Ý nghĩa |
| --- | --- | --- |
| Copy 7 nhóm runtime/cache | Checksum khớp | Bản copy được kiểm trước khi thay nguồn bằng symlink |
| Launcher/version | 17/17 đạt | pytest, coverage.py, Ruff, Vitest, Playwright, Promptfoo, Semgrep, Bandit, pip-audit, Gitleaks, k6, Trivy, ZAP, FFmpeg, ffprobe, Ragas, DeepEval |
| Python smoke | 3/3 đạt | Package test, WER/CER và đo RSS còn hoạt động |
| Vitest/V8 | 4/4 đạt | Unit fixture chạy và xuất coverage; coverage 100% chỉ áp dụng fixture này |
| Chromium/axe | 2/2 đạt | Browser hoạt động; axe đọc trang và phát hiện đúng lỗi accessibility đã biết |
| Ragas offline | 4 đối chứng đạt | Context recall/precision cho ca khớp và không khớp; không dùng semantic judge |
| DeepEval offline | 2 đối chứng đạt | Exact match đúng/sai; không đo toàn bộ chất lượng chatbot |
| Semgrep | Phát hiện 1 lỗi mẫu | Local rule bắt đúng `eval()` trong fixture, không có lỗi scanner |
| Tháo/mount lại | Thành công; 17/17 đạt | Công cụ hoạt động sau khi mở lại image |
| Xóa backup đã kiểm | 7/7 hoàn tất | Dung lượng trống tăng khoảng 6,33 GB tại thời điểm đo |

Tổng kích thước backup theo `du` khoảng 7,52 GB; dung lượng trống đo trước/sau xóa khoảng 10,02 → 16,35 GB. Hardlink và hoạt động khác trên máy làm hai số khác nhau. Homebrew và runtime nền vẫn dùng vị trí cài hệ thống.

## Xác minh gói GitHub

- Shell syntax và Ruff của các script đạt.
- Script APFS mới đã tạo image thử 512 MiB trên SSD, mount, gọi mount lần nữa, unmount, remount và unmount thành công. Đã dọn image thử.
- `doctor.py` trong repo dùng activation mới và nhận diện được 17/17 công cụ trên bộ đã chuyển.
- Script mount trong repo nhận đúng ID của volume đang dùng.
- Launcher ZAP trong repo trả phiên bản 2.17.0 trên Java hiện có.
- Các package/lock được lấy từ bản cài đã kiểm. Không thực hiện thêm một lượt tải và cài sạch toàn bộ package trong lần xuất bản này; máy mới cần chạy installer và tự kiểm lại theo README.

Manifest chứa đường dẫn home, image nhiều GB, cache và evidence sản phẩm được giữ trên SSD. Repo chỉ chứa script, package manifest/lock, hướng dẫn và bản tóm tắt kết quả.
