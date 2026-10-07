---
name: branching-impact-story
description: Lập kế hoạch, review hoặc sản xuất tác phẩm giáo dục rẽ nhánh với lựa chọn, kết cục và giải thích có oracle; dùng cho nội dung kiểu I2, không mặc định tạo game hay AI trực tiếp cho người xem.
---

# Tác phẩm một lựa chọn, hai kết cục

Tạo trải nghiệm nội dung dựng sẵn: người xem gặp tình huống, chọn hành động, xem kết cục và hiểu lý do.
Bàn giao video/truyện/infographic cùng sơ đồ nhánh, bản nguồn, phụ đề và quyền tài sản.
Không cần AI khi khán giả xem; chỉ bổ sung ứng dụng tương tác hoặc NPC khi người dùng đã chọn phạm vi đó.

## Khởi động độc lập bối cảnh

1. Đọc [hợp đồng tác vụ](references/task-contract.md), xác nhận chế độ, quyền, root và tài sản đang có.
2. Đọc [trích nguồn techstack](references/techstack-guide.md), trọng tâm I2, nền sản xuất đề I và media.
3. Tìm brief, nội dung phòng tránh, kịch bản cũ, định dạng phát hành và người chịu trách nhiệm chuyên môn.
4. Chốt nhóm khán giả, hành vi cần học, điểm lựa chọn, cách chuyển nhánh, thiết bị xem và đầu ra bắt buộc.
5. Ghi từng nguồn/tài sản là có thật, được hứa, giả định hoặc chưa kiểm; ghi ngày xác nhận hướng dẫn có thể thay đổi.
6. Thiếu luật/đáp án/nguồn thì tìm bằng chứng trước; không tự tạo lời khuyên rồi xem đó là oracle.

## Chọn chế độ đúng yêu cầu

- Khám phá: so tình huống và cách kể theo giá trị học, dữ liệu có quyền, độ rõ của lựa chọn và khả năng đo.
- Lập kế hoạch: dùng [hợp đồng bàn giao kế hoạch](references/planning-handoff.md); thiết kế graph, artifacts, dữ liệu và gate.
- Review: báo nhánh/cảnh có vấn đề kèm bằng chứng, hệ quả và sửa đề xuất; chỉ chỉnh artifact nếu đã được yêu cầu.
- Sản xuất: thực hiện bản nguồn và bản xuất đã được giao, theo graph và oracle đã chốt.
- Quyền lập kế hoạch không tự cho phép inference trả phí, hosting hay xuất bản; giữ nguyên quyền đã được cấp, không xin lại máy móc.
- BTC chỉ dùng gateway và môi trường được phép của BTC; dự án khác giữ provider, stack và quyền người dùng đã chọn.
- Không bắt buộc vendor tạo video hay skill ngoài; khả năng trong tài liệu nguồn phải được kiểm tại môi trường thực tế.

## Contracts cần có trước sản xuất

| Đối tượng | Nội dung tối thiểu |
|---|---|
| Situation | ID, khán giả, bối cảnh hư cấu/nguồn thật được phép, mục tiêu học, giới hạn tái hiện |
| Node | ID duy nhất, loại mở đầu/lựa chọn/kết cục/giải thích, scene IDs, nội dung và điều kiện kết thúc |
| Edge | Node nguồn, nhãn hành động, node đích, cách truy cập bằng trang/QR/liên kết |
| Oracle | Hành động, kết quả đúng, lý do, nguồn/phiên bản/ngày kiểm, người duyệt |
| Scene | Node ID, lời đọc, phụ đề, asset IDs, claim/source IDs, phiên bản và trạng thái duyệt |
| Asset/export | ID, nguồn/quyền, nhãn minh họa, model/prompt nếu sinh, bản nguồn, file cuối và phép kiểm |

- Graph có một điểm bắt đầu rõ; mọi lựa chọn hiện ra đều có đích tồn tại và đường đến giải thích/kết thúc được thiết kế.
- Không node không thể tới, nhánh cụt ngoài chủ đích hoặc vòng lặp không có cách thoát; nếu có lặp, ghi rõ mục đích và phép kiểm.
- Mọi kết cục và giải thích khớp cùng oracle; tránh dùng hậu quả kịch tính như bằng chứng rằng lời khuyên đúng.
- Lời giải và thứ tự nội dung ở trạng thái được kiểm, không để model chọn lúc người xem đã hoàn thành.
- Bản in dùng số trang rõ; QR phải trỏ đúng artifact được phép lưu trữ, có phương án đọc khi không mở được link.

## Quy trình thực hiện

