---
name: ai-qa-evals
description: Chạy hoặc chạy lại eval chatbot, RAG, LLM và agent; thu bằng chứng và xuất báo cáo nghiệm thu QA tiếng Việt dạng HTML/PDF. Dùng khi cần test chất lượng AI hoặc tái sử dụng bộ QA cho sản phẩm mới; không dùng chỉ để lập kế hoạch hay thiết kế giao diện.
---

# QA và eval sản phẩm AI

Chọn đúng sản phẩm, dữ liệu và ngân sách của người dùng. Bàn giao kết quả thực, ca Đạt/Chưa đạt, phần chưa đo và báo cáo có thể truy vết. Không thay một yêu cầu kiểm sản phẩm thật bằng demo dùng luật.

## Tìm bộ công cụ

Skill này không cần file trên máy tác giả. Nếu workspace có `chatbot-eval-kit/qa-report/render.py`, dùng bộ đó và ghi commit/version. Nếu chưa có, clone vào thư mục mới trong workspace:

```sh
git clone https://github.com/SIReal3103/ai-project-starter.git qa-resources
cd qa-resources/chatbot-eval-kit
```

Git và Python 3.12+ là điều kiện đầu vào. Đọc `README.md`, `agent-guide.md`, `qa-report/README.md` và `qa-report/agent-guide.md` từ thư mục kit. Chỉ đọc `integrations/README.md` khi chạy Ragas/DeepEval/judge. Không coi các lệnh clone/demo là đã đánh giá sản phẩm. Không tự ghi đè checkout hoặc output đã tồn tại.

## Chọn lượt thực thi

- **Sản phẩm mới:** đọc yêu cầu và hợp đồng API; chọn ca liên quan từ template, tạo dataset có reference độc lập, dùng adapter sản phẩm thật. Nếu API chỉ trả text, không kết luận đã test agent/tool execution.
- **Chạy lại model:** giữ dataset/prompt/version để so sánh; gọi lại model và tạo raw responses mới. Với API đọc hướng dẫn adapter `adapters/openai-chat.py` hoặc `adapters/http-product.py`. Với MLX trên macOS Apple Silicon, xem README của ví dụ `qa-report/evaluations/20261007-qwen-rerun/`; đó là bộ thử đóng băng, không phải sản phẩm mặc định.
- **Chấm lại output:** `main.py replay` chỉ chấm câu trả lời đã có; ghi rõ không có inference mới. Lượt mới luôn dùng thư mục output mới.
- **Chỉ xuất báo cáo:** dùng JSON có bằng chứng, không gọi lại model/API nếu không được yêu cầu.

Ghi trước lượt chạy: model/revision, dataset hash, nguồn dữ liệu thật/tổng hợp, phạm vi, budget và các điều kiện thiếu. Nếu chỉ có khoảng 10 phút, ưu tiên kiểm contract và ca trọng yếu; semantic judge chọn mẫu theo budget, không âm thầm rút mẫu rồi báo đã phủ toàn bộ.

Core không cần package. `sh setup-tools.sh` cài môi trường Ragas/DeepEval riêng khi cần. Dùng interpreter mà setup tạo hoặc biến `EVAL_RAGAS_PYTHON`/`EVAL_DEEPEVAL_PYTHON` được cấu hình rõ; không suy ra từ home của tác giả. Để chấm output lưu sẵn, từ thư mục kit:

```sh
python3 main.py replay --dataset datasets/product-cases.jsonl \
  --responses runs/product-inference/responses.json \
  --out runs/product-score-01 --frameworks auto
```

Thay các đường dẫn ví dụ bằng file đã xác minh. Exit 1 có ca fail là kết quả cần báo, không phải lý do đổi expected. Exit 2 cần đọc lỗi/bằng chứng thiếu. Judge chỉ chạy khi có endpoint/model/key phù hợp và budget; dùng `--judge --judge-max-cases` theo README. Không mặc định dùng model đang test làm judge; không in key hoặc tự chọn dịch vụ trả phí khác khi lỗi. Dừng khi hết budget hoặc lỗi cấu hình/auth, không retry vô hạn.

## Những điều ảnh hưởng kết luận

