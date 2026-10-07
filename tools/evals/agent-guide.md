# Hướng dẫn dùng lại bộ eval chatbot, agent và guardrail

Đây là bộ khung chạy được: chuẩn hóa ca kiểm thử, gọi adapter, chấm điều kiện, chạy Ragas/DeepEval khi có môi trường phù hợp và xuất báo cáo HTML. Bộ mẫu có **40 ca tiếng Việt: 12 chatbot, 8 RAG, 8 agent và 12 guardrail**. Tài liệu thư viện và đáp án mẫu được soạn thủ công; assistant demo dùng luật xác định, không gọi LLM. Kết quả demo chỉ minh họa quy trình và các giới hạn đã ghi, không phải chứng nhận chất lượng sản phẩm.

## 1. Chạy mẫu và đọc kết quả

Chạy lệnh từ thư mục bộ kit. Phần runner, adapter demo và báo cáo chỉ cần Python >=3.12, dùng thư viện chuẩn. Từ repo starter vào `tools/evals`; bản kit sao chép riêng dùng ngay thư mục chứa `main.py`. Ragas và DeepEval là tích hợp tùy chọn, chạy bằng Python riêng khi được cấu hình.

```bash
python3 main.py validate --dataset datasets/demo-cases.jsonl
python3 main.py self-test
python3 main.py demo --out runs/demo --frameworks auto
python3 report.py --input runs/demo/results.json --output reports/my-demo.html
```

Mỗi lượt phải dùng thư mục `--out` mới hoặc rỗng. Nếu `runs/demo` đã có bằng chứng, đổi thành `runs/demo-02`; không xóa hoặc ghi đè kết quả cũ để làm đẹp báo cáo. Dùng `--frameworks off` khi chỉ cần runner và các kiểm tra xác định.

Mở HTML bằng trình duyệt; chọn In → Lưu PDF, khổ A4 dọc, bật màu nền và tắt header/footer của trình duyệt. HTML đã có CSS phân trang; kiểm lại các bảng, dấu tiếng Việt và phần cuối trang sau khi xuất. Sửa `templates/report-template.html` để đổi nhận diện hoặc bố cục; giữ các placeholder `{{TEN_TRUONG}}` mà `report.py` hỗ trợ, rồi render lại. Không điền điểm bằng tay vào template.

Các tệp quan trọng của một lượt:

| Tệp | Nội dung |
| --- | --- |
| `results.json` | Metadata, kết luận từng ca, kiểm tra con, framework, đối chứng âm và bản đồ phạm vi |
| `responses.json` | Câu trả lời và telemetry nguyên bản để replay |
| `framework-input.json` | Bộ ca cùng phản hồi dùng làm đầu vào cho Ragas/DeepEval |
| `ragas.json`, `deepeval.json` | Điểm và trạng thái thực do từng tích hợp trả về, nếu framework đã chạy |
| `*.log` | Chẩn đoán kỹ thuật cục bộ; không chép nguyên log vào báo cáo người đọc |

Exit code: `0` khi các gate đã chạy không lỗi/không fail; `1` khi ca hoặc đối chứng âm không đạt; `2` khi có lỗi thực thi, ca chưa chạy hoặc lỗi framework. Luôn đọc `results.json`: framework tắt, metric không phù hợp hoặc judge chưa bật phải được ghi riêng, không suy từ exit `0` rằng mọi phép đo đã thực hiện.

## 2. Phạm vi eval cần chọn cho sản phẩm

Đây là danh mục thực dụng để lập kế hoạch, không phải bộ phủ mọi loại AI. Chỉ bật gate khi có dữ liệu chuẩn, trace hoặc rubric đủ để chấm.

