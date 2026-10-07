---
name: product-campaign-generator
description: Lập kế hoạch, triển khai hoặc rà soát ứng dụng tái sử dụng tạo bài viết, ảnh và video có giọng đọc từ hồ sơ sản phẩm đã xác nhận. Dùng cho Gian hàng có tiếng nói/E1; không dành cho một bộ nội dung làm sẵn hoặc tự đăng quảng cáo lên mạng xã hội.
---

# Công cụ tạo bộ quảng bá sản phẩm

## Phạm vi và chế độ

Luồng: nhập sản phẩm → bổ sung phần thiếu → duyệt facts → sinh nội dung → sửa/duyệt → render và xuất trong app.
Đầu ra là ứng dụng có thể dùng lại với sản phẩm mới; một bộ media làm sẵn không chứng minh yêu cầu này.
MVP tham khảo: một ngành hàng, hai mẫu ảnh, một mẫu video 30 giây và một giọng TTS.
Giữ phạm vi/stack/provider người dùng đã chọn; nhiều tỷ lệ/ngôn ngữ/cảnh video sinh là mở rộng sau nghiệm thu.

- **Lập kế hoạch:** khảo sát repo và thiết kế pipeline/contracts/oracle; không tự tạo app hoặc gọi dịch vụ sinh media mất phí.
- **Triển khai:** hoàn thành luồng trong phạm vi được giao; giữ quyền tạo file tách với quyền công bố ra ngoài.
- **Review:** kiểm facts, quyền asset, duyệt và job lifecycle; chỉ sửa artifact khi yêu cầu bao gồm cập nhật.

## Đọc trước và khám phá

Đọc [hợp đồng tác vụ](references/task-contract.md) và [hướng dẫn kỹ thuật](references/techstack-guide.md), phần E1, media/jobs, quyền và eval.
Đọc [bàn giao kế hoạch](references/planning-handoff.md) khi cần chuyển thành gói thực thi cho agent mới.

Tìm bằng chứng trước khi yêu cầu bổ sung:

- Người dùng/doanh nghiệp, ngành hàng, nơi dùng file, định dạng/kích thước/thời lượng, giọng và brand assets đã chọn.
- Hồ sơ sản phẩm thật: tên, giá/currency, quy cách/đơn vị, điểm khác biệt, công dụng/chứng nhận có nguồn.
- Ai sửa facts, ai duyệt lời đọc/ấn phẩm, ai xuất; nguồn và quyền ảnh/logo/font/giọng/nhạc theo mục đích sử dụng.
- Storage, auth/tenant, worker/render, templates, adapter text/ảnh/TTS đang có và mức năng lực đã kiểm.
- Ngân sách media/eval, cơ chế retry, bảng đáp án chủ hàng duyệt và dữ liệu dev/holdout.

Khi chưa có stack, cân nhắc React/Next.js, backend typed, PostgreSQL, file storage và worker bền; giữ stack tương đương hiện có.
Giữ ảnh sản phẩm thật; sinh nền riêng nếu cần, chèn ảnh/logo/chữ tiếng Việt/giá bằng layout local.
Tác vụ BTC dùng gateway được cấp cho cả AI/judge; ngoài BTC dùng provider hợp lệ của dự án.
Vision, reference editing, strict schema và video sinh phải qua gate riêng; tên model không chứng minh khả năng đã dùng được.

## Contracts facts, assets và job

- `ProductProfile`: tenant/product_id, version, tên, price/currency, quy cách, confirmed_fields và nguồn cho từng field.
- `Claim`: claim_id, text, source_id, product_field, product_version; thiếu chứng cứ thì không được sinh như sự thật.
- `Asset`: asset_id, kind, owner/scope, source_id/version, rights, file/MIME, model/prompt version và trạng thái duyệt.
- `Campaign`: campaign_id, profile_version, brief, selected_templates, copy/image/script/audio/video asset IDs và revision.
- `Approval`: actor, payload_hash, profile/asset_version, timestamp; sửa nội dung hoặc facts liên quan làm duyệt cũ hết hiệu lực.
- `MediaJob`: job_id, owner, step, input_hash/version, status, attempt, provider_job_id, deadline, cost và output_asset_id.
- `validate_profile(profile)` → missing/unsupported/unverified fields; không tự thêm giá/chứng nhận để lấp ô trống.
- `generate_draft(campaign_id, profile_version)` → drafts/claims; `render_asset(asset_id, approved_version)` → job/output metadata.
- `export_campaign(campaign_id, revision)` kiểm scope, version và trạng thái duyệt rồi trả file do server tạo đường dẫn.

Mỗi action có schema lỗi, quota/deadline, quyền do server cấp và retry policy; model không truyền tenant/approved để tự cấp quyền.
AI viết/đề xuất hình và lời đọc; code kiểm facts, dựng layout/render và chuyển state; chủ hàng duyệt claim/lời đọc/ấn phẩm.
Không đưa bảng đáp án holdout vào prompt. Duyệt là sự kiện nghiệp vụ gắn nội dung, không là câu model nói “đã duyệt”.

