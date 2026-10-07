# Chọn bài toán và kiến trúc sản phẩm AI

Bộ hướng dẫn này giúp chuyển một đề bài mới thành một sản phẩm có thể chạy, kiểm và bàn giao. Đây là hướng dẫn thiết kế; phần ứng dụng phải được xây theo dữ liệu và hợp đồng thật. Bộ công cụ thực thi đi kèm nằm tại [tools/evals](../../tools/evals/README.md).

## Đường đọc

| Cần làm | Hướng dẫn |
| --- | --- |
| Chọn một tác vụ, dữ liệu và stack | Tài liệu này |
| Chatbot, RAG, số liệu và agent có tools | [Chatbot, RAG và agent](chatbot-rag-and-agents.md) |
| Backend, quyền, dữ liệu cá nhân và hành vi có tác động | [Bảo mật, quyền riêng tư và trách nhiệm](backend-security-and-privacy.md) |
| Giọng nói, ảnh, nội dung sinh và xuất media | [Voice và media](voice-and-media.md) |
| Tests, oracle, đánh giá AI và vận hành | [Evals và observability](evals-and-observability.md) |
| Hoàn thành một luồng trong phiên 120 phút | [Quy trình hai giờ](two-hour-workflow.md) |
| Kết nối dịch vụ AI, gồm cấu hình BTC tùy chọn | [Provider profiles](provider-profiles.md) |

Không cần dùng mọi công nghệ trong bộ này. Chọn một người dùng chính, một tác vụ và một đường từ đầu vào đến kết quả kiểm được.

## Phân biệt thành phần trước khi chọn công cụ

| Khái niệm | Nó thực hiện việc gì |
| --- | --- |
| Chatbot | Giao diện hội thoại với backend trả lời |
| LLM | Hiểu, trích trường, đề xuất hoặc diễn đạt; không cấp quyền và không làm nguồn sự thật cho số liệu |
| Workflow | Code quyết định bước tiếp theo, nhánh, thời hạn và điều kiện dừng |
| Agent/tool calling | Model đề xuất tên tool và đối số; backend kiểm rồi thực thi |
| RAG | Truy hồi bằng chứng phù hợp rồi dùng nó để trả lời |
| Embedding/vector search | Tìm gần nghĩa; không thay điều kiện quyền, phiên bản hoặc phép tính |
| Hybrid search/reranking | Kết hợp tìm từ khóa với vector/xếp lại ứng viên; thêm sau khi đo lỗi truy hồi |
| NL2SQL | Đề xuất truy vấn trên schema có kiểm soát; cần kiểm truy vấn và quyền độc lập model |
| State/memory/checkpoint | Trạng thái tác vụ/thông tin qua các phiên/điểm khôi phục; mỗi loại có vòng đời riêng |
| Guardrails | Kiểm schema, quyền, tài nguyên và hành động ở đúng nơi phát sinh tác động |
| HITL | Người có quyền kiểm hoặc duyệt quyết định cụ thể |
| Evals/observability | Đo hành vi trên ca có oracle/theo dõi những gì xảy ra khi chạy |

Ví dụ: model chọn tool đối soát; SQL/Python thực hiện ghép bản ghi; RAG chỉ tra quy tắc. Nếu code chọn hàm từ bộ lọc, gọi đó là workflow. IDE và coding agent là công cụ phát triển, không phải capability của sản phẩm.

## Tám bước cho một đề mới

