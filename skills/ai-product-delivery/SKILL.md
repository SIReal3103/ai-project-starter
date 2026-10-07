---
name: ai-product-delivery
description: "Thực hiện một kế hoạch sản phẩm AI đã chọn tới nghiệm thu và bàn giao: kiểm đầu vào, tích hợp, xử lý lỗi, demo, runbook và giới hạn. Dùng khi đã được giao triển khai/hoàn thiện; không tự chọn lại ý tưởng hoặc xuất bản."
---

# Triển khai và bàn giao sản phẩm AI

Biến phương án đã chốt thành đầu ra thực có bằng chứng. Đích có thể là ứng dụng hoặc tác phẩm; không bắt nội dung tĩnh phải có app chỉ để chứng minh công nghệ.

## Nhận việc và xác định điểm bắt đầu

Đọc [task contract](references/task-contract.md), phần 16–17 trong [nguồn](references/techstack-guide.md) và gói kế hoạch dự án nếu có. Nếu yêu cầu hiện tại chỉ là kế hoạch/review, dùng [planning handoff](references/planning-handoff.md) hoặc trả findings; không triển khai từ một lời nhờ nhận xét.

Nhắc lại người dùng, tác vụ, phạm vi đã chốt, đầu ra và điều kiện xong. Scout root/branch, AGENTS/docs, code hiện có, lệnh chạy/test, dependencies, dữ liệu, tài sản, capability, quota và quyền tác động. Giữ thay đổi ngoài task. Repository tài liệu không tự là repository sản phẩm; chưa rõ root thì tìm bằng chứng hoặc hỏi đúng điều thiếu.

Đọc phase đầu có đủ điều kiện vào. Nếu chưa có kế hoạch và việc vượt một sửa trực tiếp, tạo gói gọn tại đường dẫn theo repo; ghi rõ files hiện có/dự kiến. Không mở lại lựa chọn sản phẩm đã chốt hoặc tự thu hẹp yêu cầu bắt buộc để vừa thời gian.

## Các chặng và bằng chứng chuyển tiếp

| Chặng | Hành động | Điều kiện chuyển tiếp |
|---|---|---|
| Chốt scope | Một luồng chính, inputs/outputs, quyền, oracle, mandatory/optional và timebox thực tế | Không có quyết định trọng yếu bị biến thành giả định ngầm |
| Kiểm phụ thuộc | Spike nhỏ đúng API/model/codec/kênh/data trong quyền và budget | Capability có record thật; phần chưa đủ có gate và owner |
| Nền dữ liệu/luật | Schema, auth, nguồn/version, state, phép tính, side effects | Unit/contract/integration ở lớp quyết định đạt |
| Luồng đầu-cuối | Input được phép → xử lý thật → đầu ra dùng được | Người dùng hoàn thành một tác vụ; không chỉ nhiều API rời rạc |
| Lỗi và khôi phục | Thiếu/mơ hồ, retry, timeout, hủy, double click, restart, quota | Không rò quyền, giả thành công hoặc nhân tác động |
| Nghiệm thu | So baseline, oracle/holdout đã chốt, giữ lỗi trong báo cáo | Mỗi yêu cầu có bằng chứng, hard failure chặn phần liên quan |
| Bàn giao | Runbook, artifacts, sources/quyền, phiên bản, demo và giới hạn | Người nhận tái hiện được trong môi trường được cấp |

Xây data/rules/auth trước tính năng trình diễn. Stack hiện có phù hợp được giữ. Chỉ thêm một khác biệt sau core đạt và vẫn trong phạm vi; không chữa mọi vấn đề bằng thêm model/agent/framework.

## Thực hiện khi chưa có đủ đầu vào

- Data/capability/luật bắt buộc thiếu: ghi rõ owner, bằng chứng cần và phần bị chặn; tiếp tục schema, UI/state hoặc phép kiểm độc lập khi hữu ích và thuộc quyền đã cấp. Không dựng dữ liệu demo để biến gate thành đạt.
- Không có đường hợp lệ cho requirement: báo trade-off cụ thể; phương án thay chỉ được gọi đạt nếu vẫn thỏa yêu cầu. Không âm thầm bỏ ảnh/voice/kênh thật hoặc chuyển provider.
- Timebox không đủ: hoãn optional trước, giữ thời gian kiểm. Nếu phải thay yêu cầu người dùng đã chốt, trình lựa chọn thay vì tự quyết định.
- Tác động đã commit nhưng response mất: đối soát nguồn sự thật trước retry. Rollback code không tự hoàn tác hành động nghiệp vụ; ghi recovery riêng, không reset DB đang có dữ liệu người dùng.

## Tiêu chí theo loại đầu ra

Ảnh/voice phải tham gia giải tác vụ, không chỉ trang trí. Chat trên nền tảng phải nhận/gửi thật trong tài khoản được phép; web chat chưa chứng minh bot nền tảng. Dữ liệu/biểu đồ cần phép tính độc lập, đơn vị/kỳ/coverage đúng. Game cần luật/state/rubric đúng dù lời AI thay đổi. App tạo nội dung cần chạy lại với input mới; tác phẩm nội dung cần kiểm file xuất hoàn chỉnh và quyền tài sản.

Nếu dự án dùng Godot, giữ quy tắc dự án: chỉ mở thủ công khi product owner yêu cầu, chạy game trực tiếp từ worktree task đã đăng ký, kiểm không có instance khác và có test entrypoint độc lập. Không mở editor/game để kiểm một nhiệm vụ tài liệu.

## Kiểm và báo cáo đúng mức

Chạy phép kiểm hẹp trước, mở rộng khi contract/shared behavior thay đổi. Không gọi syntax/import/graph compile hay HTTP 200 là nghiệm thu sản phẩm. Phân biệt tests offline, integration dependency thật, AI eval và kiểm media xuất. Trường hợp không chấm được là pending/inconclusive, không pass.

Demo gồm luồng thành công, ca thiếu/mơ hồ và ca lỗi/hủy phù hợp với tác vụ. Không công bố dữ liệu fixture hoặc kết quả cache cũ như inference mới. Nguồn/đáp án do người hoặc code độc lập kiểm; threshold chưa chốt có người quyết định trước holdout. Giữ lỗi, timeout, n và chi phí/độ trễ có giới hạn rõ.

## Gói bàn giao cuối

Ghi đầu ra thực, file task-scoped và root/branch; prerequisites/lockfile; lệnh start/import/test/stop đã thử hoặc ghi chưa thử; cấu hình chỉ tên biến; nguồn/version/cách cấp dữ liệu private; quyền/capability và hard gates; report ca pass/fail; demo runbook và giới hạn/cách xử lý tiếp.

Chỉ kết luận hoàn thành khi yêu cầu bắt buộc có bằng chứng và đầu ra dùng được. Quyền deploy/commit/push/gửi tin theo người dùng, không phát sinh từ skill. Nếu đã có quyền rõ thì thực hiện đúng phạm vi, không hỏi lại; không tự tạo approval flow cho mọi bước local có thể đảo ngược.
