# Kiểm bản starter độc lập

Ngày: 07/10/2026. Đây là báo cáo kiểm **khả năng đóng gói và tái sử dụng starter**, không phải điểm chất lượng của một sản phẩm AI mới.

| Phép kiểm | Kết quả | Ý nghĩa |
| --- | --- | --- |
| Clone từ Git commit vào thư mục sạch | Đạt | Chỉ dùng file đã commit, không mang runtime/caches theo |
| Kiểm đường dẫn, liên kết Markdown và cú pháp Python | Đạt | Không có đường dẫn máy hardcode hoặc link tài liệu thiếu; links trong template được kiểm sau sinh dự án |
| Tests scaffolder và kiểm đóng gói | 23/23 đạt | Không ghi đè dữ liệu; xử lý Unicode, đường dẫn tương đối, symlink, nguồn thiếu và tài liệu được tạo |
| Tests evaluator/transport/portability | 25/25 đạt | Oracle không gửi cho target, trace thiếu không được coi đạt, output sai bị bắt, runtime ngoài kit không tự được tìm |
| Demo tổng hợp | 40/40 ca đạt | Chỉ xác nhận hành vi trợ lý dùng luật và bộ kiểm trên tập mẫu |
| Đối chứng sai | 8/8 bị phát hiện | Kiểm bộ chấm, không cộng vào điểm sản phẩm |
| Ragas offline từ môi trường Python 3.12 mới | 24 phép đo | Context recall/precision dựa trên khớp văn bản; không phải judge ngữ nghĩa |
| DeepEval offline từ môi trường Python 3.12 mới | 7 phép đo | ExactMatch cho ca đáp án đóng; không phải inference LLM |
| Chạy lại setup và cài dependency PDF theo lock | Đạt | Hai môi trường framework tách biệt; npm install và cú pháp renderer hợp lệ |
| Di chuyển dự án sinh ra, đổi vị trí starter, chạy từ cwd khác | Đạt | Đủ bảy guides, demo 40/40 và HTML hoạt động độc lập |
| Chạy core/report không nạp site packages, không có timezone database | Đạt | Core dùng thư viện chuẩn, không cần package hệ thống bên ngoài |
| Gitleaks trên snapshot các file chuẩn bị commit | Không phát hiện secret | Không đưa credentials, dotenv, runtime hoặc dữ liệu sản phẩm riêng vào repo |

## Những gì còn cần khi dùng cho sản phẩm thật

Cần triển khai app, chuẩn bị dữ liệu/oracle có quyền sử dụng, nối adapter và trace thật, chọn provider/model cùng ngân sách. LLM judge live chưa được xác nhận trong mẫu này. PDF renderer đã kiểm dependency/cú pháp; lượt đóng gói này kiểm HTML, không có lượt render/review PDF mới.

Danh mục Vitest, Promptfoo, coverage.py, Gitleaks và các công cụ khác nằm trong guide evals; ngoài các thành phần ghi rõ được bundle, chúng là lựa chọn cài theo stack. Starter không tự cài mọi công cụ hoặc coi chúng đã đánh giá ứng dụng mới.

## Tái chạy

```sh
python3 scripts/check_repository.py
python3 -m unittest discover -s tests -v
python3 tools/evals/main.py self-test
python3 tools/evals/main.py demo --out tools/evals/runs/verification-01 --frameworks off
python3 tools/evals/report.py --input tools/evals/runs/verification-01/results.json --output tools/evals/reports/verification-01.html
```

Muốn kiểm framework, cài bằng `sh tools/evals/setup-tools.sh` rồi dùng `--frameworks auto` với output directory mới. Muốn kiểm dự án đã sinh, dùng `python3 scripts/check_repository.py --root ../ten-du-an` và chạy bộ eval bên trong dự án đó.

[Workflow CI](../../../.github/workflows/verify.yml) cấu hình core trên Linux/Windows với Python 3.12/3.14, và hai job Linux cài lock Ragas/DeepEval rồi chấm offline. Trạng thái các lần chạy được lưu tại [GitHub Actions](https://github.com/SIReal3103/ai-project-starter/actions); cấu hình workflow tự nó không phải bằng chứng một lần chạy đã đạt.
