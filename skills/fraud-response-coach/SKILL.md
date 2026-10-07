---
name: fraud-response-coach
description: Lập kế hoạch, triển khai hoặc rà soát gia sư giọng nói tiếng Việt cho người dùng thực hành phản ứng an toàn trước tình huống lừa đảo theo rubric có nguồn. Dùng cho Tập nói để tự bảo vệ/D2; không dành cho giám sát cuộc gọi thật, điều tra hoặc kết luận danh tính lừa đảo.
---

# Gia sư luyện phản ứng an toàn

## Phạm vi và chế độ

Luồng: chọn bài thực hành → nghe tình huống → nói cách xử lý → nhận phản hồi có căn cứ → nói lại bước an toàn.
MVP tham khảo gồm 10 tình huống theo lượt; không nghe lén, giám sát cuộc gọi đang diễn ra hay thực hiện giao dịch.
Mọi cảnh mô phỏng phải ghi rõ “thực hành”; không đóng giả người thân/cơ quan để đánh lừa người học.

- **Lập kế hoạch:** thiết kế nội dung, rubric, voice/state và nghiệm thu; không tự xây app, gọi AI mất phí hay gửi thông điệp.
- **Triển khai:** thực hiện luồng đã được giao với stack/provider hiện có và dữ liệu được phép.
- **Review:** kiểm nguy cơ thật qua contracts, rubric và ca thử; chỉ sửa artifact nếu yêu cầu bao gồm cập nhật.

## Đọc trước và khám phá

Đọc [hợp đồng tác vụ](references/task-contract.md) cùng [hướng dẫn kỹ thuật](references/techstack-guide.md), phần D2, voice, rubric và eval học tập.
Đọc [bàn giao kế hoạch](references/planning-handoff.md) chỉ khi lập kế hoạch.

Tìm trước khi hỏi các dữ kiện quyết định:

- Nhóm học viên, khả năng dùng nút/bàn phím, thiết bị, mức tiếng Việt và mục tiêu hành vi sau bài học.
- Cảnh báo công khai đã được duyệt, source/version, người phụ trách nội dung và ngày cần rà soát.
- Tình huống lừa đảo, tình huống hợp lệ và tình huống chưa đủ căn cứ; không coi mọi liên hệ lạ đều là lừa đảo.
- Rubric hành vi an toàn/thiếu/nguy hiểm, ví dụ diễn đạt tương đương và người chấm độc lập.
- Audio/transcript được phép dùng, phủ định/tự sửa, baseline nếu có, retention và quyền học viên xem/xóa lịch sử.
- Adapter voice, lưu tiến trình và action registry; không cần thông tin tài khoản, OTP hoặc dữ liệu thanh toán.

Giữ stack/provider đã chọn; React, backend typed, MediaRecorder và SQLite là lựa chọn gọn nếu chưa có app.
Với BTC, mọi STT/LLM/TTS/judge phải qua gateway được cấp; không fallback browser hoặc provider ngoài.
Với dự án khác áp đúng quyền provider của dự án. Kiểm capability end-to-end trước khi ghi verified.

## Contracts học tập

- `TrainingScenario`: scenario_id/version, nhãn thực hành, bối cảnh, câu hỏi, source_ids và skill mục tiêu.
- `Rubric`: version, criterion_id, hành vi đạt/thiếu/nguy hiểm, mức bằng chứng, ngoại lệ và người duyệt.
- `Assessment`: scenario_version, rubric_version, transcript_revision, kết quả từng criterion, trích đoạn và uncertainty.
- `TrainingState`: scope server, session/turn_id, revision, scenario_id, attempts, confirmed_transcript, bước hiện tại.
- `load_training_scenario(scenario_id)` → bối cảnh, nguồn, câu hỏi; giữ đáp án/rubric ngoài context đóng vai.
- `score_response(scenario_id, confirmed_transcript)` → hành vi đạt/thiếu/nguy hiểm và evidence spans có thật.
- `next_training_step(state, assessment)` → giải thích/hỏi lại/yêu cầu nói lại/thử bài khác theo luật đã chốt.
- Tool kiểm schema, quyền, state/version, deadline; trả needs_clarification, api_error hoặc cancelled riêng với kết quả học tập.

Code giữ bất biến và quyết định bước; LLM hỗ trợ đánh giá ngữ nghĩa trong rubric, không tự tạo tiêu chí/điểm mới.
Phủ định, trích lời kẻ xấu và câu tự sửa phải được hiểu trong ngữ cảnh; thiếu chắc chắn thì hỏi lại, không gán hành vi nguy hiểm tùy tiện.
Người biên soạn duyệt nguồn/rubric; người chấm độc lập kiểm scorer; người học sửa transcript trước kết luận có hệ quả.
Không suy điểm phát âm từ transcript hoặc suy đặc điểm cá nhân từ giọng nói.

## Luồng thực hiện

