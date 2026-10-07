# Xây chatbot, RAG và agent có bằng chứng

Đọc [kiến trúc](architecture-and-use-cases.md) để chọn tác vụ, [provider profiles](provider-profiles.md) để kiểm API và [backend](backend-security-and-privacy.md) để đặt quyền. Các schema và pseudocode dưới đây là **thiết kế tham khảo cần triển khai**, không phải ứng dụng đã chạy trong starter.

## Hợp đồng đầu vào và kết quả

Backend xác thực rồi tạo scope; browser/model không tự chọn tenant, role hay quyền duyệt. Hợp đồng nghiệp vụ cần định nghĩa trường, đơn vị, timezone, khoảng thời gian, trạng thái dữ liệu và trường thiếu. Đừng để “tổng chi” có nhiều nghĩa mà vẫn trả một con số chắc chắn.

Một kết quả tool có thể gồm:

```text
# Pseudocode schema — không phải schema của eval kit
ToolResult:
  status: ok | partial | no_rows | no_evidence | ambiguous |
          insufficient_history | invalid_input | dependency_error
  data: dữ kiện có kiểu hoặc null
  filters: bộ lọc đã áp dụng
  source: IDs, versions, vị trí thật và query/import references
  data_quality: số hàng lỗi/thiếu/trùng, cảnh báo
  coverage: phạm vi quan sát hoặc unknown
  run_id, call_id: định danh do hệ thống cấp
```

`no_rows` không đồng nghĩa toàn bộ tài khoản không có giao dịch; `null` không bằng 0. `partial` không được render như kết quả đầy đủ. UI dùng dữ kiện có kiểu để dựng số/bảng/biểu đồ; lời văn chỉ diễn giải. Không hiển thị chain-of-thought; hiện nguồn, phép tính, thao tác và giới hạn đủ để kiểm.

## SQL, đối soát và số liệu

- Bắt đầu bằng tool hẹp và SQL cố định có tham số. Scope tài nguyên do backend cấp. Role DB chỉ có quyền cần thiết; read-only transaction không tự tạo phân quyền theo hàng.
- Tiền dùng decimal hoặc integer minor units theo currency contract. Khi cần giữ chính xác qua JSON, dùng chuỗi decimal đã validate; không parse qua float rồi mới sửa. Giữ mã có số 0 đầu như chuỗi.
- Khoảng ngày có timezone rõ, thường dùng `[start, end)`. Chốt posted/pending/refund, dấu của amount và currency trước aggregation. Không cộng nhiều currency nếu chưa có nguồn/quy tắc quy đổi.
- Import giữ nguồn, hash/version, số hàng và lỗi. Không đổi amount lỗi thành 0 hoặc silently drop hàng. Số dư cần opening balance và độ phủ phù hợp; dữ liệu một phần chỉ cho kết luận trên phần đã quan sát.
- Đối soát cần reference, amount, currency, ngày, nguồn và quy tắc settlement. Amount đơn lẻ không phải khóa. Trả 0/1/nhiều ứng viên với lý do và trường chưa khớp; fuzzy match chỉ là đề xuất cần xử lý theo nghiệp vụ.
- Ảnh biên nhận/OCR không xác nhận settlement. “Không thấy trong dữ liệu này” không bằng “chưa thanh toán”.

Chỉ mở NL2SQL nếu templates không đáp ứng nhu cầu đo được. Cấp schema/views tối thiểu, parse AST, allowlist tables/functions, giới hạn một statement, read-only role, scope, timeout, row/scan limit. Chặn write/DDL và thao tác nguy hiểm tại DB, không chỉ kiểm chuỗi bắt đầu bằng `SELECT`. Giải thích truy vấn và đối chiếu oracle. Query lỗi/timeout phải trả lỗi; không sinh số liệu thay thế.

## RAG: từ nguồn được phép đến câu trả lời

Luồng ingest: nhận nguồn → parse → giữ provenance → kiểm chất lượng/hiệu lực/quyền → chunk → embedding/index → review nếu nghiệp vụ cần → publish nguyên phiên bản. Luồng query: xác thực → xác định ngày/phạm vi → lọc nguồn hợp lệ → retrieve → kiểm đủ evidence → trả lời/trích dẫn hoặc hỏi lại.

