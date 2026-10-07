# Hướng dẫn BTC và bộ báo cáo/eval

Repo chứa hướng dẫn BTC, script thử gateway và bộ báo cáo/template eval. Ứng dụng Crawl & RAG pipeline được phát triển trong [repo riêng](https://github.com/SIReal3103/crawl-rag-pipeline); thư mục `rag-review/` ở đây là bản mã lưu trước khi tách.

## QA và eval mới nhất

- [Template QA Apple-like và hướng dẫn agent](chatbot-eval-kit/qa-report/README.md): ca kiểm thử có bước thực hiện, kỳ vọng/thực tế, Đạt/Chưa đạt, bằng chứng, lỗi và kiểm lại; 14 chỉ số có cách đo và diễn giải.
- [Lượt inference mới ngày 07/10/2026](chatbot-eval-kit/qa-report/evaluations/20261007-qwen-rerun/README.md): Qwen2.5-0.5B đạt 6/24 sau audit, 18 chưa đạt; Ragas/DeepEval offline chạy lại. Dữ liệu tổng hợp, context lưu sẵn; chưa có semantic judge hoặc agent executor.
- [HTML mới](chatbot-eval-kit/qa-report/evaluations/20261007-qwen-rerun/report.html) và [PDF mới](chatbot-eval-kit/qa-report/evaluations/20261007-qwen-rerun/report.pdf). Tải HTML về rồi mở bằng trình duyệt; trang file trên GitHub hiển thị mã nguồn.
- [Skill ai-qa-evals](skills/ai-qa-evals/SKILL.md) để giao việc chạy eval và báo cáo cho sản phẩm khác.

### Cài skill cho Codex

Sau khi clone repo này, mở terminal tại root `ai-project-starter` (macOS/Linux):

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/ai-qa-evals "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Nếu đã có skill cùng tên, đối chiếu rồi cập nhật nội dung thay vì chép lồng thư mục. Mở phiên Codex mới để nhận skill, rồi dùng: **`$ai-qa-evals Đánh giá sản phẩm này và xuất báo cáo QA tiếng Việt từ bằng chứng thật.`** Skill tự hướng dẫn clone bộ công cụ nếu workspace mới chưa có kit; không phụ thuộc file local của tác giả.

## Tài liệu

| Nội dung | File |
| --- | --- |
| Hướng dẫn chatbot và agent BTC — bản gốc | [agent-chatbot-btc-guide.md](agent-chatbot-btc-guide.md) |
| Hướng dẫn voicebot BTC — bản gốc | [agent-voice-bot-btc-guide.md](agent-voice-bot-btc-guide.md) |
| Các hướng phát triển sản phẩm — bản gốc | [cac-huong-phat-trien-san-pham-dua-vao-techstack.md](cac-huong-phat-trien-san-pham-dua-vao-techstack.md) |
| Gameplay chung cho game phiêu lưu văn bản AI | [Khung gameplay](skills/ai-story-gameplay/references/gameplay-guide.md) |
| Skill tạo và rà soát gameplay AI | [ai-story-gameplay](skills/ai-story-gameplay/SKILL.md) |
| Script thử gateway — bản gốc | [gateway-test.sh](gateway-test.sh) |
| **Hướng dẫn agent và prompt giao việc cho eval** | [chatbot-eval-kit/agent-guide.md](chatbot-eval-kit/agent-guide.md) |
| **Báo cáo mẫu HTML** | [bao-cao-evals.html](chatbot-eval-kit/reports/bao-cao-evals.html) |
| **Báo cáo mẫu PDF** | [bao-cao-evals.pdf](chatbot-eval-kit/reports/bao-cao-evals.pdf) |
| Template HTML và ca đánh giá | [report-template.html](chatbot-eval-kit/templates/report-template.html), [case-template.json](chatbot-eval-kit/templates/case-template.json) |
| Toàn bộ bộ eval, dataset, adapter, Ragas/DeepEval và cách chạy | [chatbot-eval-kit/README.md](chatbot-eval-kit/README.md) |
| Gói ZIP bộ eval để giao cho agent | [chatbot-agent-guardrail-eval-template.zip](chatbot-agent-guardrail-eval-template.zip) |
| **Ứng dụng Crawl & RAG pipeline** | [Repo crawl-rag-pipeline](https://github.com/SIReal3103/crawl-rag-pipeline) |
| **Hướng dẫn trang Crawl & RAG pipeline** | [huong-dan-crawl-rag-pipeline.md](huong-dan-crawl-rag-pipeline.md) |

Ba hướng dẫn BTC/techstack và script gateway giữ nguyên nội dung nguồn. Báo cáo cũ trong `reports/` và bốn JSON trong `example-results/` được giữ để tham chiếu; báo cáo QA mới nằm trong `qa-report/`. ZIP chứa bộ kit hiện tại; skill nằm riêng trong `skills/` của repo.

## Skill thiết kế gameplay phiêu lưu AI

[Khung gameplay](skills/ai-story-gameplay/references/gameplay-guide.md) mô tả vòng chơi, hành động tự do, nhân vật, hậu quả, bộ nhớ, combat tùy chọn và voice/TTS. Dùng chung cho nhiều bối cảnh; không cố định một cốt truyện hoặc nhà cung cấp AI. Tài liệu nằm trong gói skill để bản copy vẫn tự đủ nội dung.

Copy toàn bộ `skills/ai-story-gameplay/` vào `$CODEX_HOME/skills` nếu đã cấu hình, hoặc `~/.codex/skills` theo mặc định. Đối chiếu trước khi thay một bản cài đã tùy chỉnh. Skill gồm `SKILL.md`, metadata và `references/gameplay-guide.md`; không cần cài thư viện hay gọi API để dùng hướng dẫn.

```text
Dùng $ai-story-gameplay viết gameplay chung cho game phiêu lưu văn bản AI.
Giữ cơ chế tái sử dụng, không gắn vào một câu chuyện cụ thể.
```

```text
Dùng $ai-story-gameplay thiết kế gameplay cho game web nhập vai của tôi.
Bối cảnh: [ý tưởng]. Người chơi: [đối tượng].
Yêu cầu: [hành động tự do, mức combat, voice/TTS nếu cần].
Viết tài liệu độc lập để bàn giao cho agent; chưa triển khai ứng dụng.
```

Skill cũng dùng để rà soát gameplay có sẵn. Yêu cầu thiết kế không tự cấp quyền xây app, gọi dịch vụ trả phí hoặc xuất bản. Các cơ chế và số minh họa là đề xuất cần chơi thử, không phải sản phẩm AI đã được kiểm chứng.

## Chạy lại bộ eval

Core cần Python 3.12+, không cần key hay package bên ngoài. Lần đầu, mở terminal tại nơi muốn lưu repo và chạy:

```sh
git clone https://github.com/SIReal3103/ai-project-starter.git
cd ai-project-starter/chatbot-eval-kit
python3 main.py validate
python3 main.py self-test
python3 main.py demo --frameworks off --out runs/demo-01
python3 report.py --input runs/demo-01/results.json --output reports/demo-01.html
```

Nếu đã clone, mở terminal trong `ai-project-starter/chatbot-eval-kit` và bắt đầu từ lệnh `python3 main.py validate`. Đổi tên thư mục output ở lượt tiếp theo. Trên Windows dùng `python` nếu không có lệnh `python3`. Ragas/DeepEval và xuất PDF tự động cần cài dependency theo README của kit. LLM judge live cần endpoint/model/key và ngân sách riêng.

Báo cáo có sẵn là **mẫu tổng hợp**, không phải kết luận chất lượng của sản phẩm mới. Cấu hình model, endpoint và quota trong hướng dẫn gốc cần được xác nhận tại thời điểm sử dụng; lượt đóng gói này không gọi gateway hay provider.

## Clone và chạy ứng dụng Crawl & RAG pipeline

Ứng dụng có [repo GitHub riêng](https://github.com/SIReal3103/crawl-rag-pipeline). Cần Git, Python 3.12 và Bash (macOS/Linux hoặc WSL trên Windows). Mở terminal tại nơi muốn lưu project:

```bash
git clone https://github.com/SIReal3103/crawl-rag-pipeline.git
cd crawl-rag-pipeline
bash setup.sh
bash run.sh
```

Giữ terminal mở và truy cập **http://127.0.0.1:8765/#pipeline** trên cùng máy. Xem [README ứng dụng](https://github.com/SIReal3103/crawl-rag-pipeline#readme) để cài điều kiện cần, đổi cổng, cập nhật và xử lý lỗi.

Thư mục `rag-review/` ở repo tài liệu là bản mã đi kèm trước khi tách. Để cài mới hoặc cập nhật ứng dụng, dùng repo `crawl-rag-pipeline` ở trên. Bộ báo cáo/eval tiếp tục nằm trong repo tài liệu này.

Hướng dẫn từng bước, bao gồm kiểm công cụ, dừng/mở lại, cập nhật và kiểm lần đầu: [Cài và sử dụng pipeline](huong-dan-crawl-rag-pipeline.md#0-clone-cài-đặt-và-mở-ứng-dụng).
