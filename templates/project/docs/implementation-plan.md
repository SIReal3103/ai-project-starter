# Kế hoạch triển khai

Trạng thái: **chưa bắt đầu**. Phụ thuộc: [đề bài](project-brief.md) và [contract](acceptance-contract.md) được chốt đủ để làm luồng đầu tiên.

| Bước | Đầu ra cần có | Kiểm chứng | Trạng thái |
| --- | --- | --- | --- |
| Chốt luồng | Input/output, ca critical, phạm vi | Chủ sản phẩm xác nhận quyết định chưa rõ | Chưa làm |
| Làm luồng đầu tiên | Một đường đi thực từ input đến output | Test hành vi thật đầu tiên | Chưa làm |
| Hoàn thiện logic | Biên, input sai, lỗi phụ thuộc, quyền nếu có | Unit/contract/integration theo rủi ro | Chưa làm |
| Tích hợp UI/API | Luồng chính và phục hồi lỗi | E2E thực khi có UI/API; build/lint/type theo stack | Chưa làm |
| Baseline eval | Dataset, oracle, adapter và output thật | Ca đúng, ca sai có chủ đích, ca thiếu output | Chưa làm |
| Nghiệm thu | Phiên bản cuối, report, giới hạn và lệnh chạy lại | Mọi ca critical có bằng chứng | Chưa làm |

Với phiên khoảng 120 phút, có thể dành 10 phút đầu chốt scope, 15 phút dựng luồng, 60 phút logic, 20 phút tích hợp, 5 phút khóa bản và 10 phút nghiệm thu. Đây là gợi ý lập lịch, không phải cam kết tốc độ hoặc quy định bắt buộc. Nếu setup dài hơn, giảm phạm vi theo quyết định đã chấp nhận.

Test và bộ ca được chuẩn bị trong lúc phát triển, không đợi cuối mới cài tool. Chọn runner hợp stack; không cài mọi framework. Giữ một bước chạy nhanh tái hiện được; ghi lệnh thực vào README khi đã có.

Nếu cần chia phase lớn, tạo `plans/<timestamp>-<slug>/plan.md` và file phase với phạm vi file, dependencies, nghiệm thu và rollback. Khi nhiều người/agent làm song song, tách quyền sửa file và thống nhất contract trước.

## Rủi ro và rollback

[Cần điền rủi ro thực]. Hoàn tác đúng thay đổi gây regression; giữ bằng chứng fail. Không xóa dữ liệu thật, sửa expected hoặc giấu test lỗi để trở về trạng thái xanh.
