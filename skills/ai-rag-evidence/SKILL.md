---
name: ai-rag-evidence
description: "Xây, cải tiến hoặc kiểm RAG từ tài liệu có quyền: parser, chunking, index phiên bản, truy hồi theo scope, citations và eval nguồn. Dùng khi câu trả lời cần bằng chứng từ corpus; không thay SQL để tính số liệu."
---

# RAG có bằng chứng và phiên bản

Đích là tìm đúng bằng chứng được phép rồi trả lời trong phạm vi nó hỗ trợ, có vị trí nguồn mở kiểm được. Vector similarity không phải xác suất đúng hoặc bằng chứng quyền.

## Khởi đầu

Đọc [task contract](references/task-contract.md), phần 12.4 và 14 trong [nguồn kỹ thuật](references/techstack-guide.md). Nếu lập kế hoạch, dùng [planning handoff](references/planning-handoff.md); nếu review thì đưa finding có nguồn trước khi sửa theo phạm vi được giao.

Scout corpus/manifest, parser, schema metadata, index/query, auth và các câu hỏi thật. Chốt nguồn, owner, quyền ingest/gửi model/xem tài liệu, định dạng (text/PDF/scan/bảng), phiên bản/hiệu lực, nhu cầu freshness và oracle. Tài liệu được hứa cấp chưa là corpus sẵn có. Đừng lấy web search thay kho dữ liệu riêng hoặc gửi câu hỏi chứa dữ liệu riêng ra search.

## Quy trình

1. Giải nghĩa tác vụ: tra điều khoản, tìm bằng chứng hay tổng hợp số. Tính số tổng hợp bằng SQL/code khi phù hợp; RAG cấp định nghĩa/chính sách và giải thích, không thay phép tính.
2. Lấy baseline trên câu hỏi có evidence chuẩn: exact lookup hoặc lexical search cho corpus nhỏ/mã/thuật ngữ. Chỉ thêm embedding/hybrid/reranker khi có lỗi recall đáng giải và quyền/capability phù hợp. Không cài nhiều vector DB để phòng xa.
3. Ingest nguồn có quyền → hash/parse → staging kiểm cấu trúc → chunk → embed nếu cần → kiểm vectors → publish một revision nguyên tử. Lỗi giữ serving version cũ, không nạp nửa nguồn.
4. Giữ metadata tối thiểu ở mỗi bằng chứng: source_id, document/version, parser/chunker version, raw location thật, scope/owner, effective dates, trạng thái published/superseded/retracted. Ngày upload không tự là ngày hiệu lực.
5. Chunk theo điều khoản/tiêu đề; giữ bảng, header, đơn vị và ngoại lệ cùng dữ kiện. PDF có page thật; scan cần OCR được phép với nhãn kiểm. Không bịa page cho nội dung không phân trang hoặc coi parse thành công là nội dung đúng.
6. Query bind identity/scope từ server, lọc nguồn/phiên bản/thời điểm/miền trước cấp context. Retrieval trả typed evidence và trạng thái riêng cho không có bằng chứng, nguồn mâu thuẫn, lỗi index/parser và dữ liệu không được phép.
7. Tạo đáp án với claim → evidence IDs; kiểm ID/location/version có thật và thuộc context đã cấp, rồi kiểm claim thực sự được nguồn hỗ trợ. UI mở nguồn cũng kiểm quyền; citations có thật vẫn có thể không chứng minh câu trả lời.
8. Đo lại, sửa đúng lớp input/parser/chunking/filter/retrieval/generation; chỉ giữ nâng cấp cải thiện metric mục tiêu trong budget mà không nới quyền.

## Contracts và các trường hợp khó

- `DocumentRevision`: nguồn bất biến, version và hiệu lực nghiệp vụ; reparse/re-embed tạo revision xử lý mới nhưng không tự thay kỳ hiệu lực. Publisher khóa theo nguồn khi cần, không để các lần ingest đè nhau.
- `Evidence`: ID, text, source/version/location, scope và metadata có ý nghĩa. Trích xuất unknown giữ unknown; confidence model không mở quyền hoặc biến text thành dữ kiện đã xác nhận.
- `RetrievalResult`: candidates, filters, index/data version, coverage/warnings, status. `no_evidence` khác `unavailable`; không đổi một trong hai thành câu trả lời trống được chấm pass.
- `Answer`: facts/claims cùng evidence IDs và caveats. Hỏi lại khi câu hỏi mơ hồ; nguồn mâu thuẫn cần precedence đã xác nhận hoặc chuyển người kiểm, không để model chọn ngẫu nhiên.
- Bản nguồn thay/thu hồi phải vô hiệu cache phụ thuộc; checkpoint và link tải cũ vẫn cần kiểm quyền hiện tại. Xóa bao gồm raw/OCR/chunks/vectors/cache/exports theo chính sách đã chốt.

Nếu dùng embeddings, kiểm model/dimension và batch index thực; không tái dùng vector khác model. Cache theo scope+text hash+model+dimensions+processing version. Chặn vector không hữu hạn/zero trước cosine. Không suy batch giảm token phí.

Nếu dùng hybrid, cả lexical và vector có cùng ACL/hiệu lực; fusion cần được đo, không cộng score khác thang tùy ý. PostgreSQL full-text không mặc định BM25. ANN phải so recall với exact trên cùng filter; thiếu top-k không cho phép nới quyền.

## Kiểm và nghiệm thu

Chuẩn bị người kiểm gán evidence chuẩn và claim được hỗ trợ, tách dev/holdout theo nguồn/nhóm để giảm rò đáp án. Chọn k/ngưỡng/budget trên dev; không tuning sau xem holdout. Corpus ít nguồn phải báo giới hạn.

Kiểm câu có/không nguồn, scan/bảng/ngoại lệ, số 0 đầu, typo, khác phiên bản hiệu lực, nguồn bị thu hồi, ngoài scope, publish lỗi và injection trong nguồn. Oracle parser/citations là raw document; recall/MRR là evidence labels; groundedness cần người kiểm hoặc judge đã hiệu chỉnh, không target model tự chứng nhận.

Đo retrieval và câu trả lời riêng: Recall@k/MRR, đúng source/version/location, claim hỗ trợ, abstention/false refusal, task success gồm lỗi, latency/cost. Không tính câu không có nguồn là recall 100%; không lấy ID hợp lệ làm toàn bộ tiêu chí grounding.

Bàn giao manifest/quyền, pipeline và query contracts, phiên bản/parser/model thực, config/ngưỡng có căn cứ, các lệnh ingest/query/test đã chạy, case failures và cách phục hồi serving version. Chỉ phát hành phần đã có evidence/oracle; nêu rõ corpus/capability chưa kiểm thay vì tuyên bố toàn bộ RAG đáng tin cậy.
