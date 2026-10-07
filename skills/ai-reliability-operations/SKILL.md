---
name: ai-reliability-operations
description: Thiết kế, review hoặc triển khai giới hạn chi phí, retry, job recovery, logs và release cho sản phẩm AI; dùng khi cần vận hành có quota và bằng chứng độ tin cậy, không tự đổi provider hoặc triển khai production từ yêu cầu lập kế hoạch.
---

# Chi phí và độ tin cậy của sản phẩm AI

Giới hạn tác vụ trước khi gửi, phân loại kết quả khi lỗi, khôi phục state và side effect bằng bằng chứng.
Đo chất lượng phục vụ cùng chi phí; không coi một request thành công là vận hành toàn sản phẩm đã đạt.

## Khởi động và phạm vi công việc

1. Đọc [hợp đồng tác vụ](references/task-contract.md) và [trích nguồn techstack](references/techstack-guide.md), trọng tâm 15 và 12.9.
2. Xác định yêu cầu kế hoạch, review hay sửa vận hành; đọc client, workers, queue/DB, cấu hình, dashboards và runbook hiện có.
3. Thu thập provider/key scope không có giá trị secret, quota, workload, side effects, SLO đã chốt, baseline và môi trường được phép.
4. Ghi budget/quota/giá có thật hay ước tính, ngày đối chiếu và nguồn; không đọc/in toàn response có thể chứa key hoặc credential.
5. Với kế hoạch dùng [hợp đồng bàn giao](references/planning-handoff.md); chỉ rõ file/lệnh dự kiến, gate và phụ thuộc.
6. Giữ stack, provider và quyền đã chọn; BTC áp gateway/quy tắc BTC, ngoài BTC không tự mang ràng buộc thi sang.
7. Lập kế hoạch không cho quyền tạo job trả phí, stress gateway hoặc deploy; quyền hiện có được dùng tiếp trong phạm vi đã cấp.

## Contract run, job và ngân sách

| Đối tượng | Trường tối thiểu |
|---|---|
| Run | `run_id/turn_id`, owner/scope, input/revision, deadline, token/tool caps, version và trạng thái |
| Job | ID bền, owner, input/version, provider ID, idempotency, attempts, outcome, cleanup và recovery state |
| Budget | Nhóm chi phí, hạn mức xác nhận, reserve, đã đối soát, đang giữ chỗ, estimate và thời điểm |
| Usage | Endpoint/model, token/audio/media, retries, cost hoặc estimated/unknown, nguồn giá và currency |
| Error | Loại, retryable, outcome known/unknown, request ID, thời điểm, user-visible status và bước khôi phục |

- Code quyết định quota, quyền, retry, deadline và state; AI có thể diễn đạt lỗi nhưng không sửa số dư hay kết luận thao tác đã commit.
- Nguồn/DB unavailable khác no_rows; cost thiếu khác 0; không có task thành công thì cost/success là N/A.
- UI “đã xong” yêu cầu kết quả được kiểm và side effect được đối chiếu; abort HTTP không tự hoàn tác dữ liệu đã ghi.

## Thiết lập ngân sách có thể thi hành

1. Tách coding agent và runtime theo nguồn cấp thật; không cộng hoặc tự chuyển dư giữa các ví.
2. Các mức 50 USD/50 USD trong nguồn là bối cảnh chuẩn bị của đội, không là mặc định BTC hay số dư hiện tại.
3. Liệt kê runtime: model chính/phụ, embedding, STT/TTS, ảnh/video, search, retries, eval/judge; một request chỉ vào một nhóm.
4. Nếu sản phẩm dùng media, phân bổ lại có dòng ảnh/video; không cộng media ngoài tổng đã chốt.
5. Kiểm giá đang áp dụng qua provider/gateway được phép; giá provider trực tiếp không tự là giá gateway.
6. Dự toán mức tối đa trước dispatch, giữ chỗ atomically cho run đang chạy và đối soát sau; tránh nhiều worker cùng tiêu một khoản còn lại.
7. Reasoning có thể dùng output token/cost; voice tính riêng audio nghe và audio nói, không nhân cả phiên cho hai đơn giá.
8. Đọc quota tối thiểu cần thiết theo API hiện hành; giới hạn đồng thời theo key, team, model, RPM/TPM và concurrency thực có.
9. Trong BTC, chỉ dùng các field như `/key/info` và `/team/info` sau kiểm hợp đồng; field thiếu/null là chưa biết, không vô hạn.
10. Key mới có thể chung quota team; không coi đó là ví mới hoặc cách tránh giới hạn.
11. Dùng queue/semaphore và admission control; khi chạm reserve, dừng thử nghiệm tùy chọn và rà ngân sách trước dispatch thêm.
12. Khi có cost header được xác minh, đối soát với usage; thiếu cost dùng estimate có nhãn và theo dõi khoản chưa đối soát.

## Ma trận lỗi và retry