| Nhóm | Bộ kit kiểm được ngay | Cần bổ sung hoặc chạy riêng |
| --- | --- | --- |
| Chatbot | Có nội dung; cụm dữ kiện bắt buộc/cấm; đáp án đóng khớp nguyên văn; JSON; ca hỏi lại và hội thoại nhiều lượt | Đúng, đủ, liên quan, giọng điệu và chất lượng hội thoại bằng rubric/người đánh giá hoặc LLM judge; các ngôn ngữ khác |
| RAG và hallucination | Recall/precision@k, MRR, nDCG từ ID nguồn chuẩn; đủ và hợp lệ ID trích dẫn; ca thiếu nguồn, nguồn nhiễu, mâu thuẫn | Faithfulness, factual correctness, tính hỗ trợ ngữ nghĩa của trích dẫn; dữ kiện ngoài corpus; lỗi retrieval trên holdout thực |
| Agent | Tên/thứ tự/đối số công cụ; giới hạn số lần gọi; cấm công cụ; ca lỗi công cụ và tác vụ cần từ chối | Thành công của tác vụ từ trạng thái thật; retry, rollback, quyền công cụ, phê duyệt và tính idempotent theo sản phẩm |
| Guardrail | Ca injection trực tiếp/qua tài liệu, bí mật, riêng tư, ngoài phạm vi, từ chối quá mức; kiểm nội dung và action telemetry | Red-team nhiều lượt, obfuscation, toxicity/bias, jailbreak rộng; kiểm tác động thực và chính sách theo miền |
| Vận hành | Độ trễ wall time của adapter; timeout, ngân sách lượt chạy; giữ usage nếu sản phẩm cung cấp | p95/p99 trên mẫu đủ lớn, tải đồng thời, ổn định nhiều lần, chi phí dựa trên usage và bảng giá đã xác nhận |

Kiểm tra chuỗi không phân biệt câu “đúng 10” và “không phải 10” chỉ vì cùng chứa “10”. ID citation hợp lệ cũng chưa chứng minh nguồn hỗ trợ phát biểu. Vì vậy, hallucination và độ đúng ngữ nghĩa không được đánh dấu đã giải quyết chỉ bằng keyword, exact match hoặc framework smoke test.

## 3. Tạo bộ ca thật trước khi gọi sản phẩm

Đọc [hướng dẫn dataset](datasets/dataset-guide.md). Tạo `datasets/product-cases.jsonl`, mỗi dòng một JSON object UTF-8 với các trường:

| Trường | Quy tắc |
| --- | --- |
| `id` | Chuỗi duy nhất; ổn định để so các lượt |
| `category` | Một trong `chatbot`, `rag`, `agent`, `guardrail` |
| `question` | Câu hỏi/yêu cầu thực tế, không chứa lời giải của evaluator |
| `expected_answer` | Đáp án hoặc hành vi tham chiếu do người soạn xác nhận; không gửi cho sản phẩm |
| `history` | Mảng `{role, content}` các lượt trước; dùng nội dung đã khử thông tin riêng tư |
| `contexts` | Corpus tham chiếu `{id, text}` cho evaluator; có cả nguồn đúng và nguồn gây nhiễu |
| `expected` | Oracle máy kiểm được; có ít nhất một điều kiện thực sự hoạt động |
| `tags` | Nhãn phân tích. Chỉ dùng `exact-match` khi cần khớp nguyên văn và đáp án có một dạng chuẩn |
| `input` | Tùy chọn: dữ liệu sản phẩm thực sự cần như bộ lọc tìm kiếm hoặc mã tài liệu được phép; tuyệt đối không nhét oracle vào đây |

Các oracle hỗ trợ trong `expected`:

- Nội dung: `answer_contains_all`, `answer_contains_any`, `answer_not_contains` — mảng chuỗi; dùng cho điều kiện đóng, không gọi chúng là đánh giá ngữ nghĩa.
- Nguồn: `required_citation_ids`, `expected_context_ids` — mảng ID. Gold context phải tồn tại trong `contexts`; corpus sản phẩm cần dùng cùng ID hoặc adapter phải ánh xạ ổn định.
- Công cụ: `tool_calls` — mảng `{name, arguments}` theo thứ tự; `forbidden_tools` — mảng tên bị cấm; `max_tool_calls` — số tối đa. `tool_calls: []` có nghĩa là kỳ vọng không gọi công cụ.
- Chính sách: `must_refuse` — boolean; `required_guardrail_action` — `allow`, `refuse` hoặc `clarify`. Ghép với assertion nội dung và trace để không chỉ tin nhãn tự khai.
- Đầu ra/vận hành: `output_json` — boolean; `max_latency_ms` — số hữu hạn không âm. Ngưỡng demo 2.000 ms chỉ dành cho ví dụ cục bộ; chọn lại từ yêu cầu thực của sản phẩm.

Soạn tham chiếu độc lập với câu trả lời của hệ thống. Kiểm nguồn, thời điểm, định nghĩa và tiêu chí đạt trước; giữ tập phát triển tách khỏi holdout để tránh tối ưu riêng cho mẫu. Ca guardrail cần cả yêu cầu phải chặn lẫn yêu cầu hợp lệ dễ bị chặn nhầm. Ca agent phải nói rõ kết quả cuối cùng và tác động được phép; chọn môi trường kiểm thử phù hợp trước khi gọi công cụ thật.

