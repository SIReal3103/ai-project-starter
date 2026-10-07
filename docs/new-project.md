# Khởi tạo dự án mới

Scaffolder tạo **bộ khởi đầu phát triển**, gồm tài liệu có chỗ điền và bản độc lập của bộ eval. Nó chưa triển khai tính năng sản phẩm, chưa cài dependency, chưa khởi tạo Git/remote và không gọi mạng.

Từ thư mục repo starter:

```bash
python3 scripts/new_project.py --name "Trợ lý tài liệu" --destination "../du-an-moi" --stack python
```

Lệnh tạo thư mục bên cạnh repo starter. Cũng có thể chọn đường dẫn tuyệt đối:

```bash
python3 scripts/new_project.py --name "Trợ lý tài liệu" --destination "/duong-dan/du an moi" --stack python
```

Thay `/duong-dan/du an moi` bằng nơi muốn tạo; giữ dấu ngoặc kép khi đường dẫn có khoảng trắng. Đường dẫn tương đối được tính từ nơi gọi lệnh và chuẩn hóa, bao gồm `..` khi bạn chủ động chọn thư mục cha. `--name` chỉ là tên hiển thị, không được dùng để ghép đường dẫn.

`--stack` nhận `python`, `web` hoặc `undecided` (mặc định). Nó chọn `docs/stack-guide.md`, không tự sinh app, dependency hoặc lệnh build chưa tồn tại. Khi chưa có đủ thông tin để chọn stack, giữ `undecided`.

## An toàn với thư mục đích

Đích phải chưa có hoặc là thư mục thật sự rỗng; file ẩn như `.gitkeep`, `.DS_Store` cũng làm đích không rỗng. Đích là file hoặc symlink bị từ chối. Tên dự án không nhận dấu phân cách đường dẫn. Sau chuẩn hóa, đích không được nằm trong repo starter hoặc bao quanh repo nguồn. Lệnh không có `--force` và không ghi đè. Nếu có lỗi filesystem giữa lúc xuất, có thể còn phần scaffold đã tạo; kiểm lại trước khi xử lý, không xóa dữ liệu đang có.

Nguồn template/eval được kiểm trước khi tạo đích. Bộ eval thiếu file bắt buộc hoặc chứa symlink trong phần được copy thì báo lỗi thay vì tạo liên kết về repo nguồn. Không dùng cùng đích cho hai lượt tạo đồng thời.

## File được tạo

```text
README.md
AGENTS.md
.gitignore
docs/
  project-brief.md
  acceptance-contract.md
  architecture-decisions.md
  implementation-plan.md
  eval-plan.md
  data-handling.md
  configuration.md
  handoff.md
  stack-guide.md
  guides/
    ... hướng dẫn sản phẩm, kiến trúc, dữ liệu và quy trình
tools/evals/
  ... mã nguồn, dataset demo, adapter, hướng dẫn và test của bộ eval
```

Không copy kết quả cũ trong `runs`, `reports`, `example-results`, `old-results`, `results`, `artifacts`; không copy `.git`, `node_modules`, môi trường `.venv*`, browser đã tải, cache, log, bytecode hoặc metadata `._*`. Mọi file dotenv được bỏ qua. Danh mục biến cấu hình nằm trong `docs/configuration.md`, chỉ gồm tên, mục đích và khi nào cần dùng. README của bản eval sinh ra được thay bằng hướng dẫn chạy mới, không còn link tới snapshot bị loại. Các output lần sau được tạo mới, có nhãn demo hoặc sản phẩm tương ứng.

Đọc README dự án vừa tạo và điền đề bài/contract trước khi triển khai. Bộ demo có thể chạy độc lập bằng những lệnh tương đối trong README; không cần giữ starter nguồn ở vị trí cũ. Thư mục mới không được Git init tự động; người dùng quyết định nơi quản lý phiên bản và lúc publish.

## Giao việc cho agent

> Dùng AGENTS.md và docs trong dự án mới làm điểm bắt đầu. Chốt một luồng thật theo project-brief và acceptance-contract, đọc stack-guide rồi chọn kiến trúc tối thiểu. Điền các quyết định còn thiếu từ bằng chứng; hỏi riêng mục tiêu/quyền/ngân sách chưa rõ. Triển khai hành vi thật, viết test cùng logic quan trọng, nối eval vào output/trace sản phẩm mà không lộ expected. Phân biệt demo của harness, test phần mềm, live, replay và review người. Chỉ cài công cụ cần cho stack; giữ lỗi và phần chưa đo trung thực. Bàn giao lệnh chạy thực cùng evidence và hạn chế; không tự commit/push.

## Kiểm scaffolder

```bash
python3 -m unittest discover -s tests -p 'test_new_project.py' -v
```

Các test chạy trong thư mục tạm, kiểm không ghi đè, tên không thể trở thành path traversal, từ chối đích chồng source, file ẩn, tên/path có khoảng trắng, liên kết tài liệu và khả năng di chuyển bản sinh ra khỏi source. Chúng kiểm generator; không phải test một sản phẩm đã được xây.
