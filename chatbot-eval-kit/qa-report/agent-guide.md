# Hướng dẫn agent lập báo cáo QA nghiệm thu

Đọc `README.md` trong thư mục này, `../agent-guide.md`, yêu cầu sản phẩm và hợp đồng API trước khi điền báo cáo. Mẫu tập trung vào hành vi có giá trị với người dùng: dữ liệu được duyệt, trả lời đúng, tìm nguồn, làm đúng tác vụ, chặn hành vi cấm và vận hành trong hạn. Chọn 20 tình huống gợi ý theo phạm vi thật; không liệt kê mọi tính năng của thư viện để tạo cảm giác bao phủ.

## 1. Chuẩn bị tiêu chí trước khi chạy

Ghi tên/phiên bản sản phẩm, môi trường, model/revision/tham số, version/hash dataset, ngày và người phụ trách. Phân biệt dữ liệu khách hàng đã khử thông tin, dữ liệu tổng hợp, demo dùng luật, inference thật và replay. Có reference được soạn độc lập với output; nguồn phải có thời điểm/phiên bản và người xác nhận. Giữ tập phát triển tách holdout.

Mỗi ca cần:

- `requirement`: yêu cầu sản phẩm mà ca kiểm; `priority`: P0/P1/P2 theo hậu quả nếu sai.
- `preconditions`: trạng thái và dữ liệu phải có trước khi chạy; ví dụ tài liệu đang chờ duyệt, tài khoản có quyền, kho test riêng, state probe hoạt động. Không viết kết quả kỳ vọng vào đây như một điều đã xảy ra.
- `steps`: thao tác đánh số, đủ để QA khác lặp lại; mỗi bước có đối tượng và cách quan sát.
- `input`, `expected`: yêu cầu thực và tiêu chí độc lập. Tách nội dung, định dạng, citation, tool và trạng thái đích thành `checks` khi cần.
- `actual`, `evidence`: output/quan sát thật và bằng chứng khớp case ID. Giữ nguyên raw output, kể cả markdown, sai số hoặc lời từ chối.
- `defect`, `follow_up`, `retest`: ID/URL lỗi, phương án xử lý và lần kiểm tra lại có version/kết quả riêng. Chưa sửa/chưa retest phải ghi rõ.

Phân biệt **priority của ca** (cần kiểm trước ở mức nào) với **severity của lỗi** (hậu quả thực khi lỗi xảy ra). Không tự suy severity chỉ từ nhãn priority; chủ sản phẩm chốt lại theo miền nghiệp vụ.

| Mức | Ý nghĩa dùng trong mẫu |
| --- | --- |
| P0 | Ca bắt buộc trước nghiệm thu; sai có thể làm hỏng luồng cốt lõi, ranh giới quyền hoặc tác động dữ liệu. |
| P1 | Ca quan trọng của chức năng thông thường; cần kiểm trong phạm vi nghiệm thu đã chốt. |
| P2 | Ca bổ sung, ít gặp hoặc tác động thấp hơn; chọn theo phạm vi và rủi ro thực. |
| S1 | Lỗi nghiêm trọng: mất/hỏng dữ liệu, hành động trái quyền hoặc luồng cốt lõi không dùng được; cần xử lý trước nghiệm thu. |
| S2 | Sai chức năng hoặc chất lượng đáng kể trong phạm vi đã thử; đánh giá ảnh hưởng và cách khắc phục trước quyết định. |
| S3 | Lỗi nhỏ về trình bày hoặc tiện dụng, không làm sai kết quả chính hay vượt quyền; vẫn ghi nhận và theo dõi. |

Ngưỡng trong 14 metric của mẫu là **đề xuất cần chủ sản phẩm chấp thuận**. Chốt mẫu tối thiểu, phương pháp tính và ngoại lệ trước khi nghiệm thu. Không diễn giải mặc định của framework thành quyết định sản phẩm. Severity S1/S2/S3 trong defect cần liên hệ tác động thật; các mức của ví dụ chỉ là đề xuất QA.

## 2. Thu bằng chứng thật và chấm đúng điều đo được

Không đưa `expected_answer`, oracle, gold ID hoặc gold context vào prompt/request của sản phẩm, kể cả qua trường `input`. Với RAG, sản phẩm được nhận dữ liệu người dùng và context do chính retrieval của nó trả về; gold dành cho evaluator. Ví dụ nhiệm vụ trích xuất có văn bản trong input là hợp lệ, nhưng đáp án do evaluator chuẩn bị không được lén đưa thêm vào prompt.

Lưu request đã khử dữ liệu nhạy cảm, raw response, retrieved contexts, trace executor và trạng thái trước/sau. Không tạo trace từ câu “tôi đã gọi công cụ”, không lấy gold làm nguồn truy hồi giả, không dùng `status=success` của tool để thay việc đọc state đích. Với agent, kiểm đúng đối tượng và giá trị, tool/đối số, quyền, phê duyệt đúng payload, retry hữu hạn và đúng một tác động khi gửi lại cùng idempotency key. Nếu chưa có executor/state probe thì ghi chưa xây/chưa chạy.

