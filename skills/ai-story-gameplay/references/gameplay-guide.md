# Khung gameplay cho game phiêu lưu văn bản AI

Cập nhật: 07/10/2026. Tài liệu chung, độc lập với cốt truyện, nhà cung cấp AI và công nghệ triển khai. Các con số minh họa là lựa chọn thiết kế để thử, không phải chuẩn ngành hoặc kết quả đo.

## Mục lục

1. Định vị và quyền của người chơi
2. Bắt đầu và vòng chơi
3. Chọn hành động, nhập tự do và điều khiển nhịp
4. Thế giới, tình thế và phát triển cốt truyện
5. Nhân vật và quan hệ
6. Phân xử và combat đơn giản
7. Bộ nhớ, tiến triển và phần thưởng
8. Đồng sáng tác, sửa và phân nhánh
9. Voice, TTS và màn hình đọc
10. AI, luật và lỗi sinh nội dung
11. Luồng minh họa và bộ bàn giao
12. Đánh giá và phạm vi phiên bản đầu
13. Các sản phẩm tham khảo

## 1. Định vị và quyền của người chơi

Lời hứa cốt lõi: người chơi trở thành một nhân vật trong thế giới, thử điều mình muốn, thấy phản ứng hợp lý và những thay đổi được nhớ qua các cảnh.

Bốn hướng trải nghiệm có thể phối hợp:

| Trọng tâm | Điều người chơi mong đợi | Dấu hiệu thiết kế đang lệch |
|---|---|---|
| Khám phá | Tìm hiểu thế giới, điều tra, thử cách giải quyết mới | AI buộc quay về một tuyến bất kể hành động. |
| Quan hệ | Nhân vật có cá tính và lịch sử chung | Chỉ trò chuyện lặp, mọi NPC đều đồng ý. |
| Thử thách | Quyết định có rủi ro, chuẩn bị có tác dụng | Kết quả tùy ý hoặc chiến đấu chỉ bấm một nút. |
| Đồng sáng tác | Điều chỉnh giọng kể và hướng phát triển | Muốn kể chuyện lại phải quản lý quá nhiều chỉ số. |

Chọn trọng tâm trước khi thêm hệ thống. Không có một tỷ lệ đối thoại/chiến đấu đúng cho mọi thể loại. Combat và romance là lựa chọn sản phẩm, không phải điều kiện để được gọi là RPG văn bản.

Người chơi điều khiển ý định, lời nói và quyết định quan trọng của nhân vật mình. AI điều khiển thế giới và NPC trong giới hạn đã xác lập. Nếu có chế độ tác giả, đặt rõ quyền sửa thế giới và lịch sử; không trộn quyền đó với hành động nhập vai.

## 2. Bắt đầu và vòng chơi

### Bắt đầu nhanh

Cho chọn một tiền đề có sức hút hoặc mô tả ý tưởng riêng. Tiền đề cần cho biết: bạn là ai, chuyện gì đang xảy ra, ai/điều gì đáng quan tâm và vì sao cần hành động. Không bắt đọc toàn bộ lịch sử thế giới.

Tạo nhân vật ở mức vừa đủ: tên/vai, mong muốn và một đặc điểm có tác dụng. Ngoại hình, quá khứ, điểm yếu và quan hệ mở rộng là tùy chọn nếu không cần để hiểu cảnh đầu. Có mặc định và có thể bỏ qua phần trang trí.

Một tiền đề là mẫu khởi đầu. Mỗi lần chơi tạo một phiên riêng với lựa chọn và lịch sử riêng. Có thể cho chọn quan hệ khởi đầu với NPC nếu bối cảnh hỗ trợ; lựa chọn này phải đổi lời chào, hiểu biết và phản ứng, không chỉ đổi nhãn.

### Vòng chơi

