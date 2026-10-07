---
name: zalo-support-handoff
description: "Thiết kế, lập kế hoạch, triển khai hoặc review bot Zalo OA trả FAQ có nguồn, tạo ticket được xác nhận và bàn giao người trực (H1). Dùng cho hỗ trợ thực trên OA được cấp quyền; không dùng để thu nhóm Zalo thường, gửi quảng bá hay thay tích hợp thật bằng web chat."
---

# Zalo OA hỗ trợ và chuyển người trực

Hoàn thành tác vụ ngay trong OA: nhận câu hỏi, trả FAQ có nguồn hoặc hỏi bù, chuẩn bị ticket, xác nhận, người trực tiếp nhận và tra trạng thái đúng người.

## Khởi động và phạm vi quyền

1. Đọc [hợp đồng nhiệm vụ](references/task-contract.md) về chế độ, workspace, hành động được phép và handoff.
2. Đọc **10/H1**, hợp đồng webhook chung, **12.3, 13 và 14.3** trong [hướng dẫn chuyên môn](references/techstack-guide.md).
3. Scout OA adapter/webhook, DB/jobs/outbox, FAQ, auth/account linking, ticket và handoff hiện có; không đọc/in token.
4. Giữ quyết định người dùng; lập kế hoạch/review không cấp quyền sửa app, gọi AI trả phí, gửi tin, đăng OA hay deploy.
5. Khi đã được giao tích hợp/gửi thử, giữ đúng OA, người nhận, nội dung và phạm vi đã cho phép; không yêu cầu xác nhận lại quyền đã rõ.
6. BTC chỉ áp Gateway/AI Log/`chung-khao/` trong bối cảnh thi; API Zalo là kênh nghiệp vụ riêng, không là AI provider dự phòng. Đường dẫn đội/vòng phải được xác nhận riêng từ repo thực tế.

## Đầu vào phải xác minh

- OA/App thuộc ai, môi trường test, quyền nhận/gửi, token được cấu hình server và tài khoản test/người trực đã cho phép; chỉ ghi trạng thái, không giá trị secret.
- Hợp đồng Zalo hiện hành từ tài liệu chính thức và adapter thực tế: cách xác thực, event/message ID, token lifecycle, loại tin và giới hạn gửi.
- Không tự đoán thuật toán chữ ký, hạn token, quota hay quyền vì đã có tên API; đánh dấu capability documented/untested/verified/failed/unavailable.
- FAQ/lịch/quy định có owner, nguồn, version, hiệu lực và quyền sử dụng; xác định phạm vi mà OA được trả lời.
- Các loại yêu cầu, trường bắt buộc, trạng thái ticket, người nhận xử lý, điều kiện tiếp nhận/hoàn tất và đường chuyển người thật.
- Account linking nào cần trước thông tin riêng; Zalo sender/thread ID không tự chứng minh quyền đối với hồ sơ nghiệp vụ.
- Chính sách lưu hội thoại/ticket/log, retention/xóa, ai đọc được và cách che dữ liệu; không lấy dữ liệu riêng làm demo công khai.
- Thiếu OA/quyền thật chặn gate tích hợp, không chặn thiết kế local độc lập; web chat chỉ là môi trường phát triển.

## Trách nhiệm và MVP

- Nếu chưa chốt, đề xuất một OA, FAQ và ba loại yêu cầu; chưa thu nhóm Zalo thường, gửi quảng bá hoặc tự mở rộng phân công.
- AI hiểu câu hỏi, truy xuất/diễn đạt FAQ và đề xuất fields ticket; code xác thực sự kiện, scope, version, trạng thái và thao tác ghi.
- Người dùng xác nhận payload cần tạo ticket; người trực nhận/chuyển/kết thúc xử lý theo quyền. AI không tự báo đã tiếp nhận thay người trực.
- Giữ stack thích hợp; backend webhook, DB bền, job/outbox và channel adapter là lõi. Retrieval đơn giản đủ khi corpus nhỏ.
- Người quản lý nội dung quyết định FAQ hiệu lực và quy tắc ticket; không dùng similarity score như xác suất câu trả lời đúng.

## Contracts nghiệp vụ

