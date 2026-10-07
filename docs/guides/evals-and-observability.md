# Kiểm thử, đánh giá AI và observability

Một báo cáo hữu ích trả lời: kiểm gì, input/oracle từ đâu, phiên bản nào đã chạy, quan sát được gì và còn thiếu gì. Test pass của một dự án khác, example tool hoặc demo xác định không chứng minh chất lượng AI của sản phẩm mới.

Starter có [eval kit thực thi](../../tools/evals/README.md) và [hướng dẫn adapter/dataset/report](../../tools/evals/agent-guide.md). Kit demo dùng dữ liệu soạn thủ công và hành vi xác định để kiểm harness, không gọi LLM thay sản phẩm. Các kiến trúc, bảng và pseudocode ở những guide khác cần được triển khai riêng.

## Tách câu hỏi kiểm chứng

| Lớp | Chứng minh được trong phạm vi kiểm | Không suy ra |
| --- | --- | --- |
| Syntax/import | File parse, dependency/API local khởi tạo được | Provider, DB hoặc nghiệp vụ đúng |
| Unit/contract | Hàm, schema, rule, scorer xử lý input có oracle | Luồng sản phẩm tích hợp đã chạy |
| Integration | Thành phần thật nối đúng: API, DB, auth, parser | Chất lượng đại diện của mọi đầu vào |
| E2E | Người dùng hoàn thành hành trình trong môi trường đã thử | Mọi browser/thiết bị đều hỗ trợ |
| AI eval live | Hành vi app/model/prompt/tools/data hiện tại trên bộ ca | Benchmark tổng quát hoặc production-ready |
| Replay | Chấm lại output/version đã lưu | Provider/model hiện tại vừa chạy |
| Media kỹ thuật | File mở/giải mã/streams/duration hợp lệ | Nội dung đúng, hay hoặc tự nhiên |
| Review người | Tiêu chí ngữ nghĩa/nhìn/nghe trong phần đã xem | Số đo đại diện nếu mẫu quá nhỏ |

Coverage dòng/nhánh chỉ đo phần code đã chạy; scenario coverage đo các tình huống; dataset coverage đo nhóm input. Không loại code nghiệp vụ khỏi denominator để đạt ngưỡng. Line coverage = covered lines / executable lines; branch coverage = covered branches / branches. Report combined statement+branch không phải riêng line coverage. Mẫu số 0 ghi N/A theo policy, không tự coi 100%.

## Dataset và oracle

Mỗi ca cần ID duy nhất, tác vụ/nhóm, critical hay không, nguồn input/quyền sử dụng, input/history/scope, data version, expected status, điều phải đúng, điều cấm, cách chấm và nguồn oracle. Đáp án do phép tính độc lập, nguồn đã kiểm, người phụ trách hoặc rubric tạo; không lấy output target rồi chép làm gold.

Tách dev và holdout theo nguồn/tình huống/người/thời gian khi phù hợp. Các biến thể gần nhau không được chia ngẫu nhiên làm rò thông tin. Nếu xem holdout để sửa prompt, ghi nó đã trở thành dev. Vài ca chỉ dùng smoke/regression; không gọi là độ chính xác đại diện.

Một bộ tám ca khởi đầu có thể gồm ba ca thường, hai ca mơ hồ/thiếu nguồn, một input sai, một ca quyền/phạm vi và một chất lượng đặc thù. Đây là gợi ý timebox, không là chuẩn chất lượng. Thêm lỗi dependency/cancel/concurrency vào software tests; không cộng fault injection thành chất lượng model.

| Tác vụ | Oracle và metric phù hợp |
| --- | --- |
| Số liệu | SQL/phép tính độc lập, exact decimal, đơn vị/kỳ/coverage/filters |
| Retrieval | Gold IDs thật: recall@k, precision@k, MRR/nDCG khi có nhãn phù hợp |
| RAG answer | Đúng đáp án, claim được nguồn hỗ trợ, citation đúng version/vị trí |
| Agent | Tool/args hợp lệ, tác động thật, final state, task success, budget |
| Guardrail | Hành vi/action thực, ca nguy hiểm và câu hợp lệ dễ bị chặn nhầm |
| STT/OCR | Transcript/fields người kiểm, WER/CER và exact match trường quyết định |
| TTS/nội dung mở | Rubric người hoặc judge đã hiệu chuẩn; facts chấm độc lập |
| Anomaly | Precision/recall/FPR khi có nhãn; nếu chưa có thì workload/confirmed alerts và giới hạn |

