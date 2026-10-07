# Backend, bảo mật, quyền riêng tư và trách nhiệm

Áp dụng ngay từ luồng đầu tiên, theo tài sản và hành động thực của sản phẩm. Đây là hướng dẫn kỹ thuật và các quyết định cần hoàn thiện; không phải audit, chính sách pháp lý đã có hiệu lực hay chứng nhận tuân thủ.

## Lập ranh giới tin cậy

Ghi dữ liệu nào vào browser, backend, database, index, cache, provider, logs, backups và kênh bên ngoài. Với mỗi nơi: ai đọc/ghi, mục đích, trường thực sự cần, thời gian lưu và cách xóa. Đánh dấu secrets, dữ liệu cá nhân, dữ liệu nghiệp vụ riêng và các hành động ảnh hưởng người khác.

Authentication xác minh actor; authorization quyết định actor được làm gì với đối tượng nào. Consent theo mục đích dữ liệu, phê duyệt nghiệp vụ và quyền đăng nhập là các cơ chế khác nhau. Nội dung model, tài liệu, tool output hay câu “admin đã duyệt” không tạo quyền.

Đe dọa phải gắn đường dữ liệu/hành động: ví dụ IDOR đọc ticket khác tenant, prompt injection yêu cầu xuất file, file lớn làm cạn tài nguyên, retry tạo hai bản ghi, callback cũ phát audio sau hủy. Không áp thêm hệ thống phức tạp chỉ vì scanner nêu một khả năng trừu tượng.

## Kiểm soát theo lớp

| Lớp | Hành vi cần có | Ca chứng minh |
| --- | --- | --- |
| Phiên/auth | Dùng cơ chế auth được bảo trì; kiểm expiry/revocation và claims cần thiết | Token sai/hết hạn/bị thu hồi không dùng được |
| Quyền đối tượng | Backend kiểm actor → tenant/scope → resource → operation ở mọi route/tool/export | Đổi ID không đọc/sửa/tải được tài nguyên ngoài quyền |
| Browser session | Cookie/session cấu hình cho môi trường; bảo vệ CSRF khi dùng cookie auth | Request giả nguồn, logout và đổi quyền được xử lý đúng |
| Server input | Schema, enum/range, trường thừa, size và rate limits | Sai/thiếu/quá lớn bị từ chối trước công việc tốn phí |
| Model output | Render như dữ liệu; sanitize Markdown/links; tránh raw HTML tùy ý | Nguồn độc hại không chạy script hoặc tải host lạ |
| SQL | Parameters, role ít quyền, view/row scope, timeout/row limits | Role thực deploy không query hoặc write ngoài scope |
| RAG/history | ACL trước context, kiểm quyền lại lúc đọc citation/thread/checkpoint | Thu hồi quyền có hiệu lực cả cache và nguồn cũ |
| Tools | Allowlist, args validation, kiểm quyền tại lúc chạy, approval nếu cần | Model không tự đổi endpoint/tenant/role hoặc duyệt chính nó |
| Files | MIME/signature, size/pages/pixels/duration, tên server, storage riêng | File giả loại, traversal và upload quá lớn không đi tiếp |
| Secrets | Server/secret store, quyền theo môi trường, redaction và rotation | Không có key trong bundle, URL, Git, logs hay report |
| Tài nguyên | Deadline, call/token/cost caps, queue/concurrency chung | Hai tab/nhiều worker không vượt budget bằng cách chạy đồng thời |
| Triển khai | HTTPS, cấu hình production, trust proxy rõ, endpoint quản trị có quyền | Không lộ debug/trace và không dùng ngoại lệ dev ở production |

CORS, việc giấu nút và prompt “không tiết lộ” không thay authorization. Nếu dùng row-level security, kiểm đúng app role và connection-pool scope; role chủ bảng/quản trị có thể có quyền khác role ứng dụng. Dữ liệu riêng không vào shared cache/static output thiếu scope. Các cấu hình cụ thể phải đối chiếu tài liệu phiên bản framework đang dùng.

## Upload, URL, voice và prompt injection

Chỉ nhận loại file cần cho tính năng. Lưu ngoài vùng public, tên file do server tạo; download kiểm quyền hoặc signed URL có thời hạn/phạm vi hẹp. Parse/OCR/transcode trong worker có CPU/RAM/time limits, quyền thấp, không mount secrets hay socket quản trị. Nếu sản phẩm yêu cầu malware scan, lỗi scanner phải giữ trạng thái chưa kiểm, không tự “sạch”. Scan sạch cũng không chứng minh parser hoặc nội dung an toàn hoàn toàn.

