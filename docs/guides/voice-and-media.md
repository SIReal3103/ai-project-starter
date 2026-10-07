# Voice tiếng Việt, ảnh và media

Chỉ thêm modality khi giúp người dùng thực hiện tác vụ. Giữ cùng backend facts/quyền của luồng text; audio hoặc ảnh không tạo ra một đường bỏ qua các kiểm soát. API/model/codec phải đi qua [capability probe](provider-profiles.md).

## MVP voice theo lượt

Luồng tối thiểu: người dùng ghi → hoàn tất file → STT → thấy/sửa transcript → workflow/chat → thấy text hoàn tất → TTS → phát, dừng hoặc nghe lại. Có nhập chữ thay thế. Tên “realtime” chỉ dùng khi transport, incremental events, endpointing và interruption thực sự đã được triển khai/kiểm.

Backend giữ key và cung cấp các route có auth/schema/limits. STT nhận file + turn ID; chat nhận transcript/version hoặc text; TTS nhận text version đã kiểm trong scope. Server giới hạn size, thời lượng, concurrency và deadline. History/thread do server kiểm quyền. Transcript sửa phải vô hiệu kết quả/proposal phụ thuộc; không sửa ngầm một lượt cũ đã được tiếp lời.

Chốt UX khi hết giới hạn ghi: gửi bản hoàn chỉnh, giữ để xem trước hay bỏ; công bố đúng hành vi đó. Các số như 30 giây, 300 ms hoặc một ngưỡng im lặng là lựa chọn cần đo, không phải giới hạn chung của browser/provider.

## Codec và recorder

1. Probe bằng chính browser/thiết bị đích. Xin mic từ thao tác người dùng trong môi trường browser cho phép; từ chối mic vẫn dùng text.
2. Kiểm format recorder hỗ trợ và giữ `mimeType` thực. Browser thu được không có nghĩa STT nhận được.
3. Chờ `stop` và chunk cuối trước khi ghép Blob. Blob theo timeslice không mặc nhiên là file độc lập giải mã được. Đổi đuôi WebM thành WAV không chuyển codec.
4. Nếu cần transcode, dùng môi trường có công cụ phù hợp, mảng args không qua shell, file tạm riêng, timeout/resource limits và cleanup. Kiểm codec/binary trên hosting, không chỉ laptop.
5. Đo thời gian từ lúc recorder thật sự bắt đầu. RMS/waveform chỉ là mức âm, không chứng minh có lời nói; meter lỗi không tự chứng minh bản thu im lặng.
6. Transcript rỗng hoặc đáng ngờ do im lặng/ồn phải dừng/hỏi lại; không gọi model để đoán người dùng vừa nói gì.

PTT cần giữ đúng pointer qua lúc chờ permission. Nếu người dùng thả/hủy trước khi stream về, đóng tracks và không bắt đầu ghi muộn. Nút “Bắt đầu” dạng click có intent khác PTT, không yêu cầu pointer còn giữ. Tránh `pointerup` và `click` gửi hai lần. Xử lý pointercancel, mất capture, Escape, tab hidden và unmount. `onstop` không tự chứng minh ý định gửi: giữ trạng thái gửi/bỏ rõ; source/recorder lỗi thì không upload ngoài ý muốn.

## State, hủy và phát audio

```text
# Pseudocode UI state — không phải implementation có sẵn
idle -> requesting_permission -> recording -> finalizing
     -> transcribing -> transcript_review -> answering
     -> preparing_audio -> playing -> idle
any active state -> cancelled/error/paused
```

Giữ một recorder và một player. Operation epoch đổi khi bắt đầu/hủy/thay lượt; sau mỗi `await`, kiểm epoch và turn/version trước khi ghi UI. Playback epoch riêng bảo vệ TTS pending, `play()` promise và callbacks. Hủy vô hiệu epoch trước, abort requests rồi dừng player/cleanup. Backend cũng chặn stale results; chỉ UI bỏ callback không đủ nếu server đã ghi sai state.