Deduplicate retrieval IDs trước khi tính metric, đồng thời báo duplicate rate. Câu không có tài liệu trả lời chấm abstention, không thưởng recall 100%. Citation ID hợp lệ hoặc có từ khóa chưa chứng minh nguồn hỗ trợ claim; câu phủ định có thể chứa cùng từ khóa với câu đúng. Không ép một tool sequence duy nhất nếu nhiều đường đúng; scorer cần phản ánh invariants và task outcome.

## Nối vào sản phẩm thật

Adapter chỉ gửi các input được allowlist. Không serialize nguyên test case chứa `expected`, gold contexts hoặc tags vào request model. Scope do harness/backend cấp theo quyền, không từ câu người dùng. RAG của sản phẩm truy hồi từ corpus kiểm thử đã chuẩn bị; evaluator giữ gold riêng.

Thu answer, status, typed data, contexts thực sự retrieve, citations, tool name/args/result/status, guardrail action, latency, usage/cost và version nếu ứng dụng có. Không dựng trace từ câu “tôi đã gọi tool”. Thiếu telemetry thì giữ thiếu/lỗi gate, không lấy gold để lấp. Lỗi transport/parsing/timeout là lỗi thực thi, không tự đổi thành câu từ chối đạt.

Kit dùng adapter subprocess với JSON stdin/stdout và stderr cho diagnostics; chi tiết trường bắt buộc, CLI và giới hạn ở [agent guide](../../tools/evals/agent-guide.md). Các mẫu schema của ứng dụng trong guide chatbot khác schema kit; viết mapping rõ ràng.

### Lệnh chạy được của bộ kit

Chạy từ root repo. Nhóm lệnh sau kiểm dataset demo và harness local, **không đo sản phẩm hoặc gọi AI live**. Nếu thư mục output đã có, chọn tên mới để giữ evidence.

```sh
cd tools/evals
python3 main.py validate --dataset datasets/demo-cases.jsonl
python3 main.py self-test
python3 main.py demo --out runs/demo-01 --frameworks off
python3 report.py --input runs/demo-01/results.json --output reports/demo-01.html
```

Chỉ sau khi tạo dataset sản phẩm, cấu hình API/credentials qua môi trường và nối contract của adapter, dùng lệnh `evaluate` trong [runbook kit](../../tools/evals/agent-guide.md). `http-product.py` gọi service của app; adapter model text trực tiếp chỉ đo text path và không cung cấp trace RAG/tools đầy đủ. Không chạy một model khác rồi gọi đó là eval agent sản phẩm.

`replay` chấm responses đã lưu; kiểm dataset/version, case IDs, response thiếu/trùng và freshness. Dùng thư mục run mới; không lấy JSON cũ còn sót sau step lỗi làm kết quả mới. Manifest phải gắn output vào đúng lượt chạy.

## Chọn công cụ theo bằng chứng cần lấy

| Cần kiểm | Lựa chọn theo stack | Điều kiện/giới hạn |
| --- | --- | --- |
| Logic/schema | Runner đang có; pytest hoặc Node/Vitest | Không tạo hai suite trùng nhau chỉ để tăng số tool |
| Frontend | Component tests/React Testing Library khi phù hợp | Chấm hành vi người dùng, không mirror implementation |
| Browser/accessibility | Playwright và axe nếu cần | Keyboard/focus và kết quả incomplete vẫn cần người kiểm |
| Properties | Hypothesis hoặc công cụ tương đương | Miền sinh cần ghi rõ; không đại diện mọi input |
| API contracts | OpenAPI tests/Schemathesis khi app có contract | Chọn routes/database test; không fuzz inference live tùy ý |
| Data/DB | SQL/DuckDB và schema validation | Oracle độc lập; DB integration dùng role thực phù hợp |
| AI regression | Kit này hoặc runner như Promptfoo | Một runner chính; adapter/scorer đúng sản phẩm |
| Metrics bổ sung | Ragas/DeepEval khi phù hợp dataset | Smoke metric không chứng minh semantic correctness |
| Security | Secret scanner + SAST/SCA phù hợp | Triage theo scope; network advisory lookup cần ghi |
| Media | ffprobe/decoder + nghe/xem | Tách kỹ thuật khỏi chất lượng nội dung |
| Load | Một công cụ load theo runtime | Workload/môi trường/budget rõ; không suy tải AI từ endpoint giả lập |
| Observability | Log JSON trước; UI trace self-hosted khi cần | Collector local không có nghĩa judge/provider cũng local |

