# Bằng chứng của ví dụ đã điền

Đây là bản trích từ lượt chạy ngày 07/10/2026, không phải bộ chạy mới hay dữ liệu production.

- `cases.jsonl`: bộ 24 ca/đáp án đã soạn trước inference; `requests.json`: prompt thực tế gửi model.
- `responses.json` và `evidence/generation-traces.json`: output LLM thật, thời gian, token.
- `output/eval/results.json`: kết quả thô, gồm Ragas offline và DeepEval exact-match.
- `output/audited-results.json`: kết quả sau audit, 6/24 ca đạt. R04 bị loại do số nằm trong ID citation.
- `evidence/lifecycle.json`: 5 kết quả kiểm API lưu từ lượt cũ.
- `evidence/crawl-*.json`: crawl thật trang Python, duyệt và truy hồi; khác corpus thư viện tổng hợp dùng chấm LLM.
- `evidence/retrieval-*.json`, `evidence/documents.json`: dữ liệu đã duyệt/truy hồi trong kho thử.
- `evidence/*manifest.json`, `evidence/repositories.json`: phiên bản, hash và tham số.
- Ba script ở đây là nguồn tham khảo cách tạo bằng chứng; không gọi chúng như lệnh chạy template. Model, virtualenv và server không đóng gói.

Gói đã lưu 24 output bằng Qwen2.5-0.5B-Instruct 4-bit qua MLX local; không có agent gọi tool hoặc judge độc lập. Khóa cloud chưa xác thực được, vì vậy semantic embeddings chưa chạy. Chuỗi canary trong prompt là dữ liệu tự tạo, không phải key API.

Để dùng mẫu cho sản phẩm khác, đọc `../agent-guide.md` và `../README.md`. Render báo cáo không cần tải model, mở localhost hay cung cấp key; chỉ cần JSON và renderer trong cùng gói.
