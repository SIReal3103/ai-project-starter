<!-- Generated from cac-huong-phat-trien-san-pham-dua-vao-techstack.md; sections 18.9, 18.10, 18.11, 21; sha256 2d4568876ea8e3aa86447c9e668b647ab3840eb9decded38b3ba4f5d1ad334dc. Edit the source and run scripts/sync-skills.py. -->

Phần BTC chỉ áp dụng khi nhiệm vụ thuộc bối cảnh BTC; đường dẫn đội/vòng cần được xác nhận riêng. Model/API, budget và ngưỡng trong nguồn là snapshot hoặc đề xuất, không chứng minh quyền/capability/kết quả hiện tại.

### 18.9 Hợp đồng kế hoạch cho agent chưa có context

Đầu ra lập kế hoạch phải là một gói có thể đọc mà không cần lịch sử hội thoại. Không viết "theo trao đổi", "như trên" hoặc chỉ trỏ về đề trong chat. Nhắc lại yêu cầu và quyết định đã chốt; đưa bằng chứng vào đúng chỗ người thực hiện cần. Có thể dẫn nguồn sâu hơn, nhưng không để các quyết định cốt lõi chỉ nằm trong tài liệu ngoài gói.

Nếu được yêu cầu lưu kế hoạch, hoặc đang làm việc trong repo với quy ước lưu kế hoạch, dùng:

~~~text
plans/<timestamp>-<descriptive-slug>/
  plan.md
  phase-01-<name>.md
  phase-02-<name>.md
  reports/                 # chỉ tạo báo cáo khi đã kiểm/đo
~~~

Giữ `plan.md` ngắn: bối cảnh, trạng thái, mục tiêu/kết thúc, phạm vi, quyết định, ma trận nghiệm thu, phụ thuộc và thứ tự đọc phase. Có thể dùng `context.md` hoặc `contracts.md` khi đủ lớn để tách; chúng phải được liên kết từ điểm vào và là một phần của gói bàn giao. Với yêu cầu chỉ trả lời trong chat, giữ cùng nội dung thiết yếu trong câu trả lời, không tự tạo file hoặc yêu cầu cài skill. Không ép số phase cố định.

Gói cần chứa đủ các nhóm sau; mục không áp dụng phải nêu lý do ngắn, không tạo thêm hệ thống chỉ để điền bảng:

| Nhóm | Nội dung phải cụ thể hóa |
|---|---|
| Brief độc lập | Đề đầy đủ hoặc bản diễn giải giữ đủ điều kiện bắt buộc; chính thức/giả định; người dùng, tác vụ, điểm bắt đầu/kết thúc, đầu ra được dùng để làm gì |
| Workspace | Repo/nhánh thực tế nếu đã kiểm; root và cách giải quyết đường dẫn; hướng dẫn cần đọc trước; file/module hiện có so với file dự kiến; phạm vi được sửa và thay đổi cần giữ |
| Phạm vi và quyền | Bắt buộc, tùy chọn, hoãn; hành động đã được cấp quyền; ai đọc/ghi/duyệt; không tự đổi hỗ trợ quyết định thành tự động quyết định |
| Inventory bằng chứng | Mỗi dữ liệu, tài sản, dịch vụ: vị trí hoặc cách nhận, schema/định dạng, nguồn/phiên bản/hiệu lực, owner, quyền, trạng thái có thật/được hứa/giả định/chưa kiểm |
| Quyết định và khoảng trống | Yêu cầu xác nhận, quan sát từ repo, lựa chọn thiết kế và giả định tách riêng; mỗi câu hỏi có người trả lời, bằng chứng cần lấy, phase phụ thuộc và việc vẫn làm được |
| Luồng và contracts | Input/output, state và nhánh thiếu/lỗi/hủy; phần AI đề xuất, code kiểm/tính, con người quyết định; nguồn sự thật và bất biến có hệ quả |
| Kiến trúc tối thiểu | Bước xử lý → component → lý do → dữ liệu/quyền → cách kiểm → phương án khi lỗi; giữ stack hiện có nếu đáp ứng |
| Thực hiện | Phase có điều kiện vào/ra, files, các bước theo phụ thuộc, validation, rủi ro và rollback phù hợp; điểm dừng khi đầu vào bắt buộc chưa có |
| Nghiệm thu và bàn giao | Yêu cầu → bằng chứng → oracle → tiêu chí đạt; lỗi chặn bàn giao; cách chạy/demo, đầu ra cần nộp và giới hạn cần báo |

