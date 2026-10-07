# Đo hiệu năng, thời gian phản hồi và độ tin cậy

Dùng tài liệu này khi phạm vi QA có tốc độ, tải hoặc lỗi vận hành. Kết quả phải đến từ endpoint/adapter thật đã xác nhận. Chạy health check chỉ chứng minh endpoint đó phản hồi; không chứng minh chatbot sinh đáp án nhanh, RAG truy hồi đúng hay agent hoàn thành tác vụ. Replay output và thời gian chấm judge không phải độ trễ inference mới.

## 1. Chốt phép thử trước khi chạy

Ghi vào manifest của run: commit, môi trường/region, cấu hình máy chạy tải, model/revision, tham số sinh, dataset hash, adapter version, endpoint không có secret, thời điểm UTC, deadline, retry, giới hạn request/token/chi phí và điều kiện dừng. Giữ quyền và budget đã có; hướng dẫn này không tự cấp quyền gây tải production hay gọi model trả phí.

Phân nhóm workload theo tính năng và độ dài: input/context ngắn–vừa–dài, giới hạn output và số token output thực, số lượt hội thoại, retrieval, tools, streaming/non-streaming. Dùng phân bố từ sản phẩm khi có; nếu tự chọn thì ghi là profile đề xuất. Giữ dataset, seed/thứ tự và tỷ trọng khi so phiên bản. Không rút ngắn output hoặc thay câu khó bằng câu dễ để làm đẹp latency.

Tách cache hit/miss/unknown; ghi loại cache (HTTP, retrieval, prompt/KV, response). Lần đầu không tự là cache miss. Tách cold start đã quan sát (process/model vừa khởi động) với warm; không restart dịch vụ dùng chung để tạo cold start nếu ngoài phạm vi. Ghi warm-up riêng, không âm thầm bỏ các request đầu hoặc lỗi khỏi tổng run.

## 2. Định nghĩa đồng hồ và mẫu số

Dùng đồng hồ đơn điệu tại client, ví dụ `performance.now()`, cho khoảng thời gian; dùng UTC cho đối chiếu trace. Ghi rõ điểm bắt đầu/kết thúc. Không trừ timestamp từ hai máy chưa đồng bộ hoặc cộng các span chạy song song thành độ trễ tổng.

| Chỉ số | Cách đo và đơn vị | Điều phải báo cùng |
| --- | --- | --- |
| E2E hoàn tất | Từ client gửi tác vụ đến nhận kết quả hoàn chỉnh, hợp contract; bao gồm queue, tools, model và retry trên đường phục vụ. Với UI: đo riêng từ thao tác người dùng đến render hoàn tất. | p50/p95/p99, n, mốc đồng hồ, nhóm workload, số lỗi/timeout. API hoàn tất chưa bao gồm render UI. |
| TTFT / token đầu tiên | Từ gửi request đến delta nội dung đầu tiên thực sự dùng được của câu trả lời. Nếu stream chỉ có chunk text, đặt tên chính xác là thời gian delta nội dung đầu tiên. | Bỏ role-only, metadata, heartbeat, tool arguments và câu đệm đã định nghĩa trước. Không tự chấm TTFT=0 khi không có nội dung. |
| TTFB / byte đầu tiên | Từ điểm bắt đầu của công cụ đến byte response đầu tiên; ghi định nghĩa công cụ. | Header hoặc heartbeat có thể đến sớm hơn nội dung. TTFB không thay TTFT. |
| Khoảng cách token/chunk | Với timestamp token thật: `t[i] - t[i-1]`; báo p50/p95/p99 và khoảng ngừng lớn nhất. Nếu chỉ có SSE chunk, báo inter-chunk gap. | Một chunk có thể chứa nhiều token hoặc một token bị chia nhiều byte. Không gọi chunk là token. |
| Tốc độ sinh và throughput | Decode token/s = `(N_output - 1)/(t_last_token - t_first_token)` khi biết mốc token và `N_output > 1`; cả lượt = `N_output/E2E_seconds`. Tổng hệ thống = token đã sinh trong cửa sổ đo/số giây cửa sổ. | Ghi tokenizer/usage source; không đếm từ thay token. Nếu chỉ có chunk thì ghi ước tính theo chunk và cách tính. Báo request/s, tác vụ thành công/s riêng. |
| Thành phần độ trễ | Server span: queue wait, retrieval, từng tool, model, retry/backoff; client thêm mạng và render. | Liên kết request/trace ID; báo critical path và span thiếu. Judge chạy sau output nằm ngoài E2E sản phẩm; judge là bước runtime thì nằm trong E2E và có span riêng. |
| Lỗi và timeout | Phân loại kết quả cuối mỗi tác vụ: success, HTTP/transport error, timeout, incomplete/invalid, cancelled, unknown. Tỷ lệ từng loại = số tác vụ loại đó/tổng tác vụ đã bắt đầu trong scope. | Báo tử/mẫu; timeout là một nhóm lỗi, tránh cộng trùng. Attempts/retries có mẫu số riêng. Request bị huỷ khi dừng tải không tự là lỗi server. |
| Availability quan sát | Số tác vụ đủ điều kiện hoàn tất hợp contract trong deadline/tổng tác vụ đủ điều kiện đã bắt đầu, trong cửa sổ đo đã chốt. | Nêu eligibility, deadline, exclusions, n và cửa sổ. Không loại 429/5xx vì “server không nhận”; health availability và chất lượng nội dung là chỉ số riêng. |

