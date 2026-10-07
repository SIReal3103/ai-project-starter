# Bộ công cụ QA trên ổ ngoài

Gói này dành cho macOS: tạo volume APFS trong một file sparsebundle trên SSD, cài hoặc chuyển công cụ vào volume đó, kiểm khả năng chạy và mở lại sau khi cắm SSD. Dùng được với ổ ngoài ExFAT. Toàn bộ lệnh chạy tại root repo sau khi clone; không cần file trên máy tác giả.

## 1. Clone và chuẩn bị

```sh
git clone https://github.com/SIReal3103/ai-project-starter.git
cd ai-project-starter
```

Cần Git và Python 3.12+. Nếu cài mới cả bộ, cần Node 24+, npm, uv, Homebrew và Java 17. `hdiutil`, `ditto`, `rsync` và `unzip` có sẵn trên macOS. Script không cài Homebrew hoặc sửa cấu hình shell. Chuẩn bị công cụ nền bằng Homebrew đã cài:

```sh
brew install python@3.12 node uv k6 trivy gitleaks ffmpeg openjdk@17
export QA_SETUP_PYTHON="$(brew --prefix python@3.12)/bin/python3.12"
```

Chọn thư mục trên SSD của bạn. Ví dụ dưới dùng ổ tên Hiep SDD; thay tên nếu máy có ổ khác. Các biến có khoảng trắng luôn phải nằm trong dấu ngoặc kép:

```sh
export QA_STORAGE='/Volumes/Hiep SDD/AI-QA-Tools'
export QA_RUNTIME_VOLUME='/Volumes/AI-QA-Tools'
python3 qa-tools-storage/qa-storage.py init --storage-dir "$QA_STORAGE" --mount "$QA_RUNTIME_VOLUME"
```

`init` chỉ dành cho thư mục mới. Image có trần logic 64 GiB, dung lượng thật tăng theo dữ liệu. Có thể đặt `--size 128g` khi tạo. Không chạy init vào một bộ đã có image. Volume giữ symlink, executable và SQLite của venv/Node/browser; không đặt các runtime này trực tiếp trên ExFAT. Bộ runtime vẫn phụ thuộc kiến trúc và Python/Node/Java của máy đã cài; khi đổi máy nên cài lại.

## 2A. Máy đã cài bộ QA: chuyển bản đang có

Dừng các test, browser và scanner đang sử dụng các thư mục này. Chạy:

```sh
python3 qa-tools-storage/qa-storage.py migrate --storage-dir "$QA_STORAGE" --mount "$QA_RUNTIME_VOLUME"
source qa-tools-storage/activate.sh
python3 qa-tools-storage/doctor.py
```

Script tìm các thư mục dưới home của người chạy: `ai-qa-tools`, `scope-data-bot-eval`, ba uv tool Semgrep/Bandit/pip-audit, browser Playwright và cache Trivy. Thư mục chưa có được bỏ qua. Các uv tool khác và cache npm chung không được di chuyển. Thư mục đã là symlink hoặc destination đã có dữ liệu làm lệnh dừng để kiểm hiện trạng.

Script copy bằng `ditto`, đối chiếu checksum bằng **rsync dry-run** trước khi đổi đường dẫn, rồi giữ bản gốc tên `.qa-move-backup-<mã>` và tạo symlink tại đường dẫn cũ. Manifest nằm trong `$QA_STORAGE/migration.json`. Không tự xóa bản gốc. Nếu copy lỗi, giữ nguyên nguồn; nếu chuyển đường dẫn lỗi, khôi phục nguồn của nhóm vừa lỗi. Khi thao tác bị ngắt, đọc manifest và các đường dẫn thực trước khi xử lý; không chạy lại hoặc xóa hàng loạt.

Kiểm thêm test của sản phẩm, mở Chromium, chạy một eval offline có đối chứng đúng/sai, và kiểm scanner trên fixture. `doctor.py` chỉ đo launcher/version, không nghiệm thu sản phẩm. Sau khi tất cả chạy được, mới xóa **đúng từng thư mục backup ghi trong manifest** để giải phóng ổ trong. Không xóa source symlink hoặc destination. Nếu muốn khôi phục trước khi xóa backup: dừng công cụ, kiểm source là symlink trỏ đúng destination, bỏ symlink đó rồi đổi tên backup về source. Khi backup đã xóa, muốn chuyển về ổ trong phải copy lại, kiểm checksum và có đủ dung lượng.

## 2B. Máy mới: cài trực tiếp vào volume