1. **Viết hợp đồng kết quả.** Ai làm gì, input nào, output nào, khi nào xong, dữ liệu nào được phép dùng? Ghi cả phần ngoài phạm vi. Đừng suy tiêu chí chấm hoặc yêu cầu khách hàng từ tên công nghệ.
2. **Tìm điểm nghẽn và baseline.** Quan sát vài tác vụ được phép. Đo hoặc để trống thời gian, lỗi và công sức hiện tại. So với form, lookup, search hoặc template trước khi giả định cần AI.
3. **Tạo ba phương án khác nhau.** Mỗi phương án phải có một luồng sử dụng, đóng góp của AI, nguồn dữ liệu, người chịu trách nhiệm và cách kiểm giả định quan trọng.
4. **Qua cổng bắt buộc.** Phương án cần có dữ liệu/quyền, khả năng API hoặc đường xử lý khả thi, cách chấm kết quả và nguồn lực đủ cho MVP. Chỗ chưa biết ghi `unknown` cùng phép thử; không tự tính thành đạt.
5. **Ánh xạ từng bước vào thành phần tối thiểu.** Ghi input/output có kiểu, nơi quyết định, nguồn sự thật, mode lỗi và test. Một app và một database thường là điểm khởi đầu dễ kiểm.
6. **Chốt data/tool/state contracts.** Quyền từ backend; oracle độc lập với output model; ca thiếu nguồn, mơ hồ, lỗi và hành động sai có tiêu chí rõ. Ngưỡng mềm phải chốt trước lượt đánh giá quyết định.
7. **Kiểm điểm nghẽn sớm rồi hoàn thiện một luồng.** Ví dụ codec browser, truy cập kênh chat, vòng tool-call hoặc parser bảng. Xây data/rules/auth → tool → workflow/AI → UI → phục hồi lỗi → eval.
8. **Quyết định bằng bằng chứng.** Giữ, sửa, bỏ tính năng hoặc đổi phương án. Xác định lỗi ở input, nguồn, retrieval, logic, quyền, model hay UX trước khi thêm framework/model/agent.

Có thể ưu tiên phương án theo giá trị cho người dùng, khả thi, khả năng kiểm và giá trị AI bổ sung. Ghi bằng chứng bên cạnh điểm; điểm thiết kế không phải xác suất thành công. Không dùng tổng điểm để che một cổng bắt buộc chưa đạt.

## Các hướng sản phẩm có thể phát triển

Đây là ví dụ thiết kế, không phải dữ liệu thị trường, đề thi chính thức hay sản phẩm đã hoạt động.

| Nhóm | Hai hướng sử dụng | Điều kiện cần kiểm sớm | Kết quả quyết định |
| --- | --- | --- | --- |
| Hiểu ảnh/tài liệu | Đọc hóa đơn; phân loại đồ vật theo quy tắc tiếp nhận | OCR/vision, nhãn trường, danh mục/quy định đúng nơi | Trường quan trọng đúng và người dùng sửa được |
| Voice tiếng Việt | Hướng dẫn thủ tục; luyện phản ứng trước tình huống lừa đảo | Clip thật, codec, nguồn đã kiểm, hội thoại có giới hạn | Hoàn thành tác vụ bằng nghe/nói, không chỉ TTS hay |
| Công cụ nội dung | Bộ giới thiệu sản phẩm; cập nhật chiến dịch khi hồ sơ đổi | Facts, quyền tài sản, dependency giữa facts và output | Tạo lại nội dung mới đúng facts, không sót dữ kiện cũ |
| Hỏi đáp số liệu | Phân tích có bằng chứng; mô phỏng phương án | Schema, định nghĩa chỉ tiêu, oracle, giả định mô phỏng | Số/đơn vị/kỳ/quyền đúng, giả định tách khỏi quan sát |
| Học tập/game | NPC luyện hội thoại; điều tra kiến thức theo nhánh | Luật/state, học liệu, rubric, nhóm tuổi | Hành động người học thay đổi phản hồi/tiến trình |
| Bot trên kênh chat | FAQ và chuyển người; thảo luận thành việc cần duyệt | Tài khoản test, webhook, chữ ký, token và quyền kênh | Nhận/gửi thật, không trùng, không vượt quyền |
| Tác phẩm nội dung | Chuyện nghề địa phương; câu chuyện hai kết cục | Tư liệu, biên tập, quyền sử dụng, xuất file | Tác phẩm hoàn chỉnh, có kiểm nội dung và media |

Công cụ tạo nội dung là ứng dụng dùng lại; tác phẩm nội dung là đầu ra hoàn chỉnh. Ảnh trang trí không chứng minh ứng dụng hiểu ảnh. Web chat riêng không chứng minh bot chạy trên một kênh bên ngoài. Hư cấu là hợp lệ trong game/truyện được ghi rõ; không được dùng làm dữ kiện đo lường hoặc bằng chứng đã chạy.

## Bản đồ yêu cầu → kiến trúc tối thiểu

