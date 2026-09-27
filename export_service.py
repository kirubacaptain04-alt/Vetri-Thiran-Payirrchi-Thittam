import base64
import io
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Inches, Pt
from fpdf import FPDF

from ..utils.text import pdf_safe_text, sanitize_text, terms_list


def _logo_bytes(logo_data_url: str | None) -> bytes | None:
    if not logo_data_url or "," not in logo_data_url:
        return None
    try:
        _, encoded = logo_data_url.split(",", 1)
        return base64.b64decode(encoded)
    except Exception:
        return None


def format_docx(
    text: str,
    doc_type: str,
    terms: str = "",
    company_name: str = "LegalEase",
    footer_text: str = "",
    logo_data_url: str | None = None,
) -> bytes:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)

    logo = _logo_bytes(logo_data_url)
    if logo:
        try:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(io.BytesIO(logo), width=Inches(1.25))
        except Exception:
            pass

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run(sanitize_text(doc_type).upper())
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)

    brand = doc.add_paragraph()
    brand.alignment = WD_ALIGN_PARAGRAPH.CENTER
    br = brand.add_run(company_name)
    br.italic = True
    br.font.size = Pt(9)

    for line in sanitize_text(text).split("\n"):
        line = line.strip()
        if not line:
            continue

        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)

        if re.match(r"^\d+[\.\)]\s+", line) or (
            line.upper() == line and len(line) < 100
        ):
            run = p.add_run(line)
            run.bold = True
        else:
            p.add_run(line)

    parsed_terms = terms_list(terms)
    if parsed_terms:
        doc.add_heading("Key Terms", level=2)
        table = doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"
        table.rows[0].cells[0].text = "No."
        table.rows[0].cells[1].text = "Term"
        for index, term in enumerate(parsed_terms, start=1):
            cells = table.add_row().cells
            cells[0].text = str(index)
            cells[1].text = term

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run(
        footer_text
        or f"{company_name} — AI-assisted draft. Review before use."
    ).font.size = Pt(8)

    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()


class LegalEasePDF(FPDF):
    def __init__(self, company_name: str, footer_text: str):
        super().__init__()
        self.company_name = company_name
        self.footer_text = footer_text
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, pdf_safe_text(self.company_name), align="C")
        self.ln(8)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 7)
        self.cell(0, 8, pdf_safe_text(self.footer_text), align="C")


def format_pdf(
    text: str,
    doc_type: str,
    terms: str = "",
    company_name: str = "LegalEase",
    footer_text: str = "",
    logo_data_url: str | None = None,
) -> bytes:
    pdf = LegalEasePDF(
        company_name,
        footer_text or f"{company_name} — AI-assisted draft. Review before use.",
    )
    pdf.add_page()
    pdf.set_title(sanitize_text(doc_type))

    logo = _logo_bytes(logo_data_url)
    if logo:
        # FPDF image support is format-dependent. If it fails, continue without it.
        try:
            temp = io.BytesIO(logo)
            # fpdf2 accepts BytesIO in recent versions.
            pdf.image(temp, w=28, h=28, x=(210 - 28) / 2)
            pdf.ln(30)
        except Exception:
            pass

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 9, pdf_safe_text(doc_type.upper()), align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 10)
    for line in sanitize_text(text).split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue

        is_heading = bool(
            re.match(r"^\d+[\.\)]\s+", line)
            or (line.upper() == line and len(line) < 100)
        )
        pdf.set_font("Helvetica", "B" if is_heading else "", 11 if is_heading else 10)
        pdf.multi_cell(0, 6, pdf_safe_text(line))
        pdf.ln(1)

    parsed_terms = terms_list(terms)
    if parsed_terms:
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 7, "Key Terms")
        pdf.ln(8)
        pdf.set_font("Helvetica", "", 9)
        for index, term in enumerate(parsed_terms, start=1):
            pdf.multi_cell(0, 5, pdf_safe_text(f"{index}. {term}"))
            pdf.ln(1)

    return bytes(pdf.output(dest="S"))
