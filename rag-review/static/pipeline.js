export async function renderPipeline(container, api, openQueue, options = {}) {
  container.replaceChildren();
  const el = (tag, text, cls) => { const node = document.createElement(tag); if (text) node.textContent = text; if (cls) node.className = cls; return node; };
  const intro = el('p', 'Tìm nguồn → crawl → kiểm sơ bộ → người duyệt → embedding/index → evidence. Mọi tài liệu crawl đều chờ duyệt; điểm trích xuất không phải xác suất đúng.', 'notice');
  container.append(intro);
  const guide = el('ol', '', 'pipeline-guide');
  for (const [title, description] of [
    ['1. Lấy nguồn', 'Nhập chủ đề và URL bài viết/PDF. Chạy thử: 1–3 trang, độ sâu 0. Độ sâu 1 là đi thêm một lớp liên kết từ trang đầu.'],
    ['2. Duyệt', 'Mở tài liệu của phiên, đối chiếu bản gốc, ghi người duyệt rồi phê duyệt hoặc từ chối.'],
    ['3. Tạo index', 'Chỉ bản đã duyệt còn hiệu lực được chia đoạn và gửi tới provider đã chọn để embedding. Cần key hợp lệ.'],
    ['4. Kiểm tra evidence', 'Đặt câu hỏi, đọc đoạn nguồn trả về và tải gói JSON cho agent. Đây là căn cứ để LLM trả lời, chưa phải câu trả lời.'],
  ]) {
    const item = el('li', '', 'panel'); item.append(el('strong', title), el('p', description)); guide.append(item);
  }
  container.append(guide);
  const toolbar = el('div', '', 'credential-actions');
  const fresh = el('button', '＋ Tạo phiên mới', 'button primary'); fresh.type = 'button';
  toolbar.append(fresh, el('p', 'Phiên mới bắt đầu bằng biểu mẫu trống. Các phiên trước được giữ trong Lịch sử.', 'field-hint')); container.append(toolbar);
  const form = el('form', '', 'panel credential-card');
  const formTitle = el('h2', 'Cấu hình phiên mới'); form.append(formTitle);
  const field = (name, title, value, type = 'text') => {
    const label = el('label', title), input = el(name === 'scope' ? 'textarea' : 'input'); input.name = name; if (input.tagName === 'INPUT') input.type = type; else input.rows = 3; input.value = value; input.required = true;
    label.append(input); form.append(label); return input;
  };
  const scope = field('scope', 'Phạm vi thu thập (nêu rõ chủ đề, địa bàn, giai đoạn)', ''); scope.minLength = 12; scope.maxLength = 8000; scope.placeholder = 'Ví dụ: Kinh tế, văn hóa Hà Nam giai đoạn 2020–2024';
  const collection = field('collection', 'Bộ tài liệu', ''); collection.maxLength = 100; collection.placeholder = 'Ví dụ: ha-nam';
  const modeLabel = el('label', 'Cách lấy nguồn'), mode = el('select'); mode.id = 'pipeline-source-mode'; modeLabel.htmlFor = mode.id;
  for (const [value, text] of [['urls', 'Nhập URL bài viết/PDF trực tiếp'], ['auto', 'Tự tìm qua DuckDuckGo (có thể bị chặn)']]) { const option = el('option', text); option.value = value; mode.append(option); }
  form.append(modeLabel, mode);
  const seeds = field('seed_urls', 'URL nguồn (nhiều URL phân cách bằng dấu phẩy)', '');
  const sourceHint = el('p', '', 'field-hint'); form.append(sourceHint);
  const updateSourceMode = () => {
    seeds.disabled = mode.value === 'auto'; seeds.required = !seeds.disabled;
    sourceHint.textContent = seeds.disabled ? 'Đang chọn tự tìm nguồn. DuckDuckGo có thể trả HTTP 202 và không tìm được bài. Nếu gặp lỗi này, chuyển sang URL trực tiếp; thay key AI không khắc phục lỗi tìm nguồn.' : 'Dán URL bài viết hoặc PDF công khai để crawl. Crawl không dùng key AI. Đối chiếu địa giới và thời điểm trong tài liệu khi duyệt.';
  };
  mode.addEventListener('change', updateSourceMode); updateSourceMode();
  const pages = field('max_pages', 'Tối đa trang mỗi phiên (1–30)', '3', 'number'); pages.min = 1; pages.max = 30;
  const depth = field('max_depth', 'Độ sâu liên kết (0–2)', '0', 'number'); depth.min = 0; depth.max = 2;
  const label = el('label', 'Provider embedding (chỉ dùng sau khi duyệt)'), provider = el('select');
  provider.id = 'pipeline-provider'; label.htmlFor = provider.id;
  for (const [value, text] of [['btc', 'BTC · text-multilingual-embedding-002'], ['openai', 'OpenAI riêng · text-embedding-3-small']]) { const option = el('option', text); option.value = value; provider.append(option); }
  form.append(label, provider);
  const actions = el('div', '', 'credential-actions');
  const crawl = el('button', 'Bắt đầu crawl', 'button primary'); crawl.type = 'submit';
  const build = el('button', 'Tạo index từ bản đã duyệt', 'button'); build.type = 'button';
  const queue = el('button', 'Mở hàng chờ duyệt', 'button'); queue.type = 'button'; queue.addEventListener('click', async () => { try { await openQueue(); } catch(error) { status.textContent = error.message; } });
  actions.append(crawl, build, queue); form.append(actions);
  form.append(el('p', 'Tạo index gửi nội dung đã duyệt tới provider đã chọn và có thể phát sinh phí. Tra evidence gửi câu hỏi để tạo embedding. Không tự chuyển sang provider khác. Thu hồi/sửa nguồn làm index cũ bị chặn.', 'field-hint'));
  const status = el('p', '', 'field-hint'); status.setAttribute('role', 'status'); form.append(status); container.append(form);
  const prepare = job => {
    scope.value = job.scope; collection.value = job.collection;
    pages.value = job.max_pages || 3; depth.value = job.max_depth ?? 0;
    seeds.value = (job.seed_urls || []).join(', ');
    mode.value = job.action === 'crawl' && !job.seed_urls?.length ? 'auto' : 'urls'; updateSourceMode();
    formTitle.textContent = `Cấu hình từ phiên · ${job.collection}`;
  };
  if (options.preset) {
    prepare(options.preset);
    status.textContent = 'Bước 3: đã chọn bộ tài liệu vừa duyệt. Chọn provider có key hợp lệ, rồi bấm Tạo index từ bản đã duyệt. BTC vẫn là mặc định.';
  }
  const currentTitle = el('h2', 'Phiên đang xem', 'pipeline-jobs-title'); container.append(currentTitle);
  const jobs = el('section'); jobs.id = 'pipeline-current-job'; jobs.setAttribute('aria-label', 'Phiên đang xem'); container.append(jobs);
  const history = el('details', '', 'pipeline-history panel'), historyTitle = el('summary', 'Lịch sử các phiên'), historyList = el('div');
  history.append(historyTitle, historyList); container.append(history);
  const cards = new Map();
  const selectionKey = 'human-mind-pipeline-selection';
  let selectedId = options.preset?.id, initializeForm = !options.preset, loading = false, timer, running = false, reloadRequested = false, historySignature = '';
  if (selectedId === undefined) { try { const stored = sessionStorage.getItem(selectionKey); if (stored !== null) selectedId = stored || null; } catch { /* Selection still works without browser storage. */ } }
  const select = id => { selectedId = id; try { sessionStorage.setItem(selectionKey, id || ''); } catch { /* No credentials or document contents are stored here. */ } };
  if (options.preset) select(options.preset.id);
  const clearCard = () => { cards.clear(); jobs.replaceChildren(); };
  fresh.addEventListener('click', () => {
    select(null); clearCard(); history.open = false; scope.value = collection.value = seeds.value = '';
    pages.value = '3'; depth.value = '0'; provider.value = 'btc'; mode.value = 'urls'; updateSourceMode();
    formTitle.textContent = 'Cấu hình phiên mới'; status.textContent = 'Nhập chủ đề, bộ tài liệu và URL mới rồi bấm Bắt đầu crawl. Key đã lưu và dữ liệu cũ được giữ nguyên.';
    load(); scope.focus(); form.scrollIntoView({behavior:'smooth',block:'start'});
  });
  const active = () => container.contains(form) && !container.hidden;
  const refresh = el('button', 'Cập nhật trạng thái', 'button'); refresh.type = 'button'; container.append(refresh);
  const names = {running:'Đang chạy', needs_review:'Đã nhập vào hàng chờ', no_documents:'Chưa có tài liệu nhập được', ready:'Index đã tạo', failed:'Không hoàn tất', interrupted:'Bị gián đoạn'};
  const nextStep = (job, documents) => {
    const section = el('section', '', 'pipeline-next-step');
    section.append(el('strong', 'Bước tiếp theo'));
    const pending = documents.filter(doc => doc.status === 'pending').length;
    const action = (label, callback) => {
      const control = el('button', label, 'button primary'); control.type = 'button';
      control.addEventListener('click', async () => {
        control.disabled = true;
        try { await callback(); } catch(error) { section.append(el('p', error.message, 'notice error')); }
        finally { control.disabled = false; }
      });
      section.append(control);
    };
    if (job.action === 'crawl' && job.document_ids.length) {
      section.append(el('p', pending ? `Đã tiếp nhận ${job.document_ids.length} tài liệu, còn ${pending} tài liệu chờ duyệt. Kiểm tra nguồn và nội dung trước khi đưa vào RAG.` : 'Phiên này không còn tài liệu chờ duyệt. Xem lại quyết định bên dưới; chỉ bản được phê duyệt mới có thể đưa vào index.'));
      action(pending ? `Tiếp tục duyệt ${pending} tài liệu →` : 'Xem tài liệu của phiên →', () => openQueue(job));
      if (!pending && documents.some(doc => doc.status === 'approved')) action('Tiếp theo: cấu hình tạo index', () => { prepare(job); status.textContent = 'Đã chọn bộ tài liệu của phiên. Kiểm tra provider rồi bấm Tạo index từ bản đã duyệt; bước này có thể phát sinh phí.'; provider.focus(); form.scrollIntoView({behavior:'smooth',block:'start'}); });
    } else if (job.status === 'running') {
      section.append(el('p', job.action === 'crawl' ? 'Đang thu thập. Khi có tài liệu, nút Tiếp tục duyệt sẽ xuất hiện ở đây. Trace tự cập nhật mỗi 3 giây.' : 'Đang tạo index. Khi hoàn tất, nhập câu hỏi để kiểm tra evidence.'));
    } else if (job.action === 'crawl') {
      section.classList.add('needs-attention');
      section.append(el('p', 'Chưa thu thập được tài liệu để duyệt. Nhập URL bài viết hoặc PDF nguồn cụ thể, rồi bấm Bắt đầu crawl. Phiên kết thúc chưa có nghĩa là thu thập thành công.'));
      action('Nhập URL nguồn để thử lại →', () => { prepare(job); mode.value = 'urls'; updateSourceMode(); status.textContent = 'Bổ sung hoặc sửa URL nguồn bên trên, rồi bấm Bắt đầu crawl. Chưa chạy lại tự động.'; seeds.focus(); form.scrollIntoView({behavior:'smooth',block:'start'}); });
    } else if (job.status === 'ready') {
      section.append(el('p', 'Index đã tạo. Nhập câu hỏi bên dưới và bấm Lấy evidence để kiểm tra nguồn trả về.'));
    } else {
      section.append(el('p', 'Index chưa sẵn sàng. Kiểm tra lỗi, key và tài liệu đã duyệt trước khi tạo lại.'));
      if (options.openSettings) action('Mở cấu hình API key →', options.openSettings);
      action('Kiểm tra cấu hình tạo index →', () => { prepare(job); provider.value = job.provider || 'btc'; provider.focus(); form.scrollIntoView({behavior:'smooth',block:'start'}); });
      if (options.openSearch) {
        section.append(el('p', 'Trong lúc chưa có index, có thể kiểm tra bản đã duyệt bằng tìm từ khóa local. Cách này không tạo embedding và không gọi AI.'));
        action('Tra cứu từ khóa không dùng key →', () => options.openSearch(job.collection));
      }
    }
    return section;
  };
  const showTrace = async (job, panel) => {
    try {
      const trace = await api(`/api/pipeline/${job.id}/trace`);
      if (!active() || !panel.isConnected) return;
      const expanded = panel.querySelector('details')?.open ?? job.status === 'running';
      panel.replaceChildren();
      panel.append(el('p', `Mã phiên: ${job.id}`, 'field-hint'));
      panel.append(el('p', trace.current ? `Đang thực hiện: ${trace.current.stage_label} · ${trace.current.label}` : (job.status === 'running' ? 'Đang chờ cập nhật bước xử lý…' : `Phiên đã kết thúc · ${trace.total_nodes || 0} bước được ghi nhận.`), 'trace-current'));
      if (trace.diagnosis) panel.append(el('p', `${trace.diagnosis.title}. ${trace.diagnosis.detail}`, 'notice error'));
      else if (trace.issues.length) panel.append(el('p', `${trace.issues.length} lỗi · ${trace.issues[0].stage}: ${trace.issues[0].message}. ${trace.issues[0].hint}`, 'notice error'));
      panel.append(el('p', trace.message, 'field-hint'));
      const details = el('details'); details.open = expanded;
      details.append(el('summary', `Trace chi tiết · ${trace.events.length} sự kiện`));
      for (const issue of trace.issues) details.append(el('p', `${issue.id} · ${issue.stage} · ${issue.code}: ${issue.message} — ${issue.hint}`, 'notice error'));
      if (job.crawl_summary) details.append(el('p', `Báo cáo upstream: ${job.crawl_summary}`, 'field-hint'));
      const list = el('ol', '', 'trace-events');
      const labels = {running:'Đang chạy',success:'Hoàn tất',failed:'Lỗi'};
      for (const event of trace.events) {
        const row = el('li', '', `trace-event trace-${event.status}`);
        const state = event.status === 'running' && job.status !== 'running' ? 'Chưa ghi nhận hoàn tất' : (labels[event.status] || event.status);
        row.append(el('strong', `${event.stage_label} · ${state}`), el('p', event.label));
        row.append(el('small', `${event.at ? new Date(event.at).toLocaleString('vi-VN') : '—'} · ${event.id}${event.parents?.length ? ' ← ' + event.parents.join(', ') : ''}`));
        if (event.url) row.append(el('p', `URL: ${event.url}`, 'trace-url'));
        if (event.path) row.append(el('p', `Tệp: ${event.path}`, 'field-hint'));
        if (event.issue_id) row.append(el('p', `Lỗi liên quan: ${event.issue_id}`, 'field-hint'));
        if (event.document_id) row.append(el('p', `Tài liệu: ${event.document_id} · ${event.document_status}`, 'field-hint'));
        list.append(row);
      }
      details.append(list); panel.append(details);
    } catch(error) { if (active()) panel.replaceChildren(el('p', `Không tải được trace: ${error.message}`, 'notice')); }
  };
  const showEvidence = (job, output, bundle) => {
    output.replaceChildren();
    const evidence = bundle.evidence || [];
    output.append(el('h4', evidence.length ? `Bước 4 · Đã lấy ${evidence.length} đoạn evidence` : 'Chưa tìm thấy evidence phù hợp'));
    output.append(el('p', evidence.length ? 'Đọc các đoạn và nguồn dưới đây trước khi đưa gói JSON cho agent. Đây là trích dẫn nguồn, chưa phải câu trả lời của LLM hay xác minh sự thật.' : 'Thử câu hỏi sát nội dung hơn hoặc bổ sung nguồn rồi duyệt và tạo lại index.', 'field-hint'));
    for (const chunk of evidence) {
      const item = el('article', '', 'pipeline-evidence-card');
      item.append(el('strong', chunk.title || 'Đoạn nguồn đã duyệt'), el('blockquote', chunk.text));
      const locator = chunk.locator || {};
      const location = [locator.page != null ? `Trang ${locator.page}` : '', Number.isInteger(locator.char_start) ? `ký tự ${locator.char_start}–${locator.char_end}` : ''].filter(Boolean).join(' · ');
      item.append(el('small', `Mã trích dẫn: ${chunk.id}${location ? ' · ' + location : ''}`));
      try {
        const url = new URL(chunk.source_url);
        if (['http:', 'https:'].includes(url.protocol)) { const link = el('a', 'Mở bài nguồn ↗', 'text-link'); link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer'; item.append(link); }
      } catch { /* Uploaded files need not have a public URL. */ }
      output.append(item);
    }
    const download = el('button', 'Tải evidence JSON cho agent', 'button'); download.type = 'button';
    download.addEventListener('click', async () => {
      download.disabled = true;
      try {
        // Recheck withdrawal/expiry before a new handoff from an idle page.
        await api(`/api/pipeline/${job.id}/evidence`);
        const url = URL.createObjectURL(new Blob([JSON.stringify(bundle, null, 2)], {type:'application/json'}));
        const link = el('a'); link.href = url; link.download = 'human-mind-evidence.json'; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
      } catch (error) { output.replaceChildren(el('p', error.message, 'notice error')); }
      finally { download.disabled = false; }
    });
    const raw = el('details'), pre = el('pre', JSON.stringify(bundle, null, 2), 'pipeline-json'); raw.append(el('summary', 'Xem JSON và thông tin truy xuất'), pre);
    output.append(download, raw);
  };
  const savedEvidence = async (job, output, question) => {
    try {
      const result = await api(`/api/pipeline/${job.id}/evidence`);
      if (!active()) return;
      if (result.last_evidence) {
        if (!question.value) question.value = result.last_evidence.question;
        showEvidence(job, output, result.last_evidence.bundle);
        output.prepend(el('p', `Lần tra gần nhất: ${new Date(result.last_evidence.created_at).toLocaleString('vi-VN')} · ${result.last_evidence.question}`, 'field-hint'));
      }
    } catch (error) { if (active()) output.replaceChildren(el('p', error.message, 'notice error')); }
  };
  const load = async () => {
    if (!active()) return;
    if (loading) { reloadRequested = true; return; }
    loading = true; clearTimeout(timer);
    try {
      const [result, documentData] = await Promise.all([api('/api/pipeline'), api('/api/documents')]);
      if (!active()) return;
      running = result.jobs.some(job => job.status === 'running');
      refresh.textContent = running ? 'Đang tự cập nhật mỗi 3 giây · Cập nhật ngay' : 'Cập nhật trạng thái';
      if (selectedId === undefined) select(result.jobs[0]?.id || null);
      const visible = result.jobs.filter(job => job.id === selectedId);
      if (initializeForm) { if (visible[0] && !scope.value && !collection.value) prepare(visible[0]); initializeForm = false; }
      const older = result.jobs.filter(job => job.id !== selectedId);
      currentTitle.textContent = selectedId ? 'Phiên đang xem' : 'Phiên mới · chưa chạy';
      historyTitle.textContent = `Lịch sử · ${older.length} phiên khác`;
      const nextHistorySignature = JSON.stringify(older.map(job => [job.id, job.status, job.document_ids.length]));
      if (historySignature !== nextHistorySignature) {
        historySignature = nextHistorySignature; historyList.replaceChildren();
        for (const job of older) {
          const row = el('div', '', 'pipeline-history-row');
          row.append(el('strong', `${job.action === 'crawl' ? 'Crawl' : 'Index'} · ${job.collection}`), el('small', `${names[job.status] || job.status} · ${new Date(job.created_at).toLocaleString('vi-VN')} · ${job.id.slice(0, 8)}`));
          const open = el('button', `Mở phiên ${job.id.slice(0, 8)}`, 'button'); open.type = 'button';
          open.addEventListener('click', async () => { select(job.id); clearCard(); prepare(job); provider.value = job.provider || 'btc'; history.open = false; status.textContent = 'Đang xem lại phiên đã chọn. Bấm Bắt đầu crawl hoặc Tạo index sẽ tạo một phiên mới.'; await load(); currentTitle.scrollIntoView({behavior:'smooth',block:'start'}); });
          row.append(open); historyList.append(row);
        }
        if (!older.length) historyList.append(el('p', 'Chưa có phiên trước.', 'field-hint'));
      }
      if (!cards.size) jobs.replaceChildren();
      if (!visible.length) jobs.replaceChildren(el('p', selectedId ? 'Không tìm thấy phiên đã chọn. Mở một phiên trong Lịch sử hoặc tạo phiên mới.' : 'Chưa chạy phiên mới. Điền biểu mẫu bên trên để bắt đầu; kết quả sẽ xuất hiện tại đây.', 'notice'));
      for (const job of visible) {
        const previous = cards.get(job.id);
        const documents = documentData.documents.filter(doc => job.document_ids.includes(doc.id));
        const signature = JSON.stringify([job, documents.map(doc => [doc.id, doc.status, doc.revision])]);
        if (previous?.signature === signature) { if (previous.output) await savedEvidence(job, previous.output, previous.question); await showTrace(job, previous.panel); continue; }
        const card = el('article', '', 'panel credential-card');
        card.append(el('h3', `${job.action === 'crawl' ? 'Crawl' : 'Index'} · ${job.collection}`), el('p', `${names[job.status] || job.status} · ${new Date(job.created_at).toLocaleString('vi-VN')}`), el('p', job.scope));
        if (job.action === 'crawl') card.append(el('p', `${job.document_ids.length} tài liệu đã tiếp nhận từ phiên này.`, 'field-hint'));
        card.append(nextStep(job, documents));
        if (job.error) card.append(el('p', job.error, 'notice error'));
        for (const error of job.errors) card.append(el('p', error, 'notice error'));
        let output, question;
        if (job.status === 'ready') {
          card.append(el('p', `${job.manifest.chunk_count} đoạn · ${job.provider} · hiệu lực ${job.as_of}. Index sẽ được kiểm tra lại với quyết định duyệt khi truy vấn.`, 'field-hint'));
          question = el('input'); question.placeholder = 'Câu hỏi để lấy evidence'; question.maxLength = 8000; question.setAttribute('aria-label', 'Câu hỏi để lấy evidence');
          const ask = el('button', 'Lấy evidence', 'button primary'); ask.type = 'button'; output = el('section', '', 'pipeline-evidence'); output.setAttribute('aria-live', 'polite');
          ask.addEventListener('click', async () => {
            if (!question.value.trim()) { output.replaceChildren(el('p', 'Nhập câu hỏi trước khi lấy evidence.', 'notice error')); question.focus(); return; }
            ask.disabled = true; output.textContent = 'Đang truy hồi…';
            try { showEvidence(job, output, await api(`/api/pipeline/${job.id}/evidence`, {method:'POST',body:JSON.stringify({question:question.value})})); await showTrace(job, panel); }
            catch(error) { output.replaceChildren(el('p', error.message, 'notice error')); }
            finally { ask.disabled = false; }
          });
          card.append(question, ask, output);
        }
        const panel = el('section', '', 'pipeline-trace'); card.append(panel);
        if (previous) previous.card.replaceWith(card); else jobs.append(card);
        cards.set(job.id, {card, panel, signature, output, question});
        if (output) await savedEvidence(job, output, question);
        await showTrace(job, panel);
      }
    } catch(error) { if (active()) status.textContent = error.message; }
    finally { loading = false; if (active() && (running || reloadRequested)) timer = setTimeout(load, reloadRequested ? 0 : 3000); reloadRequested = false; }
  };
  const start = async action => {
    seeds.required = action === 'crawl' && mode.value === 'urls';
    if (!form.reportValidity()) return;
    crawl.disabled = build.disabled = fresh.disabled = true;
    try {
      const job = await api('/api/pipeline', {method:'POST', body:JSON.stringify({action, scope:scope.value, collection:collection.value, max_pages:Number(pages.value), max_depth:Number(depth.value), provider:provider.value, seed_urls:mode.value === 'urls' ? seeds.value.split(',').map(value => value.trim()).filter(Boolean) : []})});
      select(job.id); clearCard(); history.open = false;
      status.textContent = 'Đã bắt đầu. Trace tự cập nhật mỗi 3 giây khi phiên đang chạy. Có thể chuyển sang hàng chờ.'; await load();
      currentTitle.scrollIntoView({behavior:'smooth',block:'start'});
    } catch(error) { status.textContent = error.message; }
    finally { crawl.disabled = build.disabled = fresh.disabled = false; updateSourceMode(); }
  };
  form.addEventListener('submit', event => { event.preventDefault(); start('crawl'); }); build.addEventListener('click', () => start('build')); refresh.addEventListener('click', load);
  await load();
  if (options.preset) { provider.focus(); form.scrollIntoView({behavior:'smooth',block:'start'}); }
}
