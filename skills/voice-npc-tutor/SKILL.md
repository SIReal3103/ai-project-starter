---
name: voice-npc-tutor
description: "Thiết kế, lập kế hoạch, triển khai hoặc review luyện hội thoại với NPC bằng giọng nói, phản hồi rubric và thử lại (G1). Dùng khi hành động nói của người học phải thay đổi phản ứng nhân vật và bài luyện; không dùng cho chatbot giọng nói chung hay chấm âm vị chỉ từ transcript."
---

# Luyện hội thoại với NPC bằng giọng nói

Người học nhận nhiệm vụ, nói, sửa transcript khi cần, nghe NPC phản ứng, xem bằng chứng theo rubric rồi thử lại. Tách đóng vai khỏi đánh giá để lời thoại không tự quyết điểm.

## Khởi động độc lập

1. Đọc [hợp đồng nhiệm vụ](references/task-contract.md) về chế độ, workspace, quyền và bàn giao.
2. Đọc **9/G1, 9.1, 12.2, 12.5, 14.3 và 17** trong [hướng dẫn chuyên môn](references/techstack-guide.md).
3. Scout recorder/player, auth, session/state, dữ liệu kịch bản/rubric, AI adapters và tests; phân biệt cái đã chạy với thiết kế dự kiến.
4. Giữ người học, ngôn ngữ, kịch bản và provider đã chốt. Kế hoạch/review không tự cấp quyền sửa app, thu âm thật, gọi AI trả phí hay deploy.
5. Gateway BTC/AI Log/`chung-khao/` chỉ ràng buộc nhiệm vụ BTC; không áp provider của ví dụ lên dự án khác. Đường dẫn đội/vòng phải được xác nhận riêng từ repo thực tế.

## Đầu vào cần có trước khi xây rộng

- Mục tiêu học, tuổi/trình độ, ngôn ngữ cần luyện, tình huống, giới hạn chủ đề, người dạy/chủ nội dung và đầu ra muốn so sánh.
- Scenario có ID/version, vai/mục tiêu NPC, sự thật NPC được biết, nhiệm vụ người học, giới hạn lượt và điều kiện kết thúc.
- Rubric có tiêu chí, mô tả từng mức, điểm tối đa, evidence cần và cách xem lại; người dạy duyệt trước chấm chính thức.
- Bài mẫu/đối thoại và audio có quyền dùng, transcript chuẩn, nhóm người nói/thiết bị/tiếng ồn; không tạo audio giả rồi gọi là benchmark thật.
- Quyền mic, chính sách gửi/lưu/xóa audio và transcript, scope người học, retention/backup; quyền mic không là đồng ý lưu lâu dài.
- STT/TTS, codec, structured output và native tools có trạng thái documented/untested/verified/failed/unavailable; có tài liệu không chứng minh tài khoản dùng được.
- Thiếu audio/rubric/capability: nêu owner, gate và phần độc lập có thể làm; text fallback giúp dùng tiếp nhưng không chứng minh voice bắt buộc đã đạt.

## Phạm vi và trách nhiệm

- Nếu chưa chốt, đề xuất ba tình huống, tối đa tám lượt/phiên và so hai lần thử; đây là cấu hình khởi đầu, không tự ghi thành yêu cầu hoặc chuẩn thi.
- Demo khách sạn là ví dụ, không bắt buộc miền khách sạn khi người dùng chọn miền khác.
- AI đóng vai dựa vào facts được cấp, tạo phản ứng phù hợp và đề xuất nhận xét; code giữ chủ phiên, state, điểm hợp lệ, luật lượt và version.
- Người dạy chốt rubric, duyệt nội dung và xem lại đánh giá. Không suy phẩm chất, cảm xúc hoặc năng lực ổn định từ giọng/một câu trả lời.
- Tách role-play call/context khỏi assessor; NPC không thấy rubric bí mật/đáp án không được phép và không tự sửa điểm.
- Giữ stack hiện có; nếu mới, web recorder → backend kiểm audio → STT → dialogue manager/LLM → TTS binary, DB bền cho session.
- MVP theo lượt; không mặc định realtime/full duplex, chấm âm vị hay thích ứng bằng mô hình phức tạp.

## Contracts, state và nội dung