```bash
python3 main.py validate --dataset datasets/product-cases.jsonl
```

## 4. Kết nối sản phẩm qua adapter

Runner chạy command bằng `shell=False`, gửi một JSON request UTF-8 qua stdin và nhận một JSON response UTF-8 qua stdout cho từng ca. Command không được chứa pipe, chuyển hướng hoặc các chuỗi lệnh shell. Log chẩn đoán của adapter viết vào stderr; stdout chỉ chứa đúng JSON response.

Trong chế độ `evaluate`, request chỉ có `id`, `question`, `history` và `input` nếu đã khai báo. Runner **không truyền** `expected_answer`, `expected`, `tags`, `category`, gold IDs hoặc `contexts` cho adapter. Sản phẩm RAG phải truy hồi từ corpus của chính nó; chuẩn bị corpus kiểm thử trước. Chỉ chế độ `demo` nhận corpus mẫu trong `contexts` để chạy sandbox bộ nhớ.

Response contract:

```json
{
  "case_id": "ma-ca-trung-voi-request",
  "answer": "Câu trả lời thực do sản phẩm sinh",
  "retrieved_contexts": [{"id": "ma-nguon-thuc", "text": "Đoạn thực đã truy hồi"}],
  "citations": ["ma-nguon-thuc"],
  "tool_calls": [{"name": "ten_cong_cu", "arguments": {}, "result": {}, "status": "success"}],
  "guardrail": {"action": "allow", "reason": "Lý do từ hệ thống"},
  "usage": {},
  "provider_metadata": {}
}
```

Các giá trị trên mô tả schema, không phải một response đạt mẫu. `case_id` phải khớp ca, `answer` là chuỗi. Trường telemetry chỉ được điền từ bằng chứng thực: không dựng tool trace từ câu “tôi đã gọi”, không lấy retrieved contexts từ gold, không suy action để ép gate đạt. Nếu không thu được telemetry cần thiết, giữ thiếu và báo giới hạn/lỗi gate. Runner tự đo `latency_ms` bao gồm thời gian gọi adapter.

Hai adapter có sẵn:

| Adapter | Cấu hình | Phạm vi |
| --- | --- | --- |
| `adapters/http-product.py` | `EVAL_TARGET_URL`, `EVAL_TARGET_API_KEY` nếu cần | POST request tới API chatbot/agent trả response contract ở trên |
| `adapters/openai-chat.py` | `EVAL_TARGET_BASE_URL`, `EVAL_TARGET_MODEL`, `EVAL_TARGET_API_KEY`; tùy chọn `EVAL_TARGET_SYSTEM_PROMPT`, `EVAL_TARGET_MAX_TOKENS` | Endpoint chat-completions tương thích. Chỉ trả văn bản/usage; không có trace RAG, tool hay guardrail để chấm các gate đó |

Nạp key từ biến môi trường hoặc kho bí mật của bạn; không ghi key vào dataset, adapter, command line hay báo cáo. Runner giữ `EVAL_TARGET_API_KEY` cho adapter sản phẩm và `EVAL_JUDGE_API_KEY` cho tiến trình judge; không dựa vào các biến key provider khác. Base URL chat-completions là phần trước `/chat/completions`, chẳng hạn endpoint do bạn cấu hình có hậu tố `/v1`.

```bash
python3 main.py evaluate \
  --dataset datasets/product-cases.jsonl \
  --adapter "python3 adapters/http-product.py" \
  --product-name "Tên sản phẩm của bạn" \
  --out runs/product-01 \
  --frameworks auto

python3 report.py \
  --input runs/product-01/results.json \
  --output reports/bao-cao-san-pham.html
```

Hoặc đổi `--adapter` thành `"python3 adapters/openai-chat.py"` để kiểm một chatbot văn bản. Chọn tập ca đúng khả năng có thể quan sát; đừng biến các oracle yêu cầu telemetry thành pass giả. Adapter tùy chỉnh cũng theo cùng protocol stdin/stdout nên có thể nối SDK, CLI hoặc API nội bộ mà không đổi runner.

## 5. Ragas, DeepEval và LLM judge là hai bước riêng

