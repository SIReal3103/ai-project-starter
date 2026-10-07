# Cấu hình provider và kiểm capability

Starter không buộc dùng một provider, một gateway, một model hay một ví ngân sách. Chọn profile cho từng sản phẩm và kiểm cả đường target, embedding, moderation, STT/TTS, sinh dữ liệu, LLM judge, plugins và telemetry.

**Tài liệu này không xác nhận endpoint/model/giá/quota đang hoạt động.** Cấu hình được cung cấp bởi người vận hành; tài liệu chính thức hiện hành và probe trên đúng môi trường quyết định capability được bật. Dùng [hợp đồng adapter của eval kit](../../tools/evals/agent-guide.md) để nối sản phẩm, không sao chép key vào hướng dẫn.

## Một profile cần ghi gì?

| Trường | Nội dung cần có |
| --- | --- |
| Định danh | Tên profile, môi trường, owner, phiên bản cấu hình |
| Đích được phép | Base URL, giao thức, allowlist host, redirect policy |
| Credentials | Tên biến môi trường/secret reference; không có giá trị key |
| Tác vụ | Text, tools, structured output, embedding, vision, STT, TTS, search, image/video |
| Model và adapter | ID thực được cấp, endpoint, SDK/HTTP adapter và phiên bản |
| Hạn mức | Calls/token/concurrency/chi phí, số dư hoặc trần được cấp |
| Dữ liệu | Loại được gửi, bên xử lý, lưu trữ/retention cần xác minh |
| Khôi phục | Timeout, retry, error mapping; provider thay thế chỉ nếu nằm trong cấu hình được phép |
| Bằng chứng | Ngày, môi trường, probe, trạng thái, request ID an toàn và giới hạn |

Không suy hậu tố URL theo tên SDK. Endpoint tương thích Chat Completions và Responses có thể có payload, streaming, tool continuation và metadata khác nhau. Kiểm request thực của đúng adapter. Module AI client chỉ phía server; key không xuất hiện trong frontend, URL, CLI arguments, trace hay dataset.

## Trạng thái capability

| Trạng thái | Ý nghĩa |
| --- | --- |
| `documented` | Đã tìm hợp đồng ở tài liệu chính thức; chưa phải bằng chứng chạy |
| `untested` | Chưa kiểm trên cấu hình mục tiêu |
| `verified` | Probe đúng phạm vi thành công; có evidence và ngày/version |
| `failed` | Đã thử nhưng không đạt; giữ nguyên lỗi đã quan sát |
| `unavailable` | Thiếu quyền, cấu hình, runtime hoặc tính năng để chạy |

Lưu documentation và runtime status riêng nếu cần: một capability vừa có tài liệu vừa có lần chạy thất bại. Cờ `enabled=true` chỉ là quyết định cấu hình, không phải chứng cứ. Khi đổi model/endpoint/SDK/quyền, xem lại những probe bị ảnh hưởng.

## Probe nhỏ trước khi tích hợp rộng

1. Kiểm cấu hình offline, thiếu biến, host guard, response schema, deadline và redaction. Không in toàn bộ environment.
2. Đặt trần request, dữ liệu thử được phép và ngân sách. Một text response phải thật sự hoàn tất, không chỉ HTTP 200 hoặc socket đóng.
3. Với tools: gửi schema → nhận tên/args/call ID → kiểm và gọi tool thật → gửi kết quả đúng ID → nhận câu trả lời cuối. Kiểm args sai, nhiều calls, tool lỗi và history/continuation.
4. Với embedding: kiểm số lượng, indices không trùng/thiếu, đúng thứ tự input, dimension đúng, số hữu hạn; cosine không nhận zero vector. Cùng cấu hình dùng lúc index/query.
5. Với STT/TTS: audio do browser đích thu, MIME/codec thật, transcript không rỗng, audio trả về giải mã/phát được. Kiểm số/ngày/tên, timeout và giới hạn file.
6. Với vision/structured output: input hợp lệ và lỗi, schema/null/field mơ hồ; không lấy khả năng model gốc làm bằng chứng gateway hỗ trợ.
7. Với search/media jobs: kiểm citations/metadata, job ID, terminal state, quyền tải artifact, lỗi và unknown outcome. Không tạo lại job tính phí khi kết quả request trước chưa rõ.
8. Ghi version, mode, số calls, latency, usage/cost nếu có và những gì chưa kiểm. Smoke một đường không xác nhận các đường còn lại.

## Profile BTC — tùy chọn

Chỉ áp dụng khi dự án được giao chạy trong môi trường BTC. Đây là phần tổng hợp kinh nghiệm từ hướng dẫn nguồn; không kế thừa trạng thái “đã xác nhận” của tài liệu cũ.

- Xác nhận hợp đồng hiện hành với BTC, tài khoản/quyền, model, đường dẫn endpoint và giới hạn thực trước khi cấu hình.
- Nếu quy chế yêu cầu mọi inference qua gateway BTC, áp dụng cho cả target, ingest embedding, judge, generator, moderation và voice/media. Không tự chuyển sang provider trực tiếp khi gặp lỗi.
- SDK mang tên một nhà cung cấp chỉ là client; không tự cấp quyền gọi nhà cung cấp đó. Rà mặc định của framework, hosted search, plugin, vector store và các model phụ.
- AI logging của môi trường phát triển và audit log sản phẩm là hai hệ thống khác nhau. Nếu nơi tổ chức cung cấp hook/log bắt buộc, làm theo quy tắc tại nơi đó. Starter không chứa, cài hay giả định hook từ workspace nguồn.
- Chỉ gửi dữ liệu được phép. Đi qua một gateway không chứng minh vị trí lưu trữ, thời hạn giữ, việc dùng để huấn luyện hay nghĩa vụ dữ liệu đã được giải quyết.
- Nếu có các quota/ví code/runtime riêng, ánh xạ theo thông tin thực của tài khoản. Hai tên biến hoặc hai key không tự có nghĩa là hai ngân sách độc lập.
- Capability chưa qua probe giữ tắt; tiếp tục workflow có schema, SQL local hoặc text đã kiểm nếu vẫn đáp ứng yêu cầu. Không giả lập capability để demo.

Không có giá USD, model mặc định hay quota cố định của BTC trong starter vì chúng cần xác minh tại thời điểm dùng.

## Chi phí và lỗi

Trước run: ước lượng tất cả calls, output/reasoning tối đa và jobs; giữ chỗ ngân sách cho run đang chạy. Sau run: đối soát usage/cost thực, gồm retry và lỗi có thể tính phí. Thiếu cost metadata ghi `unknown` hoặc ước tính có phương pháp, không ghi 0. Cache/replay không phải inference mới.

Phân biệt thiếu quyền/cấu hình, input/codec sai, rate limit, hết budget, timeout và lỗi upstream chưa rõ. Retry có backoff chỉ cho lỗi tạm thời phù hợp trong deadline; một tầng điều khiển retry để tránh SDK × workflow nhân số calls. Abort phía client không bảo đảm upstream dừng xử lý hoặc hoàn phí. Không retry thao tác ghi/job có kết quả chưa biết trước khi tra trạng thái hoặc idempotency record.

Health/readiness thông thường kiểm local dependency và cấu hình; không gọi model tính phí mỗi lần health check. Cảnh báo theo lỗi, queue age, usage và budget; giới hạn nhiều worker cần bộ đếm chung có thao tác nguyên tử.
