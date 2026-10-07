---
name: ai-safety-privacy
description: Thiết kế hoặc rà soát safeguards, quyền truy cập, chống prompt injection và vòng đời dữ liệu khi người dùng yêu cầu bảo mật, an toàn AI hoặc quyền riêng tư; không tự kích hoạt audit toàn diện cho mọi thay đổi code.
---

# An toàn AI và quyền riêng tư theo dữ liệu thật

Bảo vệ dữ liệu và hành động thực tế của sản phẩm; tách quyền truy cập, tính đúng chuyên môn và hiệu lực nguồn.
Không mở rộng thành chứng nhận tuân thủ pháp luật hoặc đổi quyết định sản phẩm chỉ vì lo ngại chưa có bằng chứng.

## Xác định nhiệm vụ trước khi kiểm

1. Đọc [hợp đồng tác vụ](references/task-contract.md) và [trích nguồn techstack](references/techstack-guide.md), trọng tâm phần 13.
2. Xác định người dùng đang yêu cầu thiết kế, review hay triển khai sửa; review thuần túy không tự trở thành lệnh thay sản phẩm.
3. Scout routes, auth, tools, DB, upload/fetch, render, logs, telemetry, lưu/xóa dữ liệu và docs liên quan trong scope đã giao.
4. Liệt kê tài sản được bảo vệ, actor/tenant/role, đường dữ liệu, hành động có hệ quả và biên tin cậy thực tế.
5. Ghi dữ kiện đã kiểm, giả định, nguồn chưa có và phạm vi không áp dụng; không thêm hệ thống chỉ để điền checklist.
6. Với kế hoạch dùng [hợp đồng bàn giao](references/planning-handoff.md); với review trả vị trí, bằng chứng, ảnh hưởng và cách tái hiện.
7. Giữ quyền và lựa chọn đã chốt; chỉ xin quyết định khi cần đổi phạm vi/quyết định người dùng hoặc thiếu quyền thực sự.

## Contract an toàn cần thiết kế

- Lập ma trận hành động: dữ liệu đọc/ghi, ai bị ảnh hưởng, tác động, khả năng khắc phục, quyền, điều kiện và người quyết định.
- Backend cấp identity/scope, version, trạng thái và quyền; browser/LLM không được tự xác nhận facts cấp quyền.
- Safety gate nhận capability bật/tắt, run/revision hiện hành, quyền, mục đích dữ liệu và evidence `ready/partial/missing/stale/error`.
- Thiếu field/sai kiểu cần chặn phần có hệ quả; gate chọn trả đầy đủ/một phần, hỏi lại, cập nhật nguồn, thiếu căn cứ, lỗi dịch vụ hoặc chặn.
- Kiểm lại sau khoảng chờ và trước commit/UI/TTS/export; buffer phần có hệ quả nếu chỉ kiểm được sau khi sinh toàn output.
- Approval gắn payload/version/expiry; reject/timeout không thành đồng ý, và người duyệt không hợp lệ hóa hành động bị cấm.
- Cảnh báo ở cuối không thu hồi dữ liệu đã stream hoặc side effect đã chạy; kiểm nơi phát dữ liệu và công cụ thực thi.

## Kiểm bề mặt thực sự tồn tại

| Bề mặt | Invariant và phép kiểm |
|---|---|
| Secret | Chỉ server đọc cấu hình; bundle, URL giao người dùng, repo, error và report không chứa credential |
| Object riêng | Auth từng object/trường; thử A đọc/sửa file, thread, ticket, answer của B phải bị chặn |
| DB | Least privilege, parameterized SQL; scope tenant do server; RLS thử bằng app role thật, không role bypass |
| Upload | Kiểm MIME nội dung, size/duration/pages, filename ngẫu nhiên, sandbox; file giả/hỏng/traversal không tới inference |
| URL fetch | Kiểm allowlist/scheme/IP/redirect/size; chặn đích nội bộ/metadata và redirect ngoài phạm vi |
| Output | Schema + business validation; text/Markdown an toàn, HTML chỉ khi cần và đã sanitize bằng allowlist |
| Tool ghi | Auth, payload/version, transaction/idempotency; stale approval, callback lặp hoặc sai người không tạo tác động |
| Webhook | Kiểm cơ chế xác thực nền tảng, scope và dedup; event sai signature, trễ/lặp/sai chat không làm sai state |
| Web session | Backend auth, cookie phù hợp HTTPS, CSRF khi dùng cookie-auth write; CORS không thay auth |
| Resource | Cap token/tool loop/concurrency/deadline/quota; input lớn hoặc vòng lặp không vượt budget được cấp |
| Log/trace | Redaction, quyền xem, retention; không chia sẻ raw tài liệu riêng/PII/secret |

- Không chữa frontend bằng wildcard origin kèm credentials; không chèn HTML model vào DOM chưa xử lý.
- Với JWT, kiểm chữ ký/issuer/audience/expiry; private cache không dùng chung giữa người dùng; tenant pool context giới hạn transaction.
- Worker parser/OCR/FFmpeg có cap CPU/RAM/time, không mount secret hoặc Docker socket.
- Telegram token trong path chỉ do backend dựng; redact cả request/error/proxy và URL tải file, không truyền URL đó cho client.

## Chống prompt injection theo hành vi cuối