`--frameworks auto` dùng `EVAL_RAGAS_PYTHON` và `EVAL_DEEPEVAL_PYTHON` nếu đã cấu hình, hoặc `.venv-ragas` / `.venv-deepeval` ngay trong bộ kit. Không tìm môi trường ở home, repo khác hoặc interpreter đang activate. Mỗi biến trỏ tới executable Python có framework tương ứng và dependency của metric. Nếu chưa có runtime, báo `not_run`; nếu dependency thiếu/hỏng, giữ lỗi. Chạy `--frameworks off` chỉ tắt phần framework, không tắt các gate xác định của runner.

Các metric của tích hợp hiện tại:

| Framework | Không gọi LLM | Cần bật judge |
| --- | --- | --- |
| Ragas | `non_llm_context_recall`, `non_llm_context_precision_with_reference` — so khớp văn bản context theo thư viện | `faithfulness`, `factual_correctness`, `llm_context_recall` |
| DeepEval | `exact_match` trên ca có tag `exact-match` | `faithfulness`, `geval_correctness` |

Metric framework trả `scored` khi đã đo được giá trị. Báo cáo hiển thị **Đã đo**, không tự đổi thành đạt nghiệm thu chỉ vì vượt một threshold mặc định của thư viện. Gắn ngưỡng release sau khi đã hiệu chuẩn trên mẫu đúng/sai và được chủ sản phẩm chấp nhận. Các gate xác định từng ca và metric framework được báo riêng.

Muốn chạy judge, nạp riêng `EVAL_JUDGE_API_KEY`, `EVAL_JUDGE_BASE_URL`, `EVAL_JUDGE_MODEL` cho endpoint chat-completions tương thích. Thiếu một trường thì runner dừng trước khi gọi judge. `--judge` yêu cầu `--frameworks auto` và runtime framework hợp lệ; dùng cùng `--frameworks off` hoặc thiếu runtime sẽ báo lỗi, không âm thầm bỏ bước chấm. Judge có thể gọi dịch vụ tính phí; chỉ bật sau khi endpoint, dữ liệu và ngân sách đã đúng yêu cầu của lượt đánh giá.

```bash
python3 main.py replay \
  --dataset datasets/product-cases.jsonl \
  --responses runs/product-01/responses.json \
  --product-name "Tên sản phẩm của bạn" \
  --out runs/product-01-judge \
  --frameworks auto \
  --judge \
  --judge-max-cases 4

python3 report.py \
  --input runs/product-01-judge/results.json \
  --output reports/bao-cao-judge.html
```

Lệnh trên chấm lại câu trả lời đã lưu, không gọi lại chatbot. `--judge-max-cases 4` giới hạn số ca dùng judge **mỗi framework**, không phải 4 request tổng; một metric có thể cần nhiều request. Tích hợp có timeout và giới hạn request; khi hết ngân sách hoặc lỗi, báo riêng `not_run`/`error`, không thay bằng điểm 0 hoặc 1. Chỉ các ca có đủ điều kiện metric mới được chấm.

Đối chiếu một mẫu judge với đánh giá của người: reference đã đúng chưa, judge có bị nội dung trong câu trả lời dẫn dắt không, rubric có đánh giá đúng nhiệm vụ không. Nên dùng judge độc lập với sản phẩm khi phù hợp, cố định cấu hình để so các phiên bản và giữ các khác biệt do tính ngẫu nhiên. Ragas/DeepEval chạy được không tự chứng minh judge đáng tin hoặc hệ thống không hallucinate.

## 6. Replay, phân tích và đối chứng

Replay nhận `responses.json` dạng `{"responses": [...]}` hoặc mảng response, ghép theo `case_id`. Dùng đúng dataset/version của lượt gốc. Response thiếu hoặc trùng ID phải được xử lý như vấn đề bằng chứng; không nhân bản câu trả lời để lấp ca.

```bash
python3 main.py replay \
  --dataset datasets/product-cases.jsonl \
  --responses runs/product-01/responses.json \
  --out runs/product-replay-01 \
  --frameworks off
```

Đọc theo thứ tự: phạm vi demo/product/replay → lỗi adapter và ca chưa chạy → từng ca không đạt → metric framework → đối chứng âm → phần chưa đo. Tỷ lệ đạt trong báo cáo là `pass / (pass + fail)` của các gate đã chạy; errors và not_run xuất riêng cùng tổng ca. Không lấy tỷ lệ này làm điểm chất lượng ngữ nghĩa tổng hợp.

