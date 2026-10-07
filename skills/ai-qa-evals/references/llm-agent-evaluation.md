# Chạy eval chatbot, RAG, agent và guardrails

Tách inference, chấm lại response, đo code và xuất báo cáo. Các lệnh dưới từ `chatbot-eval-kit` trong repo `https://github.com/SIReal3103/ai-project-starter`; nếu chưa có, clone vào thư mục mới rồi `cd ai-project-starter/chatbot-eval-kit`. Đây là hướng dẫn sử dụng runner hiện có, không khẳng định đã chạy trên sản phẩm của người dùng.

## 1. Bộ dữ liệu và oracle

Mỗi ca có ID, nhóm, input/history, reference, source version, expected state và điều kiện fail. Adapter chỉ nhận input công khai của sản phẩm, không nhận đáp án/gold. Lưu response, context retrieval thật, tool trace/state, errors và usage vào run mới.

| Nhóm | Chỉ số / phép kiểm | Cách lấy bằng chứng |
| --- | --- | --- |
| Chatbot | Đúng/đủ nội dung, relevant, không mâu thuẫn, chỉ dẫn, JSON/schema, abstention | Reference độc lập; parse/value assertions; người/judge chấm rubric và dẫn chứng response |
| Hội thoại nhiều lượt | Giữ thông tin đúng, cập nhật khi user sửa, tôn trọng scope, không lẫn phiên, hỏi lại khi thiếu | Hội thoại có kỳ vọng theo lượt và toàn session; lỗi một lượt quan trọng không bị điểm trung bình che |
| RAG | Recall/precision/AP/MRR, freshness, tenant scope, faithfulness, correctness, citation support/completeness | Gold ID/version độc lập; retrieved contexts giữ thứ hạng; tách claim và kiểm nguồn hỗ trợ |
| Agent | Goal success, tool/args, state đích, approval, duplicate effects, cancel/recovery | Executor trace và state probe, không suy từ câu “đã xong”; cho phép trace khác nhưng cùng invariant |
| Guardrail | Attack success, lộ dữ liệu, hành động bị cấm, false refusal | Ca tấn công và benign đối chứng; canary tổng hợp; quan sát response/stream/tool/state |
| Judge | Agreement với người, bất đồng theo nhóm, invalid/timeout, bias vị trí khi so A/B | Bộ người chấm giữ riêng; ẩn phiên bản A/B, đổi thứ tự khi phù hợp; lưu rubric/model/prompt version |

Mẫu số cần rõ: ca/query/claim/turn/task. Không gộp các đơn vị thành một score. Semantic similarity không tự là factual correctness; đúng với reference khác bám context. Thiếu context/reference/judge: null và lý do, không 0 hoặc pass.

## 2. Chạy trên sản phẩm thật

Đọc README kit và contract adapter trước. Nếu API sản phẩm trả response/schema phù hợp, cấu hình `EVAL_TARGET_URL` bằng endpoint được phép và `EVAL_TARGET_API_KEY` qua secret của phiên chạy. Không viết key vào câu lệnh, dataset hoặc Git.

```sh
python3 main.py validate --dataset datasets/product-cases.jsonl
python3 main.py evaluate --dataset datasets/product-cases.jsonl \
  --adapter 'python3 adapters/http-product.py' \
  --out runs/product-inference-01 --frameworks off \
  --timeout 30 --budget-seconds 240
```

`datasets/product-cases.jsonl` phải được tạo từ yêu cầu thật theo schema của kit; không có file thì dừng preflight, không fallback demo. Endpoint khác schema cần adapter ánh xạ riêng. Plain model dùng `adapters/openai-chat.py` cùng `EVAL_TARGET_BASE_URL`, `EVAL_TARGET_MODEL`, `EVAL_TARGET_API_KEY`; chỉ chứng minh text generation, không chứng minh retrieval/tool execution của sản phẩm.

Exit 1 có ca fail; exit 2 cần xem cấu hình/dữ liệu. Giữ mọi response kể cả fail/timeout. Budget adapter không thay budget toàn workflow; chừa thời gian chấm và báo cáo.

## 3. Ragas và DeepEval

Kit pin Ragas **0.4.3**, DeepEval **4.2.8** trong hai venv riêng. Đây là phiên bản của kit, không tuyên bố mới nhất. `setup-tools.sh` dùng requirements/lock đi kèm. Chỉ cài một lần khi cần, không tính thời gian tải package vào benchmark sản phẩm.

```sh
sh setup-tools.sh
python3 main.py replay --dataset datasets/product-cases.jsonl \
  --responses runs/product-inference-01/responses.json \
  --out runs/product-score-01 --frameworks auto --framework-timeout 90
```