1. Chọn một tình huống có nguồn và rubric đã duyệt; xác định bước an toàn quan sát được để nghiệm thu.
2. Kiểm audio browser → STT → transcript → scorer → phản hồi → TTS bytes → playback, không chỉ từng endpoint riêng.
3. Hiển thị nhãn thực hành; thu bằng thao tác người dùng, kiểm MIME thật, finalize file và đổi codec thật nếu cần.
4. Hiện transcript, cho sửa/ghi lại; không dùng STT rỗng hoặc mơ hồ để đoán câu trả lời.
5. Scorer ngữ nghĩa đề xuất đánh giá và evidence; code kiểm schema, criterion hợp lệ và trích đoạn khớp transcript.
6. Tạo phản hồi ngắn về dấu hiệu cần kiểm và hành động an toàn; không khẳng định danh tính hay bảo đảm nhận diện gian lận.
7. Yêu cầu người học nói lại bước an toàn, lưu tiến trình tối thiểu và chọn bước tiếp bằng state machine.
8. Hoàn thành ca hủy/sửa/lỗi trước mở rộng tình huống hoặc cá nhân hóa dài hạn.

## Voice lifecycle và failure paths

State UI tách requesting_permission/recording/transcribing/assessing/synthesizing/playing/awaiting_input/error/cancelled.
Thả/hủy trước khi cấp mic thì đóng tracks, không thu muộn; xử lý pointercancel, Escape, tab ẩn và unmount.
Sửa transcript tăng revision và vô hiệu assessment/phản hồi/audio phụ thuộc; callback muộn không được ghi điểm hoặc phát.
Backend kiểm turn/revision sau inference và trước ghi; browser abort không đủ. Mỗi session chỉ một lượt sửa state.
Kiểm playback epoch sau await; dừng đọc hoặc bắt đầu thu mới phải xóa ý định phát đang chờ.
Nghe lại tái dùng audio; autoplay bị chặn cho phát tay, TTS lỗi vẫn giữ text và chỉ retry bước TTS.
Không công bố realtime/full-duplex khi chỉ hỗ trợ STT file; có nút bắt đầu/gửi dùng bàn phím, chống gửi đôi.
Nếu người học nói secret: không nhắc lại, đưa vào prompt phản hồi hoặc log; xử lý redaction và dữ liệu gốc theo chính sách.
Ứng dụng không có tool chuyển tiền, gọi người khác hoặc gửi OTP; quyền thu âm không đồng nghĩa quyền lưu lâu dài.
Mặc định MVP không lưu audio; mọi transcript/tiến trình lưu có scope, TTL và đường xóa thật, không tuyên bố xóa chưa làm được.
Nguồn lỗi/scorer chưa chắc → hỏi lại hoặc nêu giới hạn; không đổi provider hoặc dựng assessment để hoàn thành bài.
Timeout/hủy không tự là thất bại của học viên và không tự chứng minh provider ngừng tính phí.

## Oracle và nghiệm thu

- Khóa nguồn, rubric và nhãn người chấm trước eval; target model không vừa sinh đáp án chuẩn vừa tự chứng nhận.
- Có đáp án đúng diễn đạt khác nhau, thiếu bước, hành động nguy hiểm, phủ định/tự sửa và tình huống hợp lệ/chưa rõ.
- Tách dev/holdout theo người nói/tình huống; đo đồng thuận scorer–người chấm, task success và hỏi lại đúng.
- Đo STT với phủ định/tự sửa, người nghe kiểm TTS; không dùng WER tốt để bù phản hồi an toàn sai.
- Test scorer/state, secret redaction, dữ liệu chéo phiên; E2E chọn bài → nói → sửa → phản hồi → nói lại.
- Test mic denied, permission muộn, silence, codec lỗi, TTS lỗi, autoplay blocked, hủy và assessment về muộn.
- Yêu cầu secret, hướng dẫn giao tiền, kết luận danh tính lừa đảo hoặc TTS lượt hủy là lỗi chặn bàn giao.
- Pilot trước/sau dùng tình huống tương đương khác nhau; báo số người, không suy rộng hiệu quả từ mẫu nhỏ.
- Báo lỗi API/timeouts trong task success, phiên bản và chi phí/tác vụ thành công; thiếu oracle giữ trạng thái chưa kết luận.

## Bàn giao

Giao thư viện tình huống/nguồn, rubric và quyền truy cập, contracts, lifecycle, cách chạy, bộ ca và báo cáo thật.
Kế hoạch nêu inputs còn thiếu, owner, phase độc lập, file hiện có/dự kiến và ma trận yêu cầu–nghiệm thu.
Review nêu bằng chứng, hệ quả và cách sửa; không cắt yêu cầu nghe–nói hay đảo quyết định người dùng một cách ngầm định.
Phân biệt thiết kế giáo dục, bài thực hành hư cấu được ghi rõ và số đo người dùng thực; không tạo thành tích giả.