### Parse, chunk và metadata

| Nguồn | Cách bắt đầu | Cần đối chiếu |
| --- | --- | --- |
| Markdown/text có tiêu đề | Chia theo điều khoản/heading | Điều kiện, ngoại lệ và nội dung bổ nghĩa đi cùng nhau |
| PDF text đơn giản | Parser text có provenance | Trang, thứ tự đọc, dấu tiếng Việt |
| PDF bảng/layout/scan | Parser cấu trúc hoặc OCR local đã đánh giá | Ô gộp, cột, đơn vị, caption, số/ngày và tọa độ thực |
| Web/crawl | Fetch trong scope cho phép, giữ snapshot/hash/URL | Nội dung chính, ngày truy cập, phiên bản và nội dung bị thiếu |

Docling, pdfplumber hoặc OCR là các lựa chọn parser cần kiểm theo file thực; không phải dependency đã cài bởi guide. Nếu chạy local/offline, chuẩn bị artifacts và xác minh không bật remote processing/plugin mặc định. Tải weights và gửi tài liệu tới dịch vụ khác là hai hoạt động khác nhau cần ghi rõ.

Mỗi document/chunk giữ `source_id`, revision nội dung/xử lý, hash nguồn, title, owner/ACL, ngày hiệu lực nếu có, parser/chunker/embedding version và vị trí gốc. Không bịa số trang cho nguồn không phân trang. Ngày upload không thay ngày hiệu lực. Thiếu metadata quyết định thì giữ staging hoặc báo unknown theo policy, không tự phát minh.

Chunk theo ý nghĩa: giữ đơn vị, heading, ngoại lệ và chú thích. Bảng dài có thể chia theo nhóm hàng nhưng lặp tiêu đề cột/đơn vị/caption cần thiết. Giữ cấu trúc JSON/HTML của bảng cạnh text khi cần đối chiếu. Token budget là giới hạn cần kiểm, không là lý do cắt mất điều kiện quan trọng. Hybrid chunking khác hybrid search.

### Publish và vòng đời index

Publish document và chunks atomically; lần ingest lỗi không thay bản đang phục vụ. Revision đã phát hành không bị sửa nội dung tại chỗ. Thay parser/chunker/embedding tạo revision xử lý mới; đổi chính sách tạo nội dung/version mới.

Với chính sách thay đổi, cập nhật mốc hiệu lực cũ và bản mới trong cùng workflow có khóa/audit. Với reparse/re-embed cùng chính sách, giữ kỳ hiệu lực; đánh dấu processing revision cũ superseded. Không lấy ngày reparse để thay ngày hiệu lực nghiệp vụ. Truy hồi lịch sử phải dùng đúng phiên bản tại thời điểm hỏi; truy hồi hiện tại dùng bản đang published.

Review tài liệu nên hiện nguồn và nội dung trích cạnh nhau, metadata, lỗi parse và thay đổi so bản trước. Trạng thái `approved` chỉ do người/luồng được cấp quyền; score parser hoặc LLM “confidence” không tự phê duyệt. Crawl/review/publish là các bước riêng. Sửa nguồn/revision làm hết hiệu lực quyết định review cũ. Ghi reviewer, thời điểm và content hash; dữ liệu lấy từ web không tự được cấp quyền tái phân phối.

ACL cần lọc trước khi chunk vào context; kiểm quyền khi mở citation/download nữa. Thu hồi quyền/xóa nguồn phải ảnh hưởng search, cache, history và file dẫn xuất theo policy. Dữ liệu cũ có thể giữ hạn chế để audit nếu có nhu cầu hợp lệ, nhưng không tiếp tục phục vụ như nguồn hiện hành.

### Truy hồi và trả lời

Bắt đầu với corpus nhỏ và search đơn giản. Đo retrieval recall trước khi thêm ANN/hybrid/reranker. Kiểm embedding batch indices, dimension, finite values và cùng model/config ở index/query. Giữ exact lookup theo ID/mã khi các mã quyết định nghiệp vụ.

