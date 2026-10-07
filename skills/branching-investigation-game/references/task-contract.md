<!-- Generated from cac-huong-phat-trien-san-pham-dua-vao-techstack.md; sections 22.2; sha256 2d4568876ea8e3aa86447c9e668b647ab3840eb9decded38b3ba4f5d1ad334dc. Edit the source and run scripts/sync-skills.py. -->

Phần BTC chỉ áp dụng khi nhiệm vụ thuộc bối cảnh BTC; đường dẫn đội/vòng cần được xác nhận riêng. Model/API, budget và ngưỡng trong nguồn là snapshot hoặc đề xuất, không chứng minh quyền/capability/kết quả hiện tại.

### 22.2 Hợp đồng bắt đầu và bàn giao áp dụng cho từng skill

Một agent mới nhận skill phải làm theo nhiệm vụ thực tế, không cần lịch sử chat của tác giả:

1. **Nhận việc:** nhắc lại đề/người dùng/kết quả cần có; xác định khám phá, lập kế hoạch, review hay triển khai. Giữ quyết định đã chốt. Review-only trả findings có vị trí và bằng chứng; chỉ sửa khi yêu cầu gồm sửa. Lập kế hoạch không tự cho phép xây sản phẩm hoặc chạy inference tốn phí.
2. **Scout trước hỏi:** đọc hướng dẫn dự án, hiện trạng repo/root/nhánh, stack/entrypoint và tài sản được phép; phân biệt file/lệnh đã có với dự kiến. Không đọc/in credential. Chưa có repo thì ghi root chưa xác định và bước cần làm để xác định; không đặt đường dẫn máy tác giả thành phụ thuộc.
3. **Chốt đầu vào:** với dữ liệu/asset/API/luật ghi vị trí hoặc cách nhận, owner, quyền, phiên bản/hiệu lực và trạng thái. Lời hứa cung cấp khác file đã có; documented khác verified. Chỉ áp Gateway BTC/AI Log khi thuộc bối cảnh đó; chỉ áp repo đội và chung-khao khi đúng repository/vòng đã xác nhận. Ngoài bối cảnh đó giữ provider, kênh và đường dẫn người dùng đã chọn.
4. **Giải khoảng trống:** thiếu thông tin tìm được trong repo thì đọc trước; thiếu quyết định nghiệp vụ/quyền thì hỏi tập trung. Mỗi khoảng trống có owner hoặc người cần chỉ định, bằng chứng cần, nhánh bị chặn và việc vẫn làm được. Giả định dễ đảo ngược phải có nhãn. Không tự bịa dữ liệu/luật, KPI hay capability để mở gate.
5. **Thiết kế và làm:** dùng quy trình chuyên biệt của skill, một luồng chính, stack hiện có phù hợp. Tách AI đề xuất/diễn đạt, code kiểm/tính/commit và con người quyết định. Chỉ thêm công nghệ khi gắn bước xử lý và phép kiểm; không mặc định DB/agent/app cho tác phẩm tĩnh.
6. **Quyền và tác động:** thực hiện trong quyền đã cấp, không hỏi lại quyền rõ ràng. Chuẩn bị/phê duyệt/commit chỉ tách khi nghiệp vụ cần; xác nhận gắn đúng payload/version. Tạo nội dung không tự cấp quyền đăng hoặc gửi người khác. Không gọi API/live scan/kênh ngoài phạm vi; không đổi provider âm thầm.
7. **Kiểm:** yêu cầu → hành vi → case → oracle độc lập → điều kiện đạt. Giữ ca thường, thiếu/mơ hồ, lỗi/hủy phù hợp. Phân biệt syntax, test offline, integration thật và nghiệm thu. Ngưỡng/số mẫu/timebox trong ví dụ là đề xuất; giữ lựa chọn user, không tự biến thành chuẩn BTC hoặc số đo. Lỗi quyền/tác động/dữ kiện nghiêm trọng chặn phần liên quan; inconclusive không là pass.
8. **Bàn giao:** tóm tắt bối cảnh, scope, file/phiên bản, lệnh đã chạy hoặc dự kiến, bằng chứng, lỗi và bước tiếp theo. Kế hoạch cần điểm vào, phase có input/output/dependencies/files/steps/checks/rollback và ma trận nghiệm thu theo phần 18.9–18.11. Giữ báo cáo ngắn đủ thực hiện; dẫn contracts chung trong gói thay vì lặp. Sản phẩm chỉ báo xong khi đầu ra thật đạt kiểm.

Tài sản hư cấu hoặc fixture chỉ dùng đúng mục đích được ghi nhãn; không thay inference/side effect thật rồi công bố demo đã chạy. Các snapshot kỹ thuật phải được đối chiếu với phiên bản/provider được cấp trước khi dựa vào; không cần chạy live hoặc tra mọi API chỉ để đọc/lập kế hoạch.