Dọn tracks, timers, animation frames, AudioContext, listeners và Blob URLs. Cache audio theo message ID + text version; sửa text bỏ cache, nghe lại không gọi TTS mới khi audio còn. Bắt đầu thu dừng audio trước; không cho replay chen lúc thu/finalize. Tắt tự đọc phải hủy cả ý định autoplay đang chờ.

Chỉ báo “Đang đọc” sau khi `audio.play()` thành công và epoch còn đúng. Autoplay blocked giữ audio, hiện nút Phát; không gọi TTS lại. TTS lỗi giữ text và retry riêng TTS nếu phù hợp. Dừng đọc không xóa câu trả lời chữ đã hoàn tất. JSON lỗi hoặc MIME sai không được phát như audio.

Formatter lấy tiền/ngày/mã từ typed facts; giữ số 0 đầu. Không regex xóa dấu chấm/phẩy tùy tiện hoặc dùng LLM khác “sửa” số. Nói ngắn, giữ bảng/nguồn đầy đủ trên UI, tránh đọc trace/raw JSON/URL dài. Nhãn giọng AI và nút dừng/nghe lại cần rõ.

## Rảnh tay và streaming

Chỉ thêm rảnh tay khi core đã qua test: nghe → gửi → chờ → phát → nghe. Capture đóng/vô hiệu trong xử lý/phát để không nghe chính bot. Callback mở mic phải kiểm epoch, mode và visibility. TTS lỗi, autoplay blocked, dừng hoặc tắt tự đọc đưa về paused; không chờ một `ended` sẽ không đến. Ẩn tab/rời chat dừng tracks và lịch mở mic; quay lại cần thao tác tiếp tục.

Energy/silence heuristic có thể bị quạt/nhạc hoặc giọng nhỏ kích sai. Bắt đầu recorder đúng lúc để không mất âm đầu; đo cắt câu/ngập ngừng trên thiết bị thực. Nếu chưa ổn, giữ PTT với giới hạn rõ. VAD không xác minh danh tính/ý định.

Streaming text cần parser theo protocol, không coi network chunk là JSON/event hoàn chỉnh. Text incomplete không được trình bày như đã hoàn tất. TTS từng câu, full duplex, WebRTC hoặc media framework là các nhánh riêng cần order/cancel/session/adapter và eval. Một framework vận chuyển audio không tự biến STT file thành streaming microphone. Browser speech APIs có thể dùng dịch vụ khác; kiểm provider/egress trước khi dùng làm fallback.

## Lỗi và chi phí

| Tình huống | Phản ứng |
| --- | --- |
| Mic bị từ chối/thiết bị mất | Hướng dẫn cụ thể, giữ nhập chữ, đóng resources |
| Payload/codec sai | Báo sửa định dạng; không đổi extension để né lỗi |
| File quá giới hạn | Chặn trước inference, cho ghi ngắn hơn |
| Rate limit | Retry hữu hạn trong deadline theo contract |
| Budget hết | Dừng gọi, giữ text/input/history |
| Timeout/5xx | Giữ trạng thái lỗi hoặc chưa rõ; không tự lặp cả pipeline |
| STT rỗng/mơ hồ | Ghi lại, sửa transcript hoặc nhập chữ |
| TTS lỗi/autoplay blocked | Giữ text, thử lại TTS hoặc phát audio đã có |

STT + chat + TTS đã là nhiều requests; tools/retries tăng thêm. Một tầng retry, deadline tổng gồm queue/transcode/API/body đọc. Concurrency server cần tính nhiều tab/người dùng; giới hạn UI không đủ. Abort không bảo đảm upstream dừng tính phí. Log metadata, thời lượng/bytes/latency/usage; không lưu raw audio/transcript mặc định.

## Ảnh và document intelligence

