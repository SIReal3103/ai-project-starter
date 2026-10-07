# Hướng dẫn khi chưa chọn stack

Chưa chọn runtime hoặc framework, và starter không tạo mã ứng dụng. Bắt đầu từ contract: input/output, luồng chính, dữ liệu, môi trường chạy và năng lực đội.

CLI tác vụ đơn giản có thể dùng runtime quen thuộc với ít dependency. Web cần UI thật nếu luồng người dùng yêu cầu; API cần thiết khi có client hoặc tích hợp gọi từ ngoài. LLM chỉ dùng khi giúp tác vụ; không thêm chatbot, database hoặc agent để làm đầy danh mục.

So sánh hai hoặc ba phương án thực về thời gian dựng luồng, thư viện cần, triển khai và khả năng kiểm chứng. Có thể làm spike nhỏ để giải quyết điều chưa chắc, ghi rõ spike chưa phải sản phẩm. Ghi quyết định và trade-off vào architecture-decisions.md trước khi mở rộng.

Bộ eval có thể kiểm demo xác định ngay bằng Python, nhưng không buộc sản phẩm dùng Python hay AI. Khi có stack, cập nhật tài liệu này, chọn một test runner phù hợp và chỉ thêm tool khi có phép đo hữu ích.
