# Human Mind — Duyệt tài liệu RAG

Trang quản trị local cho luồng **nhập nguồn → kiểm sơ bộ → người duyệt → kho tri thức**. FastAPI + SQLite FTS5 + giao diện web tiếng Việt. Tích hợp parser và chunker thật từ [scope-data-bot](https://github.com/Qyroven/scope-data-bot) tại commit `cb37446a00c6283cbb596df524885cfcb08a9fe7`.

## Clone, cài và chạy trên máy của bạn

Ứng dụng có repo riêng: https://github.com/SIReal3103/crawl-rag-pipeline. Không cần clone repo tài liệu `ai-project-starter` để chạy ứng dụng.

**Chuẩn bị:** Git, Python **3.12** có `venv`/`pip`, Bash và kết nối mạng lúc cài lần đầu. macOS/Linux dùng Terminal; Windows dùng terminal **WSL Ubuntu**, chạy toàn bộ các lệnh trong WSL. Các script Bash này không chạy trực tiếp trong PowerShell. Chưa có kiểm chứng cài đặt Windows native.

Kiểm công cụ trong terminal:

```bash
git --version
python3.12 --version
```

Nếu thiếu, cài Git và Python 3.12 bằng trình quản lý gói của hệ điều hành hoặc bộ cài Python trước. Chọn một thư mục bạn có quyền ghi làm nơi chứa project, mở terminal tại đó, rồi chạy:

```bash
git clone https://github.com/SIReal3103/crawl-rag-pipeline.git
cd crawl-rag-pipeline
bash setup.sh
bash run.sh
```

**Lệnh `setup.sh` và `run.sh` chạy trong thư mục `crawl-rag-pipeline` vừa clone**, nơi có `app.py`. Nếu Python 3.12 trên máy mang tên `python3`, kiểm `python3 --version` rồi dùng `PYTHON_BIN=python3 bash setup.sh`.

`setup.sh` tự tải dependency, clone parser/chunker upstream đúng commit vào `.runtime/scope-data-bot`, tạo `.venv` trong project và chuẩn bị tokenizer. Bạn không cần tự clone upstream hay dùng file ở máy tác giả. Lần đầu cần mạng; thời gian phụ thuộc tốc độ tải. Không đưa key hoặc dữ liệu mẫu riêng vào bản cài mới.

Giữ terminal chạy server, mở trình duyệt **trên cùng máy** tại **http://127.0.0.1:8765/#pipeline**. Localhost là địa chỉ của ứng dụng sau khi bạn chạy server, không phải website đã được host trên GitHub. Trang đầu chưa có dữ liệu; làm theo [hướng dẫn thao tác](../huong-dan-crawl-rag-pipeline.md).

Dừng server bằng **Ctrl+C** trong terminal. Lần sau mở terminal trong project và chỉ chạy `bash run.sh`. Khi muốn cập nhật, dừng server rồi chạy:

```bash
git pull --ff-only
bash setup.sh
bash run.sh
```

Nếu cổng đang bận:

```bash
RAG_REVIEW_PORT=8766 bash run.sh
```

Sau đó mở **http://127.0.0.1:8766/#pipeline**. Không cần dừng ứng dụng khác đang dùng 8765.

| Vấn đề | Cách xử lý |
| --- | --- |
| `python3.12: command not found` | Cài Python 3.12; nếu executable tên khác, đặt `PYTHON_BIN` khi setup |
| Không tạo được venv/pip | Cài thành phần `venv`/`pip` cho đúng Python 3.12 rồi chạy lại setup |
| `setup.sh: No such file` | Kiểm đang ở thư mục `crawl-rag-pipeline` có `app.py`, không phải thư mục cha hoặc repo hướng dẫn |
| Setup lỗi tải dependency/tokenizer | Kiểm mạng và lỗi hiển thị; chưa chạy server cho tới khi setup thành công |
| Upstream khác commit | Dùng clone mặc định mới hoặc cấu hình `SCOPE_BOT_PATH` đúng commit; script không tự ghi đè checkout khác |
| Trình duyệt không kết nối | Giữ terminal server mở, kiểm lỗi startup và dùng đúng cổng; trên Windows mở từ máy chạy WSL |

Parse/chunk, duyệt và tìm từ khóa không cần key AI. Tạo index semantic và lấy evidence cần key hợp lệ của provider đã chọn, cấu hình trong **Cấu hình API key**; có thể phát sinh phí. Chạy server thành công không xác nhận key/model đã được cấp quyền.

## Dùng trang

### Cấu hình API key

Mở **Cấu hình API key** trên thanh điều hướng hoặc `http://localhost:8765/#settings`:

- **Gateway BTC:** ô `BTC_API_KEY` riêng cho `api.thucchien.ai`.
- **Nhà cung cấp riêng:** OpenAI, Google (Gemini/Veo), Anthropic và DeepSeek, mỗi dịch vụ có key độc lập. Key Google không tự chứng minh tài khoản có quyền dùng Veo.
- Nhập key để lưu/thay thế; chỉ hiện trạng thái “Đã lưu · Chưa kiểm tra”, không trả lại key hoặc vài ký tự cuối. Gỡ key cần đánh dấu xác nhận trong trang.
- **Reset tất cả key** → **Xác nhận xóa tất cả key** xóa toàn bộ key đã lưu trong ứng dụng (kể cả BTC), rồi đưa con trỏ về ô BTC. Hủy giữ nguyên key. Reset không xóa tài liệu RAG, file key gốc hoặc thu hồi key tại nhà cung cấp.
- Key lưu trong `<thư mục dữ liệu>/credentials/providers.json`, quyền file `0600`, thư mục `0700`, ngoài source/Git và DB tài liệu. File là plaintext được giới hạn quyền hệ điều hành, **chưa có mã hóa riêng/Keychain**. Bản sao lưu toàn thư mục dữ liệu sẽ bao gồm key; cần bảo vệ bản sao lưu tương ứng.
- Không lưu key vào sessionStorage/localStorage, audit tài liệu, source/chunks, export hoặc API response. Các lỗi validation không phản hồi lại input chứa key.
- Lưu key không gọi mạng đến nhà cung cấp, không bật AI, không tự fallback giữa BTC và provider khác. Worker parse/chunk vẫn không nhận key. Chưa có kiểm chứng key còn hiệu lực, billing, quyền model hoặc kết nối BTC.

API local: `GET /api/credentials` chỉ trả metadata; `PUT /api/credentials/{btc|openai|google|anthropic|deepseek}` nhận `{"api_key":"..."}`; `DELETE` gỡ key; `POST /api/credentials/reset` với `{"confirm":true}` xóa tất cả key đã lưu. Mutation yêu cầu token phiên/origin như API khác. `run.sh` vẫn chạy một worker local; chưa hỗ trợ chia sẻ kho key giữa nhiều process/tenant.

### Nhập và duyệt tài liệu

1. Thêm tệp PDF/TXT/MD/HTML (UTF-8 cho text), dán văn bản hoặc nhập URL HTTP(S) công khai. Tối đa 10 MB; nội dung sau parse tối đa 600.000 ký tự.
2. Chọn bộ tài liệu, mã nguồn ổn định và phiên bản. Ngày upload **không** được dùng làm ngày hiệu lực. Bật “phụ thuộc thời gian” để bắt buộc ngày bắt đầu; ngày kết thúc là mốc không bao gồm.
3. Đối chiếu **Nguồn gốc**, nội dung trích xuất, từng đoạn, lỗi/cảnh báo. Sửa text/metadata ở trạng thái chờ; bản gốc vẫn giữ nguyên. Khi sửa text, locator trang cũ bị bỏ để không tạo citation giả.
4. Nhập người duyệt, ghi chú và xác nhận đã kiểm các cảnh báo. Lỗi chặn không thể bỏ qua. Phê duyệt ghi trạng thái và chỉ mục trong một transaction.
5. Thử **Tra cứu nguồn** trên đúng bộ tài liệu/ngày áp dụng hoặc **Xuất kho JSON**. Từ chối/thu hồi không được truy hồi hay export.

Từ chối cần lý do; có thể mở lại bản bị từ chối. Bản đã duyệt bất biến: nhập phiên bản mới để thay nội dung. Nếu cùng nguồn có hiệu lực chồng, thu hồi bản cũ rồi duyệt bản mới, hoặc nhập các khoảng không chồng. Chưa có thao tác thay thế hai bản nguyên tử; thu hồi trước có thể tạo khoảng trống ngắn. Không xóa lịch sử cũ.

Mỗi quyết định có revision, tên người duyệt, thời gian server, hash nguồn/nội dung và ghi chú. Duyệt revision cũ hoặc bấm lặp không tạo publish trùng. Tên người duyệt là nhãn audit của phiên local, **chưa phải danh tính được hệ thống đăng nhập xác thực**.

## Crawl → người duyệt → semantic RAG

Mở **Crawl & RAG pipeline** hoặc `http://localhost:8765/#pipeline`:

1. Bấm **＋ Tạo phiên mới** để xóa chủ đề, bộ tài liệu và URL khỏi biểu mẫu; mặc định 3 trang, độ sâu 0 và provider BTC. Nhập chủ đề/địa bàn/giai đoạn, tên bộ tài liệu và chọn **Cách lấy nguồn**. Mặc định **Nhập URL bài viết/PDF trực tiếp** yêu cầu URL, nhiều URL phân cách dấu phẩy. Muốn tự tìm thì chọn riêng **Tự tìm qua DuckDuckGo (có thể bị chặn)**; ô URL sẽ được bỏ qua. Không vượt robots/CAPTCHA hay chạy JavaScript. Tìm kiếm miễn phí có thể không trả nguồn; không tự bịa tài liệu.
2. Bấm **Bắt đầu crawl**, theo dõi trace tự cập nhật mỗi 3 giây khi phiên đang chạy (hoặc bấm **Cập nhật trạng thái**). Mỗi bản parse hợp lệ được nhập `pending`, giữ bản gốc/hash/assessment và liên kết phiên crawl. Bảng dữ liệu connector cũng vào hàng chờ; lỗi nhập hiển thị theo phiên. Crawl không dùng key AI.
3. Trên thẻ phiên, **Tiếp tục duyệt N tài liệu →** lọc đúng tài liệu của phiên và mở bản pending có điểm trích xuất thấp nhất. Banner cho phép quay về toàn bộ hàng chờ. Nếu chưa có tài liệu, **Nhập URL nguồn để thử lại →** điền lại phạm vi/bộ tài liệu/giới hạn và đưa con trỏ về ô URL, chưa tự chạy. Sau quyết định, phần chi tiết hiện số còn chờ và **Duyệt tài liệu tiếp theo →**. Khi hết pending và có bản approved, **Tiếp tục: tạo index →** mở cấu hình đúng bộ tài liệu, BTC mặc định, chưa gọi API trả phí. **Mở hàng chờ duyệt**: danh sách pending ưu tiên điểm trích xuất thấp trước. Mọi tài liệu đều cần người duyệt; chưa có tự duyệt theo confidence hay LLM judge.
4. Chọn đúng bộ tài liệu và provider, bấm **Tạo index từ bản đã duyệt**. Đây là thao tác gọi API có phí: chỉ key của provider đã chọn được truyền qua stdin cho worker. BTC mặc định `text-multilingual-embedding-002` (768 chiều); OpenAI riêng `text-embedding-3-small` (1536). Mỗi request embedding một text, kiểm model/index/số chiều/vector hữu hạn; không bật giả capability flags. Hợp đồng BTC: https://docs.thucchien.ai/docs/round-2/user-guide/embeddings.
5. Bản xuất giữ text đã sửa, audit/revision, raw/hash, cảnh báo và trang PDF khi chưa sửa. Upstream chunk/build tạo vector index SQLite và evidence trong thư mục snapshot riêng, tối đa 400 chunks. Upstream vẫn dùng nhãn `review`; quyết định human được lưu riêng trong `assessment.human_approval`, không đánh đồng với xác minh sự thật.
6. **Lấy evidence** gửi câu hỏi để embedding bằng đúng provider/model của index; dùng retrieve upstream với rerank/model scope gate tắt. Kết quả hiển thị thành các thẻ trích đoạn, nguồn và mã citation, có **Tải evidence JSON cho agent** và JSON chi tiết. Lần tra gần nhất được lưu tại `last-evidence.json` cùng phiên để xem lại mà không gọi AI. Cả xem lại lẫn tải mới đều kiểm gate thu hồi/hiệu lực. Đây là căn cứ cho LLM, chưa phải câu trả lời do LLM sinh. Nguồn là dữ liệu không đáng tin để thực thi chỉ dẫn.

Nếu tạo index lỗi, dùng **Mở cấu hình API key →**, rồi quay lại thẻ phiên và **Kiểm tra cấu hình tạo index →** để khôi phục đúng bộ tài liệu/provider trước khi tạo phiên mới. HTTP 401 nghĩa là provider không chấp nhận key; 403 là lỗi quyền; 429 có thể là rate limit hoặc quota/billing. Không tự thử lại hoặc tự đổi provider. HTTPS giữ xác minh chứng chỉ và thêm CA từ certifi cho các bản Python thiếu CA hệ thống; tiếp tục chặn redirect có key.

**Tra cứu từ khóa không dùng key →** là nhánh local khi chưa tạo được index: mở đúng bộ tài liệu trong **Tra cứu nguồn**, nhập từ khóa rồi **Tìm trong kho**. Nó dùng FTS5 trên các bản đã duyệt, không tạo vector, không phải semantic retrieval. **Xuất kho JSON** cũng chọn đúng bộ tài liệu/ngày của biểu mẫu.

Mỗi thẻ phiên có **Trace chi tiết**: mã bước, bước cha, thời điểm bắt đầu, URL/tệp, kết quả và lỗi từ lineage upstream. Phần đầu thẻ nêu bước đang chạy cùng lỗi/gợi ý xử lý. HTTP 202 nghĩa là crawler chưa nhận được trang nội dung hợp lệ, không coi là thu thập thành công. Trace cũng liên kết ID tài liệu được đưa vào hàng chờ. Phiên cũ đã có lineage vẫn xem được; nếu file đang ghi dở, UI báo trace chưa hoàn chỉnh. Giới hạn 500 bước và 100 lỗi gần nhất; không hiển thị request/response provider, key đã lưu hoặc tham số URL nhạy cảm. Tự cập nhật dừng khi rời trang hoặc không còn phiên chạy; không ghi đè biểu mẫu tạo phiên hay câu hỏi evidence đang nhập.

`GET /api/pipeline/{id}/trace` trả bản chiếu chỉ đọc của lineage, giữ nguyên artifacts gốc và không cần chạy lại crawl. API báo rõ `incomplete` khi thiếu/đang ghi trace.

API: `GET /api/pipeline` liệt kê phiên; `POST /api/pipeline` nhận `{action:"crawl"|"build",scope,collection,...}`; crawl nhận `seed_urls,max_sources,max_pages,max_depth`; build nhận `provider:"btc"|"openai"`. `POST /api/pipeline/{id}/evidence` nhận `{question}`, giữ nguyên response evidence upstream. `GET` cùng đường dẫn trả `{last_evidence: {question,created_at,bundle}|null}`, không gọi provider và vẫn kiểm gate. Các mutation dùng token phiên/origin như API khác. Bot nên gọi endpoint evidence này để được kiểm lại gate, **không đọc trực tiếp index/llm-input.json cũ**.

Job/artifacts nằm ở `<data>/pipeline/<id>/`, không chứa key. Mỗi server chạy một tác vụ crawl/build tại một thời điểm, tối đa 30 phút; khởi động lại đánh dấu tác vụ dở là interrupted, không tự chạy lại. Tạo phiên mới để thử lại. Thu hồi, đổi tập phiên bản đã duyệt, hoặc sang ngày hiệu lực mới sẽ chặn evidence từ index cũ và yêu cầu tạo lại. Snapshot đã xuất ra ngoài ứng dụng không thể bị thu hồi từ xa.

Kiểm thử offline dùng store/trace/tokenizer/chunker thật và kiểm gate thu hồi; không tạo vector giả. Kiểm thử offline không xác nhận crawl hoặc provider live; cần kiểm riêng với dữ liệu và cấu hình của bản cài mới.

### Phiên mới, lịch sử và lỗi lấy nguồn

Trang chỉ hiển thị chi tiết một **Phiên đang xem**. **Lịch sử** mặc định thu gọn, có trạng thái/ngày/mã phiên và nút mở từng phiên. Chọn phiên cũ khôi phục cấu hình để xem hoặc thử lại; bấm crawl/build luôn tạo job mới. **Tạo phiên mới** chỉ dọn biểu mẫu/phiên đang xem, không xóa tài liệu, lịch sử hay key. Tab lưu ID phiên hoặc lựa chọn trống trong sessionStorage, nên tải lại sau khi tạo phiên mới không kéo thẻ cũ trở lại. Đổi tên bộ tài liệu để tách dữ liệu; dùng lại tên bộ là bổ sung vào cùng kho.

Nếu mọi truy vấn tìm nguồn thất bại với HTTP 202 từ DuckDuckGo, nguyên nhân được nêu ngay trên thẻ: chưa lấy được URL để crawl, không liên quan key AI. Bấm **Nhập URL nguồn để thử lại →** sẽ chuyển sang chế độ URL trực tiếp. `GET /api/pipeline/{id}/trace` có thêm `diagnosis` (hoặc `null`), không sửa job/lineage cũ.

Cả crawler và nhập URL trực tiếp hỗ trợ phản hồi `identity` hoặc `gzip` (kể cả máy chủ vẫn nén dù yêu cầu identity). Giới hạn dung lượng áp dụng cho cả byte tải về và sau giải nén; gzip hỏng/thiếu hoặc encoding khác bị từ chối. Hash và bản gốc lưu theo nội dung đã giải nén. Robots, kiểm IP public, redirect và HTTPS vẫn được giữ.


## Kiểm sơ bộ và mức tự tin

Điểm **Chất lượng trích xuất** là chỉ số quy tắc 0–100, chưa hiệu chỉnh. `quality.method=extraction-rules-v1`; mỗi finding có severity, mô tả, snippet/vị trí khi có và điểm trừ. Các kiểm hiện có: rỗng, parse một phần, cảnh báo parser, văn bản quá ngắn, ký tự lỗi, chỉ dẫn có dạng prompt injection, dấu hiệu bí mật, nguồn trùng và thiếu hiệu lực bắt buộc.

`factual_confidence=unverified`: không khẳng định phát hiện hết sai sót hay xác minh sự thật. Người duyệt phải kiểm nội dung chuyên môn, nguồn có thẩm quyền và các mâu thuẫn. Không có LLM judge đang chạy, không dùng số 85/100 như “85% đúng”. Phê duyệt không biến điểm này thành xác suất đúng.

PDF có text dùng parser native của upstream; giữ trang thật. PDF không đọc được vẫn nằm ở staging với bản gốc và lỗi chặn. Có thể nhập text đã đối chiếu thủ công hoặc dùng OCR local. Chế độ Docling là tùy chọn:

PDF trộn chữ/scan: trang có ảnh nhưng không có text khiến toàn bản bị đánh dấu partial và chặn duyệt; trang trắng không có ảnh không bị coi là thiếu nội dung. Với bản partial, chạy OCR/nhập lại bản đầy đủ hoặc nhập nguồn text hoàn chỉnh đã đối chiếu. Kiểm này không nhận ra mọi hình/bảng bị bỏ sót trên trang vẫn có chữ.

```bash
cd /path/to/scope-data-bot
bash setup-parser.sh
# Sau khi cài runtime/model local thành công:
DOCUMENT_PARSER=docling SCOPE_BOT_PATH=/path/to/scope-data-bot bash /path/to/rag-review/run.sh
```

Docling tải model một lần; runtime OCR của ứng dụng này chưa được nghiệm thu. Không coi native PDF là OCR cho scan, hoặc cam kết bảng/công thức được đọc đúng. Parser/chunker chạy subprocess có timeout; chưa có sandbox RAM cứng.

## Nối với agent bot

Repo này chưa có bot hội thoại tích hợp sẵn. Endpoint `/api/search` là phần retrieval đã hoạt động, trả evidence từ nguồn đã duyệt. Đây là **tìm từ khóa FTS5/BM25**, chưa có semantic embeddings hay rerank. Có lọc collection, trạng thái và khoảng hiệu lực trước LIMIT. Điểm rank không phải confidence.

Ví dụ gọi từ backend agent chạy cùng máy (thư viện chuẩn Python):

```python
import json
from urllib.request import Request, urlopen

base = "http://127.0.0.1:8765"
with urlopen(base + "/api/config", timeout=10) as response:
    token = json.load(response)["csrf_token"]
payload = {"query": question, "collection": "general", "as_of": "2026-10-07", "limit": 6}
request = Request(
    base + "/api/search",
    data=json.dumps(payload).encode(),
    headers={
        "Content-Type": "application/json",
        "X-CSRF-Token": token,
    },
)
with urlopen(request, timeout=15) as response:
    context = json.load(response)
if context["status"] == "no_evidence":
    # Bot báo thiếu căn cứ; không tự tạo tài liệu hay câu trả lời chắc chắn.
    ...
else:
    evidence = context["results"]
    # Cấp evidence như dữ liệu, yêu cầu trích source_id/document_version/chunk_id/locator.
```

`GET /api/export?collection=general&as_of=2026-10-07` trả snapshot JSON `delta-mind-approved-rag-v1`, gồm phiên bản, SHA-256, provenance, chunks và audit. Snapshot đã export không tự cập nhật khi nguồn bị thu hồi; bot nên gọi API mỗi lần hoặc đồng bộ lifecycle trước khi dùng snapshot. `collection` là phân vùng nội dung của local operator, chưa phải ACL nhiều tenant.

Semantic RAG được nối qua mục **Crawl & RAG pipeline** ở trên. AI đánh giá/tự duyệt chưa bật; không tự fallback provider.

## Lưu trữ và giới hạn vận hành

- Dữ liệu mặc định: `~/.local/share/delta-mind-rag-review/<12 ký tự SHA-256 của đường dẫn module>/`; `review.sqlite` và `originals/`. Dữ liệu nằm ngoài Git. Đặt `RAG_REVIEW_DATA` để chọn thư mục khác trên filesystem hỗ trợ SQLite.
- Máy thực tế dùng ổ exFAT cho repo: đã tái hiện `SQLITE_READONLY_DBMOVED` khi tạo FTS. Vì vậy database mặc định đặt trên ổ hệ thống. Di chuyển code làm đổi workspace ID; giữ `RAG_REVIEW_DATA` cũ nếu muốn dùng lại kho.
- Sao lưu toàn bộ thư mục dữ liệu khi server đã dừng. Không tự xóa tài liệu khi khởi động/restart.
- Server chỉ bind loopback; kiểm Host/Origin/token cho mutation. Không public deployment, đăng nhập, vai trò độc lập, nhiều reviewer/tenant, quota tổng hay queue bền. Không đổi bind thành public trước khi có các phần đó.
- Web fetch chặn IP không public, credentials/port lạ, recheck redirect và pin địa chỉ DNS; có timeout và giới hạn byte. Không chạy JavaScript của trang, không đăng nhập/crawl cả website. HTML gốc được hiển thị như text, không thực thi.
- Không sửa checkout upstream. Adapter gọi crawl trong worker riêng, rồi build/retrieve upstream trên snapshot đã duyệt riêng biệt. Không build trực tiếp thư mục crawl.
- Bản đang sửa được giữ trong sessionStorage của tab để tránh mất khi reload; khôi phục chỉ khi revision còn khớp. Lưu hoặc chọn bỏ thay đổi sẽ xóa bản nháp này.

## Kiểm thử

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/ruff format --check .
node --check static/app.js
```

Tests dùng thư mục tạm, parser/chunker upstream thật. Các fixture được tạo riêng trong test; giao diện không seed tài liệu giả.

## Hướng dẫn và đánh giá cùng repo

Đọc [hướng dẫn thao tác pipeline](../huong-dan-crawl-rag-pipeline.md) và [hướng dẫn agent/eval](../chatbot-eval-kit/agent-guide.md). Bộ eval không tự biết dataset/adapter của ứng dụng; cần nối theo contract trước khi đánh giá sản phẩm.