1. Đọc/nghe tình huống đang xảy ra.
2. Chọn gợi ý hoặc nhập ý định/lời thoại.
3. Làm rõ nếu cần; phân xử khi có rủi ro thật.
4. Nhận kết quả trực tiếp và phản ứng của thế giới.
5. Ghi thay đổi, tạo cơ hội tiếp theo.
6. Tiếp tục, kết thúc chặng hoặc lưu để quay lại.

Mỗi phản hồi phải xử lý điều người chơi vừa làm trước khi thêm chuyện khác. Có thể kết thúc ở một câu hỏi của NPC, một phát hiện hay một sự việc chờ phản ứng; không luôn lặp “Bạn sẽ làm gì?”.

Độ dài linh hoạt theo cảnh: đối thoại ngắn, khám phá đủ chi tiết để tương tác, nguy hiểm tập trung một pha. Cho người chơi chọn ngắn/vừa/dài nếu phù hợp. Chưa có số từ hoặc thời lượng buổi chơi nào được xem là tối ưu trước khi thử với người dùng.

### Dừng và quay lại

Lưu sau lượt hoàn tất; giữ bản nháp khi kết nối lỗi. Khi quay lại, nhắc vị trí, người đi cùng, sự việc gần nhất và điều chờ quyết định. Không tự tiêu lượt hoặc phát lại truyện dài.

Kết thúc chặng phải giải quyết được ít nhất một vấn đề hoặc thay đổi một quan hệ có ý nghĩa. Cho phép tiếp tục, thử nhánh khác hoặc viết đoạn kết. Không kéo dài vô hạn bằng việc mọi đáp án lại biến thành bí ẩn mới.

## 3. Chọn hành động, nhập tự do và điều khiển nhịp

### Gợi ý

Thường đưa vài lựa chọn khác nhau về ý định: hỏi thông tin, thử tiếp cận, chấp nhận rủi ro, thương lượng hoặc rút lui tùy cảnh. Không cố định mọi cảnh thành tốt/xấu/trung lập hay đánh/đỡ/chạy.

Gợi ý phải thực hiện được ở trạng thái hiện tại, dựa trên điều nhân vật biết. Ghi nguy cơ nhìn thấy khi cần, không tiết lộ hậu quả bí mật hay hứa chắc phần thưởng. Thay gợi ý không thay trạng thái thế giới.

### Đầu vào tự do

| Loại đầu vào | Cách xử lý |
|---|---|
| Rõ, phù hợp, nằm ngoài gợi ý | Hiểu mục tiêu và thực hiện/giải quyết rủi ro; không đòi khớp từ khóa. |
| Hành động kèm lời nói | Xử lý trong cùng nhịp nếu hợp lý. |
| Phủ định hoặc đổi ý | Hiểu toàn câu, không lấy động từ riêng lẻ thành lệnh. |
| Nhiều bước | Tiến tới trở ngại/điểm quyết định đầu tiên rồi trả lượt. |
| Đại từ hoặc mục tiêu mơ hồ | Hỏi một câu ngắn, chưa trừ tài nguyên. |
| Tự khẳng định kết quả thắng | Hiểu thành ý định thử, không coi kết quả là sự thật. |
| Đòi vật phẩm/năng lực chưa có | Đối chiếu trạng thái; cho cách tìm/học/chế nếu có cơ sở. |
| Đổi mục tiêu hoặc bỏ nhiệm vụ | Phản ứng theo động cơ NPC và quy luật thế giới; không ép tuyến vô cớ. |

Hành động rõ không cần xác nhận diễn giải mỗi lượt. Chỉ hỏi khi thiếu thông tin ảnh hưởng ý định, hoặc cần chọn giữa những cái giá mà người chơi chưa quyết định. Nguy cơ thông thường được diễn đạt trong cảnh, không tạo chuỗi popup.

Chi tiết nền hợp lý có thể được AI bổ sung khi chưa xác lập, nhưng một món đồ quyết định chiến thắng hoặc lối thoát thuận tiện không tự tồn tại chỉ vì người chơi nhắc tới. Quy luật mới phải được lưu khi giới thiệu và không mâu thuẫn sự kiện đã biết.