Đọc key từ biến môi trường hoặc kho bí mật. Không in key, authorization header, cookie, prompt có bí mật thật hoặc dữ liệu riêng tư vào log/báo cáo. Canary là chuỗi tổng hợp dành cho kiểm thử. Gói bàn giao dùng đường dẫn evidence tương đối hoặc ID có giải thích, không chứa đường dẫn home/máy tác giả. Ví dụ đi kèm evidence trong `qa-report/example-evidence/`; các đường dẫn của `example-data.json` tính từ `qa-report/`. Với lượt mới, ghi thư mục gốc rõ ràng. Nếu evidence không thể đi kèm gói, ghi nơi tham chiếu và giới hạn truy cập; đừng tạo link hứa tải được nhưng không tồn tại.

Giữ output thô và kết quả gốc khi audit. Audit mới phải có ghi chú khác biệt và bằng chứng, không ghi đè lịch sử. Render HTML/PDF từ JSON chỉ thay cách trình bày; không gọi model/API hoặc tuyên bố có lượt chạy mới.

## 3. Tránh những kết luận dễ sai

**Nội dung và định dạng:** exact match chỉ dùng khi một dạng output chuẩn duy nhất là yêu cầu thật. Với JSON thường, dùng parse/schema/giá trị; khoảng trắng và thứ tự khóa không là lỗi trừ khi hợp đồng đã yêu cầu. Ngược lại, nếu ca gốc yêu cầu chuỗi đóng, không âm thầm nới điều kiện sau khi thấy fail. C02/G01/J02 của ví dụ được nhận xét đúng nội dung nhưng vẫn fail hợp đồng; điểm đầy đủ là 6/24, không phải 9/24.

**Ngữ nghĩa:** keyword không phân biệt “là 10” với “không phải 10”. Faithfulness kiểm mệnh đề có được context thực hỗ trợ; correctness kiểm độ đúng/đủ với reference độc lập. Hai phép đo khác nhau, cần rubric, chấm được hiệu chuẩn và lý do. Semantic judge chưa chạy phải giữ null/blocked hoặc not_run phù hợp; không điền 0/1 giả. Output chỉ có citation hay câu rỗng không được đạt faithfulness vì thiếu mệnh đề. Một judge model cũng có thể sai; đối chiếu mẫu người chấm và ghi bất đồng.

**Retrieval:** recall@k, precision@k và average precision (AP) có mẫu số/ý nghĩa khác nhau. Một gold ở vị trí đầu trong ba kết quả có recall@3=1, precision@3=1/3 và AP@3=1 theo biến thể chia min(số gold,k). Ghi rõ k, đơn vị chunk/document, cách loại trùng và phiên bản metric. Ragas offline text matching chưa chứng minh semantic retrieval. Câu không có gold chấm hành vi thiếu dữ liệu riêng, không gán recall=1 để đẹp số.

**Citation:** ID tồn tại, đủ ID bắt buộc và phát biểu được đoạn nguồn hỗ trợ là ba điều kiện. Bỏ vùng citation/URL/metadata khi kiểm đáp án số và có đối chứng chỉ chứa ID có chữ số trùng đáp án. R04 của ví dụ trả chỉ `[cccfa6f9cc3821ace4bb3adca]`; tìm số `3` trên toàn chuỗi làm raw oracle pass nhầm. Audit đúng kết luận fail vì không có đáp án ngoài citation. Bước loại citation vẫn chưa thay semantic review.

**Guardrail:** đo cả attack success và false refusal trên yêu cầu hợp lệ. Ghi rõ mục tiêu tấn công, policy, output/tool/state. Không có canary nguyên văn chưa chứng minh không rò rỉ biến đổi. Ví dụ 0/3 canary leak và 0/1 false refusal chỉ là quan sát mẫu nhỏ; không suy ra an toàn toàn diện. Đừng dùng nhãn action tự khai làm bằng chứng duy nhất.

**Vận hành:** ghi ranh giới thời gian đo, tải, token, phần cứng, cold/warm và lỗi/timeout. p95 nearest-rank là phần tử `ceil(0,95*n)`; với n=24 là phần tử 23. 0,708 giây trong ví dụ là inference local, không là SLA end-to-end. Không bỏ các request lỗi khỏi báo cáo mà không nêu mẫu số.

## 4. Điền hợp đồng JSON

Root gồm `schema_version: 1`, `mode: "template" | "evidence"`, `product`, `decision`, `gates`, `metrics`, `cases`, `defects`. Dùng đúng trường có sẵn; không nhét HTML, script hoặc nội dung log cài đặt vào dữ liệu.

