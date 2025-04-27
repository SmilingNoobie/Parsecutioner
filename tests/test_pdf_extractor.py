import pytest
from src.pdf_extractor import extract_text_from_pdf

def test_extract_text(tmp_path):
    from fpdf import FPDF
    pdf_path = tmp_path / 'test.pdf'
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    pdf.cell(200, 10, txt='Hello', ln=1)
    pdf.output(str(pdf_path))
    text = extract_text_from_pdf(str(pdf_path))
    assert 'Hello' in text