# Kiểm chứng lượt eval và skill

Ngày 07/10/2026. Người dùng yêu cầu chạy lại eval, xuất báo cáo, cập nhật GitHub và tạo skill.

## Eval mới

- MLX inference mới: Qwen2.5-0.5B-Instruct 4-bit, revision `53a32aee5e9447773fd2b85988395066aef3700a`; 24 ca; kết thúc 16:57:47 +07:00.
- Dataset và messages giữ nguyên, hash ghi trước inference. Raw answers mới giống baseline 24/24; không đổi expected/output để nâng điểm.
- Replay chấm mới: thô 7/24 đạt, không lỗi framework. Exit 1 phản ánh ca fail.
- Ragas 0.4.3: 12 phép đo offline (6 recall, 6 AP). DeepEval 4.2.8: 18 exact-match. Chưa có semantic judge hoặc agent executor.
- Audit: 6/24 đạt, 18 fail; R04 false positive vì số trong citation được ghi riêng, không sửa raw results. Script audit kiểm output giống baseline trước khi dùng lại nhận xét cũ; kiểm đối chứng thay một answer trong bản tạm khiến script dừng đúng.
- Median local inference 0,161 giây; p95 nearest-rank 0,421 giây. Không suy latency end-to-end hoặc cải thiện chất lượng từ khác biệt thời gian này.
- Không gọi lại crawl/retrieval/lifecycle; context lấy snapshot. Không phải dữ liệu khách hàng hoặc nghiệm thu chatbot tích hợp.

## Báo cáo và tính portable

- HTML/PDF cùng `report-data.json`: 26 mục, 24 đã chạy, 6 đạt, 18 chưa đạt, 1 chưa chạy, 1 bị chặn. 14 chỉ số giữ ngưỡng chưa phê duyệt.
- PDF tổng hợp 17 trang, có đủ 26 mã ca và 14 metric; 4 phiếu đại diện được công bố rõ; HTML giữ toàn bộ chi tiết. Xem ảnh mọi trang và kiểm lại trang sửa cuối; không có trang trắng/chữ tràn khung.
- HTML kiểm qua trình duyệt ở 1280px, không tràn ngang; sửa nhãn evidence dùng chung để không nói nhầm lượt mới là báo cáo cũ. Renderer và thiết kế responsive đã được kiểm ở task template trước.
- ZIP cập nhật 97 file, không model/venv/cache/log/key. Giải nén sang thư mục độc lập có khoảng trắng; render HTML giống bản bàn giao từng byte; 9 test báo cáo đạt.
- 25 test evaluator/transport/portability đạt. Gitleaks scan kit: chỉ bắt canary tổng hợp trong script fixture; xác minh nguồn và gắn allow trên đúng dòng canary, scan lại không còn findings. Không dùng allowlist rộng hoặc đưa key thật vào gói.

## Skill

`skills/ai-qa-evals/` có SKILL.md và UI metadata; cài vào thư mục skills của Codex và chạy quick_validate thành công. Skill tự hướng dẫn clone repo khi workspace mới chưa có kit, đọc guide theo tác vụ, phân biệt inference/replay/render, giữ budget/evidence và điều kiện công bố. Không phụ thuộc đường dẫn máy tác giả; giữ chọn tự động mặc định.

Giới hạn kiểm chứng: không cài lại toàn bộ MLX/Ragas/DeepEval từ mạng trong một hệ điều hành mới; lượt inference dùng runtime sẵn có, còn tính độc lập của bộ render được kiểm từ ZIP mới. Không gọi API judge trả phí, không thay model/prompt và không sửa oracle chuỗi của runner gốc trong task này; lỗi oracle vẫn công khai trong báo cáo và được audit riêng.