- Gold/oracle không được đưa vào input model. Retrieval context phải từ hệ thống đích hoặc snapshot được ghi rõ; không giả trace từ câu “đã gọi tool”. Agent cần state trước/sau, đúng đối tượng, quyền/phê duyệt, retry và chống tác động trùng.
- Ragas text matching offline không phải faithfulness/correctness ngữ nghĩa. AP theo thứ hạng không phải precision@k. Exact match chỉ hợp lý cho đầu ra đóng. Metric đã đo chưa đồng nghĩa đạt ngưỡng nghiệm thu.
- Đọc lỗi đại diện và đối chứng. Số trong ID citation có thể khiến kiểm chuỗi báo đạt nhầm; tách citation khi audit đáp án số, lưu raw và audit riêng. Không tái dùng nhận xét cũ khi output thay đổi. Không gọi audit keyword là semantic judge.
- Đo guardrail cả tấn công và yêu cầu hợp lệ; canary tổng hợp không phải key thật. Báo sample size và giới hạn. Không lộ canary nguyên văn chưa chứng minh mọi dạng rò rỉ đều bị chặn.
- Thiếu điều kiện: `blocked`; chưa chạy: `not_run`; không áp dụng cần lý do. Không biến thiếu evidence thành pass. Không trộn kiểm tra cài đặt/crawl với điểm chất lượng LLM.

## Xuất báo cáo QA

Sao chép `qa-report/template-data.json` sang JSON của lượt mới. Điền theo hợp đồng trong `qa-report/agent-guide.md`; mỗi ca có requirement, preconditions, steps, expected, actual nguyên văn, checks, evidence, defect và retest. Mỗi metric có định nghĩa, cách đo, ngưỡng, mẫu số, diễn giải và giới hạn. Chỉ ghi ngưỡng đã phê duyệt khi thực sự có chấp thuận; không tự ký nghiệm thu.

Đường dẫn evidence tương đối có gốc được ghi rõ. Không dùng đường dẫn home hoặc file localhost không được đóng gói. Nếu dữ liệu riêng tư không thể công khai, giữ evidence ở nơi được phép và ghi giới hạn truy cập.

```sh
python3 qa-report/render.py --input runs/product-01/report-data.json \
  --output runs/product-01/report.html
```

Báo cáo dùng bảng QA bảy cột: Mã ca; Tình huống & đầu vào; Kết quả mong đợi; Kết quả thực tế (hoặc Kết quả giả lập với mock); Kết quả (Pass/Fail); Nhận xét QA; Bằng chứng / Mã lỗi. Cột Kết quả phải riêng, hiển thị Đạt (Pass), Chưa đạt (Fail), Chưa chạy, Bị chặn hoặc Không áp dụng; không dùng “Pass/No” hoặc gộp trạng thái vào mã ca. Điều kiện trước, bước thực hiện, priority và retest giữ ở chi tiết phụ có mã ca tham chiếu. Nếu renderer đang dùng còn năm cột, cập nhật bố cục bảy cột trước khi xuất báo cáo; không đổi schema trạng thái hoặc raw output chỉ để thay bố cục. Eval và defect dùng bảng riêng, diễn giải dễ hiểu. Dùng thiết kế Apple-like trong kit, không chuyển các ca thành thẻ dài.

**Kiểm HTML trước rồi mới xuất PDF từ chính HTML đó.** Từ thư mục kit:

```sh
npm ci
npx playwright install chromium
node render-pdf.mjs --input runs/product-01/report.html --output runs/product-01/report.pdf
```

Cần Node.js 18+; Linux có thể cần `npx playwright install --with-deps chromium`. PDF A4 ngang chứa mọi ca, mở mọi chi tiết, không giữ bộ lọc màn hình. Không dùng ReportLab, chọn ca đại diện hoặc cắt output. `render.py --pdf` cũng gọi exporter HTML này; hai bước riêng giúp kiểm thiết kế trước khi in.

Kiểm tổng số từ ca, phân biệt coverage và tỷ lệ đạt, đối chiếu evidence, xem HTML ở màn hình lớn/nhỏ và render mọi trang PDF để kiểm tiếng Việt/cắt nội dung. Bàn giao report-data, HTML/PDF, bằng chứng được phép, lỗi còn mở và hướng cải thiện. Khi chỉ dựng lại report, nói rõ không có test mới.

## Công bố

Skill không mặc nhiên cho phép commit/push, upload evidence hay sửa quyền repo. Khi người dùng đã yêu cầu cập nhật GitHub, kiểm diff và dữ liệu nhạy cảm, chỉ đưa file thuộc task, giữ lịch sử kết quả và xác nhận remote sau push. Không đưa venv, model cache, key hoặc dữ liệu người dùng riêng tư vào gói.
