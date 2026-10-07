# Kiểm chứng bộ 24 skill

Ngày: 07/10/2026. Kết quả: hoàn thành đóng gói, review, bài thử lập brief/review và cài local. Chưa kiểm triển khai 24 ứng dụng hoặc capability của provider.

## Nguồn và phạm vi

- Repo: `SIReal3103/ai-project-starter`, nhánh `main`, HEAD khi bắt đầu `bf0640b2c73ec7abdb3a9aec0754c4fcbdf5bb8e`.
- File GitHub được đối chiếu qua `gh`: `cac-huong-phat-trien-san-pham-dua-vao-techstack.md`, blob `12e8dd55bb739dbab627a795d1b05b434b14608e`, 178877 bytes. Không coi source snapshot là tài liệu API hiện hành đã thử.
- Giữ các sửa đổi của task planning trước. Task này cập nhật điều hướng/phạm vi đầu ra ở phần 11, bổ sung phần 22 và bộ skill cho toàn bộ phần 1–21.
- 14 skill theo sản phẩm C1–I2 và 10 skill nền. [Catalog](../../../skills/catalog.json) ghi primary sections và source sections; mỗi gói có entrypoint, metadata và ba reference local. Hợp đồng kế hoạch chỉ cần đọc khi tác vụ cần kế hoạch.
- Không sửa repo thi của đội, không gọi inference/media, không gửi tin, không commit/push/deploy.

## Kiểm cấu trúc và script

| Kiểm | Kết quả |
|---|---|
| Validator của `skill-creator` | 24/24 frontmatter hợp lệ |
| `agents/openai.yaml` | 24/24 parse được, short description đúng giới hạn, default prompt gọi đúng `$skill-name` |
| Liên kết trong entrypoint | 72/72 trỏ file có thật trong chính gói |
| Coverage nguồn | 92 tiêu đề có số/C1–I2 trong phần 1–21 đều nằm trong source sections được đóng gói |
| Ánh xạ sản phẩm | C1–I2 mỗi hướng có đúng một skill chính |
| `python3 scripts/sync-skills.py --check` | 72/72 reference khớp nguồn/catalog |
| `python3 scripts/sync-planning-skill.py --check` | Wrapper cũ vẫn kiểm đúng ba reference của planning |
| Gọi script bằng đường dẫn tuyệt đối từ `/tmp` | Vẫn kiểm đủ 72 reference, không phụ thuộc CWD |
| `python3 -m unittest discover -s scripts/tests -p 'test_*.py'` | 7 test qua |
| `git diff --check` | Không có lỗi whitespace trong diff tracked |

Các test script kiểm heading trong code fence, chọn parent/child không lặp, section thiếu/trùng, phát hiện missing/stale và chế độ chỉ đọc, sửa lại bundle, catalog lỗi không ghi dở, tên sai/selection lạ và source đổi làm bundle stale. Đây là kiểm cơ chế đóng gói, không tự chứng minh chất lượng chỉ dẫn.

## Review độc lập và sửa có bằng chứng

Một agent riêng đọc entrypoint/catalog/source và script, không chỉnh file. Review phát hiện chỉ dẫn đọc ở sáu skill F/G/H rộng hơn phần có trong bundle; skill media yêu cầu phần 11 nhưng chưa đóng gói phần đó.

Đã sửa danh sách đọc của sáu skill thành đúng các mục có trong gói, thêm phần 11 vào bundle media và nêu rõ phải xác nhận đường dẫn đội/vòng từ repo thực. Sau sync, reviewer kiểm lại và xác nhận finding đã giải quyết. Không còn concern trong phạm vi lượt kiểm lại.

## Bài thử sử dụng với agent chưa có lịch sử chat

Hai agent mới, `fork_turns=none`, nhận mỗi agent 12 yêu cầu và bản sao các gói skill ở thư mục tạm. Agent đọc skill/reference liên quan rồi **viết brief hoặc review thật** cho từng ca; không chỉ nhận xét skill. Không cung cấp đáp án kỳ vọng trong prompt. Controller đọc đủ 24 đầu ra, kiểm bước tiếp theo, đầu vào thiếu, phân quyền AI/code/người, oracle/nghiệm thu và giới hạn kết luận.

Các bài thử chạy trên snapshot trước sửa danh sách đọc nêu trên. Sửa cuối chỉ điều chỉnh đường đọc, thêm source và làm rõ phạm vi repo/vòng; đã được review lại và kiểm bundle. Không tuyên bố đã chạy lại 24 bài thử trên snapshot cuối. Mỗi agent xử lý 12 ca trong cùng một phiên mới; đây không phải 24 phiên độc lập hoàn toàn.

