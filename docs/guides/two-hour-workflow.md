# Quy trình làm sản phẩm AI trong hai giờ

Mục tiêu là hoàn thành **một luồng có thể kiểm**, dành khoảng mười phút cuối cho nghiệm thu và bàn giao. Các mốc dưới đây là timebox đề xuất; không phải cam kết tốc độ của máy/provider hay yêu cầu cuộc thi. Nếu setup phải nằm trong hai giờ, tính nó vào ngân sách và giảm tính năng tương ứng.

## Chốt hợp đồng trong mười phút đầu

Đọc README, hướng dẫn repo, scripts/lockfiles, source gần luồng chính và thay đổi Git hiện có. Chọn người dùng, tác vụ, input hợp lệ, output đúng, nguồn/quyền và phụ thuộc thật. Ghi mode thiếu/mơ hồ/lỗi, hành động ghi/gửi/tính phí, giới hạn thời gian/calls/cost và lỗi chặn demo.

Xác định đúng repo/worktree/cổng; không lấy CWD hoặc route từ dự án nguồn. Chọn test runner hiện có trước, thêm [eval kit](../../tools/evals/README.md) khi cần đo chatbot/RAG/agent/guardrail. Chỉ đọc các guide ứng với scope. Quyết định kỹ thuật tìm được trong repo thì tự khảo sát; hỏi khi cần nghiệp vụ, quyền dữ liệu hoặc thay quyết định người dùng.

## Lịch triển khai

| Mốc | Việc làm | Bằng chứng cần có |
| --- | --- | --- |
| 0–10 | Chốt một luồng, oracle, ca critical, dữ liệu/provider và budget | Contract nghiệm thu, danh sách phần ngoài scope |
| 10–25 | Kiểm nút thắt; dựng luồng đầu; nối một test/adapter | Một đường thực chạy được, output sai bị scorer bắt |
| 25–85 | Xây lõi và tests cạnh logic quan trọng | Output thật, tests schema/quyền/state/error |
| 85–105 | Nối UI/API/provider; baseline; build/check bắt buộc | Luồng đầu cuối, latency/usage nếu đo được, lỗi có vị trí |
| 105–110 | Ngừng thêm tính năng; khóa code/prompt/data/cases | Manifest cuối, server đúng bản, không còn placeholder trong ca chạy |
| 110–120 | Chạy bộ cuối, review người, sửa hẹp nếu đủ thời gian, report | Evidence cuối, giới hạn và lệnh tái chạy |

Nếu nút thắt chính chưa qua, hoãn tùy chọn để giải quyết. Giữ auth, stale-result handling, schema, errors và tính đúng dữ liệu. Không thay bằng fake response rồi tuyên bố tích hợp đã hoàn tất. Có thể bàn giao phần đã hoạt động với nhãn đúng nếu một capability thiếu quyền/chưa kiểm.

## Chọn bộ kiểm đủ nhỏ nhưng có ý nghĩa

Tests phần mềm: đường thành công, input thiếu/sai, dependency lỗi; thêm quyền, duplicate/idempotency, cancel/race nếu sản phẩm có. UI: một hành trình chính và một phục hồi lỗi. AI: khoảng tám ca nhỏ có oracle trước khi chạy, tách dev/holdout phù hợp. Media: một đến ba output thật với brief và kiểm kỹ thuật lẫn xem/nghe.

Các số lượng trên chỉ phục vụ timebox. Không cộng fixtures/examples, negative controls hoặc một clip smoke thành điểm chất lượng AI. Không thêm dashboard, nhiều framework eval hoặc load suite trong mười phút cuối. Tool chưa có không được ghi installed/passed.

Chuẩn bị runner và deps từ sớm: runtime, browser, lockfile, dataset, adapter, scorer, output directory và permission. Runner mới của sản phẩm phải dùng cwd/commands/routes/locators đúng sản phẩm. Bộ eval đi kèm có CLI riêng, không tự chạy mọi unit/build/browser/media check của ứng dụng; cần tích hợp các bước đó theo stack thật.

## Ngân sách runner cuối

Mục tiêu dành tối đa khoảng sáu phút cho tự động để còn bốn phút review/report. Đây là thiết kế cho runner của sản phẩm, không phải lời hứa mọi command trong starter kết thúc trong sáu phút.

| Bước | Trần đề xuất | Phạm vi |
| --- | ---: | --- |
| Preflight | 15 giây | Runtime/server/data/cấu hình cần thiết; không cài tool |
| Software tests | 75 giây | Bộ lõi đã chọn theo tác động |
| Type/lint | 45 giây | Lệnh thực, không watch |
| UI | 75 giây | Luồng chính và phục hồi |
| Eval | 120 giây | Nhánh AI hoặc media theo contract |
| Tổng hợp | 30 giây | Số đếm/status/exit/evidence |

