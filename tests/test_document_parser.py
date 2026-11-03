import os
import pytest
from backend.app.services.document_parser import document_parser

def test_parse_docx():
    path = "samples/input/sample_report.docx"
    assert os.path.exists(path)
    text, meta, chunks = document_parser.parse_document(path, "docx")
    assert "Acme Global Industries" in text
    assert meta["format"] == "DOCX"
    assert len(meta["headings"]) > 0
    assert len(meta["tables"]) > 0
    assert len(chunks) > 0

def test_parse_pptx():
    path = "samples/input/sample_presentation.pptx"
    assert os.path.exists(path)
    text, meta, chunks = document_parser.parse_document(path, "pptx")
    assert "Transformation" in text or "Executive Summary" in text
    assert meta["format"] == "PPTX"
    assert meta["slide_count"] >= 3
    assert len(chunks) >= 3

def test_parse_xlsx():
    path = "samples/input/sample_financials.xlsx"
    assert os.path.exists(path)
    text, meta, chunks = document_parser.parse_document(path, "xlsx")
    assert meta["format"] == "XLSX"
    assert meta["sheet_count"] >= 1
    sheet = meta["sheets"][0]
    assert sheet["formulas_count"] > 0
    assert len(chunks) > 0

def test_parse_pdf():
    path = "samples/input/sample_manual.pdf"
    assert os.path.exists(path)
    text, meta, chunks = document_parser.parse_document(path, "pdf")
    assert "PRODUCT SPECIFICATIONS" in text
    assert meta["format"] == "PDF"
    assert meta["page_count"] >= 1
    assert len(chunks) >= 1