Với percentile tự tính theo nearest-rank: sắp `x[1..n]`, `p(q)=x[ceil(q*n)]` cho q=0,50/0,95/0,99. Median có thể được thư viện tính khác khi n chẵn; ghi thuật toán và phiên bản, không gắn nhãn nearest-rank cho kết quả k6 nếu chưa đối chiếu. Không lấy trung bình p95 giữa các nhóm/run: gộp raw samples tương thích hoặc báo từng nhóm. Với n nhỏ, p99 thường sát cực đại; 10–20 mẫu chỉ là quan sát smoke.

Báo percentile của các lượt hoàn tất thành công **kèm n**, phân bố thời gian tới lỗi riêng và số timeout/incomplete. Request timeout chỉ biết đã chờ tới deadline, không biết thời gian hoàn tất; không đưa deadline vào nhóm thành công rồi tuyên bố p95 đạt. Nếu cần đánh giá SLO trên tất cả tác vụ, dùng tỷ lệ hoàn tất đúng hạn và báo mẫu chưa quan sát được. Mẫu số 0 → `null / Không có mẫu`, không là 0% hay 100%.

Đối soát `planned → started → terminal outcomes`; giữ `not_started`, `interrupted`, `unknown` và tải bị runner bỏ (`dropped_iterations`, nếu có) riêng. Run có thiếu dữ liệu không được báo đủ số request kế hoạch. Availability trong một phép tải ngắn không là uptime tháng hay SLA production.

## 3. Smoke HTTP bằng curl

Chỉ trỏ tới health endpoint local đã xác nhận là GET đọc, không kích hoạt inference/side effect. Cài curl theo hệ điều hành nếu thiếu; kiểm `curl --version`. Lệnh dưới cần curl 7.75+ cho `%{exitcode}`, không theo redirect, không retry. Tạo thư mục run mới, không ghi đè evidence cũ:

```sh
mkdir -p runs
mkdir runs/perf-smoke-01
curl --version > runs/perf-smoke-01/curl-version.txt
curl --silent --show-error --fail --noproxy '*' \
  --connect-timeout 2 --max-time 5 \
  --output runs/perf-smoke-01/health-body.txt \
  --write-out 'http=%{http_code}\nexit=%{exitcode}\nttfb_s=%{time_starttransfer}\ntotal_s=%{time_total}\n' \
  http://127.0.0.1:3000/health \
  > runs/perf-smoke-01/curl-timing.txt \
  2> runs/perf-smoke-01/curl-stderr.txt
```

