# Kiểm thử phần mềm, UI/API và coverage

Áp dụng cho repo sản phẩm đã xác định. Đây là hướng dẫn chạy, không phải bằng chứng rằng các công cụ đã được chạy. Lệnh ở root sản phẩm, trừ khi ghi khác. CLI đối chiếu nguồn chính thức ngày 07/10/2026; ưu tiên phiên bản đã pin trong lockfile của dự án.

## Chuẩn bị

Đọc package.json/pyproject, tests, contract API và lệnh CI. Dùng test DB và tài khoản test; biết cách dọn tài nguyên do ca tạo. Nếu chưa có tests, viết ca cho hành vi thật trước; “0 tests” là thiếu kiểm thử. Không thêm test chỉ so chính implementation với nó.

- Repo npm có lock: `npm ci`; dùng package manager tương ứng nếu lock khác. Không tự đổi Jest sang Vitest chỉ để đủ tên công cụ.
- Repo Python: tạo `python3 -m venv .venv-qa`, cài dependency theo lock/requirements của repo. Các lệnh dưới dùng `.venv-qa/bin/python`; Windows dùng `.venv-qa\Scripts\python.exe`.
- Nếu thiếu framework được chọn, cài trong phạm vi dev dependency rồi pin phiên bản và lưu lock. Ví dụ `npm install -D vitest @vitest/coverage-v8` hoặc `.venv-qa/bin/python -m pip install pytest coverage`; kiểm Vitest và coverage provider tương thích cùng phiên bản. Không chạy lệnh cài nếu chỉ được yêu cầu review.
- Mỗi lượt dùng thư mục evidence mới. `artifacts/qa-run-001` dưới đây chỉ là tên ví dụ; không ghi đè lượt trước.

## Ma trận chức năng cần chứng minh

| Nhóm | Ca tối thiểu theo tính năng | Evidence và cách kết luận |
| --- | --- | --- |
| Unit | Parse/schema, phép tính, điều kiện biên, lỗi input, state transition | Assertion với oracle độc lập; số pass/fail/skip/error; không gọi mạng nếu không cần |
| Integration | Auth + DB + queue/tool thật trong sandbox, migration, rollback/lỗi phụ thuộc | Request/result + state trước/sau + correlation ID; mock dependency không chứng minh integration thật |
| API/contract | Thành công, thiếu/sai field, code lỗi, pagination, auth/object scope, idempotency | Kiểm status + response schema + giá trị + state; HTTP 200 đơn lẻ chưa đủ |
| UI/E2E | Luồng chính, validation, loading/error/empty, sửa/hủy, responsive, session | Playwright trace/screenshot, ca theo người dùng; kiểm state backend khi UI báo ghi thành công |
| Regression | Ca lỗi đã sửa và luồng liên quan | Cùng ca và expected, ghi version trước/sau; không sửa snapshot để che regression |
| Accessibility | axe, keyboard, focus, label, contrast và trạng thái động | Violation theo rule/node/severity và scope trang; automated scan sạch không thay kiểm bàn phím/screen reader |
| Build/type/lint | Lệnh repository và CI đã quy định | Exit code/log, version; không gộp lint-pass thành functional-pass |

## JavaScript/TypeScript: Vitest

Khi repo đã có Vitest và test phù hợp:

```sh
mkdir -p artifacts/qa-run-001
npx --no-install vitest run --reporter=default --reporter=json --outputFile=artifacts/qa-run-001/vitest.json
npx --no-install vitest run --coverage --coverage.reporter=text --coverage.reporter=json-summary --coverage.reporter=lcov --coverage.reportsDirectory=artifacts/qa-run-001/coverage
```

Chọn lệnh một lượt nếu cần tiết kiệm thời gian bằng gộp cờ reporter và coverage; đừng chạy hai lượt rồi nhầm là một mẫu lớn gấp đôi. Cấu hình `coverage.include` theo toàn bộ source thuộc phạm vi, không chỉ file được tests import; lưu exclude có lý do. Line/branch/function coverage là số phần tử được chạy/tổng phần tử instrument được trong phạm vi. Không diễn giải coverage=90% là sản phẩm đúng 90%. Ngưỡng phải theo repo hoặc chủ sản phẩm, không tự đặt mặc định 80%.