Tổng 360 giây là trần kế hoạch tuần tự. Build dài phải xong trước lượt cuối. Nếu cần cả text và media, chia budget trước; không nhân đôi thời gian ngầm. Dựa latency baseline để chọn số ca live, giữ ca chưa chạy là not-run. Không chạy song song các test cùng sửa database hoặc browser state.

Runner cần deadline tổng và từng step, thu command/duration/exit/error/log, dừng child process của chính run khi timeout, không kill server hay task khác. Report vẫn được tổng hợp khi một step lỗi. Missing tool/dataset là unavailable/error, empty suite không phải pass. Tính cả requests đang chạy và retry vào trần AI.

## Mười phút cuối

Phút 0–1: kiểm đúng bản và manifest rồi bắt đầu bộ đã chuẩn bị. Phút 1–6: runner chạy, người kiểm nội dung/voice/media nếu không xung đột. Phút 6–8: đọc lỗi và chỉ sửa hẹp có nguyên nhân rõ. Phút 8–9: chạy lại ca sửa cùng ca liên quan trên phiên bản mới. Phút 9–10: tạo report, chốt luồng demo và giới hạn.

Khi có lỗi, phân biệt sản phẩm, môi trường, adapter/scorer và oracle. Oracle chỉ đổi khi có nguồn độc lập chứng minh sai, không đổi theo output target. Không hạ ngưỡng, giấu fail, đánh skip ca đỏ hay retry vô hạn. Nếu sửa shared contract mà không còn thời gian kiểm ảnh hưởng, báo chưa đủ bằng chứng. Hoàn tác riêng sửa gấp gây regression; giữ lịch sử report cũ.

## Gate demo và bàn giao

Đủ điều kiện trình diễn một luồng khi luồng đó chạy trên bản cuối; tất cả ca critical tương ứng đạt; build/check bắt buộc đạt; không còn lỗi ảnh hưởng quyền/dữ liệu/kết quả cốt lõi; giới hạn được công bố. Lỗi cosmetic có thể ghi nhận nếu không cản tác vụ và phù hợp scope đã chốt. Không lấy demo đạt làm kết luận production-ready.

Report gồm branch/commit + trạng thái sửa local hoặc fingerprint, prompt/model/data/index/scorer version, mode local/replay/live/manual, commands, counts, từng ca critical, latency/cost hoặc unknown, phần đã xem/nghe, fail/chưa kiểm và lệnh chạy lại. Source đổi sau test phải ghi và kiểm lại phần ảnh hưởng. Không chép log/keys/private payload vào repo.

Tài liệu dự án nên lưu theo `plans/<timestamp>-<slug>/`, có plan ngắn và reports. Cấu trúc đó là đầu ra cần tạo khi triển khai, không phải bằng chứng nó đã tồn tại. Chỉ commit/push/deploy theo yêu cầu và quyền đã có của task; không suy việc viết report là quyền công bố.

## Prompt giao việc có thể dùng lại

```text
Xây hoặc hoàn thiện một luồng của [sản phẩm] trong [thời gian].
Luồng: [input -> hành động -> output]. Nguồn dữ liệu/quyền: [đã chốt].
Provider và ngân sách được phép: [cấu hình, calls/cost/deadline].
Các quyết định người dùng đã chốt: [phạm vi, ngưỡng, hành động].

Đọc hướng dẫn repo/source/tests/lockfiles trước. Giữ thay đổi ngoài task.
Chốt contracts và critical cases có oracle; tận dụng runner đang có.
Kiểm nút thắt sớm rồi làm một đường đầu cuối thật. Viết tests cho
logic/quyền/lỗi/state quan trọng trong lúc làm. Nối eval vào service
thật, không gửi expected/gold cho target và không dựng telemetry.
Kiểm scorer bằng output sai/thiếu. Demo harness là example, không là
điểm sản phẩm. Live/replay/manual phải có nhãn riêng.
Trước lượt cuối khóa version, hoàn tất build và chuẩn bị output mới.
Giữ fail/error/timeout/not-run, chỉ sửa nguyên nhân đã chứng minh.
Bàn giao source, lệnh cài/chạy/kiểm đúng project, report bằng chứng,
giới hạn và bước tiếp theo. Chỉ công bố/commit theo phạm vi đã được giao.
```

Các dấu ngoặc vuông là dữ liệu đầu vào cần điền. Khi nhận một task thật, khám phá được thông tin nào từ repo thì điền từ bằng chứng; không bắt người dùng trả lời lại những gì đã có.