### Điều khiển nhịp

Có thể cung cấp “Để cảnh tiếp diễn” để NPC/môi trường diễn tiến một nhịp, nhưng không thay người chơi nhận lời, di chuyển nguy hiểm hoặc quyết định tình cảm. Trong tình huống gấp, chờ là hành động có hệ quả, phải gọi đúng là chờ.

Việc di chuyển/chuẩn bị không có lựa chọn đáng kể có thể tóm tắt. Không biến mỗi bước chân thành một lần gọi AI. Hỏi về UI, mở hành trang hoặc đọc lại nhật ký không làm thời gian trong truyện trôi.

## 4. Thế giới, tình thế và phát triển cốt truyện

Thiết kế các điều kiện tồn tại, không chỉ một cây đáp án. Một cửa bị khóa có người giữ chìa, quy trình vào, lối khác hoặc lý do không thể vào. Những điều này tạo không gian ứng biến.

Mỗi tiền đề thường cần:

- Quy luật thế giới và giới hạn năng lực.
- Tình thế mở đầu, áp lực nếu có và các bên liên quan.
- Mục tiêu của NPC, tài nguyên và điều họ biết.
- Bí mật/sự thật nền, phân biệt với lời khai và tin đồn.
- Những địa điểm hoặc đầu mối có thể tiếp cận.

Sự thật bí mật đã chốt không được thay để khiến người chơi luôn đoán sai. Nhánh có ý nghĩa phải đổi thông tin, cơ hội, tài nguyên hoặc quan hệ; thay văn phong chưa đủ.

Nhịp truyện gồm khám phá, đối thoại, xung đột và khoảng nghỉ tùy bối cảnh. Khoảng nghỉ có thể trả phần thưởng bằng sự tin cậy, một câu chuyện riêng hoặc kế hoạch mới. Không sinh kẻ địch chỉ vì người chơi đang nói chuyện lâu.

Áp lực đi theo sự kiện trong truyện đã được báo, không theo thời gian thực đọc/đóng app trừ khi người dùng chủ ý chọn cơ chế đó. Cần báo nguy cơ trước khi nó tạo hậu quả lớn.

Chuẩn bị phải có ích. Nếu người chơi đã có quyền vào một khu vực, đừng dựng thêm khóa vô cớ để ép quay về đường dự kiến. Bất ngờ cần tương thích với dấu hiệu và sự thật đã tồn tại.

## 5. Nhân vật và quan hệ

NPC đáng tương tác cần muốn một điều, biết một phần, có giới hạn và biểu hiện riêng. Có thể dùng hồ sơ ngắn:

| Thuộc tính | Dùng để quyết định |
|---|---|
| Mong muốn và nỗi sợ | Họ theo đuổi gì, chấp nhận đánh đổi gì. |
| Năng lực và giới hạn | Giúp được gì, cần nhờ ai. |
| Kiến thức và điều giấu | Nói thật, nói dối, không biết hay suy đoán. |
| Giá trị và ranh giới | Khi nào phản đối hoặc từ chối. |
| Giọng nói và thói quen | Cách thể hiện mà không mọi người cùng một giọng. |
| Lịch sử với người chơi | Lời hứa, việc đã giúp, tổn thương, món nợ. |

Quan hệ có thể có nhiều mặt: tin tưởng, tôn trọng và bất đồng không phải một điểm số duy nhất. Hiển thị bằng lời cụ thể nếu thanh chỉ số không giúp người chơi quyết định.

NPC có thể hợp tác, mặc cả hoặc phản đối có lý do. Không tự yêu người chơi, luôn tán thành hoặc phản bội chỉ để thêm kịch tính. Nếu sản phẩm hỗ trợ chọn loại quan hệ, tôn trọng lựa chọn đó.