- `product`: `name`, `version`, `environment`, `run_date`, `owner`, `scope`, `data_origin`, `model`, `dataset` là chuỗi; `limitations` là danh sách chuỗi.
- `decision`: `recommendation`, `rationale`, `approved_by`, `approved_at`. Hai trường duyệt để trống nếu chưa có người thực chấp thuận; không tự ký thay.
- `gates`: `id`, `name`, `rule`, `threshold_approved`, `status`, `evidence`. Gate pass phải có quy tắc đã được chấp thuận và bằng chứng.
- `metrics`: `id`, `group`, `name`, `question`, `definition`, `method`, `threshold`, `threshold_approved`, `status`, `value`, `sample_size`, `evidence`, `interpretation`, `limitation`. `value` là chuỗi hoặc null; `sample_size` là số nguyên hoặc null. Đã đo nhưng ngưỡng chưa duyệt: giữ `value`, `status=not_run`, `threshold_approved=false`, giải thích “đã đo” trong `interpretation`.
- `cases`: `id`, `group`, `requirement`, `title`, `priority`, `data_type`, `preconditions`, `steps`, `input`, `expected`, `actual`, `status`, `checks`, `evidence`, `defect`, `follow_up`, `retest`. `checks` gồm `criterion`, `expected`, `actual`, `status`. Preconditions/steps/evidence là mảng chuỗi.
- `defects`: `id`, `title`, `severity`, `case_ids`, `impact`, `reproduce`, `expected`, `actual`, `fix`, `retest`, `status`. `case_ids`/`reproduce` là mảng chuỗi; `status` mô tả vòng đời lỗi trung thực.

`group` chỉ dùng `product`, `llm`, `rag`, `agent`, `guardrail`, `operations`. Trạng thái ca/check/metric/gate chỉ dùng `pass`, `fail`, `not_run`, `blocked`, `na`. Mẫu trống giữ mọi actual/evidence rỗng, mọi trạng thái not_run, metric value/sample_size null và defects rỗng. Input/expected minh họa có thể có nội dung nhưng không được làm người đọc nhầm là output thật.

Kiểm số đếm từ từng ca, không tin summary được gõ tay. Tỷ lệ đạt là pass/(pass+fail); báo blocked/not_run/na và coverage riêng. Báo theo nhóm và mức ưu tiên; không trộn 5/5 lifecycle vào 6/24 LLM. Ca fail bắt buộc có defect hoặc lý do theo dõi rõ. Có check bắt buộc fail thì ca không được pass; khi lưu check thô bị audit bác bỏ, phải có check audit và diễn giải lý do như R04.

## 5. Prompt giao việc có thể sao chép

```text
Hãy dùng chatbot-eval-kit/qa-report để tạo báo cáo QA nghiệm thu cho [sản phẩm], phiên bản [commit/version], phạm vi [chức năng], môi trường [test], dataset [nguồn/version] và ngân sách [thời gian/lượt/model/judge].

Đọc README và agent-guide của qa-report, hướng dẫn eval kit, yêu cầu sản phẩm và hợp đồng API. Sao chép template-data.json sang file của lượt mới. Chọn các ca thật sự liên quan; điền requirement, priority, preconditions thật, bước đánh số, input, expected và checks trước khi chạy. Đề xuất ngưỡng với định nghĩa/cách đo/mẫu số/giới hạn; chỉ ghi threshold_approved=true khi có chấp thuận thực từ chủ sản phẩm.

Reference và gold phải độc lập với output; không gửi đáp án/oracle/gold cho model qua bất kỳ trường nào. Dùng adapter và hệ thống đích thật trong môi trường kiểm thử; thu raw output, retrieval, executor trace và state trước/sau. Không tạo dữ liệu hoặc status để làm check đạt. Nếu chỉ có văn bản thì không kết luận đã đo agent. Không in/lưu key hoặc dữ liệu riêng tư không được phép; chỉ dùng canary tổng hợp và đường dẫn evidence tương đối.

Chấm nội dung tách định dạng. Exact match chỉ cho đầu ra đóng; JSON theo schema thực. Không gọi keyword hoặc ID citation là semantic correctness/faithfulness. Kiểm false positive số trong citation; phân biệt precision@k với AP. Với agent, kiểm kết quả đích, công cụ/đối số, approval, retry/idempotence; với guardrail chạy cả attack và benign. Báo latency theo đúng ranh giới đo cùng lỗi/timeout và số mẫu.

Giữ nguyên output/kết quả gốc khi audit; ghi khác biệt và bằng chứng. Mỗi fail có defect, tác động, bước lặp lại, phương án sửa và retest trung thực. Thiếu điều kiện ghi blocked; chưa chạy ghi not_run; na cần lý do. Metric đã đo nhưng ngưỡng chưa duyệt giữ value + not_run và giải thích rõ. Không tự ký phê duyệt hoặc suy production-ready.

Render HTML và PDF tùy chọn từ cùng một JSON bằng render.py; không gọi lại model khi chỉ dựng báo cáo. Kiểm schema, số đếm theo nhóm, mọi trang PDF, dấu tiếng Việt, nội dung dài và evidence. Bàn giao file nguồn, HTML/PDF, phạm vi đã đo, phần chưa đo, lỗi còn mở và giới hạn mẫu. Nếu dùng ví dụ cũ, ghi rõ không có test mới và không gộp kiểm tra kỹ thuật vào điểm chất lượng LLM.
```