| Yêu cầu | Bắt đầu bằng | Chỉ thêm khi có bằng chứng |
| --- | --- | --- |
| Viết lại/diễn đạt facts | LLM + schema + kiểm facts | Router/few-shot khi có nhóm lỗi ổn định |
| Hỏi tài liệu riêng | Parser + nguồn/ACL/version + retrieval | Vector/hybrid/reranker khi lookup hoặc search chưa đủ |
| Tổng hợp/đối soát | SQL tham số hóa hoặc hàm cố định + typed result | NL2SQL khi templates không phủ nhu cầu có thật |
| Nhiều bước hữu hạn | Hàm/state machine + lưu state nếu cần | Framework graph khi nhánh/resume làm code phức tạp |
| Tác vụ cần chọn tools linh hoạt | Một agent với registry hẹp | Nhiều agent khi vai trò/context độc lập và có lợi ích đo được |
| Job lâu/ingest/media | Bảng job bền + worker có deadline | Queue riêng khi tải/concurrency đòi hỏi |
| Ghi hoặc gửi ra ngoài | Prepare → kiểm quyền/duyệt theo nghiệp vụ → commit/outbox | Channel adapter khi thật sự có kênh trong phạm vi |
| Học tập cá nhân hóa | Rubric + lịch sử kỹ năng + quy tắc chọn bài | Mô hình học tập khi có dữ liệu và eval tiến bộ |
| Bất thường | Validation + rule + thống kê | ML khi lịch sử/nhãn/temporal eval chứng minh giá trị |

Một cách triển khai tham khảo là UI React/TypeScript, backend hiện có hoặc Python/FastAPI, schema validation, PostgreSQL và log JSON. Có thể giữ backend Node nếu đội đã dùng tốt; không tạo hai backend chỉ vì các ví dụ dùng hai ngôn ngữ. Database/vector index/parser/framework là lựa chọn của dự án, không phải dependency bắt buộc của starter. Trước khi cài, kiểm phiên bản, tài liệu chính thức, license, egress và runtime thực tế.

## Ví dụ: tiếp nhận yêu cầu sửa thiết bị

Giả thuyết cần kiểm: người báo thiếu mã/phòng/triệu chứng, khiến bộ phận tiếp nhận phải hỏi lại. Baseline là form có trường bắt buộc. Phương án hẹp: mô tả tự nhiên → AI đề xuất trường → backend tra danh mục → người dùng sửa → xác nhận theo nghiệp vụ → tạo ticket → xem trạng thái.

Nguồn sự thật gồm danh mục thiết bị, roles, drafts, tickets và revision. AI không tự tạo mã thiết bị, tự gán người xử lý hoặc nói “đã sửa xong”. `extract_request` trả trường đề xuất, đoạn bằng chứng và trường thiếu. `resolve_asset` trả ứng viên trong quyền. `prepare_ticket` tạo payload có revision. `create_ticket` kiểm quyền/version/idempotency. `get_ticket` kiểm quyền đối tượng ở mọi lần đọc.

MVP chỉ cần một nhóm người dùng, một danh mục hẹp và nhập chữ. Chưa cần RAG nếu tác vụ không tra tài liệu; chưa cần vector DB để tạo ticket. Nếu model lỗi, giữ draft và cho dùng form; báo đúng rằng extraction AI chưa thành công. Mất mạng sau commit hoặc bấm hai lần phải trả cùng ticket, không tạo bản thứ hai.

Oracle do người phụ trách xác nhận: trường đúng, phần cần hỏi, ứng viên hợp lệ, nhóm tiếp nhận được chấp nhận. Đo thời gian tiếp nhận, task success, số lượt hỏi bổ sung, lỗi quyền/trùng và cost. Chỉ thêm voice nếu gõ là điểm nghẽn, thêm RAG nếu cần hướng dẫn có nguồn, thêm tìm trùng nếu lịch sử cho thấy vấn đề đó đáng giải.

## Đầu ra cần có trước bàn giao

Problem brief và baseline; một sơ đồ luồng; data/tool/state contracts; capability thực đã kiểm; ca nghiệm thu/oracle; lệnh chạy lại; report có phiên bản và giới hạn. Ghi rõ ai chịu trách nhiệm dữ liệu, hành động và phản ánh của người dùng. Một bài học/lab, thư viện cài được hoặc demo của dự án khác không thay bằng chứng của sản phẩm hiện tại.