Tên công cụ là lựa chọn, không phải danh sách đã cài. Cài theo lockfile được kiểm; kiểm docs/license/edition/telemetry hiện hành trước khi thêm. Chuẩn bị browser binaries hoặc parser weights trước lượt cuối. Dừng thử tool mới khi không tạo bằng chứng hữu ích, giữ tool đang bắt lỗi thật.

### Danh mục giữ lại từ các lượt nghiên cứu công cụ

**Có sẵn trong starter:** runner/scorer/adapter/report Python của `tools/evals`, dataset demo và self-test. Tích hợp Ragas/DeepEval có code nhưng cần runtime tùy chọn; xem setup của kit. Các công cụ dưới đây là lựa chọn cài/nối theo sản phẩm, không phải toàn bộ đã được bundle hoặc đã chạy trên app mới.

| Công cụ | Vai trò và giới hạn tái sử dụng |
| --- | --- |
| unittest/pytest, pytest-cov, coverage.py | Test và coverage Python; khai báo đúng source, tách line/branch/subtests |
| Node test runner, Vitest, React Testing Library | Tests Node/TS/UI theo stack; fixture component riêng không chứng minh UI sản phẩm |
| TypeScript, ESLint, Ruff, Pyright | Type/lint/format; cần config và phiên bản của dự án |
| Hypothesis, mutmut | Properties/mutation cho bất biến khó; chỉ thêm nếu assertion cần được kiểm sâu |
| Playwright, axe | Browser và accessibility tự động; cần browser binary, route/locator thật và review người |
| Promptfoo | Điều phối eval/so phiên bản; dùng adapter/scorer rõ, không tự bật judge/remote generation |
| FastAPI TestClient, Schemathesis, Testcontainers | API/schema/DB integration; cần app/schema/runtime, không dùng ví dụ API riêng như bằng chứng app |
| DuckDB, pandas/Polars, Pandera | Tính toán/oracle/data validation; không silently drop input lỗi |
| JiWER, FFmpeg, ffprobe | STT metrics/media kỹ thuật; không tự đo TTS tự nhiên hoặc nội dung video |
| Gitleaks | Secret scan files/history, redact report; không chép findings raw vào báo cáo |
| Bandit/Semgrep | SAST theo ngôn ngữ; findings cần triage theo luồng dữ liệu |
| pip-audit/OSV tooling, Trivy | Dependency/image scan theo scope/lock; ghi advisory lookup và phần chưa kiểm |
| ZAP, ClamAV, Presidio | Web runtime/malware/PII là các phạm vi riêng; không thay auth hoặc chính sách dữ liệu |
| k6 hoặc Locust | Load theo workload được phép; local synthetic load không phải năng lực inference thật |
| Langfuse hoặc Phoenix, OpenTelemetry, Prometheus/Grafana | Trace/metrics; chọn vừa đủ, rà edition/license/telemetry và mọi provider phụ |
| Label Studio/CVAT, DVC, MLflow/Evidently | Nhãn/artifact/ML experiments/drift khi dữ liệu và bài toán thực sự cần |
| DBeaver/Bruno | Kiểm DB/API thủ công, không nhúng credentials trong collection hoặc export |

Các công cụ orchestration, vector search, parser/OCR và auth/consent không thuộc runner mặc định. Chúng cần hợp đồng sản phẩm, deployment và regression riêng theo các guide tương ứng. Không copy dependency directory, model cache, snapshots hay private logs từ máy đã thử trước.

## LLM judge và egress

Ưu tiên code cho số, ngày, quyền, IDs, schema, tool args và final state. Người/judge giúp ngữ nghĩa như đủ ý, groundedness, rõ ràng. Judge có thể sai, thiên vị thứ tự/model hoặc bị output dẫn dắt; hiệu chuẩn trên mẫu đúng/sai có người chấm, rubric rõ, chấm mù và đảo thứ tự khi so A/B. Không dùng điểm văn phong bù lỗi critical.

Ragas/DeepEval trong kit là tùy chọn có runtime riêng. Judge phải cấu hình endpoint/model/key/budget riêng; metric đo được (`scored`) không tự thành release pass. Số ca judge không đồng nghĩa số request vì một metric có nhiều calls. Đọc contract kit trước khi bật; thiếu điều kiện giữ not-run/error đúng nghĩa.

