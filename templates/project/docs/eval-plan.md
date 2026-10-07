# Kế hoạch test và eval

Trạng thái: **sản phẩm chưa được đánh giá**. Bộ eval đi kèm là công cụ và ví dụ; kết quả assistant demo không chứng minh sản phẩm mới đúng.

## Chọn phạm vi theo contract

| Phần | Khi cần | Bằng chứng |
| --- | --- | --- |
| Test phần mềm | Mọi sản phẩm có logic | Schema, state, phép tính, lỗi phụ thuộc và quyền thực |
| UI/API | Có luồng giao diện/dịch vụ | Một luồng chính, một đường phục hồi; không chỉ HTTP 200 |
| AI live | Có target thật, dữ liệu và ngân sách cho phép | Output hiện tại cùng model/prompt/data/version |
| Replay | Có output đã lưu | Chấm output cũ; không chứng minh API hiện tại sống |
| RAG/agent | Có retrieval/tool | Nguồn thực, tool name/args/result và trạng thái cuối |
| Artifact/media | Sản phẩm tạo file | Giải mã/định dạng và review nội dung thật |
| Người đánh giá | Ngữ nghĩa, hình/âm hoặc tiêu chí khó xác định | Rubric, vùng đã xem và lý do cụ thể |

## Chuẩn bị dữ liệu và adapter

Khởi đầu bằng tập nhỏ có giá trị: luồng phổ biến, mơ hồ/thiếu dữ liệu, input sai, giới hạn quyền/phạm vi và chất lượng đặc thù. Giữ tập holdout riêng; mẫu nhỏ chỉ là smoke/regression, không phải benchmark đại diện. Chọn expected từ oracle độc lập hoặc nguồn đã được người kiểm.

Đọc [bộ eval](../tools/evals/README.md) và [hướng dẫn agent](../tools/evals/agent-guide.md). Các ca mẫu thuộc chatbot/RAG/agent/guardrail. Dùng [dataset guide](../tools/evals/datasets/dataset-guide.md), tạo ca sản phẩm theo schema và validate trước khi chạy. Với phần mềm không có AI, chọn test hành vi theo stack; không dựng chatbot giả để dùng bộ eval.

Adapter gọi đúng service sản phẩm và chỉ gửi input allowlist. Không chuyển expected, gold IDs hoặc nội dung evaluator vào prompt. Trace phải đến từ hoạt động thật; không suy tool call hay guardrail action từ lời kể của model. Nạp key qua môi trường; judge dùng cấu hình riêng và chỉ bật khi đã có rubric, endpoint và budget được phép.

## Đọc và kiểm kết quả

Chạy một output sai có chủ đích và một output thiếu để kiểm scorer; đối chứng không cộng vào điểm sản phẩm. Phân biệt pass, fail, error, timeout, not-run và not-applicable có lý do. Metric đã đo chưa tự thành ngưỡng release. Keyword và citation ID hợp lệ chưa chứng minh không hallucinate.

Tỷ lệ đạt phải ghi mẫu số và đặt cạnh ca lỗi/chưa chạy. Report cần: câu hỏi, mong đợi, output thực, kết luận và lý do; mode demo/live/replay; phiên bản; độ trễ; usage/chi phí có hoặc chưa đo. Không lấy report mẫu của framework làm kết quả sản phẩm.

## Lượt nghiệm thu cuối

Trước lượt cuối: khóa phiên bản code/prompt/data, chạy build bắt buộc, xác nhận đúng server/corpus và adapter. Chọn timebox phù hợp; ví dụ tự động khoảng 6 phút để còn 4 phút kiểm bằng người là kế hoạch cần đo lại. Không tải runtime/browser/model trong phút cuối.

Lệnh thực của sản phẩm và budget: [Cần điền sau khi tích hợp]. Các ca critical: [Cần điền từ contract]. Phần chưa đo: [Cần điền]. Bàn giao theo [mẫu](handoff.md).
