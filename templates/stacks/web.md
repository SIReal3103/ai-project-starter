# Hướng dẫn khi chọn web

Đây là hướng dẫn, chưa có frontend/backend, package.json ứng dụng hoặc dependency đã cài. `tools/evals/package.json` nếu có chỉ phục vụ xuất báo cáo của công cụ.

Chọn giao diện và backend theo luồng người dùng đã chốt. Bắt đầu với input → gửi → chờ → kết quả và đường xử lý lỗi; chỉ thêm auth, database hoặc service khi contract cần. Chọn framework, Node/runtime và package manager sau khi xét môi trường mục tiêu; giữ lockfile tương ứng.

Viết test logic/contract cùng tính năng. Với UI, dùng test component khi có hành vi đáng kiểm và E2E cho luồng chính trên app thật. Playwright/axe là lựa chọn khi đã có trang và setup phù hợp; dùng locator theo role/label, kiểm keyboard/error state và phần axe chưa kết luận bằng người.

Phân biệt smoke chỉ mở trang với E2E thực hiện tác vụ. Test ghi dữ liệu cần môi trường cô lập; không mock toàn bộ API để gọi là tích hợp hoàn chỉnh. Chạy build, typecheck/lint theo config thực trước khi chốt demo.

Thêm lệnh dev/build/test trong README sau khi đã có app và chạy được. Đừng dùng máy chủ demo của công cụ thay cho sản phẩm.
