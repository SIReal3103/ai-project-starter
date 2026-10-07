# Bộ ca minh họa tiếng Việt

`demo-cases.jsonl` gồm 40 ca do người soạn thiết kế trong bốn nhóm. Tất cả mang nhãn `synthetic-example`: tài liệu thư viện, con số, quy định và mã tài liệu đều là dữ liệu giả định để kiểm thử. URL đối kháng dùng tên miền dành riêng `.invalid`, không phải đích nhận dữ liệu thật. Đây không phải dữ liệu người dùng thật, bộ đánh giá chính thức của sản phẩm, hay kết quả chạy LLM.

| Nhóm | Số ca | Hành vi cần kiểm tra |
| --- | ---: | --- |
| `chatbot` | 12 | Lời chào, giới thiệu khả năng, hỏi lại, lịch sử hội thoại, JSON, số thập phân, thuật ngữ, trộn tiếng Việt/Anh, yêu cầu định dạng mâu thuẫn, đầu vào rỗng và khoảng trắng |
| `rag` | 8 | Nguồn liên quan, nhiều nguồn, không có bằng chứng, nguồn không liên quan, mâu thuẫn, chọn nguồn chỉ định, số liệu, giá trị chưa thống kê |
| `agent` | 8 | Đối số công cụ, thứ tự tìm rồi đọc, lỗi công cụ, giới hạn lượt gọi, bản nháp chưa gửi, từ chối xóa, yêu cầu không gọi công cụ |
| `guardrail` | 12 | Injection trực tiếp và qua tài liệu, bí mật, dữ liệu riêng tư, ngoài phạm vi, lăng mạ/đe dọa, phân biệt đối xử, trích dẫn giáo dục hợp lệ, lệnh rò rỉ dữ liệu qua URL |

## Hợp đồng ca kiểm thử

Mỗi dòng là một JSON object độc lập, mã hóa UTF-8. `question` là câu hỏi hiện tại; `history` chứa các lượt trước; `contexts` là tập tài liệu có thể truy hồi, gồm cả tài liệu gây nhiễu. `id` chỉ dùng ghép kết quả. `expected_answer` là câu trả lời hoặc mô tả tham chiếu được soạn thủ công, không được đưa cho hệ thống đang được đánh giá.

`expected` mô tả các oracle có thể kiểm tự động:

- `answer_contains_all`, `answer_contains_any`, `answer_not_contains`: chuỗi bắt buộc, nhóm lựa chọn và chuỗi cấm. Chúng là phép kiểm gần đúng, không chứng minh tính đúng ngữ nghĩa.
- `required_citation_ids`: mã nguồn bắt buộc được trích; `expected_context_ids`: tập nguồn liên quan chuẩn để so với tập truy hồi. Nguồn gây nhiễu không nằm trong tập chuẩn.
- `tool_calls`: tên và đối số chính xác, theo thứ tự; `forbidden_tools` và `max_tool_calls`: giới hạn tác vụ và ngân sách. Danh sách trống nghĩa là không mong đợi gọi công cụ.
- `must_refuse` và `required_guardrail_action`: yêu cầu từ chối hoặc trạng thái `allow`, `refuse`, `clarify`. Trạng thái guardrail là dữ liệu hệ thống tự báo; cần đối chiếu nội dung, công cụ và tác động thực tế khi tích hợp.
- `output_json`: yêu cầu toàn bộ câu trả lời là JSON hợp lệ. `max_latency_ms`: ngưỡng minh họa cho adapter cục bộ, không phải SLA sản phẩm.

Chỉ các ca có tag `exact-match` mới yêu cầu đối chiếu nguyên văn với `expected_answer`. Các câu tham chiếu còn lại có thể là mô tả tiêu chí; không nên tính độ giống chữ trên chúng như một thước đo chất lượng trả lời.

## Adapter demo

`adapters/demo.py` là trợ lý dựa trên luật, dùng thư viện chuẩn Python. Nó đọc `question`, `history`, `contexts`, chép `id` sang `case_id` và không đọc `expected`, `expected_answer`, `category` hay `tags` để chọn câu trả lời. Đầu vào đầy đủ được chấp nhận để thuận tiện chạy, nhưng các trường oracle không tham gia suy luận.

Ba công cụ cho phép là `calculator.add`, `search_documents`, `read_document`. Phép cộng thực sự được tính bằng `Decimal`; tìm kiếm và đọc chỉ thao tác trên corpus nằm trong bộ nhớ của ca. Kết quả công cụ ghi `sandbox: demo`. Adapter không gửi email, xóa tài liệu, truy cập mạng hay đọc/ghi tệp của người dùng. CLI đọc đúng một ca JSON từ stdin và ghi một response JSON ra stdout.

```bash
head -n 1 datasets/demo-cases.jsonl | python3 adapters/demo.py
```

Nội dung trả lời và trace ổn định với cùng đầu vào. `latency_ms` được đo bằng `perf_counter` nên thay đổi giữa các lần chạy; `usage` rỗng vì không có token LLM. `provider_metadata.mode` luôn là `demo`.

Tìm kiếm chỉ dựa trên từ trùng; trả lời chủ yếu trích nguyên dữ kiện. Lọc chỉ dẫn trong nguồn là heuristic theo dòng. Kiểm tra nội dung lạm dụng, phân biệt đối xử và ý định giáo dục cũng chỉ là luật từ khóa hẹp, không phải bộ phân loại ML. Các ca tương ứng là mẫu kiểm tra chịu lỗi, không phải phép đo đầy đủ về độc hại hoặc công bằng. Các luật này có nhiều cách bị vượt qua và không tạo thành lớp phòng vệ đủ dùng trong sản phẩm. Bộ ca này minh họa cấu trúc đánh giá và phát hiện lỗi của runner; điểm cao trên chính bộ ca không chứng minh tổng quát hóa, chất lượng tiếng Việt hay mức an toàn của LLM.

## Thay bằng bộ đánh giá thật

Giữ một tập phát triển riêng, rồi xây tập holdout độc lập từ yêu cầu sản phẩm và lỗi thực tế đã khử thông tin riêng tư. Bổ sung nhiều cách diễn đạt, nhiều độ dài hội thoại, lỗi công cụ thực tế và tài liệu đối kháng; tránh chỉ thay con số trong cùng một mẫu câu. Nhờ người đánh giá kiểm tra nguồn, câu tham chiếu và ca từ chối quá mức. Version hóa bộ ca cùng chính sách mà nó kiểm tra.

Khi gắn adapter LLM, chỉ truyền câu hỏi, lịch sử, tài liệu và chính sách công cụ hợp lệ; giữ oracle ngoài prompt. Thu trace công cụ thực tế và nguồn thực sự truy hồi, không dựng lại từ câu trả lời. Dùng đánh giá thủ công hoặc giám khảo độc lập cho các khía cạnh như tính đúng, mức hỗ trợ của trích dẫn, giọng điệu và quyết định hỏi lại; báo riêng điểm demo, điểm holdout và kết quả chạy nhà cung cấp thật.
