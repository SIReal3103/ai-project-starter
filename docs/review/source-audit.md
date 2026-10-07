# Rà nguồn và hợp nhất hướng dẫn

Ngày rà: 2026-10-07. Mục tiêu: giữ kiến thức dùng lại cho dự án mới, loại phụ thuộc máy/dự án/cuộc thi khỏi mặc định, và tách hướng dẫn thiết kế khỏi công cụ thực thi.

Tên nguồn dưới đây là **định danh tương đối để truy vết cuộc rà**, không phải link hoặc file bắt buộc phải tồn tại trong clone. Không đóng gói lịch sử workspace, credentials, dữ liệu chạy hoặc ghi chú cá nhân. Tài liệu kết quả tự đủ để áp dụng cùng source/dữ liệu/quyền thật của dự án mới.

## Phạm vi và mức rà

Đã rà cấu trúc và các chủ đề của ba guide chính, hướng dẫn voice, toàn bộ kế hoạch quick-evals cùng mẫu report; đối chiếu nguyên tắc từ runbook báo cáo và guide của eval kit. Các kế hoạch/report kỹ thuật cũ được rà để tìm kiến thức chưa nằm trong guide chính; không chạy lại sản phẩm cũ và không kế thừa số đo của chúng.

Rà tài liệu nguồn không phải tái kiểm chứng API, pháp luật, giá, quota hoặc phiên bản thư viện tại ngày tạo starter. Những claims phụ thuộc thời điểm được bỏ khỏi mặc định hoặc chuyển thành yêu cầu kiểm tài liệu chính thức/probe runtime. Pseudocode trong guides có nhãn rõ. CLI runnable nằm ở [eval kit](../../tools/evals/README.md) và phải được đánh giá độc lập với chất lượng một app tương lai.

## Nguồn chính

| Định danh nguồn | Chủ đề đã rà | Giữ lại trong starter | Loại/đổi và lý do |
| --- | --- | --- | --- |
| `chung-khao/README.md` | Bản đồ tài liệu và đường đọc | Index theo nhu cầu trong [architecture](../guides/architecture-and-use-cases.md) | Tên đội, vòng thi, link môi trường nguồn: không là đầu vào của dự án mới |
| `chung-khao/agent-chatbot-btc-guide.md` | Kiến trúc; API; data/SQL; tools; RAG; voice/media; evals; security/privacy/ethics; prompt/context; runtime; handoff | Hợp đồng và nguyên tắc phân bổ trong đủ bảy guides | Code app banking chưa tích hợp, cài đặt máy, model/endpoint/giá/quota cố định và claims kiểm cũ không chép như đã hoạt động |
| `chung-khao/agent-voice-bot-btc-guide.md` | Hai giờ, STT/chat/TTS, recorder/codec, permission race, epochs, playback, rảnh tay, errors và tests | [Voice/media](../guides/voice-and-media.md), [hai giờ](../guides/two-hour-workflow.md) | Route/model/giọng/quota/budget riêng được thay bằng contract và probe của dự án |
| `chung-khao/cac-huong-phat-trien-san-pham-dua-vao-techstack.md` | Chọn ý tưởng, bảy nhóm sản phẩm, ghép công nghệ, tám bước chọn stack, ví dụ ticket, học tập/vận hành | Use cases phổ quát, kiến trúc tối thiểu, ví dụ thiết kế và thứ tự nghiệm thu | Mã đề, tổ chức/nhân sự, trọng số giả định và ràng buộc cuộc thi không trở thành mặc định |
| `chung-khao/plans/20261007-new-product-quick-evals/plan.md` | Lịch 120 phút, dependency và nghiệm thu | Lịch và gate trong [hai giờ](../guides/two-hour-workflow.md) | Số test/thời gian của app cũ không trở thành số đo starter |
| `…/phase-01-prepare-tools-and-contract.md` | Contract, chọn tool tối thiểu, chuyển runner, setup/rollback | Đọc repo thật, nối adapter, chuẩn bị runtime trước lượt cuối | Đường dẫn máy, import/dependency từ dự án khác, package install assumptions được bỏ |
| `…/phase-02-software-tests.md` | Unit/contract/integration/UI, coverage/performance, artifacts | Bản đồ tests và nguồn evidence trong [evals](../guides/evals-and-observability.md) | Lệnh cho layout không tồn tại không quảng bá như runnable |
| `…/phase-03-product-evals.md` | Dataset/oracle, adapter/scorer, media, budgets và controls | Tách target/oracle, code vs human/judge, local/replay/live, media checks | Provider MP4/manifest/runner phụ thuộc app cũ không bundle; dùng kit và adapter dự án |
| `…/phase-04-ten-minute-run-and-handoff.md` | Deadline runner, trạng thái, xử lý lỗi, số đếm và handoff | Timebox 360 giây là mục tiêu thiết kế, gate và report trung thực | Không khẳng định mọi app/runner đã có deadline hoặc chạy dưới sáu phút |
| `…/reports/evaluation-report-template.md` | Metadata, counts, expected/actual, evidence và giới hạn | Yêu cầu report trong guide evals và runbook | Không mang số liệu/ô placeholder thành kết quả đã chạy |
| `scope-data-bot/local-evidence/20261007-full-tool-report/agent-guide.md` | Phân loại evidence, tool inventory, coverage/subtests, HTML/PDF, limitations | Phân biệt product/example/control/replay/live; named tool inventory; kiểm mọi trang khi xuất PDF | Absolute paths, local venvs, dependency tái dùng, logs/dataset/media và kết quả sản phẩm cũ không chuyển |
| `scope-data-bot/local-evidence/20261007-chatbot-eval-kit/agent-guide.md` — đối chiếu qua bản portable `tools/evals/agent-guide.md` | Dataset protocol, adapters, Ragas/DeepEval, optional judge, replay, controls và report | Link tới runbook thực của kit, lệnh demo local, ranh giới metric `scored`/release gate | Không giả định kit đã gọi provider live hoặc đã đo app mới; không nhập runtime từ máy nguồn |

