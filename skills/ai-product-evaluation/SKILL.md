---
name: ai-product-evaluation
description: Thiết kế, review hoặc triển khai bộ kiểm và eval cho sản phẩm AI với dataset, oracle độc lập, runner và cổng nghiệm thu; dùng khi cần đo chất lượng, regression hoặc so phiên bản, không coi coverage hay model tự chấm là bằng chứng đủ.
---

# Đánh giá sản phẩm AI có oracle

Đo hành vi người dùng nhận được bằng dữ liệu, luật và nhãn độc lập; giữ cả lỗi dịch vụ và tác động có hệ quả trong báo cáo.
Phân biệt kiểm phần mềm, chất lượng AI, integration và nghiệm thu sản phẩm thay vì gom thành một điểm chung.

## Khởi động không cần context trước

1. Đọc [hợp đồng tác vụ](references/task-contract.md) và [trích nguồn techstack](references/techstack-guide.md), trọng tâm phần 14.
2. Xác định chế độ lập kế hoạch, review, tạo runner/dataset hay chạy eval; đọc code, schema, tests và báo cáo liên quan.
3. Chốt tác vụ, nhóm người dùng, output/state, rủi ro sai, phiên bản và câu hỏi đánh giá cần trả lời.
4. Scout oracle, dữ liệu có quyền, test identity, provider, quota và baseline; ghi rõ phần có thật/được hứa/giả định/chưa kiểm.
5. Nếu chỉ lập kế hoạch, dùng [hợp đồng bàn giao](references/planning-handoff.md), ghi file/lệnh dự kiến và gate, chưa tự chạy inference trả phí.
6. Nếu được giao chạy, giữ phạm vi/ngân sách/quyền đã có; không xin lại tác vụ được cấp nhưng cũng không mở rộng thành load test live.
7. BTC áp gateway cho target, embedding metric, judge và red-team AI; ngoài BTC giữ provider được chọn, không tự thay.

## Chọn phép kiểm từ câu hỏi

| Loại | Cần chứng minh |
|---|---|
| Unit/contract | Tính, parse, format, schema, state và error đúng với input cụ thể |
| Integration | DB/auth/tool/upload/queue phối hợp bằng dependency thật trong môi trường được phép |
| UI/E2E | Người dùng hoàn thành luồng gồm thiếu dữ liệu, sửa, hủy và quyền |
| AI regression | Cùng case/snapshot, prompt/model mới thay đổi chất lượng thế nào |
| Retrieval/grounding | Evidence đúng được tìm, claim được nguồn đúng phiên bản hỗ trợ |
| Voice/ảnh | Trường quyết định được nghe/đọc đúng và phục vụ tác vụ |
| Load/observability | Workload đã chốt giữ quota, thành công và xác định nguyên nhân lỗi |

- Coverage, graph compile, HTTP 200 hoặc một demo đẹp không trả lời thay các câu hỏi trên.
- Bắt đầu scorer code/runner hiện có; chỉ thêm framework khi giải quyết tiêu chí chưa chấm được và đã rà dependency/egress.

## Dataset và oracle contract

- Mỗi case có `case_id`, nhóm/rủi ro, input/history/assets, identity/scope do harness cấp, data/source/prompt/model versions.
- Expected chứa status, dữ liệu chuẩn hoặc invariants, evidence IDs/version, forbidden actions, người/quy trình xác nhận nhãn.
- Latency/cost limit chỉ thêm khi đã chốt; phân biệt mục tiêu đề xuất và giới hạn có quyền áp dụng.
- Số dùng SQL/Decimal độc lập; workflow dùng bảng luật; ảnh/audio dùng nhãn người kiểm; nội dung mở dùng rubric chuyên môn.
- Target model không vừa tạo đáp án chuẩn vừa tự chứng nhận. AI sinh case chỉ là draft phải review, không là phản hồi người dùng thật.
- Tách dev và holdout theo nguồn/mẫu hóa đơn/người nói/thời gian/nhóm câu hỏi phù hợp; không đưa expected vào prompt target.
- Đề xuất khởi đầu 20–30 case cho một ý tưởng nếu chưa có bộ dữ liệu; chọn theo rủi ro, không gọi số đó là benchmark đại diện.
- Có ca thường, thiếu/mơ hồ, permission, lỗi dịch vụ, hủy và đối kháng liên quan; audio/ảnh cần đa dạng người/mẫu thực có quyền.
- Không coi placeholder là nhãn thật; thay bằng nhãn đã xác nhận trước chạy. Thiếu oracle bắt buộc là phụ thuộc nghiệm thu chưa giải quyết.

## Chọn metric đúng tác vụ

- Số liệu: exact match giá trị, filters, đơn vị, kỳ và coverage; so tiền bằng Decimal từ chuỗi, thời gian theo timezone/interval chuẩn.
- OCR/hóa đơn: field precision/recall, CER và exact match tiền; CER tốt không bù một chữ số sai ở trường quyết định.
- Phân loại: macro-F1, route accuracy, hỏi lại/từ chối đúng theo nhãn và quy tắc có nguồn.
- STT: WER/CER cùng đúng tên/số/mã/phủ định và task success; ghi normalization/tách từ tiếng Việt, không bỏ dấu/số để làm đẹp điểm.
- Im lặng phải có ca transcript bịa; chấm cả kết quả tác vụ sau sửa transcript, không chỉ bản STT thô.
- TTS: người nghe kiểm dễ hiểu, dữ kiện, ngắt câu và latency hữu ích trên cùng text; model tự chấm chưa đủ.
- Retrieval: Recall@k trên query có evidence chuẩn; MRR từ vị trí evidence đúng đầu tiên; ID trùng không tăng điểm, no-evidence chấm riêng.
- Grounding: claim-source-version, unsupported claims và abstention; nguồn sai hiệu lực vẫn là sai dù nội dung gần giống.
- Tools: đúng tool/args, quyền và task success; chấp nhận nhiều đường hợp lệ, không khóa cứng thứ tự trace không cần thiết.
- Nội dung/media: facts, tính dùng được, số chỉnh sửa, thời gian/bộ, hiểu nội dung, hình/lời và file cuối; thay đổi dữ liệu kiểm stale/sửa nhầm.
- Game/bot: state, rubric, điểm/phiếu, dedup, callback permission và handoff bằng luật/DB/người chuyên môn.
- Anomaly: precision/recall khi có nhãn hoặc workload khi chưa có; temporal split, không gọi score là xác suất gian lận.
- Vận hành: task success, error rate, latency p50/p95 và cost/task thành công; ghi n, mẫu số, retries và cache policy.

