---
name: ai-product-planning
description: "Lập hoặc rà soát hướng phát triển, MVP, techstack và kế hoạch triển khai sản phẩm AI; tạo gói bàn giao đủ bối cảnh, contracts và tiêu chí nghiệm thu cho agent mới. Dùng khi cần chuyển đề bài thành kế hoạch thực thi, không tự triển khai ứng dụng từ yêu cầu lập kế hoạch."
---

# AI Product Planning

Tạo kế hoạch mà agent chưa có lịch sử chat có thể tiếp tục đúng phạm vi. Ưu tiên kết quả quan sát được, dữ liệu có bằng chứng và quyết định có thể kiểm; không chọn công nghệ chỉ theo tên trend.

## Đọc đúng phần tham chiếu

[Hợp đồng nhận việc](references/task-contract.md), [hướng dẫn đóng gói](references/techstack-guide.md) và [hợp đồng kế hoạch](references/planning-handoff.md) đi cùng skill, không cần checkout repo nguồn hoặc truy cập Internet để đọc. Đọc hợp đồng nhận việc trước; tìm theo tiêu đề và chỉ đọc phần cần dùng:

- Lập/rà soát kế hoạch: đọc phần **18.9–18.11** (hợp đồng gói, trạng thái sẵn sàng và tự kiểm), cùng phần **21** (chế độ và giao việc).
- Chưa chọn ý tưởng: đọc thêm **18.1–18.8**; tạo các phương án rồi chọn một để kiểm chứng. Đã chốt phương án thì không mở lại lựa chọn nếu không có bằng chứng mới.
- Chọn stack: **3.2–3.4**. Contracts dữ liệu/tools/state/RAG: **12.1–12.4**. Thiết kế eval: **14.1–14.3**. Chỉ đọc mục voice/media/security tương ứng khi đề cần.
- Nhiệm vụ thuộc AI Thực Chiến: đọc ràng buộc **1.1** và capability **4**. Snapshot model/API là tài liệu, không là quyền hoặc kết quả smoke hiện tại.
- Cần ví dụ cách áp dụng: **19**, nhưng không chép miền nghiệp vụ hay tính năng của ví dụ thành yêu cầu của đề mới.

Tài liệu nguồn được xây trong bối cảnh BTC/Delta Mind. **Chỉ áp Gateway BTC/AI Log khi nhiệm vụ thuộc bối cảnh đó; đường dẫn đội/vòng như `chung-khao/` cần xác nhận riêng từ repo.** Dự án khác giữ provider, thư mục, stack và quyền đã được người dùng/repo xác nhận. Không gọi inference tốn phí chỉ để lập kế hoạch.

## Cách làm

1. Xác định khám phá, lập kế hoạch hay review. Yêu cầu này không tự cho phép xây app, deploy, commit hoặc push. Giữ lựa chọn người dùng đã chốt.
2. Scout repo/docs/artifacts được phép: root, branch, entrypoint, stack, lệnh, file và dữ liệu thực có. Không đọc secret. Nhắc lại đề và điều kiện bắt buộc trong gói; phân biệt đề giả định với yêu cầu chính thức.
3. Tách yêu cầu đã xác nhận, quan sát từ nguồn, đề xuất thiết kế và giả định. Với mỗi đầu vào quan trọng: vị trí/cách nhận, owner, quyền, phiên bản và trạng thái. Không coi dữ liệu được hứa là file đang có.
4. Chốt một luồng đầu-cuối, nguồn sự thật và vai trò AI/code/con người. Mỗi component phải gắn bước xử lý và phép kiểm. Contract cần đủ ở điểm quyết định: identity/scope, input/output/errors, luật/hiệu lực, trạng thái và side effect khi liên quan.
5. Bàn giao theo phần 18.9: điểm vào ngắn, phase files có điều kiện vào/ra, files hiện có/dự kiến, thứ tự bước, validation/oracle và xử lý lỗi. Dùng quy ước repo; mặc định `plans/<timestamp>-<slug>/`. Nếu chỉ yêu cầu trả lời trong chat thì không tự lưu file.
6. Nối mọi yêu cầu bắt buộc tới phase → phép kiểm → oracle → điều kiện đạt. Lỗi gây sai quyền/sai hành động không được bù bằng điểm trung bình. Ngưỡng chưa chốt có owner và mốc quyết định trước holdout, không giả số đo.
7. Mỗi khoảng trống có người/cách giải quyết, điều kiện mở, phase phụ thuộc và việc tiếp tục được. Thiếu luật hoặc quyền không được đoán; không biến toàn bộ task thành blocked khi vẫn còn phần độc lập hữu ích.
8. Tự kiểm theo 18.11 bằng cách bỏ lịch sử chat. Sửa thiếu sót trước khi bàn giao; ghi rõ sẵn sàng, sẵn sàng một phần hoặc cần đầu vào. Kế hoạch hoàn thành không có nghĩa sản phẩm đã kiểm thành công.

Khi người dùng chỉ yêu cầu **review kế hoạch có sẵn**, áp các tiêu chí trên để trả nhận xét theo mức ảnh hưởng, dẫn mục/file, nêu hệ quả và đề xuất sửa; không tự ghi đè hoặc sinh lại gói kế hoạch. Chỉ cập nhật artifact khi yêu cầu đã bao gồm sửa/cập nhật. Không đảo quyết định đã chốt chỉ vì một lo ngại chưa có bằng chứng.

## Chất lượng đầu ra

- Agent nhận gói biết đang giải đề nào, bắt đầu ở đâu, làm gì trước, cần hỏi ai và chứng minh xong bằng gì.
- Kết quả có liên kết nội bộ đủ dùng; quyết định quan trọng không nằm riêng trong lịch sử chat hoặc URL không đọc được.
- File/lệnh/endpoint chưa kiểm phải được ghi là dự kiến hoặc chưa xác minh. Nếu chưa có repo thì nêu bước xác định root, không bịa cấu trúc đã tồn tại.
- Capability bắt buộc có phép thử và hành động khi không đạt. Không bỏ âm thầm modality, đổi provider hoặc tạo dữ liệu demo thay kết quả thật.
- Phân chia thời gian nêu điều kiện chuẩn bị và chừa chỗ tích hợp/kiểm. Hoãn optional trước; cắt yêu cầu bắt buộc cần quyết định người dùng.
- Giữ kích thước gói vừa với việc: không bắt sản phẩm nội dung tạo DB/tools, không ép MVP đơn giản dùng nhiều agent, không điền mọi mục bằng hệ thống không cần thiết.
