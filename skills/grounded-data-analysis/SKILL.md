---
name: grounded-data-analysis
description: "Thiết kế, lập kế hoạch, triển khai hoặc review trợ lý hỏi số liệu có nguồn, SQL kiểm soát, bảng/biểu đồ và drill-down (F1). Dùng khi cần biến câu hỏi tự nhiên thành phân tích dữ liệu có thể đối chiếu; không dùng RAG thay phép tính và không mặc định thêm dự báo hay banking."
---

# Bàn phân tích số liệu có bằng chứng

Hoàn thành luồng câu hỏi → điều kiện được xác nhận → phép tính đúng → bảng/biểu đồ → hàng nguồn có thể đối chiếu. Số, đơn vị, kỳ, mẫu số và mức đầy đủ phải đi cùng nhau.

## Khởi động độc lập

1. Đọc [hợp đồng nhiệm vụ](references/task-contract.md) để xác định chế độ, workspace, quyền, cách kiểm và bàn giao.
2. Đọc phần **8/F1, 12.1, 12.4 và 14.3** trong [hướng dẫn chuyên môn](references/techstack-guide.md); đọc **8.1–8.3** chỉ khi có mở rộng tương ứng.
3. Scout docs, schema, data dictionary, import pipeline, auth, metric/query/chart hiện có. Phân biệt file thật với file dự kiến; không đọc secret hay toàn bộ dữ liệu riêng khi metadata đủ.
4. Giữ metric, provider và phạm vi người dùng đã chốt. Yêu cầu lập kế hoạch/review không tự cho phép sửa app, inference trả phí, gửi, deploy hay công bố.
5. Chỉ áp Gateway BTC, AI Log và `chung-khao/` khi đúng bối cảnh BTC; dự án khác dùng provider, stack và quyền đã xác nhận. Đường dẫn đội/vòng phải được xác nhận riêng từ repo thực tế.

## Thu thập đầu vào quyết định kết quả

- Người dùng cần tổng hợp, so sánh hay truy nguyên gì; kết quả dùng ở quyết định nào; phạm vi dữ liệu công khai hay riêng.
- Mỗi nguồn: vị trí/cách nhận, chủ sở hữu, quyền dùng, schema, source/import ID, checksum/version, kỳ thực có và lỗi nhập đã biết.
- Metric: ID, định nghĩa, phép tổng hợp, đơn vị, mẫu số, quy tắc null, làm tròn, ngoại lệ, người duyệt và ngày hiệu lực từ nguồn.
- Địa bàn: mã, hệ phân cấp và thay đổi ranh giới theo kỳ; không nối hai mã/tên gần nhau như cùng thực thể khi chưa có mapping.
- Kỳ: timezone, độ hạt và ranh giới khoảng; phân biệt kỳ không có dữ liệu với tổng bằng 0.
- Oracle: SQL viết độc lập và người đối chiếu các hàng nguồn; không lấy lời giải LLM hoặc chính query của app làm đáp án duy nhất.
- Thiếu định nghĩa/quyền/kỳ làm thay đổi kết quả: ghi owner, bằng chứng cần, phase bị chặn; tiếp tục phần schema/UI độc lập được phép.

## Phạm vi và trách nhiệm

- Khởi đầu một nguồn, khoảng 3–5 metric và tổng hợp/so sánh/drill-down nếu chưa có phạm vi khác; đây là đề xuất, không phải quota hay yêu cầu BTC.
- AI hiểu câu hỏi, đề xuất filters trong schema và diễn đạt typed result; không tự tính lại con số quyết định.
- Code xác thực identity, chọn metric cho phép, kiểm filters, chạy SQL và dựng series; con người chốt định nghĩa và trường hợp không thể so sánh.
- RAG chỉ tra định nghĩa/tài liệu; số liệu đến từ database hoặc file đã kiểm. Không thêm vector DB khi lookup đủ.
- Giữ stack phù hợp hiện có; khi bắt đầu mới, chọn PostgreSQL hoặc DuckDB, một thư viện DataFrame, schema validator và ECharts hoặc Plotly.
- SQL template tham số hóa là đường đầu tiên. Chọn công nghệ theo bước cần thực hiện và phép kiểm, không cài mọi lựa chọn.

## Contracts phải chốt trước luồng trình diễn

- `get_metric(metric_id, period, geography, grouping)` trả typed `result`, `unit`, `denominator` nếu có, `coverage`, `data_version`, `query_id`, filters và warnings.
- `drill_down(query_id, bucket)` tái dùng snapshot, filters và quyền đã lưu; kiểm bucket thuộc kết quả, không cho client/model mở rộng phạm vi.
- `explain_definition(metric_id, as_of)` trả định nghĩa, source/version, vị trí thật và hiệu lực; ngày upload không thay ngày hiệu lực.
- Backend cấp identity/tenant và kiểm quyền mỗi lần, kể cả drill-down/export; model không truyền tenant hoặc role tự chọn.
- Kết quả phân biệt `ok`, `partial`, `no_rows`, `ambiguous`, `invalid_input`, `api_error`, `cancelled`; lỗi DB không phải `no_rows`.
- State giữ filters đã xác nhận, câu hỏi đang thiếu, data/query version và run/revision; sửa kỳ hay dữ liệu làm kết quả phụ thuộc cũ trở thành stale.
- Chart chỉ nhận dữ liệu có schema; axes/legend/tooltip giữ đơn vị, kỳ và coverage. Không chạy JavaScript hoặc biểu thức model sinh.
- Export dùng cùng phạm vi/query/version; xử lý công thức nguy hiểm trong CSV theo định dạng xuất thực tế.

