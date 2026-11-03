import os
import pytest
from backend.app.services.pptx_service import pptx_service
from backend.app.services.diff_service import diff_service

def test_pptx_create():
    out_path = "samples/output/test_generated.pptx"
    pptx_service.create_presentation(
        output_path=out_path,
        title="Automated Test Deck",
        subtitle="Verification of Clean 16:9 Presentation"
    )
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 1000

def test_pptx_targeted_editing_preserves_layouts():
    src_path = "samples/input/sample_presentation.pptx"
    out_path = "samples/output/edited_presentation.pptx"

    replacements = {
        "Acme Strategic Transformation": "NextAstra AI Strategic Transformation",
        "Sarah Jenkins": "Alex Vance"
    }

    new_slides = [
        {
            "title": "Autonomous Systems Roadmap",
            "bullets": ["Agentic AI workflows active", "Format preservation guaranteed"]
        }
    ]

    diff_summary = pptx_service.edit_existing_pptx(
        source_path=src_path,
        output_path=out_path,
        replacements=replacements,
        new_slides=new_slides
    )

    assert os.path.exists(out_path)
    assert diff_summary["modified_shapes"] > 0
    assert diff_summary["added_slides"] == 1

    comp = diff_service.compare_pptx(src_path, out_path)
    assert comp["modified_slides"] > comp["original_slides"]