Nguồn: [Vitest coverage](https://vitest.dev/guide/coverage.html), [reporters](https://vitest.dev/guide/reporters.html).

## Python: pytest/unittest + coverage.py

Thay `src` bằng thư mục/package source đã scout. Đo đúng code sản phẩm, không đưa thư mục tests vào mẫu số.

```sh
mkdir -p artifacts/qa-run-001
.venv-qa/bin/python -m coverage run --branch --source=src -m pytest tests --junitxml=artifacts/qa-run-001/pytest.xml
.venv-qa/bin/python -m coverage json -o artifacts/qa-run-001/coverage.json
.venv-qa/bin/python -m coverage xml -o artifacts/qa-run-001/coverage.xml
.venv-qa/bin/python -m coverage report -m
```

Nếu dự án dùng unittest, thay lệnh chạy bằng:

```sh
.venv-qa/bin/python -m coverage run --branch --source=src -m unittest discover -s tests -v
```

Lưu exit code của lệnh chạy test ngay khi kết thúc; lệnh xuất coverage thành công sau đó không được làm mất fail của test. Pytest skip/xfail/xpass và lỗi collection báo riêng; unittest không có JUnit mặc định. Coverage parallel cần combine theo quy trình repo trước khi báo tổng.

Nguồn: [coverage commands](https://coverage.readthedocs.io/en/latest/commands/), [pytest reports](https://docs.pytest.org/en/stable/how-to/output.html).

## UI: Playwright + axe

Repo đã có `@playwright/test`, app test đang chạy và baseURL/test fixtures cấu hình đúng:

```sh
npx --no-install playwright install chromium
PLAYWRIGHT_HTML_OPEN=never PLAYWRIGHT_HTML_OUTPUT_DIR=artifacts/qa-run-001/playwright-html \
  npx --no-install playwright test --reporter=line,html --trace=retain-on-failure \
  --output=artifacts/qa-run-001/playwright-results
```

Biến môi trường trong ví dụ dùng cú pháp POSIX; Windows đặt biến tương đương trước lệnh. Lượt sau đổi run ID và giữ report/trace cũ. Nếu thiếu, thêm `@playwright/test` và `@axe-core/playwright` vào dev dependencies, pin lock; không nhầm package `playwright` dùng xuất PDF với một bộ E2E đã có tests. Ví dụ axe đặt trong test file của sản phẩm:

```ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('Trang chính có cấu trúc truy cập được', async ({ page }) => {
  await page.goto('/'); // baseURL trong config phải là app test thật
  const result = await new AxeBuilder({ page }).analyze();
  expect(result.violations).toEqual([]);
});
```

Đây chỉ là một kiểm tra accessibility, chưa chứng minh chatbot trả đúng hoặc toàn bộ app truy cập được. Thêm state sau mở dialog, sau báo lỗi, sau streaming; dùng keyboard kiểm focus và có thể dừng/hủy. Lưu trace có kiểm soát vì có thể chứa nội dung riêng, cookie hoặc thông tin tài khoản.

Nếu môi trường agent yêu cầu browser UI qua công cụ chuyên dụng, tuân thủ công cụ đó cho thao tác UI; lệnh trên là entrypoint test của repo, không là quyền bỏ qua quy tắc môi trường.

Nguồn: [Playwright CLI](https://playwright.dev/docs/test-cli), [axe integration](https://playwright.dev/docs/accessibility-testing).

## Tĩnh và build

Dùng script lint/typecheck/build có sẵn trong package.json; Python dùng Ruff/type checker nếu đã cấu hình. Với Ruff: `.venv-qa/bin/python -m ruff check . --output-format json > artifacts/qa-run-001/ruff.json`. Nguồn: [Ruff configuration và CLI](https://docs.astral.sh/ruff/configuration/). Không bật autofix trong bước chỉ đo. Không dùng `|| true` để biến lỗi thành thành công; orchestration phải ghi exit riêng rồi vẫn thu artifact.

## Nếu sản phẩm có voice/media

- STT: transcript chuẩn có người xác nhận; WER=(substitution+deletion+insertion)/số từ reference. Với tiếng Việt, chốt tách từ/chuẩn hóa và báo thêm độ đúng các slot quyết định (tên/số/ngày). Không có reference thì chưa có WER.
- OCR: độ đúng từng field quan trọng và phép tính; so tiền/ngày theo chuẩn độc lập. Exact match toàn đoạn không thay độ đúng trường nghiệp vụ.
- Audio/video: metadata bằng ffprobe; decode, silence, duration, codec, resolution; kiểm nội dung và đồng bộ bằng xem/nghe. File mở được chưa chứng minh nội dung đúng.
- TTS: người nghe chấm rõ nghĩa/phát âm từ chuyên môn; tách thời gian tạo audio với thời gian người dùng nghe tiếng đầu. Voice có kiểm barge-in/hủy và sửa transcript.

Các nhóm này chỉ áp dụng khi có tính năng; ghi N/A có lý do nếu không có. Không cài FFmpeg/OCR/STT chỉ để điền tên công cụ.
