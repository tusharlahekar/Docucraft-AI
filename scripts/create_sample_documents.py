import os
import fitz
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pptx import Presentation
from pptx.util import Inches as PptxInches, Pt as PptxPt
from pptx.dml.color import RGBColor as PptxRGBColor
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

os.makedirs("samples/input", exist_ok=True)
os.makedirs("samples/output", exist_ok=True)

# 1. Generate sample_report.docx
doc = Document()
for s in doc.sections:
    s.top_margin = Inches(1.0)
    s.bottom_margin = Inches(1.0)
    s.left_margin = Inches(1.0)
    s.right_margin = Inches(1.0)
    header = s.header.paragraphs[0]
    header.text = "Acme Global Industries | Annual Corporate Strategy"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT

title_p = doc.add_paragraph()
t_run = title_p.add_run("Acme Global Industries - Strategic Review")
t_run.font.name = "Calibri"
t_run.font.size = Pt(24)
t_run.font.bold = True
t_run.font.color.rgb = RGBColor(30, 64, 175)

h1 = doc.add_paragraph()
h1_run = h1.add_run("Company Introduction")
h1_run.font.name = "Calibri"
h1_run.font.size = Pt(16)
h1_run.font.bold = True
h1_run.font.color.rgb = RGBColor(30, 64, 175)

p1 = doc.add_paragraph()
r1 = p1.add_run("Acme Global Industries is a pioneer in enterprise automated intelligence, providing cutting-edge robotic process automation and AI copilots to Fortune 500 organizations worldwide.")
r1.font.name = "Calibri"
r1.font.size = Pt(11)

h2 = doc.add_paragraph()
h2_run = h2.add_run("Operational Milestones")
h2_run.font.name = "Calibri"
h2_run.font.size = Pt(16)
h2_run.font.bold = True
h2_run.font.color.rgb = RGBColor(30, 64, 175)

table = doc.add_table(rows=1, cols=3)
table.style = 'Table Grid'
hdr = table.rows[0].cells
hdr[0].text = "Division"
hdr[1].text = "Quarterly Target"
hdr[2].text = "Achievement Status"
for c in hdr:
    for run in c.paragraphs[0].runs:
        run.font.bold = True

data = [
    ("Autonomous Systems", "$4.5M ARR", "112% Achieved"),
    ("Document Intelligence", "$3.2M ARR", "108% Achieved"),
    ("Cloud Infrastructure", "$6.1M ARR", "97% On Track")
]
for row in data:
    r_cells = table.add_row().cells
    r_cells[0].text = row[0]
    r_cells[1].text = row[1]
    r_cells[2].text = row[2]

h3 = doc.add_paragraph()
h3.paragraph_format.space_before = Pt(14)
h3_run = h3.add_run("Contact Information")
h3_run.font.name = "Calibri"
h3_run.font.size = Pt(14)
h3_run.font.bold = True

p3 = doc.add_paragraph()
p3.add_run("Headquarters: 100 Innovation Way, Suite 400, Tech District.\nEmail: contact@acmeglobal.example.com | Phone: +1 (555) 019-2834")

docx_path = "samples/input/sample_report.docx"
doc.save(docx_path)
print(f"Created {docx_path}")

# 2. Generate sample_presentation.pptx
prs = Presentation()
prs.slide_width = PptxInches(13.333)
prs.slide_height = PptxInches(7.5)

slide1 = prs.slides.add_slide(prs.slide_layouts[0])
slide1.shapes.title.text = "Acme Strategic Transformation"
slide1.placeholders[1].text = "FY2025 Executive Overview & Roadmap"

slide2 = prs.slides.add_slide(prs.slide_layouts[1])
slide2.shapes.title.text = "Executive Summary"
tf = slide2.placeholders[1].text_frame
tf.text = "Strategic pillars driving 40% year-over-year expansion."
p = tf.add_paragraph()
p.text = "Deployment of LangGraph multi-agent cognitive architecture."
p = tf.add_paragraph()
p.text = "Universal format preservation across Word, PowerPoint, and Excel."

slide3 = prs.slides.add_slide(prs.slide_layouts[1])
slide3.shapes.title.text = "Contact Details"
tf3 = slide3.placeholders[1].text_frame
tf3.text = "Global Operations Liaison: Sarah Jenkins"
p = tf3.add_paragraph()
p.text = "Corporate Office: inquiry@acme-corp.example.com"

pptx_path = "samples/input/sample_presentation.pptx"
prs.save(pptx_path)
print(f"Created {pptx_path}")

# 3. Generate sample_financials.xlsx
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Financial Performance"

navy_fill = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid")
hdr_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
bold_font = Font(name="Calibri", size=11, bold=True)

ws["A1"] = "Acme Global - Financial Overview"
ws["A1"].font = Font(name="Calibri", size=16, bold=True, color="1E40AF")

headers = ["Department", "Q1 Budget", "Q2 Budget", "Q3 Budget", "Q4 Budget", "Annual Total"]
for col_num, h_title in enumerate(headers, 1):
    c = ws.cell(row=3, column=col_num, value=h_title)
    c.fill = navy_fill
    c.font = hdr_font
    c.alignment = Alignment(horizontal="center")

dept_data = [
    ("Research & Development", 450000, 480000, 520000, 560000),
    ("Sales & Marketing", 320000, 340000, 360000, 390000),
    ("Operations & Infrastructure", 210000, 220000, 230000, 240000),
    ("General & Administrative", 150000, 155000, 160000, 165000)
]

for r_idx, row in enumerate(dept_data, 4):
    ws.cell(row=r_idx, column=1, value=row[0])
    for c_idx in range(4):
        cell = ws.cell(row=r_idx, column=c_idx + 2, value=row[c_idx + 1])
        cell.number_format = '$#,##0'
    total_cell = ws.cell(row=r_idx, column=6, value=f"=SUM(B{r_idx}:E{r_idx})")
    total_cell.number_format = '$#,##0'
    total_cell.font = bold_font

tot_row = 8
ws.cell(row=tot_row, column=1, value="Company Wide Total").font = bold_font
for c_idx in range(2, 7):
    col_ltr = openpyxl.utils.get_column_letter(c_idx)
    tot_c = ws.cell(row=tot_row, column=c_idx, value=f"=SUM({col_ltr}4:{col_ltr}7)")
    tot_c.number_format = '$#,##0'
    tot_c.font = bold_font

xlsx_path = "samples/input/sample_financials.xlsx"
wb.save(xlsx_path)
print(f"Created {xlsx_path}")

# 4. Generate sample_manual.pdf
pdf_doc = fitz.open()
page = pdf_doc.new_page(width=595, height=842) # A4
text = (
    "ACME GLOBAL PRODUCT SPECIFICATIONS & USER MANUAL\n\n"
    "1. Overview\n"
    "This documentation outlines system requirements, network topology, and security standards for enterprise integration.\n\n"
    "2. Performance Benchmarks\n"
    "- Latency: < 20ms local semantic retrieval\n"
    "- Throughput: 150 document parsing threads per node\n"
    "- Redundancy: High availability persistent ChromaDB cluster\n\n"
    "3. Support Contact\n"
    "For inquiries, email support@acmeglobal.example.com"
)
page.insert_text((50, 72), text, fontsize=12)
pdf_path = "samples/input/sample_manual.pdf"
pdf_doc.save(pdf_path)
print(f"Created {pdf_path}")
