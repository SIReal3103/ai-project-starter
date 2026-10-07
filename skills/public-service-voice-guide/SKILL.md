---
name: public-service-voice-guide
description: Lập kế hoạch, triển khai hoặc rà soát trợ lý tiếng Việt giúp chuẩn bị thủ tục bằng nghe nói, checklist và nguồn đúng địa phương/hiệu lực. Dùng cho Một cửa dễ nghe/D1; không dành cho tự nộp hồ sơ, xác thực danh tính hoặc chatbot chỉ gắn nút đọc.
---

# Hướng dẫn thủ tục bằng giọng nói

## Phạm vi và chế độ

Luồng: nói nhu cầu → xác định thủ tục/địa phương/tình huống → nghe từng bước → xem checklist nguồn → hỏi lại hoặc sửa.
MVP tham khảo là năm thủ tục tại một địa phương, chưa thu hồ sơ, nộp hồ sơ hoặc xác thực danh tính.
Giữ quyết định và stack/provider đã có; chốt lại phạm vi chỉ khi bằng chứng cho thấy thiếu điều kiện bắt buộc.

- **Lập kế hoạch:** thiết kế dữ liệu, voice lifecycle, contracts và phép kiểm; không tự triển khai hoặc gọi inference mất phí.
- **Triển khai:** hoàn thành luồng nghe–nói thật theo quyền đã giao, không dừng để hỏi lại việc đã được cho phép.
- **Review:** kiểm gói hoặc sản phẩm theo nguồn và ca lỗi; chỉ sửa artifact khi yêu cầu gồm cập nhật.

## Đọc trước và khám phá

Đọc [hợp đồng tác vụ](references/task-contract.md) và [hướng dẫn kỹ thuật](references/techstack-guide.md), phần D1, voice, nguồn hiệu lực và eval.
Đọc [bàn giao kế hoạch](references/planning-handoff.md) khi cần gói kế hoạch độc lập lịch sử chat.

Tìm các đầu vào sau trong repo, dữ liệu và yêu cầu hiện có:

- Nhóm người dùng, thiết bị/browser, cách bấm nói/nhập chữ, yêu cầu chữ lớn và khả năng nghe lại.
- Năm hoặc số thủ tục đã chọn, địa phương/thẩm quyền, trường tình huống quyết định và người duyệt checklist.
- Nguồn chính thức, URL/bản lưu, version, effective_from/to, verified_at, ngoại lệ và owner cập nhật.
- Clip người thật được phép dùng, transcript chuẩn, giọng vùng miền/tiếng ồn, quyền xử lý và thời hạn lưu.
- Adapter STT/LLM/TTS, codec thực tế, auth/state hiện có, ngân sách và oracle; không thu căn cước để lấp khoảng trống.

Một app React, backend typed, MediaRecorder, FFmpeg và database thường đủ; giữ stack tương đương đang chạy.
Tác vụ BTC dùng STT/LLM/TTS gateway được cấp, không browser SpeechRecognition/speechSynthesis hay provider ngoài làm fallback.
Ngoài BTC giữ provider được dự án cho phép; mọi capability phải kiểm với model/endpoint/payload thật trước khi gọi verified.
Đọc tài liệu hoặc chạy riêng ba endpoint thành công chưa chứng minh hành trình voice hoàn tất.

## Contracts nghiệp vụ và voice

- `ProcedureSource`: procedure_id, jurisdiction, authority, source_id, version, URL/location, effective_from/to, verified_at.
- `Requirement`: requirement_id, điều kiện áp dụng/ngoại lệ, checklist text, fee/currency, deadline/unit, evidence_ids.
- `VoiceTurn`: scope server, thread_id, turn_id, revision, transcript, confirmed_fields, answer_id/text_version, lifecycle.
- `resolve_procedure(intent, jurisdiction, answers)` → candidates, missing_fields; không tự chọn giữa thủ tục mơ hồ.
- `retrieve_requirements(procedure_id, jurisdiction, as_of)` → checklist/ngoại lệ/source; thiếu hiệu lực xác nhận → needs_review.
- `format_spoken_answer(verified_answer)` → text ngắn đã kiểm, giữ chính xác số/ngày/mã/phí/đơn vị và answer version.
- Transcribe nhận audio đã finalize và turn_id; speech đọc answer_id thuộc người dùng, không mở proxy TTS vô hạn.
- Actions kiểm quyền, revision, schema, quota/deadline; phân biệt no_evidence, needs_review, invalid_audio, api_error, cancelled.

As-of và luật ưu tiên nguồn phải rõ; ngày upload không thay ngày hiệu lực, thiếu phí không được hiểu là miễn phí.
AI hiểu nhu cầu và diễn đạt; code lọc nguồn/quyền/hiệu lực, chọn nhánh và kiểm formatter; người nghiệp vụ duyệt checklist.
Không để model suy thêm giấy tờ, thời hạn hoặc ngoại lệ ngoài nguồn đã xác minh.

