---
name: vietnamese-voice-runtime
description: "Xây hoặc sửa luồng voice tiếng Việt: browser recording, codec, STT, transcript, dialogue, TTS, playback, hủy và sửa lượt. Dùng cho giao diện nghe/nói; không coi file STT là realtime/full-duplex hay chấm phát âm."
---

# Voice runtime tiếng Việt

Một người dùng phải hoàn thành tác vụ bằng nghe/nói, có thể sửa hiểu nhầm và dừng an toàn. Giọng đọc hay không bù được transcript hoặc facts sai.

## Khởi đầu

Đọc [hợp đồng nhận việc](references/task-contract.md), phần 12.5/12.8 và 15.2 trong [nguồn](references/techstack-guide.md). Nếu chỉ lập kế hoạch, tạo [gói handoff](references/planning-handoff.md) và phép thử codec/capability; không ghi âm hoặc gọi dịch vụ chỉ để lập kế hoạch.

Scout browser/device đích, recorder, chat/state backend, auth, STT/TTS clients, audio storage và tests. Chốt tác vụ, đối tượng/giọng vùng miền, quyền micro và gửi/lưu audio, budget, modality bắt buộc, trường quan trọng phải xác nhận và oracle. Thu âm trên máy người dùng cần thao tác/quyền phù hợp; quyền micro khác đồng ý lưu lâu dài.

## Xây đường ngắn trước

1. Bắt đầu nhấn để nói → file hoàn chỉnh → STT → transcript có thể sửa → nghiệp vụ → text đã kiểm → TTS → audio. Không cần WebRTC/LiveKit cho file upload. Nếu sản phẩm bắt buộc realtime, kiểm đúng capability trước khi cam kết kiến trúc.
2. Thử file từ chính browser đích qua provider được phép. MIME/bytes/codec đúng; WebM/Opus đổi đuôi không thành WAV. Chunks MediaRecorder chưa chắc decode độc lập; finalize/gộp container trước upload, chuyển codec local nếu cần và được phép.
3. Cài state UI tách recording/transcribing/thinking/synthesizing/playing/awaiting_input/error/cancelled. Backend giữ run/turn/revision, pending question và result version. Dữ kiện nói và trên màn hình lấy từ cùng typed result.
4. Xử lý transcript như input người dùng có thể sai: giữ phủ định/tên/mã/số, hỏi lại phần ảnh hưởng quyết định; sửa lượt mới nhất theo policy đã chốt, không nhân đôi lịch sử. Im lặng/STT rỗng không gọi LLM để đoán lời nói.
5. Nối TTS từ answer_id/text version đã kiểm trong quyền. Formatter bỏ Markdown/URL dài nhưng giữ số/ngày/đơn vị; không cắt giữa dữ kiện quan trọng. Route đọc text tự do nếu có cần quota/scope riêng.
6. Kiểm lifecycle hủy, sửa, mất mạng và cleanup; sau khi core đạt mới cân nhắc tự chia câu/TTS streaming hoặc rảnh tay theo lượt.

## Contract recorder và playback

| Tình huống | Hành vi phải giữ |
|---|---|
| Xin quyền | HTTPS/localhost, thao tác người dùng; capture pointer trước await và kiểm lại ý định khi quyền trả về |
| Thả/hủy trước khi có quyền | Đóng tracks ngay, không bắt đầu thu muộn |
| Rời nút/ẩn tab/unmount | pointerup, pointercancel, Escape, lost capture và page hidden có đường stop/cleanup |
| Input hỏng/lớn/im lặng | Giới hạn theo cấu hình app đã chốt; phân biệt no-speech, empty, invalid codec; không gửi rỗng |
| Hủy/sửa lượt | Backend vô hiệu run/revision, chặn late checkpoint/UI/audio; AbortController riêng không đủ |
| TTS thất bại | Giữ text; retry riêng TTS trong budget; nghe lại dùng audio cache hiện hành |
| Autoplay bị chặn | Giữ Blob, hiện nút phát; không gọi lại TTS để giải quyết quyền phát |
| Đang nghe bot mà nói tiếp | Dừng audio/queue cũ và áp policy lượt mới; không nghe chính tiếng bot |
| Promise/callback đến muộn | Operation epoch khác playback epoch; kiểm epoch sau await và play/ended/error |

Chỉ báo playing khi `play()` thành công. Đổi message, sửa text, dừng hoặc tắt tự đọc vô hiệu playback chờ; cache theo message/text version. Giải phóng mic tracks, timers, audio nodes và Blob URLs khi hết dùng. Hủy không chứng minh provider đã dừng tính phí.

Giới hạn 30 giây/8 MiB, output TTS hoặc deadline trong nguồn là cấu hình thử, không limit provider đã xác minh. Nếu quá dài, giữ text và đề nghị tóm tắt có kiểm hoặc báo lỗi rõ; không retry payload dài y nguyên.

## Rảnh tay và quyền provider

Chỉ thêm rảnh tay khi có giá trị và đã kiểm echo, silence, tiếng nền, ngập ngừng và stop. Khi TTS lỗi/autoplay blocked/Dừng/tắt tự đọc phải chuyển paused, không chờ `ended` của audio chưa phát. Tab trở lại cần thao tác tiếp tục; có đường keyboard/Bắt đầu/Gửi để không bắt mọi người nhấn giữ.

Trong BTC, STT/TTS và mọi fallback AI vẫn theo gateway được cấp; browser SpeechRecognition/speechSynthesis không tự là đường thay hợp lệ. Ngoài BTC, giữ provider đã chọn và kiểm quyền; không áp quy tắc BTC lên sản phẩm khác. Không công bố full-duplex khi hệ thống chỉ gửi file theo lượt.

## Kiểm, nghiệm thu và bàn giao

Kiểm thật một file mỗi browser/device chính, nhiều giọng và tiếng ồn theo người dùng mục tiêu. Người kiểm tạo transcript/nhãn độc lập; WER/CER phải giữ chuẩn hóa rõ, không xóa số/phủ định để điểm đẹp. Không suy điểm âm vị/phát âm từ transcript STT.

Kiểm permission denied, thả trước permission, pointerup ngoài nút, double send, im lặng, timeout, sửa transcript, cancel lúc model/TTS xong, autoplay block, audio cũ phát muộn, tab ẩn, refresh và quota. Oracle state là backend/events, nội dung là facts và người nghe; theo dõi task success sau sửa, latency đến audio hữu ích, thời lượng và cost thực.

Bàn giao state diagram, contracts STT/chat/TTS, matrix codec/browser, config giới hạn có căn cứ, lệnh/test đã chạy và recording samples có quyền hoặc cách nhận chúng. Nêu rõ nhấn để nói/rảnh tay/realtime mức nào verified; chưa đạt voice bắt buộc không được che bằng giao diện text rồi gọi hoàn thành đề voice.
