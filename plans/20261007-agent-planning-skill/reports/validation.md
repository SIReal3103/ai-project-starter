# Kiểm chứng tài liệu và skill

Ngày: 07/10/2026. Repository: `SIReal3103/ai-project-starter`, nhánh `main`, nền `bf0640b2c73ec7abdb3a9aec0754c4fcbdf5bb8e`. Phạm vi kiểm là tài liệu lập kế hoạch và gói skill, không phải sản phẩm đổi trả.

## Kiểm cấu trúc và đóng gói

- `quick_validate.py skills/ai-product-planning`: đạt frontmatter và cấu trúc skill.
- `python3 scripts/sync-planning-skill.py --check`: bản tham chiếu khớp byte với tài liệu gốc.
- Script sync được chạy trong fixture tạm: reference thiếu hoặc lệch trả lỗi; `--check` không ghi; đồng bộ lại khôi phục bản đúng; không cần CWD là root repo.
- Các liên kết Markdown tới file local trong README, SKILL và hai file kế hoạch đã được kiểm tồn tại. Tên có tiền tố `._` là metadata AppleDouble, loại khỏi danh sách tài liệu cần đọc.
- `git diff --check`: đạt. Sau khi loại metadata AppleDouble do clone trên ổ ngoài tạo trong `.git`, `git fsck --no-progress` đạt.
- Gói cá nhân được cài vào thư mục `skills/ai-product-planning` dưới Codex home, không dùng symlink; đã so byte từng file với gói repo và chạy validator thành công.

## Review độc lập

Agent không nhận lịch sử chat đọc nguồn cũ: xác định thiếu hợp đồng kế hoạch thực thi, phụ thuộc có người giải quyết, hiện trạng workspace và ma trận truy vết. Các nội dung đã có về kỹ thuật/gates/eval được giữ, không thêm lại như thiếu sót mới.

Lượt review sau chỉnh sửa phát hiện chế độ review có thể vô tình sửa kế hoạch. Đã thêm chế độ review riêng ở tài liệu và SKILL: trả findings, chỉ ghi artifact khi được yêu cầu cập nhật. Reviewer đọc lại xác nhận vấn đề đã giải quyết; không còn finding trong phạm vi đó.

## Forward-test với agent mới

Hai agent riêng, không fork lịch sử chat, chỉ nhận skill copy độc lập, đề bài và tài sản đầu vào tối thiểu. Chỉ ghi kế hoạch trong workspace tạm; không gọi mạng, inference, tạo ảnh hoặc xây app. Không cung cấp đáp án mong đợi hay danh sách lỗi review cho hai agent.

- Tình huống đổi trả: đề luyện BTC, tin nhắn/ảnh → tra đơn/chính sách → xác nhận → phiếu; CSV/PDF/ảnh mới được hứa, chưa có key/capability, mục tiêu 120 phút.
- Tình huống nội dung: dự án ngoài BTC, ba poster PNG, provider nội bộ đã chọn, mục tiêu một ngày, chưa có quyền công cụ/hồ sơ sự kiện/nhận diện/kích thước; không xây app hoặc đăng công khai.

Đã đọc gói nội dung gồm `plan.md` và ba phase (198 dòng tổng tại thời điểm agent bàn giao). Quan sát:

- Giữ đúng ba PNG, Studio X, người duyệt nội dung và không công khai; không thêm app/DB hoặc ràng buộc BTC.
- Ghi brief là fixture kiểm skill, không biến thành hồ sơ sự kiện thật. Hồ sơ, nhận diện, kích thước, quyền và capability có owner/gate rõ.
- Các file sản xuất và kiểm PNG đều ghi dự kiến; không bịa endpoint/lệnh Studio X. Có phép kiểm cụ thể cho cả ba file và sửa sau duyệt.
- `plan.md` nhắc lại brief, hướng dẫn xác định root tương đối, thứ tự đọc; ma trận nối đầu ra với phase, oracle và tiêu chí đạt.
- Controller kiểm độc lập 10 liên kết local của bốn file đều tồn tại. Workspace chỉ có brief và gói kế hoạch; không tạo ảnh hoặc app.

Đã đọc đủ gói đổi trả gồm tám file: `plan.md`, `context.md`, `contracts.md`, `acceptance.md` và bốn phase. Quan sát:

- Nhắc đủ đề luyện, text/ảnh, tra CSV/PDF có nguồn, hỏi thiếu, xác nhận, mã phiếu/xem lại, đổi ý, giới hạn API BTC và mục tiêu 120 phút. Không đổi lời hứa nhận dữ liệu thành dữ liệu đã có.
- Ghi workspace không phải Git repo, `PROJECT_ROOT` triển khai chưa xác định; file và lệnh code là dự kiến. Stack tối thiểu là đề xuất, không giả vờ đã kiểm code.
- Tách phiếu tiếp nhận khỏi duyệt/refund; scope lấy từ server; ảnh không chứng minh lỗi mất tiếng; đánh giá nguồn/luật còn thiếu có trạng thái riêng. Contracts có revision/hash, xác nhận cũ, response đến muộn, chống trùng và tra lại kết quả commit chưa rõ.
- Có inventory và khoảng trống với owner, điều kiện mở, phase phụ thuộc và việc làm độc lập. Trạng thái sẵn sàng một phần; 120 phút chưa được khẳng định khả thi khi chưa có data/key/root.
- Ma trận nghiệm thu nối từng yêu cầu tới hành vi, file/phase, case, oracle và điều kiện đạt. Phân biệt chỉ số đề xuất với tiêu chí đã xác nhận; không tự nhận sản phẩm hoặc capability đã pass.
- Mỗi phase có files, điều kiện vào/ra, các bước, validation và xử lý lỗi/rollback. Controller kiểm liên kết local không thiếu đích; agent báo 18 liên kết. Workspace chỉ có README và tám file kế hoạch.
- Đọc đầu ra phát hiện một câu về lỗi chặn nghiệm thu có diễn đạt mơ hồ; agent đã sửa câu trong mẫu để nói rõ một lỗi cũng chặn kết luận đạt và xác nhận chỉ thay câu đó. Không thêm quy tắc skill mới cho lỗi câu chữ này.

Hai forward-test xác nhận hành vi lập kế hoạch trên các tình huống nêu trên. Chúng dùng bản skill ngay trước bổ sung giới hạn review-only; phần lập kế hoạch không thay đổi sau đó. Chế độ review-only được kiểm bằng review nguồn độc lập, chưa có phép thử hành vi riêng.

## Giới hạn

Validator và kiểm link không chứng minh chất lượng quyết định. Forward-test là mẫu nhỏ cho hai loại nhiệm vụ, không chứng minh mọi đề bài đều được lập kế hoạch đúng. Không kiểm API BTC hoặc provider nội bộ; không tuyên bố sản phẩm, model hay KPI đã đạt. Không commit/push trong lượt này.
