---
name: ai-story-gameplay
description: "Thiết kế hoặc rà soát gameplay cho game phiêu lưu văn bản AI, nhập vai hội thoại và tiểu thuyết tương tác: vòng chơi, nhân vật, hành động tự do, hậu quả, bộ nhớ và combat nhẹ. Dùng khi cần tài liệu gameplay có thể bàn giao; không tự xây app từ yêu cầu thiết kế."
---

# AI Story Gameplay

Tạo gameplay mà người chơi có thể hình dung mình sẽ làm gì, vì sao muốn tiếp tục và lựa chọn thay đổi điều gì. Viết theo ngôn ngữ người dùng. Không lấy một truyện mẫu làm khuôn bắt buộc cho mọi game.

## Chọn phạm vi trước

- **Gameplay chung cho thể loại:** mô tả cơ chế tái sử dụng, các quyết định cấu hình và tiêu chí chất lượng. Ví dụ ngắn chỉ để giải thích, không viết một chiến dịch thay cho khung chung.
- **Thiết kế game cụ thể:** giữ bối cảnh, đối tượng, nền tảng và các quyết định đã chốt; hoàn thiện các khoảng trống bằng giả định dễ đổi, ghi rõ.
- **Rà soát:** chỉ ra chỗ người chơi thiếu quyền chủ động, thiếu động lực hoặc hậu quả không nhất quán; chỉ sửa file khi được yêu cầu.
- **Triển khai:** dùng thiết kế đã chốt làm đầu vào; skill này không thay quy trình code của repo và không tự cấp quyền deploy, gọi API trả phí hoặc xuất bản.

Đọc [khung gameplay](references/gameplay-guide.md). Với tác vụ hẹp, đọc phần tương ứng qua mục lục thay vì tải toàn bộ. Nguồn đối chiếu bốn sản phẩm ở cuối tài liệu; chỉ tra lại tính năng hiện tại khi câu trả lời cần khẳng định chúng. Không coi mô tả nhà cung cấp là kết quả chơi thử.

## Cách thiết kế

1. Xác định điều người chơi tìm kiếm: khám phá, quan hệ, thử thách hay đồng sáng tác; các yếu tố có thể cùng tồn tại nhưng cần một trọng tâm. Phân biệt yêu cầu, đề xuất và giả định. Không ép combat, romance, voice hoặc một provider vào mọi đề bài.
2. Mô tả vòng **ý định → phản ứng → thay đổi có nhớ → cơ hội tiếp theo**. Nêu rõ đầu vào bằng gợi ý/chữ/voice nếu thuộc phạm vi; khi nào chuyển cảnh, dừng chờ, kết thúc chặng hoặc tiếp tục.
3. Thiết kế tình thế và NPC có mục tiêu, năng lực, giới hạn và thông tin riêng. Cho phép rẽ hướng; giữ sự thật bí mật ổn định. NPC không quyết định hành động quan trọng thay người chơi.
4. Chốt cách phân xử hành động: việc chắc chắn, việc có rủi ro và việc không thể; phản ứng với ý tưởng ngoài gợi ý, phủ định, câu mơ hồ, kế hoạch nhiều bước. Hành động rõ không phải qua xác nhận diễn giải mỗi lần.
5. Mô tả trạng thái cần nhớ và tác dụng thực tế của lựa chọn. Tách lore, sự kiện, kiến thức NPC, quan hệ và sở thích kể. Quy định sửa lời kể, sửa lỗi, hoàn tác và nhánh mới không bị lẫn.
6. Nếu có combat, dùng bộ luật tối thiểu đủ tạo quyết định: mục tiêu cảnh, tài nguyên, tác động, hậu quả và điều kiện kết thúc. Đưa một ví dụ tính đúng số; không để AI tùy ý đổi luật sau kết quả.
7. Chứng minh bằng một luồng ngắn và ít nhất một hành động không có trong gợi ý. Khi thiết kế sản phẩm cụ thể, so sánh hai cách chơi cùng tiền đề và chỉ ra khác biệt về cơ hội/quan hệ/trạng thái. Các ví dụ là kịch bản thiết kế, không giả làm log AI thật.
8. Tự rà bằng các ca ở phần 12 của khung. Báo phần cần chơi thử; “hay hơn” là giả thuyết cho tới khi có bằng chứng.

## Đầu ra

Điều chỉnh độ dài theo yêu cầu. Một bản bàn giao cụ thể thường cần:

- Người chơi, lời hứa trải nghiệm và giới hạn phạm vi.
- Bắt đầu phiên, vòng chơi, kết thúc chặng và quay lại.
- Cách nhập, gợi ý, NPC/quan hệ, trạng thái và hậu quả.
- Combat, voice/TTS hoặc chức năng khác chỉ khi phù hợp yêu cầu.
- Một ví dụ đầu-cuối, cách rẽ hướng và xử lý lỗi.
- Nguồn quan sát, lựa chọn thiết kế và tiêu chí chơi thử tách rõ.

Nếu yêu cầu lưu file, viết tài liệu độc lập: người nhận không cần lịch sử chat hoặc cài skill này để hiểu. Nếu chỉ hỏi trong chat, trả lời trong chat. Chỉ tạo kế hoạch triển khai khi được yêu cầu; không tự thêm DB, framework, nhiều agent hay hệ thống thanh toán.

## Những điểm phải giữ

- Gợi ý hỗ trợ người chơi, không phải danh sách đóng của mọi hành động hợp lệ.
- Thay cách kể không được tự đổi kết quả hay vật phẩm. Đổi quá khứ cần nhánh/sửa trạng thái có nghĩa rõ.
- Không đưa bí mật vào gợi ý, recap hoặc hồ sơ nhân vật trước khi người chơi biết.
- Người chơi có quyền dừng, đổi mục tiêu và chơi chậm. Áp lực trong truyện không tự trở thành phạt thời gian đọc/offline.
- Nhân vật có thể bất đồng có lý do. Không làm mọi NPC luôn đồng ý, tự yêu người chơi hoặc biết mọi việc.
- Không bắt lựa chọn đau đớn bằng luật mới xuất hiện đúng lúc quyết định; chuẩn bị trước phải tạo lợi ích thật.
- Tách khả năng AI dự kiến khỏi tính năng đã chạy; không dùng regex/cây truyện cố định để chứng minh hiểu tự do.
- Khung trung lập với nhà cung cấp và cuộc thi. Chỉ áp quy định BTC hay hạ tầng riêng khi đề bài thực sự yêu cầu.