| Tình huống | Hành vi cần kiểm |
|---|---|
| 401/403 | Báo cấu hình/quyền; dừng retry vô nghĩa, không âm thầm đổi provider |
| 400/415/schema | Kiểm payload/codec/model, giữ input để sửa; không lặp cùng lỗi |
| 429 tốc độ | Theo Retry-After nếu có, backoff+jitter trong deadline và quota |
| 429 hết budget | Dừng request mới; không retry chờ ngân sách tự xuất hiện |
| Timeout/5xx đọc | Retry giới hạn khi an toàn, tránh phát kết quả trùng và tính thời gian retry vào deadline |
| Timeout ghi/tạo media | Giữ outcome unknown và đối soát trước thử lại; không tạo side effect trả phí trùng |
| Output incomplete | Không dùng JSON/text cắt dở làm kết quả đã xác nhận |
| STT rỗng/TTS lỗi | Cho ghi lại/nhập chữ; giữ text hợp lệ và chỉ retry audio cần thiết |
| Cancel | Chặn late write/playback, kiểm side effect đã commit và khắc phục riêng |
| DB/nguồn lỗi | Báo unavailable với đường thử lại phù hợp; không thay bằng 0/no_rows |

- Một lớp sở hữu retry, tránh SDK × proxy × worker nhân số lần; media client tắt retry tạo job tự động, worker phân loại outcome.
- Deadline tổng gồm queue, tools, model, retries và output; mỗi bước có budget thời gian còn lại.
- Mốc STT/text/TTS trong nguồn chỉ là đề xuất thử, không SLA gateway; đo để chốt cấu hình của sản phẩm.
- Retry an toàn không đồng nghĩa ghi đúng một lần; dùng idempotency/dedup/transaction hoặc đối soát theo hệ thống đích.

## Khôi phục và release

- Persist trạng thái/ID trước bước phụ thuộc; restart resume từ trạng thái bền, không phát lại thao tác đã hoàn tất một cách mù quáng.
- Job có deadline, owner/scope, cleanup và quy tắc khôi phục; scheduler không có quyền cao hơn người tạo lịch.
- Tách liveness process khỏi readiness DB/queue; health check không gọi model trả phí theo từng probe.
- Feature flag/kill switch backend chặn dispatch mới và commit đang chờ; chỉ ẩn nút UI không đủ.
- Cancel, thay revision hoặc thu hồi quyền làm kết quả cũ không còn quyền ghi/phát; kiểm gate ở thời điểm commit/output.
- Version application, prompt, tool schema, index và data phải tương thích; migrate checkpoint hoặc chặn resume bản không tương thích.
- Rollback về version đã kiểm; preserve dữ liệu cần thiết, đối soát side effects và không âm thầm đổi provider.
- Đổi ngưỡng/scope để đạt test hoặc cắt yêu cầu bắt buộc cần quyết định người dùng; không gọi phần nhỏ hơn là hoàn tất toàn bộ.

## Logs và quan sát

- Ghi model, status/error code, request/turn/run ID, dataset/prompt/parser/index versions, tool, latency, usage/cost và cache hit.
- Trace giữ evidence và thao tác đủ chẩn đoán, không yêu cầu chain-of-thought riêng tư.
- Tách queue, retrieval, SQL, STT, first text token, text hoàn tất, TTS và audio hữu ích đầu tiên; câu đệm không tính là đáp án.
- Theo dõi queue age, freshness, error theo endpoint/model, task success theo nhóm, quota, tool failures, cost và backlog.
- Không dùng account ID/token làm metric label cardinality cao; logs có redaction, access control và retention theo dữ liệu thật.
- Không chỉnh hook AI Log BTC để phục vụ logging app; không gửi traces sang dịch vụ mới khi chưa thuộc quyền.
- Cache hit và uncached báo riêng; cost/task thành công = tổng cost đo gồm lỗi/retry chia số thành công.

## Kiểm chứng có mức bằng chứng rõ

- Chạy kiểm hẹp của logic budget/retry/state trước; broaden contract/integration khi chạm client, queue, DB hoặc public behavior.
- Offline kiểm reserve đồng thời, null quota, budget cạn, Retry-After/deadline, incomplete output và unknown outcome có kiểm soát.
- Với tạo media, timeout test phải chứng minh một POST và trạng thái unknown; không dùng job trả phí để mô phỏng lỗi này.
- Kiểm refresh, hai tab, double click, mất mạng, restart, cancel đúng lúc tool trả, DB lỗi và quota cạn theo flow thật.
- Oracle là số đếm side effects/DB audit/usage ledger và state mong đợi, không phải câu model nói “đã hoàn tất”.
- Integration dùng dependency thật trong phạm vi được phép; load inference cần quota/ngân sách riêng đủ cho phép thử.
- Chốt tiêu chí task success, error, p50/p95 và cost sau baseline; n và workload phải hiện trong báo cáo, tập nhỏ không thành SLA.
- Syntax/import, offline contract, integration thật và nghiệm thu người dùng là bốn mức khác nhau; báo mức đạt thực tế.
- Một lỗi quyền/ghi trùng/chi phí vượt cap đã thấy chặn release phần liên quan; timeout thiếu bằng chứng là inconclusive.

## Bàn giao vận hành

- Giao cấu hình không secret, ledger/ước tính budget, retry matrix, state/recovery diagram hoặc bảng, commands/cwd và evidence đã chạy.
- Runbook chỉ rõ nhận biết lỗi, dừng dispatch, tra run/job ID, đối soát outcome, resume/rollback và người có quyền quyết định.
- Nêu owner/gate cho quota, giá, capability hay quyền chưa biết; tiếp tục phần độc lập và không bịa số dư để báo sẵn sàng.
- Ghi phiên bản phát hành, kết quả kiểm, giới hạn còn lại và phần chưa đo; không hứa toàn hệ thống chịu tải chỉ từ test local.