## Luồng triển khai xuyên suốt

1. Hoàn thiện một thủ tục có oracle, checklist và ngoại lệ trước khi mở rộng danh mục.
2. Kiểm audio thực của browser qua STT, nghiệp vụ, formatter, TTS bytes và playback; ghi bằng chứng từng bước.
3. Thu bằng getUserMedia/MediaRecorder sau thao tác người dùng, kiểm isTypeSupported và MIME thật.
4. Gộp/finalize container trước upload; chuyển codec bằng FFmpeg khi cần, không đổi đuôi giả. Bỏ audio rỗng/im lặng.
5. Hiện transcript và cho sửa, hỏi lại trường quan trọng mơ hồ; code xác định thủ tục/địa phương/tình huống.
6. Truy hồi đúng version/hiệu lực, tạo checklist có nguồn; thiếu căn cứ thì hỏi lại hoặc needs_review.
7. Đọc các bước ngắn từ answer đã kiểm, hiện chữ song song; nghe lại dùng audio đã tải.
8. Kiểm hủy/sửa/lỗi và bàn phím trước tính năng rảnh tay; không gọi upload STT file là realtime/full-duplex.

## Lifecycle và lỗi bắt buộc xử lý

UI tách idle/requesting_permission/recording/transcribing/thinking/synthesizing/playing/awaiting_input/error/cancelled.
Capture pointer trước await quyền mic; thả/hủy trước khi được cấp quyền thì đóng tracks, không thu muộn.
Xử lý pointerup ngoài nút, pointercancel, Escape, mất capture, tab ẩn và unmount; không gửi hai lần từ click/pointer.
MVP cho sửa lượt mới nhất chưa có lượt sau; tăng revision, thay đúng message, vô hiệu answer/audio cũ.
Hủy ở backend lẫn UI; mọi result/callback kiểm turn_id/revision và playback epoch sau await, không phát audio lượt cũ.
Nhấn nói khi đang đọc phải dừng audio/queue cũ theo chính sách đã chốt; đóng mic, timers và Blob URL khi hết dùng.
Chỉ báo playing sau khi play() thành công. Autoplay bị chặn thì hiện nút phát, không gọi lại TTS.
TTS lỗi giữ văn bản, retry riêng audio; STT rỗng cho ghi lại/nhập chữ, không kích LLM đoán câu nói.
Formatter quá dài cần kết quả lỗi/bản tóm tắt được kiểm, không cắt giữa số; không xóa dấu câu làm hỏng ngày/phí.
Quyền microphone không đồng nghĩa đồng ý lưu audio lâu dài. Mặc định MVP không lưu audio; cấu hình thực phải được mô tả.
Giữ nguồn, transcript và cache đúng scope; không để lịch sử hoặc answer_id của phiên khác truy cập được.
Lỗi nguồn/quota/provider không thành checklist rỗng thành công; không suy chi phí hủy là 0 khi chưa đối soát.

## Oracle và nghiệm thu

- Oracle checklist theo tình huống/version do người hiểu nghiệp vụ duyệt; không để target model tự tạo đáp án chuẩn.
- Khoảng 60 clip Bắc–Trung–Nam là quy mô tham khảo; có ồn, phủ định, tự sửa, tên/ngày/mã và tách người nói dev/holdout.
- Đo WER/CER với normalization rõ, kiểm riêng trường quyết định; WER thấp không bù sai địa phương/ngày/phí.
- Người nghe kiểm TTS đúng số, dễ hiểu, ngắt câu; đo latency tới tiếng hữu ích đầu tiên, không tính câu đệm.
- Test formatter, lọc nguồn, quyền, lifecycle; E2E nói thật → sửa transcript → checklist → nghe/dừng/nghe lại.
- Có mic denied, permission tới muộn, codec sai, STT rỗng, TTS lỗi, autoplay blocked, cancel và nguồn hết hiệu lực.
- Bịa phí/thời hạn, sai địa phương, dùng nguồn hết hiệu lực hoặc phát TTS lượt hủy là lỗi chặn bàn giao.
- Báo số mẫu, version, task success gồm timeout/API errors, latency/cost; tiêu chí mềm phải chốt trước holdout.

## Bàn giao

Giao danh mục nguồn có owner, checklist/oracle, contracts, sơ đồ lifecycle, cách chạy/demo và bằng chứng voice thật.
Kế hoạch có phase đầu chạy được, dependencies, files hiện có/dự kiến và ma trận nghiệm thu; thiếu nguồn/capability phải ghi rõ.
Review chỉ ra vị trí và ca tái hiện; implementation phân biệt đã kiểm offline, integration và người nghe thực tế.
Không gọi sản phẩm đạt nếu chỉ có text fallback trong khi nghe–nói là điều kiện bắt buộc.