Runner tạo đối chứng âm bằng cách làm sai có chủ đích một phản hồi để kiểm bộ chấm: output rỗng, thiếu dữ kiện, mất nguồn, citation bịa, tool sai đối số, tool bị cấm, lộ chuỗi bị cấm hoặc sai action. **Đối chứng chỉ kiểm evaluator, không cộng vào tổng ca hoặc tỷ lệ chất lượng của sản phẩm.** Nếu đối chứng không bị phát hiện, xem lại bộ chấm trước khi tin các ca đạt; nếu không đủ ca phù hợp thì đối chứng chưa chạy.

Phân loại nguyên nhân dựa trên bằng chứng: đáp án tham chiếu sai; corpus/index sai; retrieval thiếu; câu trả lời thêm thông tin không được hỗ trợ; tool/policy sai; telemetry thiếu; judge/rubric chưa phù hợp; lỗi vận hành. Sửa nguyên nhân đã kiểm chứng, thêm ca hồi quy thật và chạy lại tập liên quan. Không sửa oracle để hợp thức hóa câu trả lời sai hoặc che fail bằng skip.

## 7. Prompt giao cho agent ở sản phẩm kế tiếp

Sao chép đoạn sau, thay các mục trong ngoặc vuông và gửi kèm bộ kit:

> Hãy áp dụng bộ eval này cho [sản phẩm], repo tại [đường dẫn], API/CLI [hợp đồng], phạm vi [chatbot/RAG/agent/guardrail] và ngân sách [thời gian/số ca/số lần gọi judge]. Đọc hướng dẫn, code sản phẩm và hợp đồng API trước. Xây dataset JSONL từ yêu cầu, tài liệu đã kiểm và lỗi thực tế; chuẩn bị expected_answer, gold contexts và oracle độc lập với output sản phẩm. Tách tập phát triển khỏi holdout; ghi rõ ca nào là dữ liệu tổng hợp. Không đưa expected, đáp án hay gold IDs vào prompt hoặc request của sản phẩm, kể cả qua input. Triển khai adapter stdin/stdout trả câu trả lời, nguồn đã truy hồi, trace tool và action guardrail thực; không dựng telemetry. Đọc key từ EVAL_TARGET_API_KEY và cấu hình judge riêng bằng EVAL_JUDGE_*; không in hoặc lưu key. Chạy validate và self-test, demo để kiểm harness, rồi evaluate sản phẩm vào một thư mục mới. Replay câu trả lời đã lưu để so metric hoặc chấm judge; bật --judge chỉ khi đã có endpoint và ngân sách phù hợp. Giữ pass/fail/error/not_run trung thực; metric scored là đã đo, chưa tự thành release gate. Kiểm đối chứng âm riêng, không đưa vào điểm chất lượng. Phân tích lỗi theo bằng chứng, nêu phần chưa đo, rồi tạo HTML từ report.py và kiểm PDF A4 nếu xuất. Báo cáo phải có câu hỏi, đáp án mong đợi, câu trả lời thực tế, kết luận và lý do từng ca; phân biệt demo, replay, live, smoke và LLM judge. Không tuyên bố bao phủ mọi tình huống hoặc production-ready khi còn thiếu bằng chứng.

## 8. Hợp đồng dữ liệu báo cáo

`report.py --input <results.json> --output <report.html>` đọc `run`, `summary`, `cases`, `frameworks`, `controls`, `capability_coverage`. `cases` là trường bắt buộc, mỗi ca có `id` duy nhất và `status` thuộc `pass`, `fail`, `error`, `not_run`; renderer không tự biến trạng thái lạ thành đạt. Metadata và các khối bổ sung có thể vắng; báo cáo ghi phần chưa có dữ liệu.

Mỗi ca hiển thị `category`, `question`, `expected_answer`, `answer`, `checks`, `latency_ms`, `source_mode`; mỗi check có `name`, `status`, `score`, `reason`. Framework gồm tên, phiên bản, mode và các metric `{case_id, metric, score, status, reason}`; metric chấp nhận thêm `scored`. Đối chứng gồm `id`, `detected` và `description`; phạm vi gồm `name`, `category`, `status`, `note`.

Renderer tính lại số đếm từ từng ca, tách các ca đối chứng nếu có và cảnh báo khi summary nguồn khác. Nội dung câu hỏi/câu trả lời/nhận xét được escape HTML. Template và CSS nằm hoàn toàn trong báo cáo, không tải CDN; không chèn log cài đặt, đường dẫn máy dài hoặc lịch sử credential vào bản gửi người đọc.
