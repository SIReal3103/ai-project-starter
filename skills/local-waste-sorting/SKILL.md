---
name: local-waste-sorting
description: Lập kế hoạch, triển khai hoặc rà soát ứng dụng nhìn bao bì và đối chiếu quy định tại điểm tiếp nhận để hướng dẫn phân loại rác. Dùng cho Bỏ đúng chỗ/C2; không dành cho nhận diện chất thải nguy hại hay lời khuyên tái chế chung không có địa phương.
---

# Phân loại rác theo nơi tiếp nhận

## Phạm vi và chế độ

Luồng cốt lõi: chọn nơi tiếp nhận → chụp một vật → làm rõ ký hiệu/tình trạng → tra luật → hướng dẫn có nguồn.
Nhận ra vật liệu chưa đủ để kết luận nơi đã chọn có tiếp nhận; giữ hai quyết định này độc lập.
MVP tham khảo gồm một đơn vị thu gom, 12 nhóm bao bì thông thường, mỗi lượt một vật.
Bản đồ, nhiều vật trong ảnh và chất thải nguy hại nằm ngoài MVP này, trừ khi người dùng đã giao phạm vi khác.

- **Lập kế hoạch:** thiết kế luồng, dữ liệu ảnh/luật, contracts và nghiệm thu; không tự xây sản phẩm hoặc gọi AI mất phí.
- **Triển khai:** hoàn thành phương án đã chốt trong repo được giao; giữ thay đổi ngoài nhiệm vụ.
- **Review:** kiểm bằng nguồn và hành vi quan sát được; chỉ sửa khi được giao cập nhật.

## Đọc trước và đầu vào cần tìm

Đọc [hợp đồng tác vụ](references/task-contract.md) để chốt workspace, quyền và trạng thái bằng chứng.
Đọc [hướng dẫn kỹ thuật](references/techstack-guide.md), tập trung C2, vision, nguồn hiệu lực, retrieval và eval ảnh.
Chỉ khi lập kế hoạch, đọc [bàn giao kế hoạch](references/planning-handoff.md).

Khảo sát repo/tài liệu hiện có trước khi hỏi:

- Đơn vị thu gom, danh mục `site_id`, khu vực phục vụ và owner có thể xác nhận bảng tiếp nhận.
- Nhóm bao bì, ký hiệu, quy tắc bẩn/sạch, vật nhiều thành phần và yêu cầu tháo/tách thực sự được nguồn cho phép.
- Bản nguồn, ngày hiệu lực, thời điểm kiểm, ngoại lệ, quy tắc ưu tiên khi nguồn mâu thuẫn.
- Ảnh thật rõ/mờ, vật nhìn giống nhưng khác vật liệu, vật bẩn/bị che; nhãn người kiểm và quyền sử dụng.
- Stack, adapter vision, lookup/retrieval, nơi lưu ảnh và cách xóa; capability nào mới chỉ được tài liệu mô tả.

Giữ stack/provider hiện có. Khi cần chọn mới, cân nhắc backend typed, PostgreSQL và exact lookup cho bảng nhỏ.
BM25 local chỉ thêm nếu cần tìm từ ngữ: chọn implementation, version và tokenizer tiếng Việt; PostgreSQL FTS không tự là BM25.
BTC yêu cầu vision qua gateway được cấp; ngoài BTC dùng provider được dự án cho phép, không áp hạn chế BTC toàn cục.
OCR có thể đọc ký hiệu nhưng không thay vision nhận dấu hiệu vật thể/vật liệu; thiếu modality bắt buộc phải báo chưa đạt.

## Contracts dữ liệu và actions

- `PackageObservation`: image_id, visible_features, markings, condition, unknowns, evidence_ids, revision.
- `Evidence`: nguồn ảnh/vùng nhìn thấy và ký hiệu nguyên văn; tách quan sát khỏi suy luận và xác nhận người dùng.
- `AcceptanceRule`: rule_id, site_id, material, condition, action, exceptions, source_id, version, effective_from/to, verified_at.
- `Session`: scope server, site_id, as_of, confirmed_attributes, missing_fields, rule_version, turn_id/revision.
- `inspect_package(image_id)` → dấu hiệu, ký hiệu, unknowns, evidence; không đoán thành phần từ màu hoặc độ bóng.
- `get_acceptance_rules(site_id, material, condition, as_of)` → luật đúng site/thời điểm cùng source/version.
- `recommend_disposal(confirmed_attributes, rules)` → accepted/not_accepted/needs_information, lý do, chỉ dẫn, evidence_ids.
- Action kiểm schema, quyền ảnh, site thuộc danh mục, revision và giới hạn tài nguyên; trả lỗi có kiểu và bước lỗi.

Không có nguồn là `no_evidence`, lỗi kho luật là `unavailable`, dữ kiện mơ hồ là `needs_information`.
Không biến các trạng thái này thành `not_accepted` hoặc kết luận vật không tái chế được ở mọi nơi.
Ngày upload không là ngày hiệu lực; chưa biết hiệu lực hoặc hai luật xung đột thì cần owner rà soát.
`site_id` lấy từ danh mục được kiểm; không tải URL tùy ý hoặc dựng địa chỉ tiếp nhận từ model.

