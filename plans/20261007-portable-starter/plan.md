# Starter độc lập để clone và làm dự án mới

Ngày: 07/10/2026. Trạng thái: hoàn tất đóng gói và kiểm chứng clone local. CI kiểm lại trên mỗi push. Đích GitHub: `SIReal3103/ai-project-starter`, private theo lựa chọn user.

## Công việc

1. Rà toàn bộ hướng dẫn liên quan và hợp nhất thành playbook theo nhiệm vụ.
2. Port eval kit, bỏ runtime/path/keyfile cá nhân; dependency tùy chọn có setup và lock.
3. Thêm templates và scaffolder sinh dự án tự chứa.
4. Kiểm source, links, secrets; clone sạch và chạy từ cwd khác/đường có khoảng trắng; kiểm dự án sinh ra.
5. Commit phạm vi starter, tạo remote private, push và xác minh clone từ GitHub.

## Tiêu chí

Core chỉ cần Git/Python; guide/template không tham chiếu file ngoài repo. Framework/model/API/deploy là phần cấu hình rõ, không mặc định đã sẵn sàng. Không đưa code sản phẩm cũ, key, notes cá nhân, raw dữ liệu, cache hoặc lịch sử thử nghiệm riêng vào repo. Tất cả link nội bộ tồn tại. Mẫu tách khỏi điểm sản phẩm thật.

## Phụ thuộc và rollback

Agents có ownership riêng: docs/guides; tools/evals; templates/scaffolder. Controller sở hữu root/CI/checks và GitHub. Nếu kiểm fail, sửa nguyên nhân trước publish. User đã yêu cầu commit/push sang repo mới; không sửa remote hoặc commit repo nguồn. Khi cần rollback chỉ thay đổi starter mới.

## Bằng chứng

[Kiểm chứng starter](reports/validation.md): 23 tests starter, 25 tests evaluator, clone sạch và dự án di chuyển đều đạt. Demo 40/40 và 8/8 đối chứng; Ragas/DeepEval offline đã đo thực. Điểm demo không đại diện sản phẩm AI mới.