- `start_session(scenario_id)` trả `session_id, goal, content_version`; identity do backend cấp, giữ version cố định trong phiên.
- `submit_turn(session_id, audio)` trả `turn_id, transcript, awaiting_confirmation`; kiểm owner/state và audio trước inference.
- `confirm_turn(turn_id, text)` xác nhận đúng revision/transcript, trả `reply_text, audio_id`; chỉ reply đã kiểm mới được phát.
- `assess_session(session_id)` trả `rubric_scores, evidence_turn_ids, next_practice`; score giới hạn bằng code, nhận xét phải trỏ lượt thật.
- State giữ lượt hiện hành, câu đang chờ, transcript revision, role-play/assessment status và số lần thử; một writer cho state tại mỗi thời điểm.
- Sửa transcript chỉ theo policy đã chốt, MVP thường chỉ lượt mới nhất chưa có lượt sau; thay message và vô hiệu reply/assessment/audio phụ thuộc.
- Khi soạn thêm kịch bản: mục tiêu + học liệu được duyệt → draft có schema → kiểm sources/facts → người dạy duyệt → publish version.
- Quiz nếu thêm phải có objective, options, đáp án, giải thích/evidence và độ khó; duyệt trước chấm chính thức, không để NPC tự đổi đáp án.
- Writing nếu thêm dùng rubric, trích đoạn bài và evidence IDs; server kiểm trích đoạn có thật và điểm đúng miền, không làm theo lệnh nhúng trong bài.

## Luồng voice cần thực hiện đúng

1. Xin mic từ thao tác người dùng; kiểm quyền trả về muộn sau thả/hủy và đóng tracks, không bắt đầu thu trễ.
2. Kiểm MIME/container thật, bytes/duration/size; finalize file trước upload, chuyển codec bằng công cụ local được phép khi cần, không đổi đuôi giả.
3. Gửi STT, hiển thị transcript để sửa; im lặng/rỗng cần ghi lại hoặc nhập chữ, không cho LLM đoán lời nói.
4. Xác nhận đúng lượt rồi mới cập nhật state và gọi NPC với facts/history tối thiểu; phản ứng phải thay đổi theo hành động người học.
5. Kiểm reply rồi tạo TTS; UI text và audio dùng cùng phiên bản nội dung, số/mã được formatter giữ đúng.
6. Chỉ báo đang phát khi `play()` thành công; autoplay bị chặn thì giữ audio và nút phát, không gọi TTS lại.
7. Thu lượt mới/dừng/đổi text vô hiệu ý định phát cũ bằng epoch/revision; giải phóng tracks, audio nodes, timer và Blob URL.
8. Kết thúc, đánh giá riêng, hiển thị lý do/evidence và lượt thử lại; so bằng bài tương đương khi đo tiến bộ.

## Lỗi, hủy và khôi phục

- STT lỗi giữ input được phép lưu, cho thử lại/nhập chữ; TTS lỗi giữ reply text, retry riêng audio, nghe lại dùng bản đã tải.
- Hủy ở browser phải vô hiệu run backend; response muộn không cập nhật điểm/state hay phát audio. Hủy không chứng minh chi phí bằng 0.
- Kiểm pointer cancel/up ngoài nút, Escape, tab ẩn/unmount, double click; thao tác bàn phím không gửi hai lần.
- Resume kiểm quyền/session/content version và side effect đã commit; checkpoint không giữ quyền vĩnh viễn.
- Retry có giới hạn một lớp và deadline tổng, usage gồm STT/LLM/TTS; không đổi provider hoặc gọi dịch vụ đánh giá phát âm ngoài quyền.
- Nếu thêm rảnh tay, có trạng thái paused sau TTS/autoplay lỗi, không nghe mic trong lúc bot phát và cần thao tác tiếp tục sau tab ẩn.

## Kiểm và điều kiện đạt

- Unit/integration: owner/state, max turns, sửa/hủy, audio invalid, late reply, reload/resume, không đọc phiên khác và không sửa điểm qua prompt.
- STT: WER/CER với normalization tiếng Việt được ghi rõ, đúng phủ định/tên/số; ca im lặng riêng. Transcript không đủ để chấm âm vị.
- TTS: người nghe kiểm dễ hiểu, nội dung/nhịp đọc đúng và latency từ hết lời tới audio hữu ích, không tính câu đệm.
- Hội thoại holdout: người dạy chấm giữ vai, facts, phản ứng theo lượt, không làm hộ mục tiêu; tách dev/holdout theo người nói/tình huống phù hợp.
- Bản nguồn gợi ý 20 phiên và 16 đạt; chỉ dùng làm ngưỡng đề xuất nếu chưa chốt, không gọi là kết quả hoặc chuẩn BTC.
- Mọi ca quyền/state/điểm phải đúng; bịa lời từ im lặng, lộ phiên hoặc thưởng trái luật là lỗi chặn, điểm trung bình không bù được.
- Đo chi phí/phiên gồm lỗi/retry và n; cải thiện rubric trên bài tương đương khác nhau mới hỗ trợ kết luận về học tập.

## Bàn giao

- Giao scenario/rubric/content versions đã duyệt, contracts, audio lifecycle/retention, oracle, tests và cách chạy/demo theo quyền.
- Báo rõ chất lượng voice, nội dung và luật đã kiểm ở mức offline/integration/người dạy; giữ lỗi và capability chưa kiểm.
- Kế hoạch nhiều phase theo [hợp đồng kế hoạch](references/planning-handoff.md); agent mới phải biết đầu vào còn thiếu, owner, phase đầu và gate nghiệm thu.
