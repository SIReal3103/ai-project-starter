# Soạn và đóng gói

Đọc tài liệu gốc cac-huong-phat-trien-san-pham-dua-vao-techstack.md và skill-creator. Parent giữ source doc, README, catalog, scripts và 6 skill nền; ba worker sở hữu riêng C/D/E, F/G/H và I/media/quality. Không sửa chéo SKILL.md trong lúc worker đang chạy.

Tạo skills/catalog.json: tên, nhóm, tiêu đề và các phần nguồn. Tạo references/techstack-guide.md theo lát cắt nguồn; task-contract.md chung ngắn để bắt đầu và bàn giao; planning-handoff.md chỉ đọc khi lập kế hoạch. Các bản sinh có script sync --check; không duy trì nhiều bản gốc bằng tay. Giữ wrapper sync-planning-skill.py tương thích.

Mỗi skill có YAML metadata chuẩn, trigger/boundary cụ thể, tìm dữ liệu hiện có trước hỏi, các bước thực thi, trách nhiệm AI/code/người, test/oracle, lỗi và đầu ra. Chỉ áp quyền/luật/paths BTC khi bối cảnh thi đó đã được xác nhận. Không sinh scaffold app hoặc model output giả.

Kiểm: validator skill, catalog coverage từng section, liên kết đóng gói, phát hiện references lệch/thiếu. Rollback bằng diff task, giữ nội dung trước task và thay đổi ngoài phạm vi.
