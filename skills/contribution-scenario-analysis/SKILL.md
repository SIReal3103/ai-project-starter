---
name: contribution-scenario-analysis
description: "Thiết kế, lập kế hoạch, triển khai hoặc review phân rã đóng góp vào thay đổi và mô phỏng phương án có công thức được duyệt (F2). Dùng khi cần so hai kỳ, giải thích breakdown và thử giả định tách khỏi dữ liệu gốc; không coi đóng góp là nguyên nhân hay mô phỏng là dự báo."
---

# Phân tích đóng góp và mô phỏng phương án

Biến câu hỏi “nhóm nào đóng góp vào thay đổi” thành phép phân rã tái lập, rồi cho thử tham số trong công thức đã duyệt. Kết quả giả định phải giữ nhãn mô phỏng và truy về baseline.

## Khởi động độc lập

1. Đọc [hợp đồng nhiệm vụ](references/task-contract.md) để xác định chế độ, repo, phạm vi và quyền hiện có.
2. Đọc **8/F2**, nền tảng dữ liệu **8/F1**, **12.1 và 14.3** trong [hướng dẫn chuyên môn](references/techstack-guide.md); mở **8.1–8.3** chỉ khi cần.
3. Scout data dictionary, metric/query modules, formula registry, auth, charts và tests thực tế; ghi rõ các file chưa tồn tại là dự kiến.
4. Giữ công thức, phạm vi và lựa chọn người dùng đã chốt. Lập kế hoạch/review không tự cho phép sửa app, gọi AI trả phí, gửi hay deploy.
5. BTC/Gateway/AI Log/`chung-khao/` chỉ áp dụng trong bối cảnh BTC; nơi khác giữ provider và workspace được phép. Đường dẫn đội/vòng phải được xác nhận riêng từ repo thực tế.

## Đầu vào phải tìm và đối chiếu

- Metric mục tiêu, đơn vị, numerator/denominator nếu có, phép tổng hợp, rounding, nguồn định nghĩa và người duyệt.
- Hai kỳ nền: timezone/ranh giới kỳ, scope người dùng, coverage, data version, các nhóm/dimension và thay đổi phân loại hoặc địa bàn.
- Cách phân rã: tuyến tính hay phi tuyến/tỷ lệ, thứ tự hoặc phương pháp đã chốt, interaction/residual, cách reconciliation tổng.
- Công thức mô phỏng: formula ID/version, văn bản giải thích, nguồn/owner, tham số, kiểu, đơn vị, biên hợp lệ, phụ thuộc và ngoại lệ.
- Mỗi tham số là input được thay hay hằng số baseline; xác định null, chia cho 0 và precision theo nghiệp vụ, không tự chọn giả định kinh tế.
- Oracle là bảng tính độc lập hoặc phép tính tay đã đối chiếu; cần ca biên và trường hợp không thể so sánh, không dùng chính executor để tự chứng nhận.
- Đầu vào chưa có phải có owner/cách lấy, phase phụ thuộc và việc độc lập còn làm được; không tạo dữ liệu nền giả để báo sẵn sàng.

## Phạm vi và phân công quyết định

- Nếu chưa có phạm vi khác, đề xuất một metric, một công thức và khoảng ba tham số; con số này là MVP tham khảo, không tự thay yêu cầu đã chốt.
- AI diễn giải câu hỏi, chọn điều kiện/tool trong allowlist và trình bày kết quả. Code thực hiện mọi phép tính, giới hạn tham số và version checks.
- Chủ dữ liệu duyệt metric, công thức, phương pháp phân rã, đơn vị và giả định; người kiểm xác nhận lời giải không suy quan hệ nhân quả.
- Giữ stack đáp ứng hiện có; nếu bắt đầu mới, chọn PostgreSQL hoặc DuckDB, Python/schema validator và một thư viện chart.
- Dùng Decimal khi giá trị cần chính xác, truyền decimal dạng chuỗi; chọn policy rounding tường minh. Không dùng LLM làm bộ dự báo.
- Workflow code đủ cho MVP; chỉ bật native tool calling hoặc capability khác sau phép thử đúng provider/model/payload/quyền.

## Contracts cốt lõi

- `decompose_change(metric_id, periods, dimension)` nhận hai kỳ và dimension hợp lệ; trả baseline/current, contributions, units, method_version, residual/interactions, reconciliation và coverage.
- Reconciliation biểu diễn quan hệ theo phương pháp đã duyệt; không ép đóng góp tỷ lệ/phi tuyến cộng như metric tuyến tính.
- `simulate_scenario(formula_id, parameters, baseline_version)` trả typed result, assumptions, units, formula_version, baseline/data version, warnings và status.
- Backend lấy identity/scope từ phiên; tool không nhận tenant, quyền hay công thức thực thi do model tự cấp.
- Formula registry/parameter allowlist ở server; cấm `eval` biểu thức tùy ý từ người dùng hoặc LLM. Công thức sửa thành version mới theo quyền.
- Scenario có ID, owner/scope, tham số, baseline/formula version và nhãn mô phỏng; lưu riêng, không ghi đè dataset thật.
- State giữ kỳ/dimension đã chốt, scenario hiện tại và run/revision; thay baseline/formula làm kết quả cũ stale, cần tính lại rõ ràng.
- Status phân biệt `ok`, `partial`, `ambiguous`, `invalid_input`, `no_rows`, `api_error`, `cancelled`; không trả số 0 thay lỗi hoặc thiếu nền.
- Bảng, chart và export lấy cùng typed result, giữ nhãn “mô phỏng”, giả định, đơn vị, nguồn và phiên bản.