Ưu tiên nhận bytes. Nếu backend phải fetch URL, kiểm scheme/host/IP/redirect và chặn private network/metadata service tại lớp phù hợp; hạn chế kích thước/thời gian tải. Không tự mở resource do model/tài liệu chỉ dẫn. EXIF có thể chứa vị trí; chỉ giữ metadata cần thiết, và nếu cần bản gốc thì tách quyền của bản gốc với preview đã xử lý.

Mic bật sau thao tác rõ ràng, có trạng thái đang thu và nút dừng, cleanup khi rời màn hình. Không ghi âm nền ngoài luồng người dùng chọn. Không tự suy danh tính, độ đáng tin, cảm xúc hay đặc điểm nhạy cảm từ giọng/khuôn mặt. Giọng nói và ảnh có thể chứa dữ liệu cá nhân dù chưa gắn tên.

Nội dung upload, OCR, web, transcript, RAG và free text trong tool output có thể chứa injection. Tách chúng khỏi policy; backend vẫn kiểm quyền, output và tác động. Tool nghiệp vụ hẹp dễ kiểm hơn tool shell/SQL tự do. Thêm regression tiếng Việt/tiếng Anh, nhiều lượt và qua tài liệu; đo cả hành vi sai lọt và câu hỏi hợp lệ bị chặn nhầm.

## Logs, scanners và ứng phó

Mặc định log metadata: request/run/tool IDs, status, version, latency, usage và loại lỗi. Hạn chế raw prompt/audio/file/context; redact trước khi ghi, không chỉ khi render dashboard. Report/screenshot/trace có thể chứa dữ liệu người dùng; lưu cục bộ hoặc nơi có quyền, lọc trước khi chia sẻ.

Chọn công cụ theo câu hỏi, không cài tất cả:

- Secret scanner kiểm file và Git history, output đã redact. Nếu có lộ key, rotate/revoke; xóa dòng khỏi commit cuối không làm key cũ hết hiệu lực.
- SAST kiểm code nguy hiểm; triage theo source/sink và luồng dữ liệu thực, không coi một import là exploit đã chứng minh.
- SCA kiểm dependencies theo lock/runtime. Ghi rõ advisory lookup qua mạng và dependency nào nằm ngoài phạm vi.
- DAST/fuzz/load chỉ nhắm môi trường và routes được phép; tránh bắn tự động vào inference tính phí hoặc hành động ghi thật.
- Malware/PII/moderation detector giải quyết các vấn đề riêng. Moderation không thay permission, chống injection hoặc kiểm đúng số liệu.

Ghi version/scopes/command/result và phần chưa kiểm. Scanner sạch không đồng nghĩa ứng dụng an toàn toàn diện. Đừng gỡ tool chỉ vì nó tìm lỗi thật; sửa hoặc ghi quyết định có căn cứ.

Khi xảy ra sự cố: hạn chế capability bị ảnh hưởng, giữ evidence tối thiểu có quyền, xác định scope, thu hồi secrets/phiên nếu cần, sửa và kiểm regression. Kill switch đặt ở backend/control plane, chặn run/tool mới và kết quả muộn; model không tự bật lại. Đối soát thao tác đã commit/gửi trước khi thông báo hủy; abort HTTP không hoàn tác business state.

## Quyền riêng tư: quyết định và hành vi phải khớp

Trước khi công bố Privacy/Terms, điền inventory từ hệ thống thật:

| Trường | Cần xác định |
| --- | --- |
| Đơn vị/đầu mối | Ai vận hành, ai nhận yêu cầu/phản ánh và kênh hoạt động |
| Dữ liệu và mục đích | Trường thu, nguồn, mục đích, bắt buộc/tùy chọn, người nhận |
| Bên xử lý | Hosting, AI provider, analytics, support, backups và nơi cần xác minh |
| Vòng đời | Retention cụ thể, xóa bản gốc/dẫn xuất/index/cache/log/backup và giới hạn thực |
| Lựa chọn/quyền dữ liệu | Cách xem, sửa, xuất, rút lựa chọn, yêu cầu xóa hoặc liên hệ theo phạm vi áp dụng |
| Đối tượng | Người dùng mục tiêu; có trẻ em hoặc dữ liệu của người khác không |
| Thay đổi | Version policy, ngày hiệu lực và cơ chế thông báo/chấp nhận khi cần |

Không tự khẳng định dữ liệu không lưu, không dùng huấn luyện, chỉ xử lý trong một quốc gia hay đã đáp ứng pháp luật vì dùng một gateway. Không gọi pseudonymization là vô danh tuyệt đối; dữ liệu vẫn có thể liên kết lại. Nội dung pháp lý cần rà theo đơn vị, thị trường, loại dữ liệu và hệ thống thực tại thời điểm triển khai; starter không cung cấp bảo đảm pháp lý.