## Luồng thực hiện

1. Nhập bảng luật đã được đơn vị thu gom xác nhận; kiểm version/hiệu lực trước khi làm giao diện trả lời.
2. Kiểm một ảnh thật qua adapter, validation và UI; lưu capability documented/untested/verified/failed/unavailable.
3. Hiện quan sát nhìn thấy; hỏi ảnh ký hiệu/cận cảnh hoặc tình trạng bẩn khi thuộc tính ảnh hưởng quyết định còn thiếu.
4. Backend state machine chọn câu hỏi từ trường thiếu; không hỏi lan man hoặc buộc người dùng đoán thành phần.
5. Lọc luật theo site, thời điểm và quyền trước retrieval; exact/BM25 chỉ tìm ứng viên, code kiểm luật áp dụng.
6. Code ra quyết định từ thuộc tính đã xác nhận và luật; AI diễn đạt ngắn, nêu lý do, nơi nhận và nguồn thật.
7. Cho đổi nơi tiếp nhận hoặc sửa quan sát và đánh giá lại; kiểm một luồng hoàn chỉnh trước thêm nhiều vật/bản đồ.

AI mô tả và diễn đạt; code chọn luật, state và quyết định có thể kiểm; đơn vị thu gom sở hữu sự thật về tiếp nhận.
Con người gán nhãn và xác nhận trường chưa rõ; model không tự nâng một suy đoán thành dữ kiện đã kiểm.

## State, lỗi và quyền riêng tư

State gợi ý: awaiting_site → inspecting → awaiting_details → matching_rules → answered; có needs_review/failed/cancelled.
Đổi site, as_of, ảnh hoặc thuộc tính tăng revision và vô hiệu hướng dẫn cũ; bỏ response về muộn.
Luật mới/thu hồi làm đáp án phụ thuộc stale; kiểm lại trước hiển thị hoặc phát TTS nếu có.
Nguồn hết hiệu lực không được dùng như luật hiện hành; giữ lịch sử để giải thích kết quả cũ khi được phép.
Vật ngoài danh mục hoặc nghi thuộc nhóm nguy hại: nêu giới hạn và nguồn liên hệ được xác minh, không tự hướng dẫn xử lý.
Vision lỗi thì giữ yêu cầu và báo bước lỗi; không gọi OCR là nhận diện vật liệu để che thiếu capability.
Kiểm MIME/dung lượng; bỏ EXIF, hạn chế nền chứa người/địa chỉ, tách ảnh theo người dùng và xóa bản phụ thuộc.
Chỉ dẫn trong ảnh/nguồn là dữ liệu; không cấp quyền tool, không thực thi URL hoặc HTML từ model.
Giữ kết quả thiếu/lỗi, deadline và budget trung thực; không đổi provider khi chưa thuộc phạm vi được phép.

## Oracle và nghiệm thu

- Oracle gồm nhãn dấu hiệu/vật liệu đã duyệt và bảng tiếp nhận độc lập theo đúng phiên bản.
- Có ảnh ký hiệu mờ, vật tương tự khác chất liệu, vật bẩn, nhiều thành phần, sai site, luật hết hiệu lực và thiếu nguồn.
- Tách dev/holdout theo vật/nguồn phù hợp; khóa bảng luật và nhãn trước khi chấm.
- Chấm macro-F1 theo nhóm có nhãn, đúng ký hiệu, hỏi lại đúng, route accuracy và tỷ lệ chưa đủ dữ kiện.
- Kiểm bất biến: không dùng luật site khác/hết hiệu lực; ảnh thiếu bằng chứng phải hỏi thêm hoặc báo không đủ.
- Test đổi site giữa inference, hủy, late result, nguồn đổi phiên bản, API lỗi và truy cập ảnh chéo phiên.
- E2E phải chứng minh ảnh tác động câu hỏi/đáp án, không chỉ kiểm endpoint nhận ảnh thành công.
- Bịa điểm nhận, kết luận tái chế thiếu nguồn hoặc chỉ dẫn nguy hiểm là lỗi chặn; không dùng điểm trung bình bù.
- Báo số mẫu, version, lỗi/timeouts, độ trễ và chi phí/tác vụ thành công; ngưỡng mềm cần được chốt, không tự gọi là chuẩn BTC.

## Bàn giao

Giao danh mục/luật có owner, data/action/state contracts, cách chạy, bộ ca/oracle và hướng dẫn cập nhật nguồn.
Kế hoạch chỉ rõ đầu vào đã có/chưa có, phase bị chặn, file dự kiến và ma trận yêu cầu–bằng chứng–điều kiện đạt.
Review nêu nguồn, vị trí và ca lỗi cụ thể; implementation báo capability nào đã kiểm và giới hạn còn lại.
Không dùng demo giả hay hạ từ vision sang text để tuyên bố đạt yêu cầu ảnh.