`…/` trong bốn hàng phase và hàng report là tiền tố `chung-khao/plans/20261007-new-product-quick-evals/`.

## Kế hoạch và báo cáo kỹ thuật được hợp nhất

| Nhóm định danh tương đối | Chủ đề và quyết định |
| --- | --- |
| `chung-khao/plans/20261006-btc-agent-guide/plan.md` | Nền guide/API: giữ capability gate, không giữ trạng thái test/giá của lần cũ |
| `chung-khao/plans/20261006-voice-bot-guide/plan.md` | Tích hợp voice/lifecycle: giữ checklist và điều kiện core trước rảnh tay |
| `chung-khao/plans/20261006-evaluation-tooling/plan.md` | Chọn tool và độ tin cậy phép đo: hợp nhất inventory, không cài tất cả |
| `chung-khao/plans/20261006-security-privacy-terms/plan.md` | Security và các quyết định policy: giữ kỹ thuật/data inventory, không copy cam kết pháp lý |
| `chung-khao/plans/20261006-final-agent-ethics-safety/plan.md` | Safety, fairness, tác động và governance: biến thành hành vi/eval có scope |
| `chung-khao/plans/20261006-agent-reliability-final/plan.md` và `reports/btc-runtime-audit.md`, `code-sample-audit.md`, `elearning-prompt-research.md` | Rà heading/chủ đề và các kết luận liên quan runtime/prompt/adapter: giữ deadline, state, schema, preflight và phân biệt import với live; không bundle lịch sử audit hoặc test counts |
| `chung-khao/rag-review/README.md` | Rà kiến trúc/luồng ingest-review-publish và giới hạn local: chuyển thành nguyên tắc vòng đời, không chuyển source app hoặc giả định có auth/semantic index |
| `chung-khao/plans/20261007-rag-document-review/plan.md`, `phase-01-review-workflow.md` và `reports/app-validation.md`, `scope-data-bot-review.md`, `upstream-validation.md` | Review gắn revision/hash, provenance, quyền collection/hiệu lực/thu hồi, parsing: hợp nhất vào RAG; không mang private storage, dependency upstream hoặc test evidence của app cũ |
| `chung-khao/plans/20261007-crawl-review-pipeline/plan.md`, `reports/validation.md` | Crawl là pending, approved snapshot riêng, bounded jobs, stale index: giữ invariants; kết quả crawl/provider của lần cũ không là bằng chứng starter |
| `chung-khao/plans/20261007-pipeline-end-to-end/plan.md` | Luồng vận hành nguồn → review → index → evidence và lỗi provider: giữ phân biệt lexical/semantic/live, không copy cấu hình/tài khoản/tình huống riêng |
| `scope-data-bot/plans/20261007-product-evaluation/`, `20261007-full-tool-report/`, `20261007-chatbot-eval-kit/` | Rà danh mục/headings để xác định report/tool lineage; kiến thức portable lấy từ runbook và kit, không bundle lịch sử đo của parser hoặc ví dụ độc lập |

