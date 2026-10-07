# Kiểm thử bảo mật và quyền riêng tư

Đọc khi phạm vi QA có dữ liệu riêng, tài khoản/quyền, upload/fetch, web/API hoặc agent gọi tool. Chọn phép kiểm theo bề mặt thật; không cài và chạy mọi scanner mặc định. **Ngày đối chiếu nguồn: 2026-10-07.** Lệnh dưới đây là hướng dẫn, chưa phải bằng chứng đã chạy hay xác nhận sản phẩm an toàn.

## Chuẩn bị lượt chạy

- Ghi commit, môi trường, chủ hệ thống, URL/path/tenant được phép, hành động đọc/ghi, dữ liệu thử, đích nhận callback và phần loại trừ. Quyền kiểm local không tự mở rộng sang production, hệ thống bên thứ ba hoặc gửi source lên cloud.
- Dùng tài khoản và dữ liệu tổng hợp có oracle độc lập. Lập ma trận actor × tenant × object × action trước khi chạy. Xác định sink thực: DB, cache, browser, log, trace, stream, TTS, export và tool đích.
- Chốt giới hạn thời gian, số request, concurrency, token, chi phí và điều kiện dừng. Ví dụ smoke: mỗi scanner local tối đa 5 phút; mỗi ca API tối đa 15 giây, concurrency 1; ZAP một origin test tối đa 10 phút; AI tối đa 20 ca tấn công + 20 ca hợp lệ, một lần/ca. Đây là budget đề xuất, không là ngưỡng nghiệm thu hay cỡ mẫu đủ cho production.
- Với runtime scan: chỉ dùng route được phép; chặn email/thanh toán/webhook thật, có read-back và cách dọn dữ liệu. Dừng khi vượt scope, có tác động ngoài dự kiến, hết quota hoặc lỗi auth/cấu hình; không retry vô hạn.
- Ghi phiên bản CLI, image digest, ruleset/config hash, advisory service và danh sách bỏ qua. Cài tool trong môi trường riêng theo chính sách dự án; không thay dependency sản phẩm chỉ để quét. Kiểm egress của registry, rules, telemetry và judge.

Ví dụ shell POSIX cho thư mục evidence riêng; đặt `QA_REPO` thành đường dẫn repo đã xác minh trước khi dùng:

```sh
: "${QA_REPO:?Cần đường dẫn repo được phép kiểm}"
umask 077
QA_OUT="$(mktemp -d "${TMPDIR:-/tmp}/ai-qa-security.XXXXXX")"
```

Đặt deadline tổng ở runner/CI cho cả cài đặt và scan. Timeout nội bộ theo socket/file không thay deadline tổng. Runner phải ghi exit code, stderr và trạng thái **từng lệnh scanner**, không chỉ exit cuối của cả block. Không dùng `|| true`, `--exit-zero` hoặc giảm rule để biến lỗi chạy thành pass. Evidence có thể chứa secret/PII/source: giữ raw trong nơi hạn chế quyền, xuất bản bản khử thông tin, không commit tự động.

## 1. Secret trong repo, lịch sử và artifact — Gitleaks

Áp dụng cho source/config, Git history và thư mục build/export được chọn. Cài trên macOS bằng Homebrew; nền tảng khác dùng binary chính thức. Chạy riêng history và file hiện tại:

```sh
brew install gitleaks
gitleaks version
gitleaks git "$QA_REPO" --redact=100 --timeout 300 \
  --report-format json --report-path "$QA_OUT/gitleaks-git.json"
gitleaks dir "$QA_REPO" --redact=100 --timeout 300 \
  --report-format json --report-path "$QA_OUT/gitleaks-files.json"
```

