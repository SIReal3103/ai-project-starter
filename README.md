# Hướng dẫn, bộ skill và eval sản phẩm AI

Repo chứa hướng dẫn BTC, bộ 24 skill độc lập cho phát triển sản phẩm AI cùng các skill gameplay/eval, script thử gateway và bộ báo cáo/template eval. Ứng dụng Crawl & RAG pipeline được phát triển trong [repo riêng](https://github.com/SIReal3103/crawl-rag-pipeline); thư mục `rag-review/` ở đây là bản mã lưu trước khi tách.

## QA và eval mới nhất

- [Cài hoặc chuyển bộ công cụ QA lên SSD](qa-tools-storage/README.md): clone, tạo volume APFS trên ổ ngoài, cài package, giữ đường dẫn cũ bằng symlink, mount/unmount và kiểm sau khi chuyển.
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
| Các hướng phát triển sản phẩm và hợp đồng kế hoạch cho agent mới | [cac-huong-phat-trien-san-pham-dua-vao-techstack.md](cac-huong-phat-trien-san-pham-dua-vao-techstack.md) |
| Bộ 24 skill Codex — 14 hướng sản phẩm và 10 năng lực dùng chung | [Danh mục nguồn](cac-huong-phat-trien-san-pham-dua-vao-techstack.md), [catalog](skills/catalog.json) |
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

Hướng dẫn chatbot/voicebot BTC và script gateway giữ nguyên nội dung nguồn. Hướng dẫn techstack bổ sung hợp đồng kế hoạch/bàn giao ở phần 18.9–18.11, chế độ giao việc ở phần 21 và bộ 24 skill ở phần 22, cập nhật ngày 07/10/2026. Báo cáo cũ trong `reports/` và bốn JSON trong `example-results/` được giữ để tham chiếu; báo cáo QA mới nằm trong `qa-report/`. ZIP chứa bộ kit hiện tại; skill nằm riêng trong `skills/` của repo.

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
## Bộ skill độc lập cho agent mới

Nhóm phát triển sản phẩm có **24 skill**: 14 hướng C1–I2 và 10 năng lực dùng chung. Ngoài nhóm này có bộ QA thực hành `ai-qa-evals` và danh mục `ai-qa-metrics` bên dưới. Mỗi gói có `SKILL.md`, `agents/openai.yaml` và references local; không cần lịch sử chat, repo nguồn hay skill khác để hiểu cách làm. Chỉ đọc đúng phần theo tác vụ, không nạp cả bộ.

| Skill | Dùng khi |
|---|---|
| [ai-product-planning](skills/ai-product-planning/SKILL.md) | Bối cảnh, MVP và gói kế hoạch cho agent mới |
| [btc-gateway-integration](skills/btc-gateway-integration/SKILL.md) | Kiểm API, model và capability qua Gateway BTC |
| [ai-agent-runtime](skills/ai-agent-runtime/SKILL.md) | State, context, tools, duyệt và khôi phục run |
| [ai-rag-evidence](skills/ai-rag-evidence/SKILL.md) | Ingest, truy hồi theo quyền và dẫn nguồn đúng |
| [vietnamese-voice-runtime](skills/vietnamese-voice-runtime/SKILL.md) | Thu âm, STT/TTS, sửa lượt, hủy và phát audio |
| [ai-media-production](skills/ai-media-production/SKILL.md) | Tài sản, job media, render và kiểm bản xuất |
| [ai-safety-privacy](skills/ai-safety-privacy/SKILL.md) | Quyền, guardrails, dữ liệu và kiểm tác động |
| [ai-product-evaluation](skills/ai-product-evaluation/SKILL.md) | Oracle, test, AI eval và bằng chứng nghiệm thu |
| [ai-reliability-operations](skills/ai-reliability-operations/SKILL.md) | Quota, retry, logs, release và khôi phục |
| [ai-product-delivery](skills/ai-product-delivery/SKILL.md) | Thực hiện kế hoạch tới nghiệm thu và bàn giao |
| [receipt-evidence-assistant](skills/receipt-evidence-assistant/SKILL.md) | Đọc và đối chiếu hóa đơn bằng dữ kiện có nguồn |
| [local-waste-sorting](skills/local-waste-sorting/SKILL.md) | Phân loại rác theo nơi tiếp nhận và nguồn địa phương |
| [public-service-voice-guide](skills/public-service-voice-guide/SKILL.md) | Hướng dẫn thủ tục bằng voice tiếng Việt có nguồn |
| [fraud-response-coach](skills/fraud-response-coach/SKILL.md) | Diễn tập phản ứng trước tình huống lừa đảo |
| [product-campaign-generator](skills/product-campaign-generator/SKILL.md) | App tạo bộ nội dung từ hồ sơ sản phẩm được duyệt |
| [versioned-campaign-updates](skills/versioned-campaign-updates/SKILL.md) | Cập nhật nội dung theo thay đổi dữ kiện có phiên bản |
| [grounded-data-analysis](skills/grounded-data-analysis/SKILL.md) | Hỏi số liệu, tính đúng và giải thích cùng nguồn |
| [contribution-scenario-analysis](skills/contribution-scenario-analysis/SKILL.md) | Phân tích đóng góp và mô phỏng giả định minh bạch |
| [voice-npc-tutor](skills/voice-npc-tutor/SKILL.md) | Luyện nói theo rubric với nhân vật có state |
| [branching-investigation-game](skills/branching-investigation-game/SKILL.md) | Game điều tra theo nhánh với luật và bằng chứng |
| [zalo-support-handoff](skills/zalo-support-handoff/SKILL.md) | Bot FAQ, ticket và bàn giao người trực trên Zalo |
| [telegram-decision-workflow](skills/telegram-decision-workflow/SKILL.md) | Đề xuất, biểu quyết và nhận việc đúng quyền |
| [local-heritage-story](skills/local-heritage-story/SKILL.md) | Tác phẩm về nghề địa phương có nguồn và quyền |
| [branching-impact-story](skills/branching-impact-story/SKILL.md) | Tác phẩm phân nhánh có thông điệp và oracle |

Chưa chọn ý tưởng: dùng `ai-product-planning`. Đã chọn sản phẩm: dùng skill hướng đó; dùng skill nền khi cần xử lý sâu phần API/RAG/voice/runtime/eval. Skill phân biệt khám phá, lập kế hoạch, review và triển khai; mỗi chế độ chỉ thực hiện phạm vi được giao. Quy định BTC chỉ áp dụng cho bối cảnh BTC đã xác nhận; repo/vòng thi phải xác định riêng.

Copy **nguyên thư mục của skill muốn dùng** vào `$CODEX_HOME/skills` (nếu có cấu hình), mặc định `~/.codex/skills`. Có thể cài một hoặc cả bộ. Không copy `catalog.json` như một skill. Nếu đã có bản cài tùy chỉnh, đối chiếu trước khi thay thế. Các gói không dùng symlink tới máy tác giả.

Ví dụ:

```text
Dùng $receipt-evidence-assistant lập kế hoạch cho đề sau: [đề đầy đủ].
Repo: [đường dẫn nếu có]. Dữ liệu: [file thật hoặc trạng thái chưa nhận].
Ràng buộc đã chốt: [quyền, provider, thời gian, ngân sách].
Lưu gói kế hoạch để agent mới không có lịch sử chat thực hiện.
```

Khi đã giao triển khai, agent kiểm hiện trạng rồi làm luồng thật, kiểm lỗi và bàn giao bằng chứng. Không coi yêu cầu lập kế hoạch là quyền chạy inference hoặc xuất bản. Các con số/capability trong tài liệu nguồn là snapshot/đề xuất, không phải số đo hay quyền hiện có.

Tài liệu techstack tại root là nguồn chuẩn. `skills/catalog.json` ánh xạ các phần nguồn tới từng gói. Sau khi sửa, chạy:

```sh
python3 scripts/sync-skills.py
python3 scripts/sync-skills.py --check
python3 -m unittest discover -s scripts/tests -p 'test_*.py'
```

`sync-skills.py --skill ai-product-planning` chỉ đồng bộ một gói; lệnh cũ `sync-planning-skill.py` vẫn dùng được cho gói planning. `--check` không ghi. Không sửa trực tiếp `references/` sinh tự động: `task-contract.md` chứa cách nhận việc/bàn giao, `techstack-guide.md` chứa lát cắt kỹ thuật, `planning-handoff.md` chỉ đọc khi cần kế hoạch. Cập nhật bản cài cá nhân từ gói mới sau khi sync. Kiểm cấu trúc/đồng bộ không chứng minh hành vi; cần review và thử tình huống độc lập.

## Skill kiểm thử và nghiệm thu đầy đủ

- [ai-qa-evals](skills/ai-qa-evals/SKILL.md): quy trình thực thi test phần mềm, eval AI, đo phản hồi/tải và kiểm bảo mật/quyền riêng tư; chọn mức smoke khoảng 10 phút hoặc nghiệm thu mở rộng.
- [ai-qa-metrics](skills/ai-qa-metrics/SKILL.md): 34 nhóm chỉ số theo tính năng, công thức/mẫu số, dữ liệu cần thu, cách kết luận và bảng QA **7 cột với Pass/Fail riêng**.
- [Báo cáo mock mới](chatbot-eval-kit/qa-report/examples/mock-acceptance-report-v2/README.md): HTML Apple-like, PDF 13 trang, 24 ca QA, 21 chỉ số và biểu đồ; có fixture/script dựng lại. Toàn bộ dữ liệu là giả lập, không phải kết quả test sản phẩm. [Hướng dẫn agent dựng báo cáo](skills/ai-qa-evals/references/report-layout-and-mock.md).

| Muốn làm gì? | Hướng dẫn thực hành |
| --- | --- |
| Unit/API/integration/UI, coverage, accessibility | [Vitest, pytest/unittest, coverage.py, Playwright/axe](skills/ai-qa-evals/references/software-testing.md) |
| Eval chatbot/RAG/agent, multi-turn, guardrail, judge | [Ragas, DeepEval, Promptfoo và adapter sản phẩm](skills/ai-qa-evals/references/llm-agent-evaluation.md) |
| Đo p50/p95/p99, TTFT, streaming, tải, timeout | [curl, k6, timestamp/trace và workload](skills/ai-qa-evals/references/performance-testing.md) |
| Secret/dependency/code/web, quyền/tenant, PII và xóa dữ liệu | [Gitleaks, audit, SAST, ZAP và ca quyền/state](skills/ai-qa-evals/references/security-testing.md) |

Copy nguyên thư mục skill, gồm `references/` và `assets/` nếu có, khi cài trên máy khác. Các reference QA trên được viết riêng; không thuộc ba file trích nguồn tự sinh bởi `sync-skills.py`. Hướng dẫn có lệnh và giới hạn, không khẳng định công cụ đã cài/chạy trên mọi sản phẩm. Mẫu dữ liệu không được coi là bằng chứng thật.

```text
Dùng $ai-qa-evals đánh giá [repo/URL sản phẩm] và dùng $ai-qa-metrics chọn phép đo.
Ngân sách: [thời gian, request/token, chi phí]. Môi trường và scope: [test].
Xét đủ chức năng/UI/API, AI, latency/load, bảo mật/quyền riêng tư theo tính năng có thật.
Lưu evidence và báo phần thiếu; xuất bảng QA 7 cột, HTML trước rồi PDF.
```

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