NPC đồng hành có thể đề nghị kế hoạch và làm việc được giao. Họ không giải toàn bộ nút thắt hoặc tự quyết định người chơi sẽ đi đâu. Người chơi có thể tách nhóm khi hợp lý; vị trí và kiến thức mỗi người phải cập nhật.

## 6. Phân xử và combat đơn giản

### Khi nào cần luật?

- Việc khả thi, không có phản kháng: giải quyết trực tiếp.
- Việc có rủi ro và kết quả chưa chắc: dùng cơ chế đã chọn.
- Việc không thể theo luật thế giới: giải thích, cho cách gần nhất nếu có.

Có thể dùng luật xác định, kiểm tra thuộc tính hoặc xúc xắc. Chọn một cơ chế nhất quán; không để độ dài câu lệnh quyết định mức sát thương. Không cần xúc xắc để xác định mọi câu trả lời hoặc cảm xúc NPC.

### Combat tùy chọn

Combat nằm trong luồng truyện. Trước trận, người chơi hiểu mục tiêu: thoát, bảo vệ, cầm chân, lấy vật hoặc đánh bại. Kết thúc khi mục tiêu đạt hoặc xung đột chấm dứt, không luôn yêu cầu hết HP.

Giữ ít tài nguyên và trạng thái. Nếu dùng số, phải định nghĩa giới hạn, chi phí, thứ tự giải quyết, hồi phục, điều kiện thất bại và cách quay lại. Nút chiến đấu thay theo môi trường; luôn cho hành động tự do nếu sản phẩm có nhập tự do.

Một bộ luật **minh họa, không bắt buộc**:

- Người chơi 6 HP; đối thủ 3 sức chống trả.
- d6, +1 nếu có lợi thế liên quan, không cộng dồn.
- 1–2: không đạt mục đích, chịu hậu quả đã nêu; 3–4: đạt với một cái giá; 5+: đạt sạch.
- Một đòn thường thành công giảm 1 sức chống trả. Cái giá thông thường là 1 HP; hậu quả khác phải được xác định trước.
- Một phép kiểm tra giải quyết cả pha, không cộng thêm đòn địch sau đó.
- Hết HP gây thất bại cảnh với hệ quả đã định; không mặc định xóa truyện.

Ví dụ kiểm số: trước lượt người chơi 6 HP, đối thủ 3; d6=3, không lợi thế, chọn đòn thường với cái giá đã nêu là 1 HP. Sau lượt: người chơi 5, đối thủ 2. Nếu chọn giữ cửa thay vì đánh, thành công mở cơ hội thoát theo hợp đồng hành động; không tự giảm sức chống trả của địch.

Sơ hở, che chắn và cách dùng đồ phải tạo tác dụng đúng ý định. Xác lập trước hiệu ứng của hành động và thời hạn trạng thái. Hồi HP cần cơ sở như nghỉ an toàn hoặc vật tư; đổi cảnh không tự hồi đầy.

Mục tiêu là vài pha có quyết định khác nhau. Khi giằng co, thay tình thế bằng nguyên nhân có sẵn, không tự sinh thêm địch để kéo dài. Thất bại có thể mở tuyến mới: bị bắt, mất thời gian hoặc mất cơ hội, miễn giữ nguyên cái giá thật.

## 7. Bộ nhớ, tiến triển và phần thưởng

Tách thông tin theo vai trò:

| Lớp | Nội dung | Tránh |
|---|---|---|
| Lore | Quy luật, địa điểm, nền tảng nhân vật | Mỗi lượt tự viết lại luật. |
| Trạng thái | Vị trí, vật phẩm, HP, cửa/lối đi | Đồ đã dùng vẫn còn. |
| Sự kiện | Ai làm gì, khi nào, kết quả | Tóm tắt làm mất nguyên nhân. |
| Kiến thức | Ai chứng kiến/biết/suy đoán gì | NPC đọc được toàn bộ bí mật. |
| Quan hệ | Lời hứa, mâu thuẫn, sự tin cậy có căn cứ | Mọi câu tử tế thành tăng thiện cảm. |
| Tuyến mở | Mục tiêu hiện tại, vấn đề đã/chưa giải quyết | Chỉ sinh câu hỏi, không có đáp án. |
| Sở thích kể | Nhịp, độ dài, mức căng thẳng | Thay phong cách làm đổi sự kiện. |