```sh
sh qa-tools-storage/setup-libraries.sh all
source qa-tools-storage/activate.sh
python3 qa-tools-storage/doctor.py
```

Có thể cài từng nhóm `core`, `evals`, `security`, `zap` thay cho `all`. Script tải dependency từ registry và ZAP từ GitHub; không gọi model. Core có pytest, coverage.py, Ruff, jiwer, psutil, Vitest/V8, Playwright/Chromium, axe và Promptfoo. Ragas/DeepEval có hai venv riêng và dùng lock trong kit. Semgrep/Bandit/pip-audit dùng uv; ZAP dùng Java và checksum SHA-256 cố định của bản 2.17.0. k6, Trivy, Gitleaks, FFmpeg/ffprobe và các runtime nền dùng Homebrew ở bước 1.

Các bản package là snapshot đã kiểm ngày 07/10/2026; không có nghĩa mọi bản vẫn phù hợp hoặc không có advisory. Promptfoo được tách riêng do advisory dependency của snapshot. Kiểm lại `npm audit`, `pip-audit` và lock khi cập nhật. Node test import `vitest`/Playwright vẫn cần dependency resolve đúng trong project test. Không dùng bộ cài chung để che thiếu dependency của sản phẩm.

Thư mục sau khi cài/chuyển:

```text
AI-QA-Tools/                     Trên SSD
  qa-runtime.sparsebundle       Dữ liệu APFS; không chỉnh file bands
  storage.json                  ID và mount path
  migration.json                Chỉ có khi chuyển runtime cũ
/Volumes/AI-QA-Tools/            Volume được mount
  runtime/ai-qa-tools/           Python, Node, Promptfoo, ZAP
  runtime/scope-data-bot-eval/   Ragas và DeepEval
  uv-tools/                     Semgrep, Bandit, pip-audit
  caches/                       Browser, Trivy, uv, npm, pip
```

Sau kích hoạt, `uv tool list` quản lý các tool trên volume. Cache mới trong shell QA đặt trên volume; các ứng dụng khác giữ cấu hình cũ. Các biến `EVAL_RAGAS_PYTHON` và `EVAL_DEEPEVAL_PYTHON` giúp kit chọn đúng interpreter.

## 3. Dùng lại, tháo ổ và kiểm sản phẩm

Mỗi lần cắm SSD hoặc khởi động lại, mở terminal tại repo đã clone và khai báo lại hai biến đường dẫn ở bước 1, rồi chạy:

```sh
python3 qa-tools-storage/qa-storage.py mount --storage-dir "$QA_STORAGE" --mount "$QA_RUNTIME_VOLUME"
source qa-tools-storage/activate.sh
python3 qa-tools-storage/doctor.py
```

Lệnh mount kiểm ID để tránh dùng nhầm volume. Khi đã mount đúng, gọi lại vẫn thành công. Trước khi eject SSD, dừng công cụ rồi chạy:

```sh
python3 qa-tools-storage/qa-storage.py unmount --storage-dir "$QA_STORAGE" --mount "$QA_RUNTIME_VOLUME"
```

Không force-eject; nếu còn bận thì macOS từ chối tháo. Công cụ đã chuyển cần SSD được mount để chạy.

Để đánh giá sản phẩm, dùng [skill ai-qa-evals](../skills/ai-qa-evals/SKILL.md), [cách chọn chỉ số](../skills/ai-qa-metrics/SKILL.md) và [kit eval](../chatbot-eval-kit/README.md). Ca QA cần input/expected/actual, Pass/Fail và bằng chứng. Eval ngữ nghĩa cần model judge và ngân sách; Ragas text matching hoặc DeepEval exact match chỉ kiểm phép đo tương ứng.

## 4. Bằng chứng lần chuyển đã thực hiện

[Kết quả kiểm ngày 07/10/2026](migration-verification.md): 7 nhóm đã chuyển và checksum khớp; 17/17 công cụ nhận diện được sau khi tháo/mount lại; Python 3/3, Vitest 4/4, browser/axe 2/2; Ragas/DeepEval offline và Semgrep có đối chứng. Khoảng 6,33 GB được giải phóng trên ổ trong. Đây là hậu kiểm di chuyển, không phải điểm chất lượng sản phẩm. Lần clone mới cần tự kiểm lại môi trường thực tế.

Gói GitHub chứa script, manifest package và hướng dẫn. Runtime, venv, node_modules, browser, sparsebundle, cache, keys và evidence chứa dữ liệu sản phẩm được lưu trên máy/SSD của người dùng.
