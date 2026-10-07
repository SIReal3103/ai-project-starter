---
name: btc-gateway-integration
description: "Tích hợp, kiểm hoặc sửa client API Gateway AI Thực Chiến: model được cấp, route, payload, vision, tools, schema, audio/media và quota. Chỉ dùng cho Gateway BTC; không tự thay provider dự án khác."
---

# Tích hợp Gateway BTC

Đích là một capability được kiểm qua đúng gateway, client và quyền của môi trường đang dùng. Không suy gateway hỗ trợ đầy đủ chỉ vì provider gốc hoặc SDK có chức năng đó.

## Bắt đầu không cần lịch sử chat

Đọc [hợp đồng nhận việc](references/task-contract.md), rồi phần 4 và 15 trong [nguồn đi kèm](references/techstack-guide.md). Nếu chỉ lập kế hoạch, dùng [hợp đồng kế hoạch](references/planning-handoff.md), bàn giao phép kiểm và phần phụ thuộc; không gửi request tốn phí. Review-only trả findings; sửa client khi nhiệm vụ cho phép.

Tìm client đang dùng, route cấu hình, lockfile/SDK version, đường sync/async/stream, retry layers, consumers và test harness. Xác định capability mà sản phẩm thực sự cần, credential role và budget/quota đã được cấp. Chỉ kiểm key có/không hoặc để ứng dụng dùng qua môi trường; không in key, headers xác thực hoặc toàn bộ key/team response.

Nếu chưa có key hoặc quyền live, làm validation client/transport local và ghi capability `untested`/`unavailable`; không giả response thành smoke đã thành công. Quyền coding agent và inference không được mặc định là một key/hạn mức.

## Quy trình tích hợp

1. Giữ client ở backend, host BTC cố định theo cấu hình được xác nhận. Snapshot nguồn dùng `https://api.thucchien.ai`; route không đồng loạt thêm `/v1`. Kiểm tài liệu BTC hiện hành khi sửa hợp đồng API; không gọi provider trực tiếp để thử thay.
2. Chọn model từ quyền hiện có và phép thử tác vụ; tên model/giọng/giá trong nguồn chỉ là ứng viên. Tạo capability record gồm model, endpoint, payload version, SDK, ngày, phạm vi quyền và trạng thái kiểm.
3. Tạo adapter cho endpoint cần dùng. Responses và Chat có payload/response/tool protocol riêng; không hoán đổi tham số reasoning hoặc output token giữa hai đường. Parse status, incomplete/refusal/error trước khi coi output dùng được.
4. Dùng input được phép của chính tác vụ để smoke có hạn mức. Kiểm một ca thành công, input sai, timeout và output chưa hoàn tất. HTTP 200 hoặc JSON parse được không phải nghiệm thu hành vi.
5. Chỉ bật capability sau khi trọn vòng thật đạt. Ghi request ID đã che, expected/actual và giới hạn; không lưu prompt/ảnh/base64 nhạy cảm mặc định.
6. Nối consumer vào typed result và lỗi đúng loại. Cập nhật tests, config và cách chạy; giữ feature không đạt ở trạng thái chưa khả dụng, không tự chuyển provider.

## Hợp đồng cần kiểm theo capability

| Capability được chọn | Chứng minh tối thiểu | Khi không đạt |
|---|---|---|
| Text | Đúng tiếng Việt/dữ kiện, finish/status, token limits và đường async nếu có | Giữ lỗi/incomplete; không dùng text bị cắt như đã xác nhận |
| Native tools | Schema → call name/args/ID → backend validate/execute → matching tool output → model tiếp tục | Giữ protocol đầy đủ; workflow chỉ thay khi vẫn đúng đề và gọi đúng tên |
| Structured output | Schema, missing fields, refusal/truncation, nghiệp vụ độc lập | JSON mode không thành strict schema; sửa có giới hạn rồi báo lỗi |
| Vision | Ảnh thật rõ/mờ/nhúng lệnh, bytes/MIME đúng, đối chiếu field nhìn thấy | Không suy từ endpoint sinh ảnh; OCR-only không được gọi là native vision |
| Embedding | Một input trước; batch khác nội dung có đủ vectors/index/dimensions/finite values | Không gộp nhầm vector, không giữ index model khác |
| STT/TTS | File từ browser đích, codec thật, transcript/âm thanh dùng được | Không đổi đuôi giả codec; rỗng khác thành công; TTS trả binary |
| Ảnh/video | Đúng tài sản đầu ra; job ID/state/download; bytes/MIME và quyền | Timeout tạo job là unknown outcome, không tạo lại mù |
| Moderation/search | Schema/citations/metadata thực tế; policy mapping và quyền | Moderation không thay auth/độ đúng; search thiếu nguồn không được bịa |

Với Responses tools, dùng call_id đúng và giữ các output items giao thức cần, kể cả reasoning items nếu có; không hiển thị suy nghĩ nội bộ. Với Chat, giữ tool_calls và role=tool tương ứng. `previous_response_id`, strict mode, ảnh đầu vào/editing và realtime phải kiểm riêng.

## Lỗi, quota và ranh giới

- Chỉ một lớp retry. Với tạo media hoặc thao tác có tác động, tắt transport/SDK auto-retry; đối soát outcome trước thử lại. Retry đọc có deadline/budget, 429 tốc độ khác hết ngân sách; 401/403 không retry vô hạn.
- Kiểm host/redirect/timeout trên cả HTTP sync và async; custom plugin/embedding/judge là đường gọi riêng cần rà. Raw client được chọn nếu adapter làm mất metadata cần dùng.
- Bind credential và model allowlist ở server; browser không chọn provider/base URL hoặc mở quota. Cost thiếu là unknown/ước tính có nhãn, không bằng 0.
- Không chạy load live hoặc hàng loạt capability không cần thiết để xác nhận một endpoint. Chỉ dùng ngân sách đã được cấp; nếu đổi yêu cầu bắt buộc thì trình ảnh hưởng cho người dùng.

## Nghiệm thu và bàn giao

Kiểm offline request/response/error mapping bằng transport kiểm soát, đặc biệt một timeout tạo video chỉ phát một POST. Kiểm live riêng cho capability bắt buộc khi có quyền; báo rõ offline không chứng minh gateway thực. Không đánh dấu verified nếu output chưa hoàn tất nghiệp vụ hoặc chưa thử đúng key/model/client.

Bàn giao client/config task-scoped, dependency versions, biến môi trường chỉ tên, lệnh đã thử, capability matrix và lỗi chưa xử lý. Agent tiếp theo phải biết endpoint nào đã dùng được, cái nào chỉ documented và cách tái chạy với input có quyền. Không cần xây app mới để bàn giao một bản sửa adapter.