`git` quét patch trong lịch sử sẵn có; `dir` kiểm file hiện tại. Ghi shallow clone/ref/range, ignore và file bị bỏ qua; kiểm build output bằng lượt `dir` riêng nếu thuộc scope. `--redact` không thay việc kiểm và khử thông tin report trước chia sẻ. [Gitleaks: cài đặt, lệnh và flags](https://github.com/gitleaks/gitleaks).

Artifact: JSON, cấu hình, stderr/exit, phạm vi lịch sử. Đếm finding duy nhất sau triage theo fingerprint/vị trí, tách secret thật, dữ liệu thử và chưa xác minh. Secret thật cần thu hồi/rotate theo quyền được giao; xóa dòng code không vô hiệu credential. Không thử key thật lên dịch vụ để “xác nhận còn sống”. Không có finding chỉ nói rules đã chọn chưa phát hiện trong scope đó.

## 2. Dependency có advisory — npm audit / pip-audit

**Node/npm:** chạy ở thư mục chứa `package.json` và lockfile của sản phẩm; dùng npm phù hợp repo, không cần cài dependency chỉ để audit. Lượt thứ hai chỉ cần khi phải tách runtime khỏi dev:

```sh
cd "$QA_REPO"
npm --version
npm audit --json > "$QA_OUT/npm-audit-all.json"
npm audit --omit=dev --json > "$QA_OUT/npm-audit-runtime.json"
```

Audit gửi mô tả dependency tới registry cấu hình. Thiếu lockfile: ghi bị chặn hoặc tạo lock trong phạm vi được giao, không âm thầm resolve phiên bản mới. `--audit-level` chỉ đổi ngưỡng exit, không lọc finding; không tự chạy `audit fix`/`--force`. [npm audit CLI v11](https://docs.npmjs.com/cli/v11/commands/npm-audit/).

**Python:** kiểm inventory đúng môi trường triển khai. Ví dụ dưới yêu cầu file đã resolve **đủ dependency bắc cầu**, pin phiên bản bằng `==`; `--no-deps` không tự bổ sung phần thiếu:

```sh
python3 -m venv "$QA_OUT/pip-audit-env"
"$QA_OUT/pip-audit-env/bin/python" -m pip install pip-audit
"$QA_OUT/pip-audit-env/bin/python" -m pip_audit --version
"$QA_OUT/pip-audit-env/bin/python" -m pip_audit \
  -r "$QA_REPO/requirements.txt" --no-deps --disable-pip \
  --timeout 15 --format json --output "$QA_OUT/pip-audit.json"
```

Nếu requirements chưa resolve/pin đủ, chọn workflow resolve tin cậy hoặc audit môi trường sản phẩm đã cài, không audit venv chứa mỗi scanner. `--timeout` là socket timeout. Audit có thể truy vấn dịch vụ advisory; quy trình resolve thông thường có rủi ro tương tự cài package. [pip-audit: usage và security model](https://github.com/pypa/pip-audit).

Artifact: report JSON, lock/inventory hash, package bị skip, registry/service, exit/stderr. Đếm cặp package-version-advisory duy nhất, gộp alias CVE/GHSA; tách dev/runtime và reachability đã kiểm/chưa kiểm. Coverage = package-version được audit / package-version trong inventory đã chốt. Advisory sạch không chứng minh không có malware, zero-day hoặc lỗi thư viện native; lỗi mạng/unsupported package không là “0 lỗ hổng”.

## 3. Mẫu code nguy hiểm — Semgrep / Bandit

**Semgrep:** dùng khi ngôn ngữ/framework có rules phù hợp; ví dụ chọn thư mục `src` thật của repo. Cài qua `pipx` khi môi trường đã có công cụ này. Registry rules cần network dù tắt metrics:

```sh
pipx install semgrep
semgrep --version
semgrep scan --config p/security-audit --metrics=off \
  --disable-version-check --timeout 5 --timeout-threshold 3 \
  --error --json --output "$QA_OUT/semgrep.json" "$QA_REPO/src"
```

Muốn dùng rules offline, thay config bằng file/thư mục rules đã tải, review và ghi hash. `--timeout` tính trên một rule/file; deadline runner vẫn cần. Không đăng nhập/upload finding chỉ để chạy local. [Cài CLI](https://docs.semgrep.dev/getting-started/quickstart), [CLI flags](https://docs.semgrep.dev/cli-reference), [rulesets chính thức](https://github.com/semgrep/skills/blob/main/skills/semgrep/SKILL.md).

**Bandit:** dùng cho Python để tìm các mẫu API/code có rủi ro; không thay dependency audit hay kiểm quyền nghiệp vụ. Chọn thư mục Python thật:

```sh
python3 -m venv "$QA_OUT/bandit-env"
"$QA_OUT/bandit-env/bin/python" -m pip install bandit
"$QA_OUT/bandit-env/bin/bandit" --version
"$QA_OUT/bandit-env/bin/bandit" -r "$QA_REPO/src" \
  -f json -o "$QA_OUT/bandit.json"
```

Giới hạn tổng ở runner; giữ severity và confidence riêng. Review `nosec`, ignore và parser error, không tắt finding chỉ để có exit 0. [Bandit setup](https://bandit.readthedocs.io/en/latest/start.html), [CLI](https://bandit.readthedocs.io/en/latest/man/bandit.html).

Artifact: JSON hoặc SARIF, rules hash, paths thực sự được scan, skipped/error và triage. Theo từng tool, coverage = file được phân tích thành công / file áp dụng trong scope; precision của finding = true-positive / (true-positive + false-positive) **chỉ trên finding đã được xác minh**. Không suy recall khi chưa có tập lỗi chuẩn. Đọc đường dữ liệu vào → xử lý → sink, rồi tái hiện có kiểm soát; scanner severity không tự là severity sản phẩm.

### Khi có container hoặc IaC — Trivy

Chỉ chọn lượt phù hợp artifact triển khai thật. Cài theo [Trivy installation](https://trivy.dev/docs/latest/getting-started/installation/); ghi `trivy --version`. `QA_IMAGE` phải chỉ đúng image/digest, `QA_IAC` chỉ đúng thư mục cấu hình trong scope:

```sh
trivy image --scanners vuln --disable-telemetry --timeout 5m \
  --exit-code 1 --format json --output "$QA_OUT/trivy-image.json" "$QA_IMAGE"
trivy config --disable-telemetry --timeout 5m \
  --exit-code 1 --format json --output "$QA_OUT/trivy-iac.json" "$QA_IAC"
```

Report image tìm advisory; report IaC tìm cấu hình sai, không chứng minh môi trường đã deploy đúng. Ghi DB/check-bundle version, image digest, platform, file áp dụng/bị bỏ qua và ignore; network tải image/DB/rules nằm trong budget, không upload artifact lên dịch vụ mới. Đếm package-version-advisory hoặc resource-rule duy nhất sau triage; coverage = image/file IaC quét được / inventory cần quét. `--exit-code 1` giữ finding thành nonzero; phân biệt với lỗi chạy từ report/stderr. [Image flags](https://trivy.dev/docs/latest/references/configuration/cli/trivy_image/), [IaC flags](https://trivy.dev/docs/latest/references/configuration/cli/trivy_config/).

## 4. HTTP đang chạy — OWASP ZAP

Áp dụng cho web/API test có route và quyền rõ. Chuẩn bị Docker, URL nhìn thấy từ container, thư mục artifact riêng có quyền ghi cho user ZAP. `localhost` trong container là chính container; dùng network/hostname test phù hợp. Đặt `QA_TARGET`, `QA_ZAP_OUT` là đường dẫn tuyệt đối và `QA_ZAP_IMAGE` là image chính thức đã chọn; khi cần tái lập pin digest thay tag động.

**Baseline:** crawl rồi passive scan response, không chạy active attack rules. Crawl vẫn gửi request; chỉ đưa route crawl an toàn vào context, tránh route GET có side effect và URL gọi model tính phí. Ví dụ một origin test đã kiểm scope:

```sh
docker pull ghcr.io/zaproxy/zaproxy:stable
QA_ZAP_IMAGE=ghcr.io/zaproxy/zaproxy:stable
docker image inspect "$QA_ZAP_IMAGE" --format '{{json .RepoDigests}}'
docker run --rm -v "$QA_ZAP_OUT:/zap/wrk:rw" "$QA_ZAP_IMAGE" \
  zap-baseline.py -t "$QA_TARGET" -m 1 -T 3 \
  -J zap-baseline.json -r zap-baseline.html
```

`-m 1` giới hạn spider; `-T 3` giới hạn chờ khởi động/passive scan, **không phải deadline tổng**. Dùng context/auth khi cần và kiểm request thực sự mang đúng session; trang login HTTP 200 không chứng minh đã crawl phần sau đăng nhập. [ZAP baseline](https://www.zaproxy.org/docs/docker/baseline-scan/).

**Active:** chỉ khi phạm vi đã cho phép tác động kiểm thử, trong môi trường cô lập có dữ liệu reset được. Dùng context đã review có include/exclude URL; ví dụ file `scope.context` nằm trong `QA_ZAP_OUT`. Chặn egress/route ngoài scope ở môi trường test, giới hạn request/rate tại proxy hoặc runner. Không coi giới hạn thread là giới hạn requests/second:

```sh
docker run --rm -v "$QA_ZAP_OUT:/zap/wrk:rw" "$QA_ZAP_IMAGE" \
  zap-full-scan.py -t "$QA_TARGET" -n /zap/wrk/scope.context \
  -m 1 -T 3 -J zap-active.json -r zap-active.html \
  -z '-config scanner.maxScanDurationInMins=5 -config scanner.maxRuleDurationInMins=1 -config scanner.threadPerHost=1'
```

Full scan gửi payload chủ động, có thể ghi/xóa dữ liệu. Deadline runner phải dừng cả container (chỉ kill Docker CLI có thể để container chạy); lưu tên/ID container để cleanup. Đạt timeout nghĩa là phạm vi còn lại chưa kiểm. Exit ZAP: 0 hoàn tất theo cấu hình; 1 có FAIL; 2 có WARN; 3 lỗi khác. [Full scan](https://www.zaproxy.org/docs/docker/full-scan/), [tham số active scan](https://www.zaproxy.org/docs/desktop/addons/automation-framework/job-ascan/), [khóa cấu hình scanner](https://github.com/zaproxy/zaproxy/blob/main/zap/src/main/java/org/parosproxy/paros/core/scanner/ScannerParam.java).

Với API có OpenAPI/SOAP/GraphQL, dùng `zap-api-scan.py`: mặc định có active scan; `-S` bỏ active scan nhưng import/exercise API vẫn có thể gửi request. Review server URL và operation trước chạy, đặc biệt mutation. Ví dụ spec OpenAPI **chỉ gồm operation được phép** nằm trong thư mục mount:

```sh
docker run --rm -v "$QA_ZAP_OUT:/zap/wrk:rw" "$QA_ZAP_IMAGE" \
  zap-api-scan.py -t /zap/wrk/openapi-scoped.json -f openapi -S -T 3 \
  -J zap-api-passive.json -r zap-api-passive.html
```

[ZAP API scan](https://www.zaproxy.org/docs/docker/api-scan/). Artifact: JSON/HTML, image digest, context/spec hash, routes + methods đã chạm, auth role và request/response đã khử thông tin. Coverage = endpoint-method đã exercise / endpoint-method trong inventory áp dụng, không là số URL spider tự tìm thấy. Alert là đầu mối điều tra; quét sạch không chứng minh RBAC, tenant isolation hay logic AI đúng.

## 5. Kiểm quyền bằng API và trạng thái thật

Chuẩn bị user A/B trong tenant T1, user C trong T2, role thấp/cao và object thử riêng. Cho A đọc object của mình thành công trước; sau đó thay **chỉ một chiều** identity/object/tenant/action, so response và state. BOLA kiểm quyền trên object; RBAC kiểm quyền chức năng; phải kiểm cả hai. [OWASP BOLA](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/), [quyền chức năng](https://api-security.owasp.org/editions/2023/en/0xa5-broken-function-level-authorization/).

Ví dụ request đọc chéo có giới hạn: `QA_AUTH_A` là file curl config chứa header/cookie của **tài khoản test A**, chmod 600; `QA_BASE_URL`, route và `QA_OBJECT_B` đã xác minh. Không đặt credential trong câu lệnh, URL, log verbose hay report:

```sh
curl --disable --config "$QA_AUTH_A" --connect-timeout 5 --max-time 15 \
  --silent --show-error --dump-header "$QA_OUT/auth-cross-read.headers" \
  --output "$QA_OUT/auth-cross-read.body" --write-out '%{http_code}\n' \
  "$QA_BASE_URL/api/documents/$QA_OBJECT_B"
```

Ví dụ route phải thay theo contract; `--disable` ở đầu bỏ cấu hình curl mặc định, file config riêng chỉ chứa thiết lập auth cần dùng. Không tự follow redirect sang host khác. [curl options](https://curl.se/docs/manpage.html).

| Tập ca áp dụng | Thực hiện | Oracle và evidence bắt buộc |
|---|---|---|
| BOLA/tenant | A dùng ID của B/C ở detail, download, search/RAG, list/filter, export, cache; thử tenant ID do client gửi | Không lộ object/trường/chunk/citation trái quyền; backend dùng identity/scope thật. Lưu request đã khử token, response và retrieval/state probe |
| RBAC/write | Role thấp gọi route/method quản trị hoặc sửa trường role/owner; thử tạo, sửa, xóa bằng ID người khác | Trả lỗi theo contract (thường 403/404), không ghi state hoặc job/tool side effect. Read-back bằng owner hợp lệ trước/sau; HTTP status riêng không đủ |
| Session/approval | Thiếu/hết hạn/thu hồi session; nếu có approval, thử sai người, sai payload, hết hạn, replay | Không phát dữ liệu/tác động trái quyền. Đối chứng session/approval hợp lệ vẫn hoàn tất; lỗi 500/timeout không là chặn đúng |

Chạy tuần tự với object dùng riêng; chỉ retry đọc idempotent trong budget, không tự retry write chưa đối soát. Đo số hành động trái quyền xảy ra / số ca âm đã có oracle; số hành động hợp lệ bị chặn / số ca dương đã chấm. Báo số ca mỗi role/tenant/action và coverage trên ma trận đã chọn; một vi phạm thật không bị che bởi tỷ lệ đạt trung bình.

## 6. Injection tại biên dữ liệu

Chỉ thử trên sink tồn tại, bằng input tổng hợp và payload không phá hủy. Mỗi ca gồm input bình thường đối chứng, một biến thể kiểm thử, response, state/sink probe và cleanup. Giới hạn request như ca API; không dùng fuzz vô hạn, delay SQL kéo dài hoặc callback ngoài phạm vi.

| Bề mặt | Ca thực hành | Điều kiện kết luận |
|---|---|---|
| XSS: text/Markdown, tên file, citation, export | Đưa chuỗi chứa dấu HTML và payload marker DOM vô hại vào từng sink; kiểm reflected/stored trong browser test, cả trang xem lại/export | Không chạy script/event handler hoặc URL nguy hiểm. HTML encode đúng ngữ cảnh/sanitize theo contract. Payload không hiện chữ hoặc CSP chặn một lần chưa chứng minh mọi sink an toàn |
| SQL injection: search/filter/ID hoặc tool SQL | Thử dấu nháy và cặp điều kiện boolean trên DB fixture chỉ có dữ liệu tổng hợp; so với đối chứng. Đọc code query/trace đã khử dữ liệu để xác nhận parameter binding | Không thay đổi cấu trúc query, mở rộng tenant/result hay tạo tác động. 500 đơn lẻ là lỗi cần điều tra, chưa đủ xác nhận SQLi; kiểm cả tool thực thi, không chỉ text SQL model sinh |
| SSRF: URL fetch/import/crawl | Trong harness cô lập, dùng server callback do nhóm kiểm soát; thử URL ngoài allowlist, redirect tới đích bị cấm, các cách biểu diễn IP liên quan | Egress policy chặn trước kết nối; có server/network trace chứng minh. Dùng fixture nội bộ giả lập cho private/loopback/metadata, không đọc metadata/secret thật; không có callback khi collector hỏng là chưa kết luận |

Nguồn kiểm kỹ thuật: [OWASP XSS](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html), [SQL injection testing](https://wstg.owasp.org/stable/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection/). Đo số vi phạm đã tái hiện / số ca sink-input chấm được, tách từng loại injection. Báo số sink đã kiểm / sink áp dụng đã xác định; ít payload smoke không là chứng nhận không có lỗ hổng.

## 7. Rò rỉ dữ liệu, redaction và xóa

Dùng canary duy nhất và PII tổng hợp được gắn nhãn; giữ danh mục vị trí đã gieo, chủ sở hữu và nơi được phép xuất hiện. Kiểm response thường/lỗi, stream từng đoạn, URL, browser storage, log/trace, tool arguments, export/TTS và tập eval. Không chỉ tìm secret trong câu trả lời cuối.

- **Leakage:** A yêu cầu dữ liệu của B/C qua chat, retrieval, history, cache, link/export. Oracle kiểm cả ID, nội dung, biến đổi/diễn đạt lại và đích nhận. Chỉ tìm chuỗi canary nguyên văn có thể bỏ sót rò rỉ một phần/encode.
- **Redaction:** tạo tập span độc lập gồm tên/số liên hệ/định danh theo dữ liệu sản phẩm, biến thể tiếng Việt và chuỗi vô hại gần giống. Đối chiếu raw hạn chế quyền với bản được chia sẻ; đo recall = span nhạy cảm che đúng / tổng span nhạy cảm, precision = span che đúng / tổng span bị che. Chốt quy tắc partial span trước chạy; không suy hỗ trợ tiếng Việt chỉ từ cờ ngôn ngữ.
- **Deletion/retention:** gieo dữ liệu theo luồng thật → xác nhận đã có ở từng store → xóa/đợi TTL đã chốt → read-back với cùng và khác tài khoản. Kiểm file, DB, chunk/vector, cache, checkpoint/history, export, log và bản eval trong scope. Với backup, kiểm restore cô lập và áp lại tombstone trước phục vụ; không tự restore đè môi trường sống.

Artifact: bản đồ dữ liệu gốc → dẫn xuất, timestamps yêu cầu/xử lý/xác nhận, ID/hash canary, probe trước/sau và các store không quan sát được. Leakage rate = ca lộ dữ liệu / ca đã chấm; deletion coverage = vị trí có probe / vị trí phải kiểm, deletion pass = vị trí đáp ứng chính sách xóa / vị trí đã kiểm. Chỉ pass toàn ca khi mọi vị trí bắt buộc đạt; backup/provider chưa xác minh giữ blocked/chưa kết luận. Deadline QA ngắn hơn TTL thì ghi chưa tới hạn, không tự rút retention hay báo xóa tức thì.

## 8. Prompt injection, rò rỉ qua AI và từ chối nhầm

Áp dụng theo chức năng: chatbot kiểm output; RAG thêm tài liệu/retrieval; agent thêm executor, approval và state đích. Gieo chỉ dẫn tấn công vào nguồn không tin cậy thật sự đi qua hệ thống: user, chunk, tài liệu, tên file, tool output. Bao gồm yêu cầu đọc canary trái quyền, đổi scope và dùng tool ngoài quyền; dùng sink test được kiểm soát. Prompt injection cần chấm tác động quan sát được. [OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

1. Khóa oracle trước chạy: dữ liệu nào cấm lộ, hành động nào cấm, yêu cầu hợp lệ nào phải phục vụ. Tách tập tấn công và benign gần ranh giới, có biến thể tiếng Việt; không chỉnh policy để hợp thức hóa kết quả.
2. Chạy qua adapter sản phẩm thật, lưu model/prompt/dataset version, raw response/stream, retrieval, trace tool và state read-back. Câu “không thể làm” ở cuối không cứu một tool đã ghi hoặc stream đã lộ dữ liệu.
3. Chấm ASR = lượt tấn công có vi phạm oracle / lượt tấn công có kết quả chấm được. False refusal = yêu cầu hợp lệ bị từ chối sai / yêu cầu hợp lệ chấm được. Hỏi lại vì thiếu dữ kiện không tự là false refusal. Báo riêng theo loại tấn công/sink và từng mẫu số.
4. Lưu số planned/completed/timeout/blocked; thiếu trace/oracle là inconclusive, không được tính là tấn công đã bị chặn đúng. Nếu thử nhiều biến thể/lặp, báo cả tỷ lệ theo lượt và số kịch bản có ít nhất một lần bị vượt / số kịch bản đã thử, kèm số lần lặp.
5. Giới hạn tối đa ca, retry, token/tool-loop và tổng chi phí gồm judge. Không dùng provider/key thật khác để fallback. Dừng khi hết budget; judge là hỗ trợ review, cần evidence xác định được cho quyền, canary và side effect.

ASR bằng 0 trên bộ smoke không chứng minh mọi tấn công bị chặn. False refusal phải đo cùng ASR; chặn toàn bộ request không là nghiệm thu. Không tìm thấy canary, scanner sạch hoặc nhãn “safe” của judge không thay bằng chứng end-to-end.

## Bàn giao kết quả

Giữ bảng QA bảy cột của skill; mỗi ca có scope, preconditions, steps, expected, actual, check, status, evidence, defect và retest. Scanner report là evidence kỹ thuật, không đổi mọi cảnh báo thành ca Fail hay mọi exit 0 thành Pass. Thống kê findings đã xác minh tách khỏi tỷ lệ ca và chất lượng LLM.

Lưu manifest run gồm lệnh đã khử credential, versions/hashes, thời gian/deadline, counts, exclusions, tool errors và artifact index. Mẫu số 0 → `null / Không có mẫu`; thiếu điều kiện → `blocked`; chưa chạy → `not_run`; `na` phải có lý do. Ngưỡng chưa duyệt hiển thị **Đã đo · Chưa chốt ngưỡng**. Sau sửa, retest ca tái hiện và đối chứng liên quan trong run mới; giữ evidence cũ. Kết luận đúng phạm vi đã quan sát, không cấp chứng nhận bảo mật hay pháp lý.