Nếu thư mục run đã tồn tại, chọn tên mới trước khi chạy các lệnh ghi file. Kiểm exit, HTTP status và body theo contract health; không chỉ nhìn số giây. `time_total` là thời gian thao tác curl; `time_starttransfer` là byte đầu tiên, **không phải token đầu tiên**. Một lần gọi không đủ tính percentile. Đây là phép smoke endpoint, không đo UI, độ đúng nội dung hoặc công suất chatbot. Tham khảo [curl manual: write-out và timeout](https://curl.se/docs/manpage.html).

## 4. Mẫu k6 nhỏ, giới hạn sẵn

Trên macOS có Homebrew: `brew install k6`. Windows: `winget install k6 --source winget`. Linux và binary theo [hướng dẫn cài k6 chính thức](https://grafana.com/docs/k6/latest/set-up/install-k6/). Ghi `k6 version`; không cần Grafana Cloud hay API key cho phép chạy local này. Không tự cài công cụ nếu task chỉ yêu cầu mẫu tài liệu.

Lưu đoạn sau thành `health-smoke.js` trong thư mục làm việc mới. Mặc định 1 VU, tối đa 10 GET, deadline request 2 giây, toàn scenario tối đa 30 giây. Chỉ cho địa chỉ HTTP loopback, không query/credential và không theo redirect. Health route phải được xác nhận trước; cổng 3000 chỉ là placeholder.

```js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend } from 'k6/metrics';

const target = __ENV.TARGET_URL || 'http://127.0.0.1:3000/health';
if (!/^http:\/\/(localhost|127\.0\.0\.1)(:\d{1,5})?\/[A-Za-z0-9/_-]*$/.test(target)) {
  throw new Error('Chỉ dùng GET health HTTP loopback đã xác nhận.');
}
const started = new Counter('probes_started');
const returned = new Counter('probes_returned');
const elapsed = new Trend('client_http_elapsed_ms', true);
http.setResponseCallback(http.expectedStatuses(200));

export const options = {
  scenarios: {
    health: {
      executor: 'shared-iterations', vus: 1, iterations: 10,
      maxDuration: '30s', gracefulStop: '0s',
    },
  },
  discardResponseBodies: true,
  summaryTrendStats: ['count', 'med', 'p(95)', 'p(99)', 'max'],
};

export default function () {
  started.add(1);
  const t0 = Date.now();
  const response = http.get(target, {
    timeout: '2s', redirects: 0, tags: { name: 'local-health' },
  });
  const elapsedMs = Date.now() - t0;
  returned.add(1);
  elapsed.add(elapsedMs, { status: String(response.status) });
  check(response, { 'health HTTP 200': (r) => r.status === 200 });
  sleep(0.1);
}
```

Sau khi curl smoke xác nhận route, chạy trong thư mục đó; không thêm CLI override tăng VU/duration/iterations. Xóa biến proxy ở invocation để phép loopback không đi qua proxy cấu hình ngoài:

```sh
mkdir evidence
k6 version > evidence/k6-version.txt
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy \
  NO_PROXY=localhost,127.0.0.1 no_proxy=localhost,127.0.0.1 \
  k6 run --out json=evidence/health-metrics.json \
  --summary-trend-stats 'count,med,p(95),p(99),max' \
  health-smoke.js > evidence/health-summary.txt 2> evidence/health-stderr.txt
```

Lệnh shell này dùng POSIX/macOS/Linux; trên Windows chạy trong shell tương thích hoặc cấu hình môi trường tương đương. Muốn đổi cổng/route local, thêm `TARGET_URL=http://127.0.0.1:8080/health` trước `k6 run` trong invocation `env` sau khi đã kiểm route đó. Giới hạn scenario dựa trên [shared iterations](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/shared-iterations/); timeout/redirect dựa trên [HTTP Params](https://grafana.com/docs/k6/latest/javascript-api/k6-http/params/).

Đọc `probes_started`, `probes_returned`, HTTP status/error tags, `http_req_failed`, `checks` và interrupted iterations trước khi đọc percentile. `probes_returned` gồm response lỗi/timeout mà API trả về, không phải số thành công. Có request bắt đầu nhưng không returned thì ghi interrupted/unknown và đối soát; status=0 không tự có nghĩa timeout. Bộ mẫu chỉ kiểm HTTP 200; health contract khác cần sửa check/callback tương ứng, không đổi kỳ vọng để hợp lỗi hiện có. `check()` fail không tự làm k6 thoát khác 0, nên exit 0 chưa là pass; xem [k6 checks](https://grafana.com/docs/k6/latest/using-k6/checks/) và [response callback](https://grafana.com/docs/k6/latest/javascript-api/k6-http/set-response-callback/).

`client_http_elapsed_ms` bao khoảng gọi HTTP tại client bằng `Date.now()`; đây là clock tường độ phân giải millisecond, có thể bị chỉnh giờ, chưa là E2E UI. Trend tổng trong stdout gồm mọi status đã returned; muốn báo percentile success phải lọc raw sample theo status 200 và báo n, giữ phân bố lỗi riêng. `http_req_duration` chỉ gồm sending + waiting + receiving, không gồm DNS/kết nối; `http_req_waiting` là TTFB theo định nghĩa k6. Không dùng chúng làm TTFT. Chi tiết: [built-in metrics](https://grafana.com/docs/k6/latest/using-k6/metrics/reference/). JSON xuất các metric sample, không chứa toàn bộ response/trace; thêm evidence sản phẩm riêng khi cần. Cờ chạy/xuất ở [results output](https://grafana.com/docs/k6/latest/get-started/results-output/).

Không có threshold hiệu năng trong script vì chưa có ngưỡng nghiệm thu được duyệt. Các số 10 request/2 giây/30 giây là giới hạn phép smoke, không là yêu cầu tốc độ của chatbot.

## 5. Chuyển sang chatbot thật và đo streaming

Không chỉ đổi health URL thành API chat. Dùng adapter thật theo contract sản phẩm: phương thức POST, schema/body, session/context, auth từ secret store hoặc môi trường được phép, idempotency khi có tác động, giới hạn output, timeout và cách nhận biết hoàn tất. Giữ nguyên mã hóa/phương thức streaming của client thật. Ước lượng request × token tối đa × attempts cùng chi phí trước run; chỉ chạy trong quyền/budget đã xác nhận. Không in key vào lệnh, log hay evidence và không tự đổi provider.

Với non-streaming, ghi thời gian quanh toàn request, validate status/schema/completion, lưu usage và trace. Với SSE, `http.get/post` trả body hoàn tất trong mẫu trên không cung cấp timestamp nội dung từng chunk. Instrument client/adapter đọc stream thật:

1. Ghi `t_send` bằng clock đơn điệu ngay trước gửi; tách thời gian chuẩn bị input nếu UI scope cần. Ghi lúc header tới, không gọi mốc đó là TTFT.
2. Đọc byte tăng dần; dùng decoder UTF-8 có trạng thái và parser SSE đúng framing, xử lý line ending, nhiều dòng `data:`, comment/heartbeat và event bị chia giữa các network chunk. Chỉ parse JSON sau khi đủ event. Quy tắc ở [HTML Standard — Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html).
3. Theo schema endpoint, nhận diện delta câu trả lời có nội dung và ghi mốc đầu/cuối, số chunk, gap. Phân biệt text hiển thị với metadata, tool call và reasoning nội bộ; không thu chain-of-thought. Thêm mốc render đầu tiên nếu đo trải nghiệm UI.
4. Nhận diện terminal event theo contract; không mặc định mọi API dùng `[DONE]`. EOF/mất kết nối trước terminal → incomplete; event lỗi sau HTTP 200 vẫn là lỗi. Có terminal nhưng không có text thì TTFT=null và kiểm contract của tác vụ đó.
5. Deadline tổng và cancel vẫn áp dụng suốt stream; giữ partial output có nhãn, error/timeout, attempts và trace. Chặn retry/reconnect tự động không được ghi nhận. Thu usage từ provider hoặc tokenizer đúng model; chunk count không là token count.
6. Tách judge/chấm chất lượng khỏi thời gian phục vụ. Dùng output đã lưu để chấm sau nếu mục tiêu là latency sản phẩm; khi chạy judge cùng máy hoặc cùng quota, ghi ảnh hưởng tải chung.

## 6. Profile 10 phút và profile đầy đủ

**Khoảng 10 phút, công cụ/adapter đã sẵn sàng:** 2 phút xác nhận contract, endpoint, dữ liệu và budget; 1 phút curl health và kiểm trace; 4 phút chạy tối đa 10–20 tác vụ đại diện theo cap đã cho phép (dừng sớm ở deadline/budget); 3 phút đối soát mẫu số, lỗi, TTFT/E2E và viết giới hạn. Chưa có quyền inference thì chỉ chạy health local và ghi chatbot `not_run/blocked` đúng lý do. p95/p99 của mẫu ít chỉ để tìm ca chậm, chưa đủ chứng minh SLO. Thời gian setup thiếu được báo rõ, không tính như đã chạy eval.

**Profile đầy đủ, lập trước khi xin thêm tài nguyên nếu cần:** warm-up được gắn nhãn; baseline 1 user; các bậc concurrency hoặc arrival-rate theo nhu cầu đã thống nhất; cửa sổ ổn định ở mỗi bậc; cooldown/kiểm backlog; lặp lại các nhóm input/output, cold/warm và cache. Thời lượng và số mẫu phải phù hợp ngân sách cùng độ tin cậy cần có; không có mức request/s mặc định cho mọi sản phẩm.

- VU/concurrency là số worker/user đồng thời, không phải RPS. Closed model đợi request trước kết thúc nên RPS có thể giảm khi hệ thống chậm; open/arrival-rate duy trì lịch khởi phát nhưng phải theo dõi dropped iterations và khả năng máy tạo tải. Chọn theo lưu lượng thật, tham khảo [k6 open và closed models](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/).
- Ghi offered rate, started/completed/successful RPS, concurrency thực, think time, connection reuse, CPU/RAM runner, queue depth/age và quota/rate-limit. Nếu runner bão hòa hoặc thiếu VU thì chưa kết luận đó là giới hạn server.
- Chốt trước điểm dừng: budget/request/token cap, deadline, tỷ lệ lỗi hay queue age được phép; dừng ngay lỗi auth/cấu hình. Không nâng tải tiếp sau vượt cap hoặc retry vô hạn. Stress, spike, soak và fault injection là scope riêng; chỉ chạy khi được cho phép và có cách dừng/khôi phục.
- So phiên bản trên cùng profile; kèm độ đúng/task success để phát hiện “nhanh hơn vì trả lời thiếu”. Không suy SLA từ tốc độ model local, health route hay endpoint bỏ qua retrieval/tools.

## 7. Evidence và kết luận QA

Mỗi run dùng thư mục mới chứa `manifest.json`, `requests.jsonl`, raw metric export, summary, response/trace được phép và báo cáo. Dùng đường dẫn tương đối với gốc evidence đã ghi; request/session ID ở log, không làm label metric cardinality cao.

Một record request nên có: `run_id`, `case_id`, `request_id`, `started_at_utc`, `workload_group`, `input_tokens`, `output_tokens`, `token_source`, `cache_state`, `cold_warm`, `attempt_count`, `status`, `http_status`, `error_type`, `deadline_ms`, `e2e_ms`, `ttfb_ms`, `first_content_ms`, `last_content_ms`, `chunk_count`, `queue_ms`, `tool_ms`, `model_ms`, `judge_ms`, `trace_ref`, `response_ref`. Trường không đo được là `null` kèm lý do; phân biệt duration bị chặn ở deadline với completion. Chi tiết token timestamp hoặc chunk gap lưu artifact riêng để tính lại, không tự điền số đo từ expected.

Mỗi dòng metric trong báo cáo ghi: giá trị/đơn vị, n và tử/mẫu, nhóm workload, cửa sổ đo, tool/version, công thức percentile, nguồn evidence, phần loại trừ và lý do. Ngưỡng có `threshold_approved=false` khi chỉ mới đề xuất; không có ngưỡng thì ghi **Đã đo · Chưa chốt ngưỡng**. Trong schema kit dùng `status=not_run` cho metric chưa chốt ngưỡng, giữ value và diễn giải trạng thái đo; không biến nó thành ca chưa chạy hoặc điểm pass.

Ví dụ **đề xuất để thảo luận, chưa được duyệt**: “TTFT p95 ≤ 2 giây, E2E p95 ≤ 10 giây cho nhóm prompt ngắn/output tối đa 200 token, 5 user đồng thời, warm, cache miss; timeout ≤ 1% trong cửa sổ và cỡ mẫu sẽ chốt”. Các con số này không phải benchmark đã chạy hay SLA của provider. Chỉ áp thành threshold CI sau khi chủ sản phẩm chốt cả workload, cỡ mẫu, budget và quy tắc lỗi. Khi đã duyệt, giữ nguyên ngưỡng qua retest; không nới để tạo pass.

Tài liệu CLI/API chính thức được đối chiếu ngày 2026-10-07. Ghi phiên bản cài thực tế trong mỗi run và kiểm lại nguồn khi dùng phiên bản khác. Tài liệu này không chứa kết quả performance của một sản phẩm đã chạy.