## Trình tự thực hiện

1. Kiểm schema, kiểu, trùng khóa, kỳ/đơn vị/địa bàn và quyền; lưu lỗi parse/null, staging trước khi publish một data version nhất quán.
2. Chốt metric dictionary với chủ dữ liệu; viết oracle độc lập trên các ca có dữ liệu, thiếu, biên và không thể so sánh.
3. Làm SQL templates và typed tools trước phần giải thích AI; dùng read-only role, timeout, row/resource limit và RLS nếu có nhiều tenant.
4. Nhận câu hỏi, giữ filters còn hiệu lực; hỏi đúng trường thiếu thay vì đoán hoặc hỏi lại toàn bộ.
5. Kiểm filters/metric/phiên bản; chạy query, ghi `query_id` đủ để tái lập và đối chiếu trong đúng quyền.
6. Dựng bảng/series từ cùng result; AI chỉ diễn đạt facts được cấp, đưa cảnh báo thiếu hoặc khác định nghĩa sát con số.
7. Cho mở định nghĩa và hàng nguồn; kiểm đường export, refresh, hủy và đổi filters không phát result cũ.
8. Chỉ thêm nâng cấp đã chọn sau khi luồng xuyên suốt và oracle đạt; thiếu modality hoặc phạm vi bắt buộc phải báo chưa đạt.

## Mở rộng có điều kiện

- Banking chỉ khi đề chọn: Decimal truyền JSON bằng chuỗi, tách currency, kỳ `[start,end)`, status giao dịch theo định nghĩa, không suy số dư khi thiếu opening balance/coverage.
- Đối soát chỉ đọc/phân tích: receipt cần trường đã kiểm; ghép currency/amount/time/reference theo rule được duyệt, mơ hồ trả nhiều ứng viên. Không tìm thấy chưa chứng minh chưa thanh toán; không thêm chuyển tiền/khóa tài khoản.
- NL2SQL chỉ khi templates thiếu: allowlist view/schema/joins, parse AST cả CTE/subquery, một SELECT, quyền tối thiểu và giới hạn tài nguyên; không dùng regex hay `eval` làm hàng rào.
- Anomaly chỉ khi có mục tiêu/lịch sử: validation → rule → robust statistics → ML nếu có bằng chứng; temporal split, `insufficient_history`, reason/evidence/version; score không phải xác suất gian lận.

## Lỗi, khôi phục và kiểm chứng

- Thiếu dữ liệu giữ `partial`/coverage; không đổi null thành 0. Nguồn mâu thuẫn hoặc metric khác định nghĩa cần cảnh báo/hỏi lại theo quy tắc đã duyệt.
- Retry đọc có giới hạn ở một lớp theo deadline; 401/403 cần sửa quyền, budget cạn dừng. Không đổi provider hay tạo dữ liệu để che lỗi.
- Mỗi result gắn run/revision; hủy hoặc sửa phải chặn late commit và UI cũ. Snapshot nguồn cũ giữ để audit theo chính sách lưu trữ.
- Unit/contract: exact match giá trị, mẫu số, đơn vị, filters, kỳ, null, làm tròn; đối chiếu bằng SQL/Decimal độc lập.
- Integration: query vượt quyền, ID của người khác, joins nhân đôi hàng, thiếu kỳ, đổi ranh giới, export, drill-down và dữ liệu stale.
- UI/E2E: series bằng bảng, nhãn/đơn vị đúng, cảnh báo thấy được và truy về hàng nguồn thật; không chỉ kiểm HTTP 200.
- AI eval: bộ dev/holdout tách biệt, hỏi mơ hồ và injection trong dữ liệu/định nghĩa; kiểm đúng tool/args, grounded claims và từ chối đúng.
- Ghi n, versions, lỗi dịch vụ, latency/cost và giới hạn. Sai số nghiệp vụ, che phần thiếu hoặc lộ dữ liệu chặn bàn giao phần liên quan.

## Kết thúc và bàn giao

- Nghiệm thu khi một câu hỏi thật đi trọn luồng, số/series đúng oracle và drill-down tái lập trong cùng scope; ngưỡng mềm cần chủ sản phẩm chốt trước holdout.
- Bàn giao inventory, metric dictionary, data/tool/state contracts, oracle, lệnh/cách demo đã kiểm, bằng chứng test và phần chưa xác minh.
- Khi lập kế hoạch nhiều phase, dùng [hợp đồng kế hoạch](references/planning-handoff.md); mỗi yêu cầu có phase, phép kiểm, oracle và điều kiện mở phụ thuộc.
- Báo riêng kiểm offline, tích hợp thật và nghiệm thu; capability chỉ `verified` với bằng chứng đúng môi trường, không vì có tài liệu API.
