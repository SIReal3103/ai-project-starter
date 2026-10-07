---
name: versioned-campaign-updates
description: Lập kế hoạch, triển khai hoặc rà soát công cụ cập nhật chiến dịch theo phiên bản hồ sơ sản phẩm, truy vết claim–ấn phẩm và vô hiệu bản cũ khi facts đổi. Dùng cho Chiến dịch luôn đúng/E2; không dành cho tối ưu doanh thu hay tự xuất bản nội dung.
---

# Cập nhật chiến dịch theo phiên bản

## Phạm vi và chế độ

Luồng: hồ sơ → chiến dịch đa định dạng → đổi facts → xem ấn phẩm bị ảnh hưởng → tái tạo chọn lọc → duyệt mới → xuất.
Giá trị chính là không sót dữ kiện cũ trong bài, ảnh, lời đọc và phụ đề; cần kiểm quan hệ phụ thuộc bằng code.
MVP tham khảo: năm sản phẩm, ba định dạng, thay giá/trọng lượng/hạn ưu đãi; giữ phạm vi người dùng đã chọn.
Tối ưu doanh thu, tự chọn chiến lược và kết nối xuất bản chưa thuộc MVP này.

- **Lập kế hoạch:** thiết kế version/dependencies/race handling và bộ oracle; không tự sửa app hoặc chạy media mất phí.
- **Triển khai:** làm luồng đã chốt trên stack/provider hiện có; không thay mô hình duyệt hay quyền xuất của chủ sản phẩm.
- **Review:** tái hiện việc cập nhật/xuất và kiểm bằng oracle; chỉ sửa artifact khi được giao cập nhật.

## Đọc trước và khám phá

Đọc [hợp đồng tác vụ](references/task-contract.md) và [hướng dẫn kỹ thuật](references/techstack-guide.md), phần E2, state, media jobs và eval thay đổi.
Đọc [bàn giao kế hoạch](references/planning-handoff.md) khi tạo gói thực thi; không phụ thuộc skill E1.

Khảo sát repo và dữ liệu để xác định:

- Product/campaign/asset schemas, file export, pipeline text/ảnh/TTS/render, version và approval hiện có.
- Trường thay đổi, currency/đơn vị/múi giờ, thời điểm hiệu lực, ý nghĩa xóa nguồn và hết ưu đãi.
- Ai sửa/duyệt/xuất; scope doanh nghiệp; quy tắc nhiều người sửa đồng thời và lịch sử cần giữ.
- Đồ thị nguồn–field–claim–ấn phẩm, gồm chữ trên ảnh, lời đọc, phụ đề và media đã render.
- Hồ sơ/tài sản thật, nguồn và quyền; editor có thể lập bảng tác động độc lập và owner xử lý luật thiếu.
- Provider, worker, khả năng truy vấn job, retry/budget và cách kiểm trước tải file; không suy có sẵn khi chưa thấy.

Giữ stack hiện có nếu đáp ứng; PostgreSQL, storage và worker bền là phương án khởi đầu khi chưa có kiến trúc.
AI chỉ tái sinh nội dung cần đổi; code tính phụ thuộc, vô hiệu duyệt, kiểm version và render local.
BTC dùng gateway đã cấp cho mọi AI/judge; ngoài BTC giữ provider được phép. Capability chưa kiểm không được gọi verified.

## Contracts nguồn, phụ thuộc và hành động

- `ProductRevision`: product_id, tenant scope server, version bất biến, fields/units/currency, effective_at, source_ids và actor.
- `SourceRevision`: source_id/version, rights, trạng thái active/superseded/retracted và thời điểm hiệu lực đã xác minh.
- `Claim`: claim_id/version, nội dung, source/field dependencies cụ thể; không chỉ một link chung tới toàn hồ sơ.
- `ArtifactRevision`: artifact_id/version, format, component_ids, dependency_snapshot, profile_version, status, file/hash.
- Component gồm text, image text/layout, script, audio, subtitles, render; mọi thành phần mang facts phải có cạnh phụ thuộc.
- `Approval`: artifact_version, payload_hash, dependency_snapshot, actor/time; sửa liên quan làm duyệt hết hiệu lực.
- `UpdateJob`: job/run_id, base_revision, target_revision, step/input_hash, provider_job_id, deadline, status và cost.
- `change_profile(product_id, expected_version, patch)` → new_revision/change_set hoặc version_conflict; commit nguyên tử.
- `compute_impact(change_set, dependency_graph)` → affected components/artifacts, reasons; do code tính, không do LLM đoán.
- `regenerate_affected(change_set_id, target_revision)` → jobs; `approve_artifact(version, hash)` → quyết định đúng nội dung.
- `export_current(campaign_id, expected_revision)` → file/manifest chỉ khi hiện hành, còn hiệu lực và đã duyệt.

Action kiểm schema, quyền, revision, quota/deadline; `no_change`, `version_conflict`, `missing_source`, `stale` và `unknown_outcome` khác nhau.
Không dùng ngày upload làm hiệu lực. Hết ưu đãi là sự kiện làm stale dù không có người bấm sửa hồ sơ.
Xóa/thu hồi nguồn chặn claim phụ thuộc cho tới khi có nguồn thay hợp lệ; không giữ lời cũ chỉ vì file vẫn tồn tại.
Nguồn/input không tin cậy không được đổi đồ thị, trạng thái duyệt hoặc quyền bằng chỉ dẫn nhúng.