**Ma trận truy vết** là phần bắt buộc của kế hoạch thực thi. Mỗi yêu cầu bắt buộc có ít nhất một hàng, không chỉ một danh sách "chạy tests":

| Yêu cầu và nguồn | Hành vi/đầu ra quan sát được | Phase/file chịu trách nhiệm | Case hoặc phép đo | Oracle và điều kiện đạt | Trạng thái/phụ thuộc |
|---|---|---|---|---|---|
| Điều kiện từ đề hoặc quyết định đã xác nhận | Input cụ thể dẫn tới trạng thái hoặc artifact nào | File hiện có hoặc dự kiến, ghi rõ | Ca thường và ca lỗi có liên quan | Đáp án/luật/người kiểm độc lập; ngưỡng là đã chốt hay đề xuất | Sẵn sàng kiểm, cần dữ liệu, chưa có oracle... |

ID yêu cầu chỉ phục vụ truy vết trong kế hoạch, không đưa vào tên hàm/test/migration. Không tự đặt KPI rồi gọi là chuẩn BTC hoặc kết quả thật. Chỉ số mềm chưa có baseline cần có cách đo, người chốt ngưỡng và mốc chốt trước holdout. Thiếu oracle cho yêu cầu bắt buộc là phụ thuộc nghiệm thu chưa giải quyết, không phải pass.

**Mỗi phase là một hướng dẫn làm việc:**

~~~text
Mục tiêu và đầu ra được dùng ở bước nào:
Đọc trước: đường dẫn trong gói + file repo/đoạn nguồn liên quan.
Điều kiện vào: dữ liệu, capability, quyết định và phase trước cần có.
Files: đọc / sửa / tạo; ghi hiện có hoặc dự kiến. Không tạo tên file như đã tồn tại.
Contracts: input/output/errors/state/quyền/bất biến liên quan, hoặc link tới mục cụ thể trong gói.
Các bước: hành động theo thứ tự, tích hợp và phần có thể làm độc lập.
Kiểm: case, oracle, lệnh chạy tại thư mục nào, bằng chứng lưu ở đâu.
Điều kiện ra: hành vi/artifact có thể kiểm; ai quyết định khi cần nghiệp vụ.
Khi lỗi hoặc thiếu đầu vào: nhánh nào dừng, ai cần trả lời, nhánh nào tiếp tục.
Rủi ro và rollback: cách giữ/khôi phục dữ liệu và thay đổi của phase nếu có tác động.
~~~

Lệnh chưa có script hoặc dependency phải ghi **dự kiến, chưa chạy**, cùng phase tạo điều kiện cho lệnh đó. Không viết lệnh mẫu thành kết quả kiểm chứng. Nếu chưa biết repo, dùng `PROJECT_ROOT: chưa xác định` và bước tìm/xác nhận root; không để đường dẫn máy người lập kế hoạch trở thành phụ thuộc của agent nhận việc.

### 18.10 Dữ kiện chưa có, capability và tiêu chí sẵn sàng

Không ép mọi kế hoạch thành "sẵn sàng triển khai". Tách mức đầy đủ của kế hoạch khỏi trạng thái sản phẩm. Dùng một trạng thái trung thực:

- **Sẵn sàng triển khai:** các đầu vào bắt buộc để bắt đầu đã kiểm, contracts và quyền đủ rõ; phase đầu có việc chạy được. Những capability chưa kiểm phải có gate trước phase sử dụng và không được mô tả là đã có.
- **Sẵn sàng một phần:** chỉ rõ các phase có thể bắt đầu, các phase phụ thuộc còn bị chặn và điều kiện mở chúng.
- **Cần quyết định/đầu vào:** chưa có phần triển khai hữu ích có thể bắt đầu; bàn giao câu hỏi có owner và phép kiểm để gỡ, không xây giả để thay thế.

