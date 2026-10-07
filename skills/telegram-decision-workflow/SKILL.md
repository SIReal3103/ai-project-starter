---
name: telegram-decision-workflow
description: "Thiết kế, lập kế hoạch, triển khai hoặc review bot Telegram gom đề xuất, duyệt poll, chốt biểu quyết và nhận việc trong đúng topic (H2). Dùng cho quy trình quyết định nhóm có quyền và nguồn rõ; không mặc định đọc toàn bộ lịch sử, gửi dồn tin hay tự gán việc."
---

# Telegram từ đề xuất đến việc thực hiện

Thành viên gửi đề xuất chủ động; bot tóm tắt có nguồn, quản trị viên duyệt phương án, nhóm biểu quyết rồi thành viên nhận việc. AI không quyết định thay số phiếu, quản trị viên hoặc người nhận việc.

## Khởi động và quyền

1. Đọc [hợp đồng nhiệm vụ](references/task-contract.md) để xác định chế độ, workspace, scope và hành động đã được phép.
2. Đọc **10/H2**, webhook chung/hợp đồng poll, **12.3, 13 và 14.3** trong [hướng dẫn chuyên môn](references/techstack-guide.md).
3. Scout Bot API adapter, webhook, auth/roles, topic routing, DB/jobs/outbox, poll/task modules và tests; không đọc/in token.
4. Giữ luật nhóm và lựa chọn đã chốt; lập kế hoạch/review không cấp quyền sửa app, inference trả phí, gửi poll/tin hay deploy.
5. Gửi thử thật cần nằm trong quyền đã cấp về bot/nhóm/topic/người nhận và nội dung; không yêu cầu xác nhận lại chỉ vì skill được gọi.
6. Gateway BTC/AI Log/`chung-khao/` chỉ áp bối cảnh BTC; Telegram là kênh truyền tin riêng, không thay AI provider khi lỗi. Đường dẫn đội/vòng phải được xác nhận riêng từ repo thực tế.

## Đầu vào quyết định thiết kế

- Bot/nhóm/topic, chủ bot, admin, token server và người thử được phép; khả năng nhận command/reply/poll/callback phải kiểm bằng quyền bot thật.
- Tài liệu Bot API chính thức hiện hành + adapter/version: webhook header, updates, poll mode và lifecycle; không coi nội dung snapshot là đã verify API.
- Ai được gửi đề xuất, duyệt, biểu quyết, đóng poll, tạo/nhận việc; cách kiểm vai trò khi người dùng mất quyền giữa quy trình.
- Chốt trước mode poll, phiếu ẩn danh hay định danh, eligibility, deadline/timezone, quorum, quy tắc hòa và finality; thiếu luật không tự chọn người thắng.
- Proposal có source message IDs/version, topic, tác giả/scope được phép lưu; dataset thảo luận và kết quả nhóm ý do người kiểm xác nhận.
- Task có trạng thái, điều kiện nhận/hoàn tất, người có quyền cập nhật; chỉ thêm nhắc hạn khi có yêu cầu và đăng ký phù hợp.
- Retention/xóa, log redaction và chính sách nội dung nhóm; chưa đọc toàn bộ lịch sử khi chỉ có quyền nhận đề xuất chủ động.
- Mỗi khoảng trống có owner/gate; thiếu bot thật chặn tích hợp, vẫn làm được contracts/tests local theo phạm vi.

## MVP và ranh giới trách nhiệm

- Nếu chưa chốt, đề xuất một nhóm, hai topic và một vòng đề xuất–duyệt–biểu quyết–nhận việc; đây là phạm vi tham khảo.
- AI nhóm ý trùng, nêu bất đồng và tóm tắt kèm source IDs; không bịa đồng thuận, thay lựa chọn hoặc tự tính phiếu.
- Code xác thực sự kiện/callback, scope, quyền, dedup, count/finality và state; admin duyệt poll, người bấm nút quyết định nhận việc.
- Chỉ đề xuất task từ kết quả đã chốt và duyệt; không tự gán người, không dùng tổng kết LLM làm quyết định chính thức.
- Giữ stack hiện có nếu đủ; backend + DB bền + job/outbox + Bot API adapter đủ cho MVP.

## Contracts và state

