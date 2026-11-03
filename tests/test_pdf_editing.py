import os
import pytest
import fitz
from backend.app.services.pdf_service import pdf_service
from backend.app.services.diff_service import diff_service

def test_pdf_create():
    out_path = "samples/output/test_generated.pdf"
    pdf_service.create_document(
        output_path=out_path,
        title="Automated Test PDF Report",
        subtitle="Verification of Clean ReportLab Layouts",
        sections=[{"heading": "Testing Section", "content": "Sample content testing PDF compilation."}]
    )
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 500

    doc = fitz.open(out_path)
    assert len(doc) >= 1
    assert "Automated Test PDF Report" in doc[0].get_text()
    doc.close()

def test_pdf_targeted_editing_preserves_formatting():
    src_path = "samples/input/sample_manual.pdf"
    out_path = "samples/output/edited_manual.pdf"

    replacements = {
        "This documentation outlines system requirements, network topology, and security standards": "Updated Overview: Enhanced enterprise document intelligence and autonomous multi-agent pipelines.",
        "support@acmeglobal.example.com": "operations@acmeglobal-ai.com"
    }

    additions = [
        {
            "heading": "4. Revised Autonomous Protocols (2026)",
            "content": "Strictly preserved original margins, typography, vector hierarchy, and headers across all pages."
        }
    ]

    diff_summary = pdf_service.edit_existing_pdf(
        source_path=src_path,
        output_path=out_path,
        replacements=replacements,
        section_additions=additions
    )

    assert os.path.exists(out_path)
    assert diff_summary["modified_elements"] > 0
    assert diff_summary["added_sections"] == 1

    # Verify that the generated file is a valid PDF
    doc = fitz.open(out_path)
    assert len(doc) >= 1
    text = doc[0].get_text()
    assert "operations@acmeglobal-ai.com" in text
    assert "Revised Autonomous Protocols" in text
    doc.close()

    # Run Diff Service comparison
    comp = diff_service.compare_pdf(src_path, out_path)
    assert comp["format"] == "PDF"
    assert comp["added_count"] > 0
    assert comp["preserved_count"] > 0