Có thể tự lưu và cho xem một sổ hành trình. Chỉ hiển thị điều người chơi biết. Ghim khoảnh khắc giúp đọc lại/ưu tiên ghi nhớ; không biến lời nói dối thành sự thật hoặc đưa bí mật lên màn hình.

Phần thưởng phù hợp thể loại: thông tin, đồng minh, quyền tiếp cận, vật có công dụng, kỹ năng mới có cơ sở, cảnh nghỉ hoặc đoạn kết đáng nhớ. XP/trang bị chỉ thêm khi chúng tạo lựa chọn hữu ích. Quan hệ phát triển cũng phải đổi cách nhân vật hành động.

## 8. Đồng sáng tác, sửa và phân nhánh

Phân biệt rõ:

| Thao tác | Đổi gì? | Giữ gì? |
|---|---|---|
| Định hướng kể | Giọng, nhịp, trọng tâm các lượt sau | Sự kiện, kết quả và nhân cách đã xác lập. |
| Viết lại lời kể | Cách thể hiện cùng một kết quả | Xúc xắc, vật phẩm, trạng thái. |
| Sửa lỗi AI | Chi tiết sai sau đối chiếu lịch sử | Các sự kiện đúng và quyết định người chơi. |
| Thử hướng khác | Tạo nhánh từ một mốc trước hành động | Nhánh cũ để đọc lại nếu hỗ trợ lưu nhánh. |
| Sửa tiền đề | Quy luật hoặc nền tảng theo quyền tác giả | Không âm thầm hồi tố phiên đang chơi; dùng phiên/nhánh được chỉ rõ. |

Khi quay về mốc cũ phải phục hồi trạng thái lẫn bộ nhớ. Nhân vật không nhớ sự kiện của tương lai đã bỏ. Nếu có ngẫu nhiên, chốt việc replay giữ hay tung lại kết quả và diễn đạt cho người chơi hiểu.

Tính năng chỉnh truyện không nhất thiết phải có đầy đủ trong MVP. Nếu cung cấp một thao tác, tên và tác dụng phải rõ để người dùng không tưởng sửa câu văn là sửa chiến thắng.

## 9. Voice, TTS và màn hình đọc

Voice và TTS là hai tùy chọn độc lập khi thuộc phạm vi:

- Nói → nhận transcript → sửa → gửi; không tự thực hiện từ kết quả nhận dạng chưa duyệt.
- Gửi một lần nếu câu rõ; không bắt thêm bước xác nhận máy hiểu sau mỗi lần gửi.
- Bật/tắt TTS, dừng/đọc lại; không bắt người chơi nghe hết mới được chọn.
- Bật microphone dừng TTS để tránh nhận lại tiếng kể.
- Không có quyền mic hoặc dịch vụ lỗi vẫn nhập chữ được; không giả vờ đã nhận âm thanh.

Màn chơi ưu tiên văn bản, gợi ý và ô nhập; thông tin nguy hiểm/tài nguyên hiện đúng lúc. Hành trang, NPC và nhật ký mở khi cần. Tranh không bắt buộc cho mỗi lượt. Nếu nhắm mobile web, cần thao tác chạm dễ, chữ đọc được, bàn phím không che nút gửi và tiến trình không mất khi đổi hướng màn hình.

Việc nghe, mở menu, sửa transcript và chờ mạng không phải hành động trong thế giới game.

## 10. AI, luật và lỗi sinh nội dung