Với mỗi khoảng trống trọng yếu, ghi: điều chưa biết → bằng chứng cần → ai cung cấp/kiểm → timebox hoặc ngân sách nếu có → phase bị ảnh hưởng → hành động sau đạt/không đạt. Scout file và docs trước khi hỏi. Thiếu preference có thể dùng giả định dễ đảo ngược được ghi rõ; thiếu quyền, luật nghiệp vụ hoặc dữ liệu quyết định kết quả thì không tự điền.

Các contracts phải đủ để tránh quyết định thay người dùng:

- **Data:** entity, khóa và quan hệ, trường bắt buộc, kiểu/đơn vị/múi giờ nếu liên quan, null/unknown, nguồn sự thật, provenance, quyền và vòng đời. Phân biệt lời khai, kết quả trích xuất và dữ kiện đã đối chiếu.
- **Business rules:** điều kiện, ngoại lệ, thứ tự ưu tiên, nguồn và mốc hiệu lực. Không lấy ngày upload làm ngày hiệu lực hoặc tự chọn mốc tính hạn. Trường hợp chưa đủ căn cứ phải có trạng thái riêng, không ép thành đúng/sai.
- **Tool/action:** schema input/output/errors, scope từ server, side effect, timeout/retry và quyền. Nếu có xác nhận thì gắn payload/version; mô tả chống trùng và cách xử lý kết quả chưa biết sau lỗi mạng.
- **State/UI:** ai được chuyển trạng thái, sửa/hủy/đổi ý ảnh hưởng kết quả cũ thế nào, khi nào UI được báo hoàn tất và cách người dùng sửa sai. Mã đối tượng hoặc ảnh chứng từ không tự thay danh tính/quyền.
- **Capability:** documented/untested/verified/failed/unavailable, bằng chứng và ngày kiểm. Mỗi năng lực bắt buộc có phép thử nhỏ, kết quả mong đợi và hành động nếu không đạt. Workflow thay agent chỉ hợp lệ nếu vẫn đáp ứng đề và được mô tả đúng; thiếu modality bắt buộc phải báo chưa đáp ứng.

Nêu giả định của timebox: đã có boilerplate/data/account hay phải làm từ đầu. Chừa thời gian kiểm và tích hợp. Khi thời gian không đủ, hoãn phần tùy chọn; nếu phải cắt yêu cầu bắt buộc hoặc đảo quyết định người dùng thì đưa trade-off và chờ quyết định, không tự tuyên bố hoàn tất phạm vi nhỏ hơn.

### 18.11 Tự kiểm kế hoạch bằng cách bỏ lịch sử chat

Trước bàn giao, chỉ dựa vào gói đầu ra và những file được dẫn rõ để trả lời:

1. Đề nào, chính thức hay giả định, ai sử dụng, đầu ra nào chứng minh xong? Có yêu cầu bắt buộc bị bỏ hoặc tính năng ngoài phạm vi bị thêm không?
2. Agent biết bắt đầu ở root/file/phase nào và hành động đầu tiên là gì không? Đường dẫn, file và lệnh nào đã kiểm, cái nào dự kiến?
3. Có phân biệt dữ liệu tồn tại với lời hứa cung cấp, và capability có tài liệu với capability đã chạy không? Có secret hoặc phụ thuộc chỉ tồn tại trên máy tác giả không?
4. Mỗi yêu cầu bắt buộc có phase, phép kiểm, oracle và điều kiện đạt không? Có ca thiếu/mơ hồ và lỗi/hủy phù hợp, không chỉ happy path?
5. AI/code/con người có ranh giới quyết định rõ không? State, quyền, phiên bản và side effect có đủ contract cho điểm có hệ quả không?
6. Mỗi khoảng trống có người giải quyết, điều kiện mở, nhánh bị chặn và việc tiếp tục được không? Có âm thầm đổi provider, bỏ modality hoặc tự tạo luật không?
7. Chỉ số/ngưỡng/timebox là dữ kiện hay đề xuất? Lỗi chặn bàn giao và giới hạn chưa kiểm có được giữ lại trong báo cáo không?
8. Agent biết cần bàn giao file, cách chạy, demo và bằng chứng gì; quyền commit/push/deploy có được giữ đúng không?