Không coi cosine score là xác suất đúng. Ngưỡng no-evidence phải hiệu chuẩn trên ca có/không có nguồn. Nếu top-k thiếu điều kiện, sai version hoặc nguồn mâu thuẫn, hỏi lại/báo thiếu/công bố mâu thuẫn. Không làm tròn thông tin chưa chắc thành câu trả lời chắc chắn. Citation cần đúng source/version/vị trí và thực sự hỗ trợ claim; ID hợp lệ riêng lẻ chưa đủ.

Kiểm retrieval riêng bằng gold IDs, rồi kiểm câu trả lời. Khi answer sai, xác định lỗi nguồn/parse/chunk/filter/retrieval hay generation; đừng đổi prompt để che một index thiếu dữ liệu.

## Prompt và context

Prompt runtime khác prompt giao việc coding agent. Chỉ gửi policy đã review, facts cần thiết, user request, lịch sử liên quan và evidence trong quyền. Không đưa secrets, cấu hình deploy hay toàn bộ hướng dẫn repo vào system prompt.

Một prompt runtime tham khảo cần diễn đạt: nhiệm vụ/phạm vi; tool nào được dùng và khi nào; facts nào là nguồn quyết định; mơ hồ thì hỏi gì; thiếu evidence thì phản hồi ra sao; output mong đợi. Auth, quota, tính toán và approval vẫn nằm ở code.

Giữ các lớp riêng: system policy; backend runtime facts; user input; history; retrieved evidence; tool result. Upload/OCR/web/transcript và ghi chú trong tool output là dữ liệu chưa tin cậy. Nhãn JSON/XML hỗ trợ cấu trúc nhưng không ngăn injection bằng bản thân nó.

Context budget tính cả schemas, history, evidence, output và reasoning nếu có. Cắt nội dung lặp/không liên quan trước; giữ filters đã xác nhận, pending question, source/version và các cặp tool-call/result hợp lệ. Summary có thể sai; không nâng nó thành quyền hay nguồn sự thật. Long-term memory chỉ thêm khi có mục đích, quyền, xem/sửa/xóa và retention rõ.

Cache key phải bao gồm scope/tenant, quyền, filters, model/prompt/index/data version và thời hạn cần thiết. Đổi quyền hoặc dữ liệu phải invalidation. Không cache câu trả lời riêng tư chỉ theo câu hỏi.

## Tools và vòng agent có giới hạn

Mỗi tool cần tên ổn định, khi dùng/không dùng, input/output schema, đơn vị, errors và side effects. Registry chỉ gồm tools được phép cho tác vụ hiện tại. Args không nhận các trường cấp quyền như `role`, `approved` hay tenant do model tự chọn.

```text
# Pseudocode orchestration — cần adapter/executor thực
start_run(actor, thread, request):
  authenticate + authorize_thread + acquire_single_writer
  bind run_id, state_revision, deadline, call/token/cost budgets
  while run_is_current and budgets_remaining:
    response = call_model(context, remaining_deadline)
    if completed_answer: validate_output_and_publish(); stop
    calls = parse_all_calls(response)
    validate_entire_batch(calls, registry, schemas, IDs, budgets)
    reserve_budget_atomically()
    for call in calls:
      recheck actor_permission, run_ownership, data_version, deadline
      result = execute_validated_call_or_safe_error(call)
      validate_result_and_attach_to_original_call_id()
    preserve_valid_protocol_history()
  finish_with_explicit_terminal_state()
```

Preflight toàn batch trước khi chạy giúp tránh thực hiện một phần batch có input sai. Nó không thay authorization tại thời điểm thực thi, không hoàn tác tác vụ trước đó và không tự làm side effects an toàn. Dùng object đã validate, không parse input lại theo cách khác. Duplicate call IDs phải tra kết quả cũ hoặc báo rõ; không khiến model lặp vô hạn. Tool validation error có thể cho sửa hữu hạn nếu policy cho phép; không trả raw SQL/trace/secret trong error.