Đây là **hợp nhất báo cáo kỹ thuật thành hướng dẫn**, không xóa lỗi lịch sử hoặc đổi kết quả cũ thành pass. Những kết quả cũ vẫn thuộc source của chúng; starter chỉ công bố bằng chứng thực sự chạy trên starter ở báo cáo riêng của lượt tích hợp.

## Phần chủ ý không đưa vào repo mới

- Các file Markdown đặt theo tên cá nhân ở `chung-khao/`: chỉ kiểm loại nội dung/heading để nhận diện check-in; không chép tên, ghi chú hoặc nội dung cá nhân.
- Secrets/keyfiles/dotenv/session tokens, log/raw prompts, snapshots, audio/video, dữ liệu riêng, storage/DB và credential errors của từng tài khoản: không phải tài liệu portable.
- Source/history của dự án bên thứ ba hoặc ứng dụng local cũ: không vendor chỉ để hướng dẫn có vẻ đầy đủ; quyền phân phối và dependencies là phạm vi riêng.
- Hooks/AI-log và quy tắc môi trường tổ chức: không tự cài, giả định hay vô hiệu; chỉ ghi trong profile BTC tùy chọn rằng phải theo môi trường thực khi áp dụng.
- Kết quả benchmark, installed tool claims, thư viện phiên bản cũ, USD/quota/model/endpoint hardcode: cần bằng chứng mới trên cấu hình thật.
- Bản PDF/HTML nhiều trang, báo cáo cũ và cache của tools: chỉ giữ cách tạo/kiểm report, không bundle lịch sử.
- AppleDouble, caches, node_modules/venv và đường dẫn tuyệt đối tới máy nguồn: không là dependency sau clone.

## Bản đồ độ phủ của bản hợp nhất

| Nhóm cần giữ | Nơi dùng sau clone |
| --- | --- |
| Ý tưởng/use cases/stack/workflow/agent | [Architecture](../guides/architecture-and-use-cases.md) |
| SQL/RAG/reconciliation/NL2SQL/anomaly/prompt/tools/state/runtime | [Chatbot, RAG và agent](../guides/chatbot-rag-and-agents.md) |
| Backend/auth/tenant/secrets/uploads/security/privacy/Terms/consent/ethics | [Backend, security và privacy](../guides/backend-security-and-privacy.md) |
| Voice/codec/cancel/dialogue/vision/media/jobs | [Voice và media](../guides/voice-and-media.md) |
| Software tests/coverage/evals/tool inventory/judge/observability/report | [Evals](../guides/evals-and-observability.md) |
| 120 phút, 10 phút cuối, gate/rollback/handoff | [Hai giờ](../guides/two-hour-workflow.md) |
| Gateway/client/capability probes/egress/cost/BTC tùy chọn | [Provider profiles](../guides/provider-profiles.md) |

Các liên kết sử dụng trong guides chỉ trỏ tới sibling guides và `tools/evals` cùng repo. Không cần workspace gốc, tài khoản của đội cũ hoặc một dự án khác để đọc hướng dẫn hay chạy demo local của kit. Dự án AI thực vẫn cần app, dữ liệu, credentials và ngân sách riêng; chúng không được giả lập như đã có.