Nếu bất kỳ câu nào còn buộc người đọc đoán quyết định trọng yếu, sửa kế hoạch hoặc ghi rõ phụ thuộc và hạ trạng thái sẵn sàng. Không dùng tổng điểm đẹp để bù thiếu quyền, nguồn hoặc oracle. Với nhiệm vụ phức tạp và có công cụ delegation, có thể cho agent không nhận lịch sử chat đọc thử gói; chỉ đưa đề gốc, gói kế hoạch và tài sản được phép. Không coi kiểm Markdown/heading là bằng chứng agent làm đúng.

Ví dụ kiểm phạm vi với đề đổi trả: ảnh tai nghe có thể cho biết nhãn/ngoại quan, không xác nhận lỗi mất tiếng; tạo phiếu tiếp nhận không đồng nghĩa duyệt hoàn tiền; đổi từ "đổi" sang "trả" phải đánh giá lại điều kiện và phiên bản đề xuất. Đây là minh họa cách suy ra contracts từ đề, không phải tính năng mặc định cho mọi sản phẩm.

## 21 Lệnh giao việc độc lập cho agent

Đoạn dưới dùng cho đề mới và ý tưởng đã chọn. Điền từ yêu cầu hiện tại và bằng chứng đọc được; không buộc người dùng tự điền mọi ô trước khi agent có thể làm việc. Nếu không tìm được thông tin, ghi "chưa xác định" cùng cách giải quyết, không giữ ô trống như dữ kiện đã có. Agent lập kế hoạch phải chuyển thông tin này thành gói ở phần 18.9, không chỉ chép lại biểu mẫu.

~~~text
Vai trò: agent lập kế hoạch hoặc phát triển sản phẩm AI theo phạm vi được giao.

Chế độ: <khám phá / lập kế hoạch / review kế hoạch / triển khai>.
Bối cảnh: <dự thi BTC / dự án khác; đội/chủ sản phẩm nếu đã xác nhận>.
Đề bài đầy đủ và điều kiện bắt buộc: <nguyên văn hoặc nội dung đã xác nhận>.
Tính chất đề: <chính thức / đề luyện giả định / yêu cầu sản phẩm>.
Mã đề nếu có: <không tự bịa đề chính thức>.
Ý tưởng đã chọn nếu có: <tên; để chưa chốt nếu cần khám phá>.
Người dùng và tác vụ chính: <mô tả cụ thể>.
Điểm bắt đầu/kết thúc và đầu ra: <kết quả nào chứng minh tác vụ hoàn thành>.
Workspace: <repo/root/nhánh, phạm vi sửa và hướng dẫn cần đọc; chưa biết thì kiểm trước>.
Hiện trạng: <file/entrypoint/stack/lệnh đã kiểm; file dự kiến ghi riêng>.
Dữ liệu và quyền: <vị trí hoặc cách nhận, schema, nguồn, phiên bản, owner,
  quyền; phân biệt có thật, được hứa cung cấp, giả định và chưa kiểm>.
Môi trường, thời gian, ngân sách: <đã được cấp hay mục tiêu đề xuất;
  điều kiện chuẩn bị; không điền giá trị key>.
Capability: <documented/untested/verified/failed/unavailable + bằng chứng>.
Hành động bên ngoài đã được cấp quyền: <nếu có>.
Baseline và evidence đang có: <số đo, quan sát hoặc chưa đo>.
Oracle và nghiệm thu: <ai/dữ liệu/luật nào xác nhận đúng; tiêu chí đã chốt,
  đề xuất hoặc cần quyết định; ca thành công, thiếu/mơ hồ và lỗi/hủy>.
Đầu ra cần bàn giao: <trong chat / gói kế hoạch tại đường dẫn / sản phẩm>.

