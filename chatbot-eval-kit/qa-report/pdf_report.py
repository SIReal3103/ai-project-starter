"""Readable print layout for the same QA data as the standalone HTML."""
from pathlib import Path
import re
from html import escape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Flowable
from render import GROUPS, STATUSES, summarize, metric_status

ROOT = Path(__file__).resolve().parent
INK = colors.HexColor('#1d1d1f')
MUTED = colors.HexColor('#626267')
LINE = colors.HexColor('#dedee3')
PAPER = colors.HexColor('#f5f5f7')
BLUE = colors.HexColor('#0066cc')
STATUS_COLOR = {'pass': '#176a3a', 'fail': '#b02936', 'not_run': '#626267', 'blocked': '#835500', 'na': '#626267'}
ST = {}
WIDTH = 511


def setup_fonts():
    for name, file in [('QA', 'DejaVuSans.ttf'), ('QA-Bold', 'DejaVuSans-Bold.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(ROOT/'fonts'/file)))
    base = ParagraphStyle('body', fontName='QA', fontSize=9.5, leading=13, textColor=INK, spaceAfter=6)
    ST.update(body=base,
        title=ParagraphStyle('title', parent=base, fontName='QA-Bold', fontSize=29, leading=34, spaceAfter=15),
        h2=ParagraphStyle('h2', parent=base, fontName='QA-Bold', fontSize=20, leading=26, spaceAfter=16),
        h3=ParagraphStyle('h3', parent=base, fontName='QA-Bold', fontSize=12, leading=16, spaceAfter=7),
        small=ParagraphStyle('small', parent=base, fontSize=8.5, leading=11, textColor=MUTED, spaceAfter=4),
        label=ParagraphStyle('label', parent=base, fontName='QA-Bold', fontSize=8, leading=10, textColor=MUTED, spaceAfter=3),
        cell=ParagraphStyle('cell', parent=base, fontSize=8.5, leading=11.5, spaceAfter=2))


def p(text, style='body'):
    return Paragraph(escape(str(text or 'Chưa ghi nhận')).replace('\n', '<br/>'), ST[style])


def labeled(label, value, style='body'):
    return [p(label.upper(), 'label'), p(value, style)]


def table(headers, rows, widths):
    values = [[p(v, 'label') for v in headers]] + [[p(v, 'cell') for v in row] for row in rows]
    t = Table(values, colWidths=widths, hAlign='LEFT', repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), PAPER), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LINEBELOW', (0, 0), (-1, 0), .5, LINE), ('LINEBELOW', (0, 1), (-1, -1), .35, LINE), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6), ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10)]))
    return t


class Coverage(Flowable):
    def __init__(self, cases):
        super().__init__()
        self.rows = [(group, [c for c in cases if c['group'] == group]) for group in GROUPS]
        self.rows = [(g, rows) for g, rows in self.rows if rows]
        self.width = WIDTH
        self.height = len(self.rows)*34+20

    def draw(self):
        palette = {'pass':'#238349','fail':'#bf3d49','blocked':'#aa761d','not_run':'#d2d2d7','na':'#efeff2'}
        from collections import Counter
        y = self.height-15
        for group, rows in self.rows:
            counts = Counter(c['status'] for c in rows)
            self.canv.setFont('QA-Bold', 9); self.canv.setFillColor(INK)
            self.canv.drawString(0, y, GROUPS[group])
            x = 163
            for status in STATUSES:
                w = 230*counts[status]/len(rows)
                self.canv.setFillColor(colors.HexColor(palette[status]))
                self.canv.rect(x, y-2, w, 10, fill=1, stroke=0); x += w
            self.canv.setFillColor(MUTED);self.canv.setFont('QA', 7.5)
            self.canv.drawRightString(WIDTH, y, f"{counts['pass']} đạt / {counts['fail']} chưa đạt")
            self.canv.drawString(163, y-14, f"{counts['not_run']} chưa chạy · {counts['blocked']} bị chặn · {counts['na']} không áp dụng")
            y -= 34


def footer(c, doc):
    c.saveState(); c.setFillColor(INK); c.setFont('QA-Bold', 8)
    c.drawString(42, 808, 'QA / AI ACCEPTANCE')
    c.setStrokeColor(LINE); c.line(42, 797, 553, 797)
    c.setFillColor(MUTED); c.setFont('QA', 7)
    c.drawString(42, 25, 'Đề xuất QA không thay cho phê duyệt của chủ sản phẩm.')
    c.drawRightString(553, 25, str(doc.page));c.restoreState()


def render_pdf(data, output, all_cases=False):
    setup_fonts()
    doc = SimpleDocTemplate(str(output), pagesize=(595.28,841.89), leftMargin=42,rightMargin=42,topMargin=61,bottomMargin=48,title=data['product']['name']+' - Nghiệm thu QA',author='QA Report')
    story=[]; product=data['product']; decision=data['decision']; summary=summarize(data['cases'])
    story += [p('MẪU CHƯA CHẠY' if data['mode']=='template' else 'BẰNG CHỨNG TỪ LƯỢT ĐÃ LƯU', 'label'), p(product['name'], 'title'),p('Báo cáo nghiệm thu QA.', 'h2'),p(('Bản chi tiết đầy đủ.' if all_cases else 'Bản tổng hợp: chỉ mục tất cả ca, toàn bộ chỉ số và phiếu đại diện theo phạm vi. Toàn bộ phiếu nằm trong HTML/JSON đi kèm; dùng --all-cases để xuất PDF đầy đủ.'),'small'),p(product['scope'])]
    story += [p('Phiên bản: '+(product['version'] or 'Chưa điền')+' · Môi trường: '+(product['environment'] or 'Chưa điền')+' · Ngày kiểm: '+(product['run_date'] or 'Chưa điền'), 'small'),Spacer(1,12)]
    story += labeled('Đề xuất QA',decision['recommendation'],'h3')+ [p(decision['rationale']), p('Phê duyệt: '+(decision['approved_by'] or 'Chưa xác nhận')+' · '+(decision['approved_at'] or 'Chưa có ngày phê duyệt'),'small')]
    story += [Spacer(1,12),table(['Đã chạy','Đạt','Chưa đạt','Chưa có kết quả'],[[f"{summary['executed']}/{summary['planned']}",str(summary['passed']),str(summary['failed']),str(summary['pending'])]],[127.75]*4),Spacer(1,20),p('Phạm vi đã có bằng chứng','h3'),Coverage(data['cases']),p('Tỷ lệ chạy và số ca đạt là hai thông tin khác nhau. Biểu đồ không gộp điểm sản phẩm, LLM và agent thành một điểm chất lượng.','small')]
    story += [PageBreak(),p('01 / Điều kiện nghiệm thu','h2'),p('Đánh giá từng yêu cầu bắt buộc. Điểm trung bình tốt không bù cho lỗi chặn phát hành.','small')]
    for g in data['gates']:
        story.append(KeepTogether([p(g['id']+' · '+g['name'],'h3'),p(STATUSES[g['status']]+' · '+('Điều kiện đã thống nhất' if g['threshold_approved'] else 'Ngưỡng đề xuất, chưa phê duyệt'),'label'),p(g['rule']),p('Bằng chứng: '+(g['evidence'] or 'Chưa có'),'small'),Spacer(1,14)]))
    story += [PageBreak(),p('02 / Đánh giá LLM và agent','h2'),p('Đo điều gì, chấm như thế nào và cần bằng chứng nào để kết luận? Các ngưỡng đề xuất chưa được coi là điều kiện nghiệm thu đã thống nhất.','small')]
    for m in data['metrics']:
        block=[p(GROUPS[m['group']]+' / '+m['name'],'h3'),p(m['question']),p(str(m['value']) if m['value'] is not None else 'Chưa đo','h3'),p(metric_status(m)+' · Mẫu: '+str(m['sample_size'] if m['sample_size'] is not None else 'chưa có'),'label')]
        block += labeled('Đo điều gì?',m['definition']) + labeled('Cách chấm',m['method'],'small')
        block += labeled('Điều kiện đạt',m['threshold'],'small')+[p('Ngưỡng đã thống nhất.' if m['threshold_approved'] else 'Ngưỡng đề xuất; cần xác nhận trước lượt nghiệm thu.','small')]
        block += labeled('Kết quả có ý nghĩa gì?',m['interpretation'],'small')+labeled('Bằng chứng / giới hạn',(m['evidence'] or 'Chưa có bằng chứng.')+'\n'+m['limitation'],'small')+[Spacer(1,16)]
        story.append(KeepTogether(block))
    story += [PageBreak(),p('03 / Danh sách kiểm thử','h2'),p('Tất cả ca và trạng thái của lượt này. Đây là chỉ mục; bước thực hiện, mong đợi/thực tế và kiểm tra con đầy đủ có trong HTML và JSON đi kèm.','small')]
    story += [table(['Mã ca','Tình huống','Phạm vi','Kết quả'],[[c['id'],c['title'],GROUPS[c['group']],STATUSES[c['status']]] for c in data['cases']],[44,285,105,77])]
    if all_cases:
        selected = data['cases']
    else:
        selected = []
        for group in GROUPS:
            rows = [c for c in data['cases'] if c['group'] == group]
            if rows:
                # Illustrate a failure when available; all other outcomes remain in the index.
                selected.append(next((c for c in rows if c['status'] == 'fail'), rows[0]))
    detail_note = 'Mọi phiếu chi tiết của lượt này.' if all_cases else f"{len(selected)} phiếu đại diện, tối đa một phiếu mỗi phạm vi; ưu tiên ca chưa đạt nếu có. Đây không phải toàn bộ chi tiết {len(data['cases'])} ca. Mở HTML/JSON để xem đầy đủ hoặc xuất PDF với --all-cases. Các trạng thái đều đã được liệt kê ở chỉ mục."
    story += [PageBreak(),p('04 / Phiếu QA chi tiết','h2'),p(detail_note,'small')]
    for c in selected:
        block=[p(c['id']+' / '+c['title'],'h3'),p(GROUPS[c['group']]+' · '+c['priority']+' · '+STATUSES[c['status']],'label'),p('Dữ liệu: '+c['data_type'],'small')]
        block+=labeled('Yêu cầu cần nghiệm thu',c['requirement'],'small')
        block+=labeled('Điều kiện trước khi kiểm','\n'.join('• '+x for x in c['preconditions']),'small')
        block+=labeled('Các bước thực hiện','\n'.join(str(i)+'. '+re.sub(r'^\s*\d+[a-zA-Z]?[.)]\s*', '', x) for i,x in enumerate(c['steps'],1)),'small')
        block+=labeled('Đầu vào / yêu cầu',c['input'] or 'Không cần nhập thêm.','small')
        block += [table(['Mong đợi','Thực tế'],[[c['expected'],c['actual'] or 'Chưa chạy. Điền kết quả quan sát được.']],[255.5,255.5]),Spacer(1,9)]
        if c['checks']:
            block += [table(['Tiêu chí','Mong đợi / Thực tế','Kết luận'],[[x['criterion'],'Cần: '+x['expected']+'\nCó: '+(x['actual'] or 'Chưa ghi nhận'),STATUSES[x['status']]] for x in c['checks']],[119,317,75]),Spacer(1,10)]
        block+=labeled('Bằng chứng','\n'.join(c['evidence']) or 'Chưa có bằng chứng thực thi.','small')
        if c['defect'] or c['follow_up']:
            block+=labeled('Việc cần xử lý',(c['defect']+'\n'+c['follow_up']).strip(),'small')
        block+=labeled('Kiểm lại sau sửa',c['retest'] or 'Chưa kiểm lại.','small')+[Spacer(1,22)]
        # Keep a case together when it fits; ReportLab may split oversized cases safely.
        story.append(KeepTogether(block))
    story += [PageBreak(),p('05 / Lỗi và việc cần hoàn tất','h2')]
    if not data['defects']:
        story.append(p('Chưa ghi nhận lỗi. Với bộ ca chưa chạy, điều này không chứng minh sản phẩm không có lỗi.'))
    for x in data['defects']:
        block=[p(x['id']+' / '+x['title'],'h3'),p(x['severity']+' · '+x['status']+' · '+', '.join(x['case_ids']),'label'),p(x['impact'])]
        for label,value in [('Tái hiện','\n'.join(f'{i}. {v}' for i,v in enumerate(x['reproduce'],1))),('Mong đợi',x['expected']),('Thực tế',x['actual']),('Cần sửa',x['fix']),('Điều kiện đóng lỗi',x['retest'])]:
            block+=labeled(label,value,'small')
        story.append(KeepTogether(block+[Spacer(1,18)]))
    story += [Spacer(1,14),p('Bối cảnh và giới hạn','h3')]
    for label,value in [('Nguồn dữ liệu',product['data_origin']),('Model',product['model']),('Dataset',product['dataset']),('Người phụ trách',product['owner'] or 'Chưa phân công')]:story+=labeled(label,value,'small')
    story += [p('• '+x,'small') for x in product['limitations']]
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