Xác minh file `responses.json` thực có và đúng schema trước replay. Runner offline hiện có: Ragas text context recall/ranking precision và DeepEval exact-match cho ca tag `exact-match`. Không gọi các metric này là semantic judge.

Muốn semantic judge, cấu hình `EVAL_JUDGE_BASE_URL`, `EVAL_JUDGE_MODEL`, `EVAL_JUDGE_API_KEY` cho dịch vụ được phép và budget. Thêm `--judge --judge-max-cases 4` khi replay sang output mới. Đọc `integrations/README.md` để biết giới hạn riêng mỗi subprocess; hai framework không dùng chung một cap request. Nếu thiếu khóa/endpoint hoặc hết budget, ghi phần chưa chạy; không tự đổi provider.

| Metric thực có trong integration kit | Input bắt buộc | Ý nghĩa |
| --- | --- | --- |
| Ragas faithfulness | answer + retrieved context thật | Mệnh đề trong answer được context hỗ trợ |
| Ragas factual_correctness | answer + reference | Độ đúng/đủ theo mệnh đề, F1 |
| Ragas llm_context_recall | reference answer + retrieved context | Reference claims được context hỗ trợ |
| DeepEval faithfulness | answer + retrieved context | Chấm support qua judge riêng |
| DeepEval GEval correctness | answer + reference + rubric | Chấm đúng nghĩa theo rubric, không exact-match |

Response relevancy, multi-turn, tool accuracy/goal metrics, bias/toxicity hoặc metric khác chỉ ghi là đã chạy sau khi thêm adapter/test phù hợp và có artifact. Không mặc định toàn bộ thư viện đã tích hợp. API Ragas mới có collections; không copy ví dụ API mới vào môi trường legacy của kit mà không kiểm migration. Nguồn: [Ragas faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/), [DeepEval answer relevancy](https://deepeval.com/docs/metrics-answer-relevancy).

## 4. Promptfoo nếu dự án dùng bộ prompt/assertion

Dùng dependency đã pin trong workspace đánh giá. Nếu dự án chưa dùng Promptfoo và đã chọn công cụ này, cài dev dependency bằng `npm install -D --save-exact promptfoo`, lưu lock và `npx --no-install promptfoo --version`; kiểm Node/package engine tương thích trước cài. Cấu hình provider/target, prompts, vars và assertions độc lập; chọn ca pass/fail có reference. Kiểm config chỉ tới endpoint được cấp, không để default provider lấy key khác. Sau khi tạo `promptfooconfig.yaml` phù hợp sản phẩm:

```sh
npx --no-install promptfoo eval --config promptfooconfig.yaml --output runs/promptfoo-01.json
```

Ghi phiên bản, concurrency, cache/repeat, số request dự kiến, timeout và trần chi phí trước live run. Không chạy redteam generation hoặc hosted upload chỉ vì đã cài Promptfoo. JSON/CSV output dùng để đối chiếu từng ca; assertion pass không thay phê duyệt release. Config không tồn tại hoặc chưa có provider thì ghi blocked, không giả là eval hoàn tất. Nguồn: [Promptfoo CLI](https://www.promptfoo.dev/docs/usage/command-line/).

## 5. Kiểm bằng tay và so phiên bản

- Chọn lỗi, ca sát ngưỡng và mẫu pass để đọc lại; giữ raw score và audit riêng. Judge phải có lý do; kit không lưu đầy đủ lý do judge thì ghi giới hạn và dùng nhật ký review riêng, không sáng tác rationale.
- Case có ID citation chứa đáp án số cần đối chứng: chỉ citation không được pass nội dung. JSON đúng cú pháp nhưng sai giá trị phải fail contract.
- Baseline/candidate chạy cùng dữ liệu, nguồn và workload. Báo số pass→fail, fail→pass, không đổi, chưa so được; tách delta latency/cost. Đầu ra ngẫu nhiên cần lặp với cap đã chọn, báo độ biến thiên, không chỉ lấy lượt tốt nhất.
- Chốt ngưỡng trước nghiệm thu. Hạn chế inference/judge nhỏ hoặc dữ liệu mock không cho phép kết luận production.

## 6. Evidence bàn giao

Manifest: commit/model/prompt/dataset hash, tool versions, command đã khử secret, mode live/replay/mock, thời gian, exit và budget. Kèm response/context/state, kết quả từng metric và ca, audit, lỗi và retest. Không coi hình report đẹp là bằng chứng đã chạy eval; HTML/PDF chỉ là view của evidence.