## Trình tự thực hiện

1. Kiểm quyền, schema, coverage và định nghĩa của hai kỳ; xác nhận có thể so sánh, nếu không thì chỉ rõ điều kiện thiếu.
2. Chốt phương pháp phân rã cùng bảng tính oracle, gồm residual/interactions khi liên quan; không chọn phương pháp chỉ để biểu đồ cộng đẹp.
3. Implement tool phân rã bằng SQL/Python, reconciliation và lỗi; xác minh với oracle trước khi thêm lời giải AI.
4. Implement formula registry, typed parameters, boundary/unit checks và executor; kiểm baseline bất biến sau mọi lần mô phỏng.
5. Dựng form/sliders từ cùng schema server, hiển thị biên và đơn vị; server luôn kiểm lại, UI không phải nguồn luật.
6. Tính breakdown, giải thích “đóng góp vào thay đổi” từ result có nguồn; giữ residual/coverage gần kết quả.
7. Nhận giả định mới, chạy công thức, so baseline với scenario và cho sửa/thử lại; không gọi đó là kết quả sẽ xảy ra.
8. Kiểm cancel, hai lượt điều chỉnh gần nhau, refresh và export; run cũ không được ghi đè scenario mới.

## Mở rộng chỉ khi đã chọn

- Tối ưu hóa/dự báo cần mô hình, hàm mục tiêu/ràng buộc, dữ liệu và đánh giá riêng; không suy quyền từ yêu cầu mô phỏng.
- Banking giữ tiền Decimal, currency riêng, kỳ `[start,end)`, trạng thái giao dịch phù hợp và coverage; không suy tỷ giá/số dư hoặc thêm thao tác chuyển tiền.
- NL2SQL sau MVP cần AST allowlist kể cả CTE/subquery, SELECT duy nhất, role chỉ đọc, timeout/row limit; templates vẫn phù hợp khi đáp ứng câu hỏi.
- Anomaly cần mục tiêu, lịch sử, baseline trước thời điểm dự đoán và temporal eval; thiếu history trả `insufficient_history`, không nhãn hóa gian lận từ score.

## Lỗi và khôi phục

- Khác định nghĩa, dimension hoặc ranh giới kỳ: dừng so sánh sai, chỉ ra mapping/quyết định cần lấy; không lấp thiếu bằng số 0.
- Tham số ngoài miền, unit mismatch, chia 0 hoặc null quyết định: trả lỗi có trường cần sửa; không âm thầm clamp khi chưa có rule.
- Formula/baseline đổi giữa lúc chạy: kiểm version trước commit, trả stale và đề xuất tính lại; không sửa dữ liệu gốc để khớp scenario.
- Retry đọc/tính an toàn có giới hạn một lớp; giữ input và trạng thái thật khi API/DB lỗi, chặn late write sau cancel.
- Quota/deadline/cost được cấu hình theo dự án; không đổi provider hoặc báo verified chỉ vì HTTP 200.

## Oracle, nghiệm thu và bàn giao

- Unit/contract so với bảng tính độc lập: contribution, tổng reconciliation, unit, rounding, null, 0, số âm và biên tham số theo miền cho phép.
- Integration kiểm quyền, scenario tách dataset, baseline/formula version, đồng thời, cancel, export và tái lập cùng input/version.
- AI holdout kiểm không biến đóng góp thành nguyên nhân, không gọi giả định là dự báo và không che residual/thiếu dữ liệu.
- Bất biến dữ liệu gốc, quyền và formula allowlist phải đạt mọi ca liên quan; ghi đè số thật hoặc công thức trái phép chặn bàn giao.
- Người kiểm chốt ngưỡng chất lượng lời giải trước holdout; báo số mẫu, lỗi dịch vụ, latency/cost, phiên bản và các phần chưa đánh giá.
- Kết thúc khi người dùng chọn hai kỳ hợp lệ, xem breakdown rồi sửa giả định và đối chiếu được cùng oracle/nguồn.
- Bàn giao data dictionary, formula/method registry đã duyệt, contracts, scenario lifecycle, oracle, cách chạy/demo và bằng chứng.
- Kế hoạch nhiều phase dùng [hợp đồng kế hoạch](references/planning-handoff.md); nêu readiness và bước đầu agent mới có thể thực hiện mà không cần lịch sử chat.