## Luồng thực hiện

1. Hoàn thiện một hồ sơ thật có oracle và quyền asset; phân biệt facts với nội dung sáng tạo trước generation.
2. Kiểm text schema, ảnh trả về/MIME và TTS bytes theo provider thực; lưu trạng thái capability và bằng chứng vòng UI.
3. Nhập/sửa/lưu hồ sơ để dùng lại; hỏi đúng phần thiếu và ghi sự xác nhận của chủ nội dung.
4. Tạo bài, layout ảnh và draft lời đọc từ facts; validate giá/quy cách/claims trước preview.
5. Cho sửa và duyệt lời đọc trước TTS; duyệt nội dung xuất theo vai trò đã chốt, không thêm bước xác nhận ngoài nhu cầu nghiệp vụ.
6. Worker sinh phần còn thiếu, Pillow/SVG dàn chữ/ảnh thật, FFmpeg ghép video/phụ đề/audio; từng bước có trạng thái.
7. Preview, cho sửa từng phần, vô hiệu phần phụ thuộc khi thay facts/text; chạy lại riêng bước lỗi hợp lệ.
8. Kiểm file xuất thực, xuất bản hiện hành đã duyệt và thử sản phẩm thứ hai để chứng minh app tái sử dụng.

## State, lỗi và tài nguyên

Profile draft → needs_information → confirmed; asset draft → validated → approved → rendered/exportable, có stale/failed.
Job queued/running/completed/failed/cancelled/unknown_outcome; UI chỉ báo hoàn tất sau khi output được lưu và kiểm hợp lệ.
Timeout khi tạo media có thể đã tạo job mất phí: đối soát provider/job ledger trước retry; không tạo job mới thay polling.
Tắt auto-retry ở client/transport tạo media (OpenAI SDK `max_retries=0`); worker là lớp quyết định retry duy nhất.
Poll job có ID bằng backoff/deadline; hủy giữ lịch sử và chi phí chưa đối soát, không tự ghi 0.
Lock input version cho job; kết quả muộn của revision cũ không được duyệt hoặc thay ấn phẩm hiện hành.
Giữ phần đã duyệt khi bước khác lỗi; báo phần chưa hoàn tất, không dựng file giả hoặc đổi provider âm thầm.
FFmpeg/ffprobe dùng argv, không ghép shell từ prompt/filename; giới hạn CPU/RAM/thời gian và output path do server cấp.
Kiểm MIME/dung lượng upload, quyền tải file và tenant; không log key/raw dữ liệu riêng. Không dùng URL tùy ý từ model.
Không bịa công dụng, chứng nhận hay lời chứng thực; không tự clone giọng hoặc dùng tài sản chưa rõ quyền.
Xuất file trong app không là quyền đăng mạng xã hội, gửi cho khách hoặc chạy quảng cáo.

## Oracle và nghiệm thu

- Chủ hàng duyệt bảng đáp án giá/quy cách/claims; khoảng 15 hồ sơ là quy mô tham khảo, có thiếu giá/chứng nhận.
- Tách hồ sơ dev/holdout; oracle độc lập với target model, nhãn tự sinh chưa được coi là đã xác minh.
- Test facts/claims, role/scope, invalidation, job resume/retry và không xuất khi chưa duyệt hoặc version cũ.
- Kiểm offline timeout tạo media chỉ phát một POST bằng transport kiểm soát; không dùng API mất phí để gây lỗi thử.
- E2E nhập → sửa → duyệt → tạo → preview → xuất; ffprobe kiểm duration/audio/codec, mở file để kiểm chữ/phụ đề.
- Chủ hàng chấm đúng sản phẩm, dễ đọc/dễ nghe; 100% fields quan trọng phải khớp oracle trên bộ nghiệm thu.
- Mục tiêu ≥80% bộ đạt 4/5 là đề xuất ban đầu, cần chốt sau baseline; không gọi là kết quả đã có.
- Sai giá, bịa chứng nhận, rò dữ liệu hoặc xuất nội dung chưa duyệt là lỗi chặn; lỗi API/timeouts vẫn nằm trong task success.
- Báo version, số mẫu, thời gian và chi phí/bộ thành công gồm retries; không có bộ thành công thì cost/success là N/A.

## Bàn giao

Giao ứng dụng/cách chạy hoặc gói kế hoạch đúng chế độ, contracts, nguồn/quyền, templates, job lifecycle và oracle.
Kế hoạch nêu phase đầu, file hiện có/dự kiến, dependency gates và ma trận yêu cầu–nghiệm thu.
Báo những capability đã kiểm, lỗi và phần chưa hoàn tất; không thay file preview bằng tuyên bố video đã xuất thành công.
