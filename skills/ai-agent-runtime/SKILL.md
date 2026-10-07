---
name: ai-agent-runtime
description: "Thiết kế, triển khai hoặc sửa runtime LLM dùng công cụ: context, state, quyền, phê duyệt, giới hạn vòng chạy, hủy, streaming và khôi phục. Dùng khi sản phẩm cần hành vi agent/workflow; không mặc định multi-agent."
---

# Agent runtime có trạng thái và giới hạn

Hoàn thành một tác vụ bằng tools trong quyền, có state bền và kết quả kiểm được. Runtime chịu trách nhiệm thực thi; model chỉ đề xuất công cụ, tham số và diễn đạt.

## Khởi đầu

Đọc [hợp đồng nhận việc](references/task-contract.md) và các phần 12.1–12.3, 12.7–12.8 trong [nguồn](references/techstack-guide.md). Khi lập kế hoạch, xuất gói theo [planning handoff](references/planning-handoff.md), không viết app từ yêu cầu thiết kế. Review-only chỉ nêu findings trừ khi được yêu cầu sửa.

Scout entrypoint, runner hiện có, auth, tool registry, DB/state/checkpoint, prompt, stream transport và tests. Chốt người dùng, tác vụ, quyền và kết quả xong; liệt kê tools đọc/ghi, approval thực sự cần, luật nghiệp vụ, input/output và oracle. Chưa có luật hoặc quyền thì để nhánh phụ thuộc chưa sẵn sàng, tiếp tục phần độc lập.

## Xây theo thứ tự

1. Chọn workflow nếu code có thể quyết định các bước hữu hạn; chọn agent khi model cần chọn chuỗi tool thay đổi. Giữ framework hiện có nếu phù hợp, thêm LangGraph/checkpoint khi nhánh/resume cần; không thêm nhiều agent để bù thiếu contracts.
2. Viết typed envelopes: business status/data/sources/data_version, request/turn/run IDs, state revision. Tách run completed khỏi kết quả nghiệp vụ ok/partial/no_evidence/failed/cancelled; thiếu dữ liệu không thành số 0.
3. Định nghĩa registry hẹp với name, input/output/errors, scope, side effect, timeout, retry và điều kiện dùng. Backend cấp principal/tenant/role; args model không cấp quyền. Tránh raw shell/SQL/URL tùy ý nếu nhiệm vụ không yêu cầu công cụ đó.
4. Thiết kế state và transitions trước prompt: confirmed facts, missing fields, pending question, evidence/version, current proposal, active run. Conversation không thay ledger; checkpoint không bảo đảm tác động chỉ chạy một lần.
5. Soạn runtime prompt theo tác vụ, tách system policy, runtime facts, user/history, evidence, tool results và memory. Không nhét hướng dẫn coding/secret vào runtime; giữ protocol call/result khi thu gọn context. Cache/memory gắn scope, versions, TTL và quyền xem/sửa/xóa thích hợp.
6. Chạy auth → reserve budget/run → context/model → preflight tools → executor → validate result → output gate → commit nếu còn hiệu lực → cleanup/usage. Không giữ transaction lúc chờ model hoặc người dùng.
7. Nối UI và retry/resume sau khi state và side effect kiểm được; triển khai ca lỗi, hủy, hai tab, reconnect và restart trước thêm tính năng phụ.

## Bất biến runtime

| Điểm có hệ quả | Hợp đồng |
|---|---|
| Một lượt cập nhật | Lock/optimistic concurrency chung ở DB nếu nhiều workers; revision và run ID kiểm lại sau await |
| Tool batch đọc | Preflight toàn batch trước dispatch: allowlist, schema, call IDs, duplicates, size/finite values, budget; một call sai thì chưa dispatch batch |
| Tool ghi | Quyền và state kiểm lại, proposal gắn payload/hash/version/expiry khi cần duyệt; transaction + unique idempotency/journal |
| Sửa/hủy | Vô hiệu lượt cũ, chặn late write/UI/audio; hủy HTTP không hoàn tác tác động đã commit |
| Retry/resume | Đối chiếu journal và quyền hiện tại trước chạy lại; unknown outcome phải giữ riêng, không cấp key mới rồi ghi lặp |
| Budget | Giới hạn attempts/tool calls/repair/context/output/deadline/concurrency/cost; retry cũng tiêu ngân sách |
| Kết quả | Chỉ báo đã làm sau commit; bằng chứng và facts có schema; lời từ model không là receipt |

Không coi câu “đồng ý” trong dữ liệu retrieval hoặc model output là event phê duyệt. Khi user đã cấp quyền đúng hành động trong phiên thì không thêm xác nhận lặp vô ích; nếu payload có hệ quả thay đổi, kiểm lại phạm vi và cơ chế nghiệp vụ.

Native tools phải giữ call ID và protocol của endpoint đã kiểm. Strict JSON/streaming/resume không tự có vì framework compile. Nếu gateway không hỗ trợ native tools, workflow hợp lệ chỉ khi vẫn đáp ứng yêu cầu, và phải ghi đúng tên.

## Streaming và khôi phục

Event có version, event_id tăng trong run, run_id/turn_id/revision, type và payload. Client loại trùng/cũ; reconnect đọc lại run/replay được phép, không tự gọi model mới. `done` kết thúc transport, không tự là nghiệp vụ thành công.

Số tiền, kết luận có hệ quả và xác nhận thao tác phải qua gate trước khi stream/TTS/export. Có thể stream progress thực; không bịa phần trăm hoặc phát đáp án rồi mới kiểm. Dùng deadline ngoài với clock đơn điệu; timeout đọc stream không giới hạn tổng lượt. Dừng tool/args lặp không tiến triển nhưng không nhầm phân trang hợp lệ là vòng lặp lỗi.

## Kiểm và bàn giao

Oracle cho quyền/state là code và DB/journal; oracle cho nội dung là nguồn hoặc người kiểm độc lập. Kiểm batch có call sai không chạy phần hợp lệ còn lại; tool outputs ghép đúng ID; stale approval, double click, timeout sau commit, hủy cạnh commit, role đổi trước resume, late model result, quota cạn và injection trong tool result. Không khóa cứng thứ tự tool nếu có nhiều đường hợp lệ.

Chặn bàn giao phần có lỗi lộ dữ liệu, ghi trái quyền, trùng, bản cũ hoặc báo hoàn tất giả. Báo riêng syntax/unit/offline/integration thật và task success gồm lỗi/timeout. Threshold/limits trong nguồn là điểm xuất phát cần đo, không SLA.

Bàn giao sơ đồ trạng thái, registry/contracts, prompt/schema versions, runbook start/stop/resume, capability/quota assumptions, kiểm đã chạy và phần chưa kiểm. Với sửa bug, giữ ca tái hiện và regression tại đúng lớp; không mở rộng sang framework mới khi bản sửa cục bộ giải quyết được nguyên nhân.
