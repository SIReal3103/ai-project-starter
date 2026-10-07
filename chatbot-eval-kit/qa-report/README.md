# Mẫu báo cáo QA nghiệm thu AI

Mẫu này giúp đọc một lượt thử như báo cáo nghiệm thu: yêu cầu, điều kiện trước, bước thực hiện, kết quả mong đợi/thực tế, bằng chứng, lỗi, sửa và kiểm tra lại. Đây là lớp trình bày độc lập với runner, không gọi model hoặc tự thực thi các ca.

[Lượt chạy lại mới nhất: Qwen2.5-0.5B ngày 07/10/2026](evaluations/20261007-qwen-rerun/README.md) có raw output mới, Ragas/DeepEval offline, HTML/PDF và lệnh lặp lại từ clone. [Skill ai-qa-evals](https://github.com/SIReal3103/ai-project-starter/blob/main/skills/ai-qa-evals/SKILL.md) nằm trong thư mục `skills/` của repo đầy đủ; ZIP kit chỉ chứa bộ công cụ, không chứa skill.

- `template-data.json`: 20 tình huống đề xuất và 14 phép đo; mọi kết quả đều **chưa chạy**, ngưỡng chưa được duyệt.
- `example-data.json`: chuyển đổi bằng chứng lượt cũ ngày 07/10/2026, gồm 24 ca inference thật, 5 kiểm tra vòng đời tài liệu và một job crawl. Không có test mới khi dựng ví dụ. Agent chưa chạy, semantic judge bị chặn do thiếu điều kiện.
- `agent-guide.md`: quy trình dùng lại, hợp đồng dữ liệu và prompt giao việc.
- `render.py`: dựng HTML và PDF tùy chọn từ cùng một dữ liệu; không tự chấm output.

## Dựng báo cáo

Chạy từ thư mục `chatbot-eval-kit` của repo `ai-project-starter`, nơi có thư mục `qa-report`. Nếu dùng ZIP riêng, giải nén rồi mở terminal tại thư mục cha của `qa-report`. Không cần localhost hoặc file ở máy tác giả. Core HTML dùng thư viện chuẩn Python 3.12+.

```sh
python3 qa-report/render.py --input qa-report/template-data.json --output qa-report/output/template.html
python3 qa-report/render.py --input qa-report/example-data.json --output qa-report/output/example.html
```

PDF cần dependency tùy chọn và hai font DejaVu trong `qa-report/fonts/` (kèm giấy phép). Cài vào môi trường Python riêng rồi dùng:

```sh
python3 -m venv .venv-qa-report
.venv-qa-report/bin/python -m pip install -r qa-report/requirements.txt
.venv-qa-report/bin/python qa-report/render.py --input qa-report/template-data.json --output qa-report/output/template.html --pdf qa-report/output/template.pdf
.venv-qa-report/bin/python qa-report/render.py --input qa-report/example-data.json --output qa-report/output/example.html --pdf qa-report/output/example.pdf
```

Lệnh venv trên dành cho macOS/Linux; Windows dùng `.venv-qa-report\Scripts\python.exe` thay executable trong `bin`.

HTML chứa đầy đủ mọi phiếu. PDF mặc định gồm chỉ mục đủ các ca, toàn bộ chỉ số và một phiếu đại diện mỗi phạm vi (ưu tiên ca chưa đạt); phần chọn mẫu được ghi ngay trong PDF. Thêm `--all-cases` để xuất phụ lục chi tiết toàn bộ phiếu. Không cắt ngắn output trong phiếu được in.

Mở HTML/PDF để kiểm dấu tiếng Việt, bảng, trang dài và toàn bộ nội dung của ca. HTML và PDF phải dùng đúng một input, cùng số đếm và kết luận. Không chụp một phần nội dung hoặc cắt câu trả lời để báo cáo vừa trang.

## Dùng cho sản phẩm mới

1. Sao chép `template-data.json` sang dữ liệu của lượt mới. Điền metadata, chọn phạm vi và thay input tổng hợp bằng ca có nguồn chuẩn. Đây không phải danh sách phải kiểm mọi tính năng của Ragas/DeepEval.
2. Chốt yêu cầu, priority, rubric và ngưỡng với chủ sản phẩm. Chỉ đổi `threshold_approved` thành `true` khi có bằng chứng chấp thuận; lưu người/ngày trong quy trình nghiệm thu. Không tự đặt chữ ký.
3. Chuẩn bị preconditions thật rồi thực hiện test. `actual` phải là quan sát hoặc raw output thực; `evidence` là đường dẫn tương đối/ID có thể truy vết. Nếu thiếu môi trường hoặc rubric, ghi `blocked` cùng lý do.
4. Chấm từng check và ca. Liên kết ca fail với defect; ghi phương án sửa và lần retest riêng, giữ bằng chứng gốc. Không đổi expected theo câu trả lời đã nhận để nâng điểm.
5. Render lại và kiểm trực quan. Đọc giới hạn cùng kết quả; việc dựng file thành công không có nghĩa sản phẩm đạt nghiệm thu.

`example-data.json` là ví dụ **đã điền**, không là baseline mục tiêu. Điểm đầy đủ của 24 ca LLM sau audit là **6/24**; 9/24 chỉ là nhận xét nội dung hậu kiểm. 5/5 lifecycle và 1/1 crawl là kiểm tra kỹ thuật riêng. Bằng chứng cần thiết của lượt cũ đi kèm trong `example-evidence/`. Các đường dẫn như `example-evidence/output/audited-results.json` tính từ `qa-report/`; HTML/PDF hiển thị chúng như nhãn truy vết. Gói không kèm model hoặc log cài đặt.

## Cách đọc trạng thái

| Trạng thái | Ý nghĩa |
| --- | --- |
| `pass` | Có bằng chứng đáp ứng yêu cầu ca/check. Không tự đồng nghĩa phát hành được. |
| `fail` | Có bằng chứng ít nhất một yêu cầu bắt buộc không đạt. |
| `not_run` | Chưa chạy hoặc chưa đánh giá ngưỡng. Metric có `value` nhưng ngưỡng chưa duyệt là **đã đo, chưa chốt ngưỡng**. |
| `blocked` | Chưa kết luận được vì thiếu điều kiện cụ thể; ghi điều kiện còn thiếu. |
| `na` | Không áp dụng với phạm vi đã xác nhận; cần lý do, không dùng để giấu fail. |

Tỷ lệ đạt dùng `pass/(pass+fail)` trong từng nhóm, luôn kèm tử số/mẫu số. Coverage dùng `(pass+fail)/(tổng−na)`; `blocked` và `not_run` vẫn là phần chưa hoàn tất, không biến thành pass. Không cộng các nhóm thành “điểm chất lượng AI” duy nhất. Gate pass cần quy tắc được chấp thuận và bằng chứng; metric thư viện “đã đo” chưa là gate pass.