- Phân vùng mọi dữ liệu/state bằng `bot_id, chat_id, message_thread_id`; source/callback từ topic khác không tự được nhập vào đề xuất hiện tại.
- `prepare_poll(proposal_ids)` trả `draft_id,payload_hash,expires_at`; lưu source versions, options, mode/rules và scope ở server.
- `approve_poll(draft_id)` kiểm admin hiện tại, payload/version/expiry và quyền gửi; sửa options hay rule phải tạo approval phù hợp phiên bản mới.
- Callback trỏ record server, có hạn và bind người/scope/action hợp lệ; kiểm lại quyền, payload/version, không nhận `approved` từ callback/model.
- `claim_task(task_id)` dùng danh tính người bấm nút và transaction chống tranh nhận/trùng; AI không tự điền assignee.
- Outbox lưu ý định gửi, hash/version và kết quả message/poll ID; một event ghi nhận không có nghĩa poll đã gửi thành công.
- Ngay khi tạo poll trả kết quả, lưu `poll_id → bot_id,chat_id,topic_id,draft_version`; map thiếu phải đối soát trước xử lý update.
- `close_poll(poll_id)` kiểm quyền, đối chiếu poll thực đã đóng rồi lưu snapshot; không báo đóng chỉ vì đã gửi request.
- `get_poll_result(poll_id)` trả `counts,quorum_status,tie_status,finality` và nguồn/snapshot version; chưa final không dùng làm kết quả cuối.
- Nếu dùng tổng phiếu nền tảng, không dựng danh tính người bầu; nếu định danh, upsert lựa chọn hiện tại theo poll/người, xử lý đổi/rút thay vì cộng event.

## Trình tự nhận, duyệt, gửi và chốt

1. Kiểm `X-Telegram-Bot-Api-Secret-Token` theo cấu hình thật, bind bot; unique `(bot_id,update_id)` cho dedup.
2. Ghi event + job trong cùng transaction; ACK sau commit, event trùng ACK nhưng không tạo job mới. AI chạy ở worker bất đồng bộ.
3. Thu command/reply được phép trong đúng topic, tổng hợp kèm nguồn và bất đồng; người duyệt thấy chính options/rules sắp gửi.
4. Kiểm approval hiện tại, ghi outbox và gửi poll bằng adapter; giữ outcome thật và mapping platform IDs.
5. Nhận poll/callback updates, kiểm scope/state và ghi idempotent; không để event cũ làm lùi snapshot hoặc cộng phiếu hai lần.
6. Đến hạn hoặc theo lệnh được phép, đóng/đối soát poll, áp quorum/hòa/finality theo luật đã công bố.
7. Kết quả thiếu/hòa giữ nhánh luật tương ứng; chỉ tạo đề xuất công việc sau finality và approval cần thiết.
8. Thành viên bấm nhận việc, transaction xác nhận người nhận và state; cập nhật tiến độ đúng topic từ dữ liệu đã commit.

## Lỗi và phục hồi

- Timeout tạo poll/gửi tin chưa rõ outcome chuyển pending/unknown, đối soát theo khả năng API; không gửi lại mù hoặc tuyên bố exactly-once ngoài bảo đảm thật.
- Job/outbox recover sau crash trước/sau commit, ACK và side effect; checkpoint không thay nhật ký kết quả/unique constraints.
- Update muộn/thiếu phải đối soát, không ghi đè final bằng snapshot cũ; chưa đủ dữ kiện giữ pending/inconclusive.
- Callback cũ/hết hạn, admin mất quyền hoặc payload đổi: từ chối tác động, cho chuẩn bị phiên bản hợp lệ; không để LLM giải thích thành chấp thuận.
- 401/403/quota/rate limit phân loại đúng, retry một lớp có giới hạn/deadline khi an toàn; không đổi provider/kênh hoặc tự tăng quyền.
- URL Bot API có token trong path chỉ dựng ở backend; che toàn bộ token trong client/proxy/error logs và URL tải file, không đưa ra browser/report.
- Khi hủy hoặc đổi state, kiểm lại revision trước gửi/commit; ghi rõ side effect đã xảy ra nếu không thể thu hồi.

## Oracle và nghiệm thu

- Oracle tóm tắt là message sources có quyền; oracle poll/task là luật đã chốt, platform snapshots và DB, không phải lời LLM.
- Unit/contract kiểm sai header, trùng update/callback, topic chéo, approval cũ, quyền mất, callback hết hạn và tranh nhận việc.
- Poll tests: đổi/rút phiếu, event lặp/muộn, mode không hỗ trợ update cần dùng, quorum thiếu, hòa, close lỗi và kết quả chưa final.
- Integration kiểm crash quanh commit/ACK/send, unknown outcome và recovery; thử nhận/gửi/poll/callback thật chỉ trong scope đã cấp.
- Nguồn gợi ý 20 kịch bản và 90% claim tóm tắt có nguồn; giữ là ngưỡng đề xuất khi chưa chốt, không gọi là chuẩn BTC/đã đạt.
- Mọi bất biến quyền/scope/dedup/finality phải đạt; duyệt trái quyền, lẫn nhóm/topic, phiếu sai hoặc việc trùng chặn bàn giao.
- Báo n, platform/app/content versions, lỗi gửi, latency/cost, nguồn của từng claim và capability chưa kiểm; API 200 không đủ nghiệm thu.

## Bàn giao

- Giao inventory quyền không secret, poll rules đã duyệt, contracts/state, outbox recovery runbook, oracle và demo vòng hoàn chỉnh đúng topic.
- Phân biệt offline, tích hợp thật và nghiệm thu; với kế hoạch nhiều phase dùng [hợp đồng kế hoạch](references/planning-handoff.md), nêu owner và gate cho mọi đầu vào còn thiếu.