Native function calling chỉ bật sau probe trọn vòng qua provider. Nếu chưa có, dùng form/typed filters → backend tool → diễn đạt facts đã có, hoặc model đề xuất JSON rồi backend kiểm. Không chạy shell/Python/SQL tùy ý từ text. Nếu dùng framework graph, graph compile/import chỉ kiểm wiring; chưa chứng minh invoke, persistence, quyền hay provider đã hoạt động.

## State, concurrency và phục hồi

Phân biệt `request_id` (HTTP), `turn_id` (ý định/lượt người dùng), `run_id` (lần thực thi) và `call_id` (tool). State có filters, fields còn mơ hồ, nguồn/version, schema version, ownership/revision và status. Server cấp thread ID, ràng buộc actor/scope ở cả read và resume.

Chỉ một writer sửa state của một thread. Nhiều worker cần khóa/queue hoặc optimistic concurrency chung, không dùng mutex một process làm đảm bảo toàn hệ thống. Không giữ transaction nghiệp vụ mở trong lúc chờ model. Khi worker mất quyền sở hữu/lease, chặn write/checkpoint và phát kết quả.

Event/result gắn run/revision; backend chỉ công bố khi vẫn current. UI cũng loại kết quả cũ. Cancel tăng generation/epoch hoặc vô hiệu run trước khi abort. Sửa filters/data làm stale results/proposals phụ thuộc. Checkpoint cần schema tương thích; resume kiểm lại quyền, dữ liệu và trạng thái side effect, không chạy lại toàn bộ mù.

Deadline toàn run gồm queue, model, tool, retry và body đọc; HTTP timeout từng pha không thay deadline tổng. Giới hạn vòng, calls, tokens, bytes và cost riêng. SSE/network chunk không phải event hoàn chỉnh; kết nối đóng không chứng minh completed. Khi mất mạng giữa output, giữ trạng thái incomplete và cho phục hồi có kiểm.

## Thao tác ghi và hệ thống ngoài

Nếu trong scope có ghi/gửi, thiết kế prepare → xác nhận/duyệt theo tác động → kiểm lại quyền/version → commit idempotent → audit. Không thêm duyệt cho mọi thao tác đọc đã được cấp quyền; không bỏ duyệt nghiệp vụ chỉ vì model nói “người dùng đồng ý”.

Approval gắn actor, tài nguyên, payload hash, data revision, expiry và phạm vi; reject/expiry/payload đổi thì không thực thi. Tiêu thụ approval cùng transaction phù hợp. Unique idempotency key và kết quả đi cùng business write; checkpoint không đảm bảo exactly-once. Kiểm process chết sau commit nhưng trước response/checkpoint. Với gửi ngoài DB, dùng outbox/remote idempotency và đối soát trạng thái; không hứa rollback được email đã gửi.

## Anomaly và mô phỏng

Đi từ rule minh bạch → thống kê → ML nếu có bằng chứng. Fit trên lịch sử trước thời điểm chấm; không fit lại mỗi lượt hỏi hoặc dùng tương lai làm feature. Giữ feature/model/train-data version; kiểm thiếu history, null, nonfinite và drift. Mô hình chấm score, code/analyst quyết định ngưỡng theo workload/lỗi có thể chấp nhận.

Không có nhãn thì không báo precision/recall/FPR giả từ score. Báo số cảnh báo, lý do rule/feature, tỷ lệ được người kiểm xác nhận và giới hạn. Bất thường không đồng nghĩa gian lận hay đánh giá phẩm chất con người. Mô phỏng phải phân biệt dữ liệu quan sát, giả định do người dùng chọn và kết quả tính; không trình bày như dự báo đã xác minh.

## Nghiệm thu đường chatbot

Kiểm số/filters/currency/timezone/null; quyền khác user/tenant/thread; thiếu/mâu thuẫn/hết hiệu lực nguồn; args sai/nhiều calls/call IDs; budget/deadline/cancel; hai request cùng thread; đổi dữ liệu và resume; side effect sau crash nếu có. Với RAG kiểm publish lỗi vẫn giữ bản cũ, xóa/thu hồi không rò, citation thật hỗ trợ claim. Dùng [evals](evals-and-observability.md) cho dataset, oracle và báo cáo, không suy chất lượng từ câu trả lời nghe tự tin.