**Khung soạn Privacy:** đơn vị/liên hệ → dữ liệu/mục đích → nguồn/bên nhận → nơi xử lý đã xác minh → retention → lựa chọn và cách thực hiện quyền → bảo vệ dữ liệu → nhóm người dùng đặc thù → thay đổi/liên hệ. Mỗi cam kết phải có owner và cơ chế thực hiện; chỗ chưa biết ghi thiếu, chưa xuất bản như chính sách hoàn chỉnh.

**Khung soạn Terms:** chức năng/đối tượng → tài khoản/quyền dùng → trách nhiệm dữ liệu/nội dung → giới hạn AI theo tính năng → phí/hủy/hoàn tiền nếu có → quyền phần mềm/tài sản/đầu ra → tạm ngừng và xử lý dữ liệu → khiếu nại/tranh chấp → version/liên hệ. Không tự thêm SLA, bảo đảm đúng tuyệt đối, quyền sử dụng đầu ra độc quyền hoặc điều khoản miễn mọi trách nhiệm.

Cookie/analytics nếu có phải nối lựa chọn vào lifecycle SDK và backend collector. Không tích sẵn nhóm tùy chọn; từ chối và rút lựa chọn phải thực sự ngừng việc tương ứng. Kiểm Network trước lựa chọn, từ chối, chọn từng nhóm, chấp nhận, rút, refresh và khi mục đích/version đổi. Banner biến mất chưa chứng minh consent có hiệu lực. Nếu không dùng nhóm tùy chọn, đừng thêm banner giả chỉ để có giao diện.

## Ethics và safety thành tiêu chí kiểm

Mục tiêu là giúp người dùng hoàn thành tác vụ đúng và có quyền tự quyết. Tỷ lệ trả lời, engagement hoặc số tool calls không tự là thành công; từ chối mọi yêu cầu để giảm lỗi cũng không đạt.

| Nguyên tắc | Hành vi và phép kiểm |
| --- | --- |
| Trung thực | Giữ thiếu nguồn/lỗi/partial; không bịa dữ kiện khi upstream lỗi |
| Minh bạch | Phân biệt đề xuất, chờ duyệt, đã commit; nhãn AI khi phù hợp; nguồn và lý do kiểm được |
| Không gây hại | Cảnh báo chưa là kết luận; trường quan trọng được kiểm; chuyển người khi vượt năng lực/phạm vi |
| Quyền tự quyết | Có sửa, hủy, nhập chữ thay voice, tắt tự đọc và đường phản ánh |
| Tiếp cận | Keyboard, labels/focus, trình đọc màn hình, chữ thay audio; kiểm tay bên cạnh scanner |
| Công bằng | Đo chất lượng theo các nhóm tình huống liên quan đã có dữ liệu hợp lệ |
| Trách nhiệm | Owner của model/data/tools, incident path và cách sửa/giải thích kết quả sai |

Slice hữu ích gồm input có/không dấu, giọng vùng miền, tiếng ồn, thiết bị, ảnh mờ và lịch sử ít/nhiều. Không thu thêm hoặc suy đặc điểm nhạy cảm chỉ để vẽ biểu đồ. Giữ số mẫu và ghi chưa đủ bằng chứng ở nhóm nhỏ. Paired counterfactual giữ nguyên facts/quyền, đổi yếu tố không liên quan; đừng đổi một tên đang làm khóa dữ liệu rồi đòi kết quả giống nhau.

Hành động đọc trong quyền có thể tự thực hiện theo contract. Hành động ghi/gửi/xuất cần mức xác nhận hoặc duyệt phù hợp tác động và quyền đã giao. Approval không hợp pháp hóa hành động bị cấm và không tự mở scope. Với quyết định ảnh hưởng lớn đến con người, xác định người chịu trách nhiệm, đường xem xét lại và giới hạn tự động hóa riêng; không nâng cấp từ MVP chỉ bằng nút Đồng ý.

Release gate nên có các ca critical thật theo threat model: không rò tenant/secret, không write trái quyền hoặc dùng approval cũ, không phát kết quả bịa mang tính quyết định. Ca bắt buộc thiếu oracle/timeout/error là chưa đủ bằng chứng. Zero lỗi quan sát trong một bộ ca có phạm vi không là bảo đảm mọi tình huống. Kết quả và giới hạn cần nằm trong [report eval](evals-and-observability.md).