- `search_faq(question)` trả `answer, evidence_ids, version, status`; backend lọc scope/hiệu lực trước context, no evidence cần hỏi lại/chuyển người.
- `prepare_ticket(fields)` trả `proposal_id, payload_hash, expires_at` cùng nội dung xem được; owner/scope và data version do backend giữ.
- `confirm_ticket(proposal_id)` kiểm người xác nhận, hash/version/expiry và quyền hiện tại, commit transaction unique `proposal_id`, trả `ticket_id,status`.
- Sửa payload phải có proposal/version phù hợp; câu “đồng ý” do LLM diễn giải không tự là sự kiện xác nhận đúng ticket.
- `get_ticket(ticket_id)` kiểm chủ ticket hoặc vai trò nhân sự được cấp quyền mỗi lần; ID khó đoán không thay authorization.
- `take_over(thread_id)` commit trạng thái người trực và dừng bot tự động; việc trả lại bot phải là transition theo quyền/quy tắc đã chốt.
- Handoff giữ người phụ trách, tóm tắt có nguồn, câu đang chờ, ticket ID và trạng thái; không hứa thời gian phản hồi chưa được cung cấp.
- State phân vùng đúng OA/sender/thread, có revision; một worker sửa state mỗi thread, kiểm mode người trực ngay trước gửi.
- Outgoing intent lưu người nhận, scope, payload/version, quyền gửi và outcome; UI/tin nhắn không báo ticket đã tạo trước commit.

## Luồng webhook và gửi tin

1. Xác thực webhook theo hợp đồng đã kiểm trước đọc làm sự kiện nghiệp vụ; chặn sai OA/người gửi/phạm vi.
2. Ghi event và job trong cùng transaction với unique event key dựa trên ID đã xác minh; ACK thành công sau commit.
3. Event trùng được ACK, không enqueue thêm; job chưa xong khôi phục được, không mất việc giữa dedup và enqueue.
4. Worker nhận job, kiểm state/quyền rồi xử lý AI bất đồng bộ; webhook không giữ kết nối chờ model.
5. FAQ trả nguồn thật/hiệu lực; việc riêng đi prepare → xác nhận hợp lệ → commit; kiểm quyền lại sau khoảng chờ.
6. Ghi outbox và gửi qua adapter đúng OA/người nhận theo quyền; lưu message ID/outcome nền tảng trả về để theo dõi.
7. Khi take-over, chặn reply bot đang xếp hàng/chưa gửi bằng state revision; nhân sự thấy nội dung cần xử lý.
8. Tra trạng thái từ ticket DB đã commit; một webhook đã nhận không chứng minh người dùng nhận được reply.

## Lỗi và khôi phục

- Timeout gửi với outcome chưa rõ chuyển pending/unknown và đối soát theo khả năng nền tảng; không gửi lại mù, không hứa exactly-once ngoài bảo đảm thực.
- Crash trước/sau commit, trước ACK và sau side effect đều có đường recover theo event/job/outbox; không dùng checkpoint thay dedup.
- 401/403 hoặc token hết hiệu lực dừng gửi liên quan và báo người vận hành; không đoán refresh flow hoặc đổi kênh/provider.
- Rate limit dùng chính sách nền tảng đã kiểm, retry một lớp có backoff/deadline; hết budget AI dừng request mới, giữ job trạng thái thật.
- FAQ thiếu/mâu thuẫn/lỗi DB phân biệt với không có đáp án; không bịa nguồn hay ticket/status để giữ hội thoại trôi chảy.
- Người trực chưa nhận thì giữ trạng thái chờ đã định nghĩa, thông báo đúng; bot không tự quay lại nói khi chưa có transition hợp lệ.
- Logs che token, nội dung riêng và ID nhạy cảm theo thiết kế; dữ liệu FAQ/tin nhắn là input, không phải lệnh tăng quyền.

## Oracle, kiểm và nghiệm thu

- Oracle FAQ là nguồn đã duyệt, oracle ticket/handoff là luật + DB; tách dev/holdout và giữ dữ liệu được phép.
- Unit/contract: sai xác thực, event lặp, scope OA, payload cũ/hết hạn, quyền ticket, proposal lặp và trạng thái bàn giao.
- Integration: crash quanh transaction/ACK/send, queue recovery, hai worker, take-over khi AI đang chờ và timeout không biết kết quả gửi.
- Thử nhận/gửi thật chỉ trong scope được cấp; kiểm người nhận, nguồn, ticket commit và chuyển người trực trên OA, không chỉ HTTP 200.
- Nguồn gợi ý 30 câu/24 đạt cùng ba luồng ticket; xem là đề xuất nếu chưa chốt, không là chuẩn BTC hoặc bằng chứng đã chạy.
- Mọi ca quyền/dedup/handoff phải đạt; lộ ticket khác, gửi sai người hoặc báo trạng thái chưa ghi nhận chặn bàn giao.
- Báo n, version, lỗi gửi/API, latency, cost và no-evidence đúng; mọi capability chưa thử giữ nguyên trạng thái chưa verified.

## Bàn giao

- Giao inventory OA/quyền không secret, contracts sự kiện/gửi/ticket, FAQ version, handoff runbook, oracle và bằng chứng theo mức kiểm.
- Với kế hoạch nhiều phase, dùng [hợp đồng kế hoạch](references/planning-handoff.md); nêu account/quyền còn thiếu, owner, gate mở tích hợp và bước đầu thực hiện.