## Runner và scorer

1. Khóa dataset/rubric/ngưỡng trước holdout; chụp version code, prompt, model, parser/index/data và cấu hình có ảnh hưởng.
2. Runner gọi đúng app/workflow được đánh giá, thu status, final text, tool calls/results, usage, latency và error.
3. Kiểm schema/status/permission/invariants trước lời văn; exception hoặc output incomplete không được nuốt thành pass.
4. So nguồn/evidence trong tập thật đã cấp; ghép tool song song theo call ID/name/args hợp lệ.
5. Tách lỗi API, timeout, schema, hành vi sai và thiếu oracle; giữ toàn bộ trong mẫu số task success khi có liên quan.
6. Trả điểm từng tiêu chí và lý do; một lỗi quyền/tiền/luật/side effect không bị trung bình chất lượng che đi.
7. Fault injection offline được ghi là ca lỗi kiểm soát, không trình diễn nó như inference thật thành công.
8. Judge chỉ chấm ngữ nghĩa cần thiết; chốt rubric, calibrate với người trên tập con, che tên model/đảo thứ tự khi so A/B.
9. Judge không quyết định quyền, tổng tiền hay trạng thái đã commit; thêm ca nguồn chứa injection nhằm đánh lừa judge.
10. Lưu mọi run; không chỉ chọn lần đẹp nhất, không sửa holdout để che fail; thêm lỗi vào regression sau khi lưu kết quả.

## Egress, dữ liệu và ngân sách

- Cấu hình tường minh mọi provider phụ; không giả định self-hosted runner/tracing đồng nghĩa judge local.
- Kiểm phiên bản hiện cài và tài liệu chính thức trước dùng biến tắt telemetry/update/remote generation; snapshot cấu hình không đủ.
- Tắt sharing/sync/telemetry không cần; kiểm destination thực, plugins, callbacks/updater và dùng isolation phù hợp với môi trường.
- Không gửi source/PII/secret qua report hoặc framework mặc định; canary đối kháng là dữ liệu giả trong harness cô lập, không secret thật.
- Dự toán target + judge + embedding + retries, giới hạn concurrency/deadline; thiếu cost ghi chưa đối soát thay vì 0.
- Local SQL/UI/queue load không chứng minh gateway chịu cùng tải; live inference load phải thuộc quota/ngân sách/phạm vi đã cho.

## Cổng kết thúc và báo cáo

- Mỗi yêu cầu bắt buộc có case, oracle và điều kiện đạt; bộ an toàn bắt buộc không rỗng, đã chạy và đủ bằng chứng.
- Timeout/hạ tầng/thiếu oracle làm hành vi chưa đánh giá được là `inconclusive`, không là pass hoặc cớ bỏ case khỏi báo cáo.
- Quyền, tiền, luật thắng, phê duyệt và side effect phải đúng trên mọi case liên quan; một lỗi đã thấy chặn phát hành phần đó.
- Chấm attack success, hành động cấm, false refusal, claim thiếu evidence và lộ qua tool/DB/network/stream/TTS/export.
- Ngưỡng mềm do chủ sản phẩm chốt sau baseline trước holdout; không sao chép 80%/95% hoặc gọi ngưỡng đề xuất là chuẩn BTC.
- Báo chất lượng có điều kiện trên lượt trả lời nếu hữu ích, đồng thời giữ task success toàn bộ và lỗi dịch vụ riêng.
- So version trên cùng case/snapshot; cache hit ghi riêng, output cache cũ không chứng minh model/code mới đã chạy.
- Cặp kiểm công bằng giữ quyền/facts/khóa tra cứu tương đương, chỉ đổi yếu tố không liên quan; không suy nhóm nhạy cảm từ tên/ảnh/giọng.
- Báo n/mẫu số theo nhóm thiết bị/kênh/tiếng ồn/ảnh/cách diễn đạt; mẫu ít ghi chưa đủ kết luận, nhiều lượt một người không là nhiều mẫu độc lập.
- Khoảng tin cậy theo đơn vị lấy mẫu phù hợp; p50/p95 trên tập nhỏ là mô tả phép thử, không SLA; 0 lỗi quan sát không là bảo đảm tuyệt đối.
- Before/after học tập dùng bài tương đương khác câu, báo quy mô và giới hạn pilot, không suy rộng hiệu quả giáo dục.
- Giao cấu hình/version, dataset manifest, lệnh/cwd đã chạy, pass/fail/inconclusive từng nhóm, lỗi nghiêm trọng, latency/cost và ví dụ đã che dữ liệu.
- Nêu nguyên nhân có bằng chứng, bước sửa, owner phần thiếu và mức sẵn sàng; kế hoạch eval không đồng nghĩa sản phẩm đã được đánh giá.