AI tạo bối cảnh mới, hiểu ý định, đề xuất phản ứng phù hợp và kể. Hệ thống giữ dữ liệu chuẩn, giới hạn hiệu ứng, phiên/nhánh và kết quả phân xử. Không xem mọi đề xuất của AI là trạng thái đã xảy ra.

Luồng logic: hiểu ý định → kiểm điều kiện và tác động → phân xử → ghi sự kiện hợp lệ → kể theo kết quả → gợi ý mới. Có thể tổ chức bằng nhiều cách kỹ thuật; khung này không yêu cầu một model, framework hoặc nhiều agent.

Các bất biến trải nghiệm:

- Gửi lại do lỗi mạng không trừ thêm vật phẩm hoặc thêm lượt.
- AI kể sai HP thì sửa lời kể, không đổi HP cho khớp văn.
- Chưa có kết quả thì không báo hành động hoàn tất.
- Câu mơ hồ chưa tiêu tài nguyên.
- Lỗi sinh văn bản không được biến thành hình phạt nhân vật.
- Dữ liệu người chơi nhập không tự trở thành luật ưu tiên hơn quy tắc thế giới.

Tốc độ và chi phí cần đo trên hệ thống thật. Không đưa lời hứa độ trễ, trí nhớ hoàn hảo hoặc chất lượng tương đương sản phẩm tham khảo nếu chưa có phép kiểm.

## 11. Luồng minh họa và bộ bàn giao

Ví dụ trung lập, có thể đổi sang khoa học viễn tưởng, kỳ ảo hoặc đời thường:

1. Người chơi cần vào một nơi để tìm thông tin; một NPC muốn nhờ giúp việc riêng.
2. Game gợi ý hỏi thêm, thương lượng hoặc tìm lối khác.
3. Người chơi tự đề xuất sửa một thiết bị hỏng để đổi quyền vào. Nếu nghề/công cụ đủ điều kiện, giải quyết; nếu chưa, cho biết thiếu gì.
4. Thành công mở lối và khiến NPC tin vào một năng lực cụ thể. Lời hứa giúp họ được lưu.
5. Khi gặp trở ngại mới, NPC phản ứng dựa trên việc lời hứa được giữ hay bị bỏ. Nếu người chơi đã có quyền vào thì không tự chặn lại chỉ để ép đánh nhau.
6. Người chơi lấy được thông tin hoặc chọn mục tiêu khác; cuối chặng có một đáp án và hệ quả quan hệ rõ.

Hai phiên khác nhau: giữ lời có thể được hỗ trợ thêm; bỏ lời để theo mục tiêu riêng có thể đi nhanh nhưng mất sự hợp tác. Không mặc định nhánh tử tế luôn được mọi phần thưởng còn nhánh khác chỉ bị phạt. Cái giá/cơ hội phụ thuộc động cơ thế giới đã thiết kế.

Khi bàn giao game cụ thể, tài liệu nên tự chứa: đối tượng, tiền đề, vòng chơi, phạm vi input, hồ sơ NPC, luật phân xử, trạng thái, ví dụ và tiêu chí kiểm. Không để người nhận phải đọc lịch sử chat hoặc tự suy ra luật từ một HTML cũ.

## 12. Đánh giá và phạm vi phiên bản đầu

### Kiểm hành vi

| Ca kiểm | Điều cần quan sát |
|---|---|
| Ý tưởng mới ngoài gợi ý | Được xử lý theo ý định, có hậu quả khác thực sự. |
| Phủ định/mơ hồ/nhiều bước | Không làm ngược ý; hỏi đúng lúc; trả lượt ở điểm cần quyết định. |
| Đổi mục tiêu | Thế giới phản ứng, không vô cớ ép tuyến. |
| Hai NPC nhận cùng đề nghị | Lý do và câu trả lời khác nhau theo nhân vật. |
| Thất hứa rồi gặp lại | NPC nhớ sự kiện, phản ứng đúng phần họ biết. |
| Đã dùng hoặc cho vật phẩm | Không thể dùng lại khi chưa lấy về. |
| Điều tra bí mật | Bí mật giữ nguyên; lời kể không tự tiết lộ sớm. |
| Thoát thay vì đánh | Xung đột kết thúc khi đạt mục tiêu phù hợp. |
| Viết lại/undo/nhánh | Kết quả và ký ức thay đổi đúng phạm vi. |
| Retry mạng và voice lỗi | Không nhân đôi lượt, giữ bản nháp, còn đường nhập chữ. |