Ảnh → OCR/vision → fields cùng provenance → validate → người sửa trường mơ hồ → tool nghiệp vụ → kết quả có bằng chứng. Giữ trạng thái extracted/unverified; ảnh mờ/xoay/sửa, field thiếu và ngày/đơn vị mơ hồ phải được nhận biết. Output theo JSON schema chưa chứng minh trường đúng.

Phân biệt tên đồ vật, bounding box, địa danh ứng viên, GPS thiết bị và EXIF ảnh. Một kết quả mô tả không chứng minh tọa độ; vị trí thiết bị không chứng minh nơi chụp. Chỉ chấm bounding boxes khi có nhãn vùng thật; chỉ chấm tọa độ khi có ground truth phù hợp. Không suy danh tính/đặc điểm nhạy cảm từ ảnh.

Nếu dùng URL media, áp dụng kiểm fetch/redirect/quyền; nếu upload, kiểm MIME/signature/size. Giữ bản gốc/preview theo data policy. Không dùng ảnh sinh làm bằng chứng nghiệp vụ hoặc ngụy tạo chứng từ thật.

## Tạo nội dung và jobs media

Khóa hồ sơ facts và quyền tài sản đầu vào: tên/giá/thông số/claims được xác nhận; ai có quyền dùng ảnh/giọng/nhạc/logo; output phục vụ mục đích nào. Lưu facts version → script → hình/voice → render để khi facts đổi biết phần nào cần tạo lại. Review claim và số trước khi xuất/chia sẻ; quyền dùng đầu ra cần xác minh theo nguồn/điều khoản áp dụng, không tự hứa nội dung AI luôn độc quyền.

Image/video jobs cần job ID bền, owner/scope, status, deadline, polling có backoff, lỗi terminal và cleanup. Lưu ID ngay khi nhận. Request tạo job timeout có thể có outcome chưa rõ; tra trạng thái/idempotency trước khi tạo lại có phí. Artifact tải về phải kiểm MIME/size/decoder và giữ provenance; tên file do server cấp.

Chọn chart renderer cho biểu đồ từ số liệu thật. Template/render local có thể đủ cho sản phẩm nội dung; video sinh chỉ thêm khi tạo giá trị. Search dùng nguồn/citations thực, không đưa dữ liệu nội bộ nhạy cảm vào query công khai. Output HTML/metadata provider được render theo cơ chế an toàn đã kiểm, không chèn raw HTML do model tùy ý viết.

## Kiểm nghiệm voice/media

Voice tối thiểu cần audio người thật: câu thường; số/ngày/mã có số 0 đầu; tên gần nhau; tự sửa câu; im lặng/ồn. Kiểm ba lượt liên tiếp, thả/hủy khi permission còn pending, pointercancel, TTS pending rồi dừng, bot đang nói rồi ghi mới, autoplay blocked, replay, hai tab, rời/quay lại chat. Nếu bật rảnh tay, thêm lỗi/tắt tự đọc/ẩn tab lúc đang chờ hoặc phát. Chỉ công bố browser/thiết bị đã thử.

Đo STT bằng transcript người kiểm và WER/CER với normalization đã ghi, giữ nguyên trường quyết định. Thêm field exact match và task success vì WER tốt vẫn có thể sai một chữ số. TTS cần nghe thật: dễ hiểu, phát âm/số, ngắt câu và latency. Một hai clip chỉ smoke integration, chưa đủ tỷ lệ chất lượng đại diện hoặc SLA.

Media kỹ thuật: streams/codec, duration, resolution, frame rate, audio, decode toàn file, frames lỗi/đen và lỗi sync theo mục tiêu. Kiểm bằng người riêng: facts, chữ tiếng Việt, phụ đề, hình/giọng nhất quán, pacing, thông điệp và quyền asset. Video giải mã được không đồng nghĩa nội dung đúng/hay. Report ghi phần đã xem/nghe, timestamps lỗi và mode của bằng chứng; không dùng media tổng hợp để chứng minh chất lượng model live.
