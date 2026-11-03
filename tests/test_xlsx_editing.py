import os
import pytest
from backend.app.services.xlsx_service import xlsx_service
from backend.app.services.diff_service import diff_service

def test_xlsx_create():
    out_path = "samples/output/test_generated.xlsx"
    xlsx_service.create_workbook(
        output_path=out_path,
        title="Automated Test Financials"
    )
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 1000

def test_xlsx_targeted_editing_preserves_formulas():
    src_path = "samples/input/sample_financials.xlsx"
    out_path = "samples/output/edited_financials.xlsx"

    replacements = {
        "Acme Global": "NextAstra AI Global",
        "450000": "500000"
    }

    diff_summary = xlsx_service.edit_existing_xlsx(
        source_path=src_path,
        output_path=out_path,
        replacements=replacements
    )

    assert os.path.exists(out_path)
    assert diff_summary["modified_cells"] > 0
    assert diff_summary["preserved_formulas"] > 0

    comp = diff_service.compare_xlsx(src_path, out_path)
    assert comp["modified_cells_count"] > 0
    assert comp["formulas_preserved_count"] > 0