Nếu ở chế độ khám phá: làm bước 1–6 ở mức phân tích, đề xuất ba phương án,
kiểm hard gates, chỉ chấm ưu tiên có căn cứ; phần chưa biết giữ là chưa biết.
Bước 7–8 chỉ bàn giao kế hoạch kiểm chứng; không tự xây MVP.

Nếu ở chế độ lập kế hoạch:
- Giữ phương án và quyết định người dùng đã chốt; không bắt chọn lại ba ý tưởng.
- Đọc hiện trạng, làm bước 1–8 ở mức thiết kế; chỉ chạy kiểm tra/spike trong quyền.
- Xuất gói theo 18.9: brief độc lập, inventory có bằng chứng, kiến trúc,
  data/tool/state contracts, ma trận yêu cầu-nghiệm thu và phase files có thể làm theo.
- plan.md là điểm vào; nêu thứ tự đọc và hành động đầu tiên của agent mới.
- Mọi khoảng trống gắn owner/cách giải quyết, điều kiện mở và phase bị chặn;
  chỉ rõ việc độc lập vẫn làm được. Không giả lập đầu vào để đánh dấu đã đủ.
- Phân biệt lệnh/file dự kiến với hiện trạng đã kiểm; oracle độc lập với target model.
- Dùng trạng thái sẵn sàng theo 18.10; tự kiểm gói khi bỏ lịch sử chat theo 18.11.
- Kế hoạch không phải kết quả nghiệm thu sản phẩm. Không sửa app hoặc gọi dịch vụ
  tốn phí chỉ vì đang lập kế hoạch.

Nếu ở chế độ review kế hoạch: đọc đề và gói hiện có, kiểm theo 18.9–18.11.
- Trả nhận xét theo mức ảnh hưởng, vị trí, bằng chứng, hệ quả và đề xuất sửa.
- Chỉ sửa hoặc sinh lại artifact khi yêu cầu đã bao gồm cập nhật.
- Không đảo quyết định đã xác nhận do lo ngại trừu tượng; nêu trade-off
  và hỏi khi thay đổi cần quyết định của người dùng.

Nếu ở chế độ triển khai: đọc gói và thực hiện phương án đã chốt.
- Bắt đầu ở phase có đủ điều kiện vào, xác minh lại capability dễ thay đổi.
- Xử lý phụ thuộc chưa giải quyết; không đoán quyền, luật hay dữ liệu.
- Implement dữ liệu/quyền/luật/oracle trước phần trình diễn nâng cao.
- Tách system prompt runtime khỏi prompt giao việc này. Version context/tool schema.
- Kiểm tool calls, giới hạn run/cost, ghi có kiểm và output trước khi hiển thị.
- Hoàn thành một luồng xuyên suốt, xử lý lỗi/hủy/retry/trùng; chạy kiểm tương ứng.
- Giữ lỗi và timeout trong báo cáo; phân biệt offline, integration và nghiệm thu.
- Chỉ thêm một nâng cấp tạo khác biệt sau khi MVP đạt và vẫn thuộc phạm vi.

Trong mọi chế độ:
Mỗi công nghệ gắn với yêu cầu, bằng chứng cần đo và cách xử lý khi lỗi.
Chỉ áp Gateway BTC/AI Log/chung-khao khi nhiệm vụ thuộc bối cảnh đó;
ngoài BTC dùng đúng provider, quyền và workspace đã được người dùng cho phép.
Không đọc/in secret, không đụng thay đổi ngoài task.
Không tự tạo dữ liệu/ngưỡng/điểm eval rồi gọi là kết quả thật.
Giữ đúng quyền commit/push/deploy; yêu cầu lập kế hoạch không cấp quyền xuất bản.
~~~

Nếu gói đầu vào thiếu, agent tự scout phần tìm được và chỉ hỏi quyết định còn thiếu. Các ô biểu mẫu trên là hướng dẫn thu thập, không phải thông tin đã được xác nhận hoặc prompt cuối cùng để chuyển nguyên xi cho agent thực hiện.