Rà target, judge, embedding metric, synthetic generator, red-team generator, plugins, tracing/cloud sync, telemetry và update checks. Tắt telemetry không bằng network isolation. Dùng egress policy theo phạm vi được phép; không tự fallback provider. Cache/replay tiết kiệm calls nhưng không đo latency live hiện tại.

## Negative controls và trạng thái

Trước khi tin scorer, cố ý đưa một output sai và một output/input/file thiếu; phải bị bắt đúng. Có thể thêm citation bịa, tool sai args, source thiếu hoặc action bị cấm. Negative control kiểm **bộ chấm**, không cộng vào tỷ lệ đạt của sản phẩm. Fixtures và examples có nhãn riêng, không thay inference thật.

| Trạng thái báo cáo | Ý nghĩa |
| --- | --- |
| pass | Assertion đã chạy và đạt trong phạm vi của nó |
| fail | Có output nhưng vi phạm expected |
| error | Không hoàn tất phép kiểm, ví dụ API/parser/tool lỗi |
| timeout | Hết deadline; không mất khỏi báo cáo |
| skipped/not-run/unavailable | Chưa kiểm hoặc thiếu điều kiện; critical vẫn chưa đạt gate |
| not-applicable | Ngoài contract đã chốt, phải có lý do |
| needs-review | Tự động chưa kết luận, cần người kiểm |

Tên trạng thái machine-readable của kit có thể gộp một số loại; map theo schema kit và giữ nguyên nguyên nhân chi tiết. Một command exit 0 chưa đủ nếu framework có case failures hoặc metric chưa chạy. Exit lỗi phải còn trong manifest; report vẫn cần tạo từ evidence hợp lệ. Không dùng `|| true` để đổi ý nghĩa kết quả.

Đếm số ca độc lập khác số subtests, số assertions và số reruns. Ví dụ minh họa: 8 planned, 6 pass, 1 fail, 1 timeout thì ghi 6/8 trên planned; nếu thêm 6/7 trên các ca đã chấm phải đặt cạnh timeout. Không chỉ nói “86% đạt”. Demo/replay/live/manual/example/negative-control có denominator riêng.

## Observability và phiên bản

Mỗi step/run giữ command đã loại secret, working context portable, start/timezone, elapsed, exit code, status, source fingerprint, prompt/model/config/data/index/scorer versions và output hash. Commit hash chưa đủ khi worktree còn thay đổi. Run directory mới giúp tránh ghi đè baseline.

Đo queue, retrieval, SQL, time to first token, answer hoàn tất, STT, TTS và âm hữu ích đầu tiên riêng. Không dùng câu đệm làm thời điểm đáp án có ích. Báo từng mẫu/min–max khi ít dữ liệu; percentile trên vài mẫu chỉ mô tả mẫu đó, không là SLA. Tính cost cả lượt fail/retry/judge và giữ unknown nếu không đo được; cost trên tác vụ thành công là N/A nếu chưa có tác vụ thành công.

Log metadata theo scope cần thiết, không raw secrets/PII/chain-of-thought. Tránh user ID hoặc token làm nhãn metrics có cardinality cao. Traces nối các bước để xác định lỗi; không tự làm chứng cứ nội dung model đúng. Health checks không gọi inference có phí liên tục.

## Báo cáo và quyết định

Report tối thiểu có: phạm vi/mode/version; command/runtime; planned/pass/fail/error/not-run; mỗi ca với question, expected, observed, reason và evidence; controls; phần chưa đo; latency/cost có số mẫu; review người đã xem/nghe đoạn nào; lỗi critical; quyết định demo/release và lệnh tái chạy.

HTML/PDF phải sinh từ cùng dữ liệu có version, không sửa điểm bằng tay. Renderer cần escape nội dung untrusted, tính lại số đếm và nhận biết dữ liệu thiếu. Khi xuất PDF, kiểm mọi trang: dấu tiếng Việt, bảng, footer, cắt/tràn, trang trắng và link. Bố cục mẫu không bắt buộc số trang cố định; nội dung thay đổi thì kiểm lại cả prose và data.

Khi sửa code, chạy test hẹp rồi mở rộng theo contract ảnh hưởng. Khi sửa prompt/model/tools, chạy bộ ca cố định. Khi sửa ingest/index, đo retrieval trước answer. Khi thêm voice/media, chạy inputs thật cùng lỗi lifecycle. Giữ fail có ý nghĩa; sửa oracle chỉ khi nguồn độc lập chứng minh oracle sai và lưu version/lý do. Demo đạt một luồng không đồng nghĩa production sẵn sàng.