1. Tách policy khỏi nội dung không tin cậy trong PDF, ảnh, transcript, tên file, retrieval, tin nhắn và tool output.
2. Cấp context tối thiểu đúng quyền, tool allowlist hẹp và schema kiểm được.
3. Backend kiểm quyền, business invariants, version và phạm vi trước mọi tác động dù model bỏ qua chỉ dẫn.
4. Dùng canary giả trong harness cô lập; thử đọc chéo, tool bị cấm, exfil qua URL, stream/TTS/export và injection vào judge.
5. Chấm lộ dữ liệu/hành động thật, false refusal và evidence sai; không lấy nhãn “an toàn” hoặc câu cuối từ chối làm oracle.
6. Ghi đường nguồn → context → tool/output → nơi nhận và lớp chặn; thiếu oracle/timeout hạ tầng là inconclusive.

## Vòng đời dữ liệu và quyền lựa chọn

- Lập bảng từng loại dữ liệu: mục đích, nguồn, nơi lưu/xử lý, bên nhận, quyền truy cập, retention, mốc TTL và cách xóa.
- Bao gồm file gốc, audio/transcript, chunk/vector, history/checkpoint, cache, TTS/export, log/trace, eval copy và backup.
- Theo dõi quan hệ source → dữ liệu dẫn xuất để xóa/thu hồi thật; sau restore áp lại danh sách xóa trước phục vụ.
- Kiểm tải/truy hồi qua index/cache cũ bị chặn; embedding/hash/pseudonym không tự làm dữ liệu vô danh.
- Thông báo phản ánh operator/kênh liên hệ thật, loại/mục đích dữ liệu, bên xử lý, retention, xem/sửa/xóa và giới hạn thực tế.
- Retention/training của provider chưa xác nhận phải ghi chưa xác minh; không hứa không lưu/không huấn luyện theo suy đoán.
- Quyền micro khác quyền lưu lâu dài/cải thiện sản phẩm; tách thông báo thu âm, lựa chọn mục đích phụ và approval một tool ghi.
- Đối tượng trẻ em/học sinh cần chủ sản phẩm chốt cơ chế phù hợp; không tự thu giấy tờ hoặc dữ liệu nhạy cảm cho demo.
- Nếu chỉ có storage thiết yếu, mô tả đúng; không thêm tracker để có banner.
- Nếu có analytics tùy chọn: chưa chọn thì chưa khởi tạo SDK; từ chối vẫn dùng chức năng chính; cho rút dễ như cho phép.
- Gate cả server events; record thiếu/hỏng, mục đích mới chưa chọn đều giữ xử lý tùy chọn tắt.
- Lưu mục đích, lựa chọn, notice version, server time và rút lựa chọn; refresh không tự bật lại, rút phải dừng SDK/storage liên quan.
- Điều khoản nêu chức năng/quyền/hạn chế AI/hỗ trợ thật; không tự thêm giá, hoàn tiền, SLA hay miễn mọi trách nhiệm.
- Khi cần kết luận luật hiện hành, kiểm nguồn chính thức đúng thị trường/ngày và nhờ chủ sản phẩm chốt; không bịa hạn pháp lý hoặc chứng nhận.

## Công cụ và giới hạn egress

- Chọn scanner đúng stack/scope: secret, static code, dependency, container hoặc passive web; không cài cả bộ mặc định.
- Kiểm rules/advisory/telemetry và nơi gửi dữ liệu trước chạy; không tải source hoặc dữ liệu riêng lên scanner cloud chưa được phép.
- Active scan hệ thống dùng chung/kênh thật cần phạm vi được giao rõ; kiểm local được phép không tự mở rộng sang hệ thống ngoài.
- Xác minh finding theo đường thực thi và tái hiện; không sửa chỉ vì tên rule, tắt rule hoặc hạ severity để làm report sạch.
- Kiểm PII recognizer tiếng Việt nếu dùng; `language=vi` hoặc malware scan sạch không chứng minh dữ liệu/parser đã an toàn.
- Model guardrail/judge dùng đúng provider được phép; BTC không có fallback AI ngoài gateway. Không thêm moderation/tracing cloud trái phạm vi.

## Nghiệm thu, khắc phục và bàn giao

- Chốt yêu cầu → bề mặt/file → case → oracle → điều kiện đạt; case auth/state theo hai người dùng quan trọng hơn điểm scanner.
- Bộ an toàn bắt buộc không rỗng, đã chạy và đủ oracle; mọi vi phạm invariant đã thấy chặn phát hành phần liên quan.
- Kiểm consent trước/chấp nhận/từ chối/rút/refresh; kiểm deletion cả bản dẫn xuất, cache/index và sau restore.
- AI không suy danh tính/sức khỏe/cảm xúc/phẩm chất từ giọng/ảnh ngoài mục đích và căn cứ; hiển thị vai trò AI phù hợp.
- Đo false refusal, bỏ sót tác vụ và nhóm thiết bị/ngôn ngữ phù hợp; mẫu thiếu ghi chưa đủ kết luận.
- Sự cố: kill switch backend chặn dispatch/commit, giữ bằng chứng tối thiểu, đối soát side effect và sửa riêng; abort không hoàn tác ghi đã commit.
- Xác minh nghĩa vụ thông báo theo sự cố/thị trường hiện hành, không áp deadline tự đặt; có owner xử lý theo run/result ID.
- Sau sửa chạy lại ca tái hiện và regression phù hợp; báo rõ chưa kiểm thay vì chuyển thành pass.
- Giao threat/data-flow summary, findings đã xác minh, non-issues có nguồn, contracts, test evidence và các quyết định còn chờ owner.
- Phân biệt kế hoạch, kiểm offline, integration và trạng thái phát hành; giữ quyết định đã xác minh trừ khi có bằng chứng mới.