| Skill | Ca thử | Hành vi quan sát được trong đầu ra |
|---|---|---|
| ai-product-planning | Bảo trì, chưa có repo/data/provider | Có trạng thái sẵn sàng một phần, owner và phase; file dự kiến không bị mô tả là đã tồn tại |
| btc-gateway-integration | Nhầm Chat/Responses, item ID, HTTP 200 | Tách protocol, chỉ rõ `call_id`, phân biệt kiểm offline với verified live |
| ai-agent-runtime | Hai tab duyệt ticket, mất response | Revision/hash, idempotency và unknown outcome; không hứa exactly-once khi đích không hỗ trợ |
| ai-rag-evidence | Hai phòng ban, scan, hai bản hiệu lực | Giữ provider nội bộ, ACL/as-of, OCR đối chiếu, phân biệt hiệu lực với processing revision |
| vietnamese-voice-runtime | WebM đổi đuôi, STT rỗng, autoplay, hủy | Đòi codec thật, zero model calls khi rỗng, dùng lại audio, chặn kết quả muộn |
| ai-product-delivery | Thiếu repo/data, demo HTTP 200 | Chuẩn bị acceptance matrix/runbook; không coi ứng dụng đã nghiệm thu |
| receipt-evidence-assistant | Hóa đơn mờ/trùng, đề luyện hai giờ | Evidence từng field, Decimal/rule, xác nhận trùng, thời gian có điều kiện đầu vào |
| local-waste-sorting | Nhiều vật liệu, thiếu luật/site/GPS | Không bịa nơi nhận; chọn site thủ công, tách observation với acceptance rule |
| public-service-voice-guide | Thiếu nguồn/key, mã nghe sai, sửa câu | Không tạo checklist vô căn cứ, giữ số 0 đầu mã, vô hiệu answer/audio cũ |
| fraud-response-coach | Có trẻ vị thành niên, thiếu rubric | Người duyệt/kịch bản phù hợp, không thu secret, không chấm chính thức trước oracle |
| product-campaign-generator | Giá/chứng nhận chưa xác nhận, non-BTC | Giữ provider đã chọn; không bịa claim, approval/version và kiểm file xuất |
| versioned-campaign-updates | Approval cũ, job/export race | Graph phụ thuộc, invalidation, revision bất biến, xuất cùng snapshot |
| grounded-data-analysis | Ngày mơ hồ, thiếu tháng, nghìn đồng | Giữ giá trị gốc, không đổi thiếu thành 0, đơn vị và coverage rõ, không thêm banking |
| contribution-scenario-analysis | Đóng góp và giả định giá/sản lượng | Actual/scenario tách biệt, công thức được duyệt, không gọi mô phỏng là dự báo ML |
| voice-npc-tutor | Dùng STT chấm phát âm, model tự cộng điểm | Không suy phát âm từ transcript, rubric/người dạy và state điểm ở server |
| branching-investigation-game | Đáp án frontend, model tự cho thắng | Đáp án/luật server, approval theo nguồn/version, ca lộ đáp án/gửi trùng |
| zalo-support-handoff | Chỉ có web chat, thiếu quyền OA/FAQ | Không coi web chat là tích hợp OA; account linking, takeover và pending thật |
| telegram-decision-workflow | Đổi/rút phiếu, actor payload, timeout | Current vote/upsert, identity từ sự kiện xác thực, finality và đối soát unknown |
| local-heritage-story | Chưa có tư liệu/consent clone giọng | Quyền/source, không âm thầm thay yêu cầu giọng, có thể tiếp tục manifest |
| branching-impact-story | Offline, một điểm rẽ, không cần app | Giữ dạng tệp tĩnh, không ép AI runtime; graph/đường đi offline và oracle |
| ai-media-production | Retry chồng, URL thành path, bỏ kiểm MP4 | Một lớp retry, unknown outcome, đường dẫn server và kiểm file cuối |
| ai-safety-privacy | Xóa thiếu dẫn xuất, analytics, retention chưa rõ | Data inventory/TTL/restore, kiểm network và không hứa provider không lưu |
| ai-product-evaluation | Bỏ timeout, safety rỗng, tự chấm, best-of | Mẫu số đầy đủ, inconclusive, oracle độc lập và lưu mọi run |
| ai-reliability-operations | Null quota, retry vô hạn, paid probe | Null là unknown, reserve ngân sách, retry hữu hạn, resume và ví riêng |

24/24 bài tạo được đầu ra có nội dung; controller không thấy vi phạm các ràng buộc chính của ca thử. Đây là đánh giá định tính một lượt, không phải tỷ lệ thành công đo trên holdout hoặc bảo đảm mọi agent/model luôn làm đúng. Các bài chỉ lập brief/review ngắn, chưa kiểm agent thực thi toàn bộ gói kế hoạch dài hoặc triển khai ứng dụng.

## Cài đặt và bàn giao

Đã cài đủ 24 thư mục vào `/Users/macbook/.codex/skills`, cập nhật `ai-product-planning` của task trước và thêm 23 gói mới. Không ghi đè skill ngoài catalog. Bản planning trước cập nhật được sao lưu tạm. 120/120 file bản cài được so byte với gói repo; không dùng symlink.

[README](../../../README.md) có bảng chọn skill, ví dụ gọi và cách cài/cập nhật. Tài liệu root là nguồn chuẩn; sửa root/catalog rồi chạy sync, không chỉnh reference sinh tự động. Kết quả đang ở local, GitHub chưa nhận các thay đổi này.
