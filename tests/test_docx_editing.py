import os
import pytest
from backend.app.services.docx_service import docx_service
from backend.app.services.diff_service import diff_service

def test_docx_create():
    out_path = "samples/output/test_generated.docx"
    docx_service.create_document(
        output_path=out_path,
        title="Automated Test Report",
        subtitle="Verification of Clean Layouts",
        sections=[{"heading": "Testing Section", "content": "Sample content testing."}]
    )
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 1000

def test_docx_targeted_editing_preserves_formatting():
    src_path = "samples/input/sample_report.docx"
    out_path = "samples/output/edited_report.docx"

    replacements = {
        "Acme Global Industries is a pioneer in enterprise automated intelligence": "NextAstra Industries is the premier provider of enterprise generative AI agents",
        "contact@acmeglobal.example.com": "contact@nextastra.example.com"
    }

    additions = [
        {
            "heading": "New Project Section",
            "content": "This project section was injected while preserving document margins and fonts."
        }
    ]

    diff_summary = docx_service.edit_existing_docx(
        source_path=src_path,
        output_path=out_path,
        replacements=replacements,
        section_additions=additions
    )

    assert os.path.exists(out_path)
    assert diff_summary["modified_runs"] > 0 or diff_summary["modified_paragraphs"] > 0
    assert diff_summary["added_sections"] == 1

    # Run Diff Service comparison
    comp = diff_service.compare_docx(src_path, out_path)
    assert comp["modified_paragraphs"] > comp["original_paragraphs"]
    assert comp["added_count"] > 0
    assert comp["preserved_count"] > 0