### Kiểm độ hấp dẫn

Cho người thử một buổi ngắn và hỏi: bạn muốn làm gì tiếp, bạn quan tâm ai/điều gì, lựa chọn nào có tác dụng, lúc nào thấy bị ép hoặc lặp? Quan sát cả người bấm gợi ý lẫn người tự gõ. Việc chơi lâu chưa đủ chứng minh hay; có thể họ đang mắc kẹt.

Chốt tiêu chí/ngưỡng cùng chủ sản phẩm trước khi đánh giá bản chính thức. Báo lỗi và giới hạn; không ghi “đã cải thiện giữ chân” từ việc chỉ đọc tài liệu đối thủ.

### Phạm vi nhỏ để kiểm được ý tưởng

Một số ít tiền đề được biên tập, AI hiểu tự do thật, vài NPC có nhớ, hậu quả nhất quán và lưu/tiếp tục thường quan trọng hơn thư viện lớn. Các tính năng chỉ thêm khi phục vụ mục tiêu đã chọn. Không mặc định hoãn yêu cầu bắt buộc của người dùng.

Demo viết sẵn có thể dùng để minh họa UI nếu công bố rõ. Nó không chứng minh được năng lực AI hiểu ngôn ngữ, giữ nhân cách hay tạo tình tiết mới.

## 13. Các sản phẩm tham khảo

Snapshot nghiên cứu ngày 07/10/2026 từ tài liệu chính thức, không phải thử chơi trực tiếp hay khẳng định luôn đúng trên mọi tài khoản/phiên bản. Đọc lại nguồn khi cần thông tin hiện hành.

| Sản phẩm | Quan sát có nguồn | Bài học thiết kế đề xuất |
|---|---|---|
| StoryZone | Cho chọn gợi ý hoặc nhập hành động riêng. [Choices](https://www.storyzone.app/faq-items/how-do-choices-work-in-storyzone/) | Giảm khó khăn lúc bắt đầu nhưng giữ quyền tự chọn cách làm. |
| AI Dungeon | Do/Say/Story và scenario làm điểm khởi đầu cho các adventure. [Player Guide](https://help.aidungeon.com/new-player-guide), [Scenarios](https://help.aidungeon.com/faq/what-are-scenarios) | Tách mẫu thế giới khỏi phiên chơi; cho thay đổi hướng hành động. |
| NovelAI | Có Storyteller và Text Adventure; Memory, Author’s Note, Lorebook hỗ trợ bối cảnh/cách kể. [FAQ](https://docs.novelai.net/en/faq/), [Text Adventure](https://docs.novelai.net/en/text/textadventure/), [Settings](https://docs.novelai.net/en/text/editor/storysettings/), [Lorebook](https://docs.novelai.net/en/text/lorebook/) | Phân biệt nhập vai với quyền định hướng tác giả; giữ thông tin thế giới có cấu trúc. |
| Character.AI | Scenes đặt vai, bối cảnh, mục tiêu; Story Memory và ghim khoảnh khắc hỗ trợ nhớ. [Scenes](https://blog.character.ai/introducing-scenes-your-new-way-to-tell-stories-on-c-ai/), [Memory](https://blog.character.ai/memory/) | Nhân vật và lịch sử chung có thể tạo động lực tiếp tục, cần kiểm bằng chơi thử. |

Không sao chép cốt truyện, giao diện, nhân vật hay lời văn của các sản phẩm. Không coi một bộ luật combat minh họa trong tài liệu này là tính năng của họ.