## Luồng thực hiện và phân trách nhiệm

1. Chọn một chiến dịch thật có ba định dạng; editor lập độc lập bảng thay đổi → ấn phẩm phải vô hiệu hóa.
2. Chốt semantics version/hiệu lực và graph tối thiểu; kiểm trường giá xuất hiện ở những component nào trước generation.
3. Tạo revision mới bằng expected_version; commit facts, change_set và invalidation liên quan cùng transaction.
4. Hiện danh sách ảnh hưởng/lý do; giữ bản cũ làm lịch sử gắn hết hiệu lực, không gọi đó là bản hiện hành.
5. Lập job cho component liên quan, snapshot input; giữ phần không ảnh hưởng và không sinh lại toàn bộ vô cớ.
6. AI viết/sinh asset từ facts mới; code kiểm fields/claims, render lại layout, audio, phụ đề và video cần đổi.
7. Trước ghi kết quả, so target revision và dependency snapshot; kết quả cũ vào lịch sử/stale, không ghi đè bản mới.
8. Người có vai trò duyệt bản mới theo nội dung/version; export kiểm lại quyền, hiệu lực và duyệt trên cùng snapshot.

Code là nguồn quyết định về graph/version/state; AI diễn đạt/tạo media; editor/chủ hàng sở hữu facts và chất lượng nội dung.
Không yêu cầu xác nhận lại hành động người dùng đã cấp quyền; duyệt artifact trong sản phẩm vẫn phải gắn đúng payload/version.
Không giữ transaction DB mở trong lúc chờ AI; dùng optimistic concurrency hoặc khóa ngắn theo mẫu hiện có.

## State, races và recovery

Artifact draft → validated → approved → exportable; facts/source đổi → stale, sau tái sinh trở về draft cần duyệt mới.
Khi người dùng đổi liên tiếp A→B→C, job B không thể biến B thành hiện hành hoặc phục hồi approval A.
Kiểm version khi enqueue, hoàn tất, duyệt và xuất/tải; chỉ kiểm lúc render bắt đầu không chống thay giá giữa render.
Export tạo manifest snapshot nguyên tử; nếu revision đổi trước phát hành file thì báo stale và tạo bản đúng theo yêu cầu đã giao.
Giữ history có quyền đọc; lịch sử/export URL cũ không được trình bày như chiến dịch còn hiệu lực.
Job queued/running/completed/failed/cancelled/unknown_outcome; resume đối chiếu ledger/output trước làm lại.
Timeout tạo media phải đối soát outcome; tắt retry tự động ở client/transport tạo media, chỉ worker quyết định retry.
Poll provider job ID theo backoff/deadline; không tạo POST mới thay polling, không ghi chi phí hủy/chưa biết thành 0.
AI/render lỗi giữ phần hợp lệ và đánh dấu phần stale; không xuất bộ pha trộn facts mới/cũ để báo hoàn tất.
FFmpeg dùng argv, output path do server tạo, có cap CPU/RAM/time; upload/download kiểm MIME, scope và quyền asset.
Nếu không biết một component phụ thuộc facts nào, đánh dấu chưa đủ căn cứ xuất và hoàn thiện mapping, không giả định không ảnh hưởng.
Ngân sách cạn dừng sinh tùy chọn; không chuyển provider hoặc dùng dữ liệu giả. Xuất không cấp quyền tự đăng bên ngoài.

## Oracle và nghiệm thu

- Editor lập bảng impact độc lập trước chạy; so toàn bộ quan hệ bị ảnh hưởng và phần không nên đổi, không chỉ tổng số.
- Có đổi liên tiếp, sửa đồng thời, xóa nguồn, hết ưu đãi, chỉnh trong lúc render/duyệt/xuất và lỗi AI.
- Chốt oracle cho giá/currency, trọng lượng/đơn vị, hạn ưu đãi/múi giờ ở text, ảnh, lời đọc và phụ đề.
- Test graph/invalidation, expected_version, quyền tenant, approval cũ, idempotency, resume và late results.
- Test offline timeout tạo media chỉ một POST; E2E facts đổi → impacted list → tái sinh → duyệt → file xuất thật.
- Đối chiếu 100% quan hệ ảnh hưởng trên bộ nghiệm thu; mọi thay đổi quan trọng thu hồi duyệt của ấn phẩm phụ thuộc.
- Giá cũ trong bản xuất mới, lọt bản hết hiệu lực, approval sai version hoặc lẫn doanh nghiệp là lỗi chặn bàn giao.
- Người kiểm chấm tự nhiên; mốc ≥4/5 là mục tiêu đề xuất cần chốt, không là kết quả hoặc chuẩn BTC.
- Báo recall thay đổi, thông tin cũ còn sót, sửa nhầm, số mẫu/version, lỗi/timeouts và cost/chiến dịch thành công gồm retry.

## Bàn giao

Giao graph/data/action/state contracts, nguồn/owner, chính sách hiệu lực, cách cập nhật/demo, oracle và bằng chứng export.
Kế hoạch nêu file hiện có/dự kiến, phase đầu đủ điều kiện, phụ thuộc chưa giải quyết và ma trận yêu cầu–nghiệm thu.
Review nêu ca race/version cụ thể; implementation báo rõ offline/integration/holdout và capability chưa kiểm.
Không dùng vài bản xuất đẹp làm bằng chứng hệ thống không bỏ sót phụ thuộc.
