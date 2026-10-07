# Hoàn thiện bộ skill QA, eval, hiệu năng và bảo mật

Trạng thái: hoàn thành nội dung và kiểm tra; sẵn sàng công bố commit thuộc task.

Phạm vi: bổ sung hướng dẫn có thể thực hiện cho test phần mềm, LLM/RAG/agent, latency/load/reliability và security/privacy; mở rộng danh mục chỉ số và giữ bảng QA 7 cột. Không chạy scan/load/inference của sản phẩm trong task viết skill.

- [x] Viết reference theo nhóm, đối chiếu CLI với tài liệu chính thức và runner hiện có.
- [x] Cập nhật skill entrypoint, danh mục chỉ số và README để dễ tìm.
- [x] Kiểm link, YAML, ví dụ/công thức và tính tự chứa khi copy gói.
- [x] Đồng bộ bản cài local; giới hạn phạm vi commit/push vào skill/docs thuộc task.

Tiêu chí: agent biết công cụ nào áp dụng, chạy ở đâu, dữ liệu/evidence cần lưu, cách chấm và giới hạn; phần chưa chạy hoặc mock không được coi là pass thật. Giữ nguyên báo cáo/output đang sửa từ các lượt trước.

Kiểm tra và giới hạn: [báo cáo xác minh](reports/verification.md).