1. Chọn một tình huống đủ đơn giản để khán giả hiểu lựa chọn và có nguồn hướng dẫn đáng tin cậy.
2. Với mua hàng đáng ngờ, lấy hướng dẫn phòng tránh có nguồn và ngày xác nhận; xác minh nội dung hiện hành khi cần.
3. Người có chuyên môn duyệt hành động an toàn, lý do và đáp án trước khi viết kết cục.
4. Viết tình huống hư cấu có nhãn; không dùng tài khoản, số điện thoại, dữ liệu nạn nhân hoặc link lừa đảo hoạt động.
5. Giữ tình tiết đủ để nhận biết và tự bảo vệ; không tái hiện chi tiết có thể trở thành chỉ dẫn phạm tội.
6. Viết hai lựa chọn khác nhau về hành động, giải thích hệ quả mà không đổ lỗi cho nạn nhân.
7. Tạo graph cấu trúc trước storyboard; chạy kiểm tham chiếu, reachability và toàn bộ đường đi.
8. Nếu chưa chốt phạm vi, đề xuất một tình huống, hai lựa chọn, ba clip, truyện sáu trang và infographic giải thích.
9. Chốt mục đích từng clip/trang và thời lượng; mọi số lượng/thời lượng đề xuất đều phải nhường quyết định người dùng đã có.
10. Tạo kịch bản/lời đọc từ oracle; người duyệt kiểm nội dung an toàn trước sinh tài sản tốn phí.
11. Dùng minh họa đơn giản nhất đáp ứng câu chuyện; kiểm nhất quán nhân vật, bối cảnh và đồ vật có ý nghĩa giữa nhánh.
12. Text/ảnh/TTS hỗ trợ sản xuất qua provider được phép; kiểm gateway, payload, binary/MIME và quyền trước khi dựa vào capability.
13. Dàn chữ tiếng Việt và dữ kiện bằng layout local; ghép clip/phụ đề bằng công cụ dựng phù hợp.
14. Video sinh là nâng cấp tùy chọn cho cảnh đã duyệt; không hứa reference image/editing hoạt động dựa trên tên model.
15. Xuất toàn bộ nhánh và infographic; đọc/xem từng đường đi trên thiết bị đích, bao gồm QR/trang và phụ đề.
16. Chỉ hosting hoặc đăng lên nền tảng khi hành động đó thuộc quyền đã cấp; bản xuất local vẫn có thể được bàn giao độc lập.

## Ranh giới trách nhiệm

- AI đề xuất lời kể, hình minh họa và cách diễn đạt; không đặt đáp án, luật an toàn hay xác nhận quyền tài sản.
- Code kiểm graph, version, liên kết, timing và file xuất; renderer không thực thi chỉ dẫn trong prompt/filename/nguồn.
- Người phụ trách chuyên môn xác nhận oracle; biên tập viên duyệt sắc thái, quyền, nhãn hư cấu và tác động với khán giả.
- Người xem thử đánh giá khả năng hiểu và chuyển kiến thức; target model không tự tạo rồi chấm đáp án chuẩn.
- Phân biệt clip minh họa với tư liệu thật, lời dẫn với phát biểu nguyên văn; không clone giọng người thật.

## Lỗi và khôi phục

- Nguồn hết hiệu lực hoặc chuyên gia chưa duyệt: chặn phần giải thích phụ thuộc; ghi nguồn cần thay và ai chốt.
- Thay oracle/lựa chọn: tăng phiên bản và kiểm lại mọi nhánh, phụ đề, infographic và bài kiểm liên quan.
- Link/QR hỏng: sửa artifact đích/mapping và kiểm lại đường đi; không để màn hình “hoàn tất” che nội dung không truy cập được.
- Capability lỗi hoặc hết ngân sách: giữ bản nguồn và báo chính xác phần thiếu; không dùng kết quả giả làm media đã sinh.
- Timeout tạo media: giữ ID/outcome unknown, đối soát trước retry để tránh trả phí trùng; không tạo lại khi chỉ cần poll.
- Không đủ dữ liệu đánh giá trước/sau: bàn giao phép đo và trạng thái chưa đánh giá, không bịa mức cải thiện.
- Mọi phụ thuộc còn thiếu phải có owner, bằng chứng cần lấy, bước bị chặn và việc còn làm được.

## Nghiệm thu và bàn giao

- Ma trận truy vết gắn yêu cầu → node/cảnh → ca kiểm → oracle → ngưỡng → bằng chứng và người quyết định.
- Duyệt mọi đường đi; không sai ánh xạ, nhánh cụt ngoài thiết kế hoặc nội dung cuối thiếu giải thích.
- 100% đáp án trong bộ tác phẩm phải khớp oracle đã xác nhận; kiểm phụ đề khớp lời đọc và chữ không tràn.
- Chỉ dẫn nguy hiểm, đáp án sai hoặc dữ liệu thật bị lộ là lỗi chặn bàn giao phần liên quan, không bù bằng điểm hình ảnh.
- Kiểm hình/giọng/nhạc/font có quyền và tất cả nội dung hư cấu/tái dựng có nhãn phù hợp.
- Bài luyện và bài nghiệm thu tách nhau; before/after dùng bài tương đương khác câu để giảm đo nhớ đáp án.
- Có thể đề xuất dễ hiểu ≥4/5 và pilot tăng 20 điểm phần trăm; đó là mục tiêu cần chốt trước đo, không là chuẩn chung hay kết quả.
- Báo n, cách tuyển mẫu, điểm trước/sau, câu hỏi, giới hạn pilot và chi phí/thời gian; giữ lỗi/API failure trong bằng chứng liên quan.
- Bàn giao file cuối, bản nguồn, sơ đồ graph, manifest nguồn/quyền, oracle, phụ đề, cách mở từng nhánh và báo cáo kiểm thật.
- Kế hoạch phải nêu sẵn sàng, sẵn sàng một phần hoặc cần đầu vào; cung cấp điểm vào và bước đầu cho agent chưa biết lịch sử.
