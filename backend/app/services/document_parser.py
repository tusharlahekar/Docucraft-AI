import os
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import pptx
from pptx.enum.shapes import MSO_SHAPE_TYPE
import openpyxl
from openpyxl.utils import get_column_letter
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class DocumentParserService:
    """
    Comprehensive document understanding parser for DOCX, PPTX, XLSX, and PDF.
    Extracts deep structural layout, fonts, colors, tables, slides, worksheets,
    and metadata as structured JSON.
    """

    def parse_document(self, file_path: str, file_type: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parses a document file and returns:
        1. full_text: string representation of content
        2. metadata_summary: detailed structural JSON dictionary
        3. chunks: structured chunks ready for local vector storage
        """
        file_type = file_type.lower().strip(".")
        if file_type == "docx":
            return self._parse_docx(file_path)
        elif file_type == "pptx":
            return self._parse_pptx(file_path)
        elif file_type == "xlsx":
            return self._parse_xlsx(file_path)
        elif file_type == "pdf":
            return self._parse_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_type}")

    def _parse_docx(self, file_path: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        doc = docx.Document(file_path)
        full_text_parts = []
        chunks = []
        headings = []
        fonts = set()
        colors = set()
        tables_data = []
        sections_data = []

        # Sections & Margins
        for s_idx, section in enumerate(doc.sections):
            sections_data.append({
                "section_index": s_idx,
                "orientation": "landscape" if section.orientation == docx.enum.section.WD_ORIENT.LANDSCAPE else "portrait",
                "page_width_in": round(section.page_width.inches, 2) if section.page_width else None,
                "page_height_in": round(section.page_height.inches, 2) if section.page_height else None,
                "top_margin_in": round(section.top_margin.inches, 2) if section.top_margin else None,
                "bottom_margin_in": round(section.bottom_margin.inches, 2) if section.bottom_margin else None,
                "left_margin_in": round(section.left_margin.inches, 2) if section.left_margin else None,
                "right_margin_in": round(section.right_margin.inches, 2) if section.right_margin else None,
                "has_header": section.header is not None and len(section.header.paragraphs) > 0,
                "has_footer": section.footer is not None and len(section.footer.paragraphs) > 0
            })

        # Paragraphs & Runs
        current_heading = "Document Start"
        current_chunk_text = []

        for p_idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            style_name = para.style.name if para.style else "Normal"
            is_heading_run = any(r.bold and r.font.size and r.font.size.pt >= 13 for r in para.runs)

            if text.startswith("#") or "Heading" in style_name or "Title" in style_name or is_heading_run:
                headings.append({
                    "text": text,
                    "level": style_name if "Heading" in style_name else "Heading/Title",
                    "paragraph_index": p_idx
                })
                # Flush existing chunk if substantial
                if current_chunk_text:
                    c_text = " ".join(current_chunk_text)
                    chunks.append({
                        "text": c_text,
                        "metadata": {"section": current_heading, "type": "paragraph"}
                    })
                    current_chunk_text = []
                current_heading = text

            if text:
                full_text_parts.append(text)
                current_chunk_text.append(text)

            # Analyze runs for typography
            for run in para.runs:
                if run.font.name:
                    fonts.add(run.font.name)
                if run.font.color and run.font.color.rgb:
                    colors.add(f"#{run.font.color.rgb}")

        if current_chunk_text:
            chunks.append({
                "text": " ".join(current_chunk_text),
                "metadata": {"section": current_heading, "type": "paragraph"}
            })

        # Tables
        for t_idx, table in enumerate(doc.tables):
            rows_data = []
            for row in table.rows:
                row_vals = [cell.text.strip() for cell in row.cells]
                rows_data.append(row_vals)
            
            table_summary = {
                "table_index": t_idx,
                "row_count": len(table.rows),
                "col_count": len(table.columns) if table.columns else 0,
                "headers": rows_data[0] if rows_data else [],
                "sample_rows": rows_data[1:4] if len(rows_data) > 1 else []
            }
            tables_data.append(table_summary)
            
            # Add table text to chunks
            table_text = f"Table {t_idx + 1}: " + " | ".join([", ".join(r) for r in rows_data[:5]])
            full_text_parts.append(table_text)
            chunks.append({
                "text": table_text,
                "metadata": {"section": current_heading, "type": "table", "table_index": t_idx}
            })

        # Images count
        inline_shapes_count = len(doc.inline_shapes)

        metadata_summary = {
            "format": "DOCX",
            "paragraph_count": len(doc.paragraphs),
            "headings": headings,
            "fonts": list(fonts),
            "colors": list(colors),
            "tables": tables_data,
            "sections": sections_data,
            "images_count": inline_shapes_count
        }

        return "\n".join(full_text_parts), metadata_summary, chunks

    def _parse_pptx(self, file_path: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        prs = pptx.Presentation(file_path)
        full_text_parts = []
        chunks = []
        slides_data = []
        fonts = set()
        colors = set()

        slide_width_in = round(prs.slide_width.inches, 2)
        slide_height_in = round(prs.slide_height.inches, 2)

        for s_idx, slide in enumerate(prs.slides):
            slide_no = s_idx + 1
            slide_title = ""
            slide_texts = []
            shapes_info = []
            images_in_slide = 0
            tables_in_slide = 0

            for shape in slide.shapes:
                # Text shapes
                if shape.has_text_frame:
                    shape_text = shape.text_frame.text.strip()
                    if shape_text:
                        slide_texts.append(shape_text)
                        if not slide_title:
                            slide_title = shape_text.split("\n")[0]
                        # Typography
                        for p in shape.text_frame.paragraphs:
                            for r in p.runs:
                                if r.font.name:
                                    fonts.add(r.font.name)
                                if r.font.color and getattr(r.font.color, "rgb", None):
                                    colors.add(f"#{r.font.color.rgb}")

                # Shape geometry and type
                shape_type_name = str(shape.shape_type)
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    images_in_slide += 1
                elif shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                    tables_in_slide += 1

                shapes_info.append({
                    "name": shape.name,
                    "type": shape_type_name,
                    "left_in": round(shape.left.inches, 2) if shape.left else 0,
                    "top_in": round(shape.top.inches, 2) if shape.top else 0,
                    "width_in": round(shape.width.inches, 2) if shape.width else 0,
                    "height_in": round(shape.height.inches, 2) if shape.height else 0,
                })

            combined_slide_text = f"Slide {slide_no} [{slide_title}]: " + " ".join(slide_texts)
            full_text_parts.append(combined_slide_text)
            chunks.append({
                "text": combined_slide_text,
                "metadata": {
                    "slide_number": slide_no,
                    "slide_title": slide_title,
                    "type": "slide"
                }
            })

            slides_data.append({
                "slide_number": slide_no,
                "title": slide_title,
                "shape_count": len(slide.shapes),
                "images_count": images_in_slide,
                "tables_count": tables_in_slide,
                "shapes": shapes_info[:10]  # sample top 10 shapes
            })

        metadata_summary = {
            "format": "PPTX",
            "slide_count": len(prs.slides),
            "dimensions": {"width_in": slide_width_in, "height_in": slide_height_in},
            "slides": slides_data,
            "fonts": list(fonts),
            "colors": list(colors)
        }

        return "\n".join(full_text_parts), metadata_summary, chunks

    def _parse_xlsx(self, file_path: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        wb = openpyxl.load_workbook(file_path, data_only=False)
        full_text_parts = []
        chunks = []
        worksheets_data = []
        fonts = set()
        colors = set()

        for sheetname in wb.sheetnames:
            ws = wb[sheetname]
            rows_data = []
            formulas_count = 0
            merged_ranges = [str(r) for r in ws.merged_cells.ranges]

            # Inspect dimensions
            max_row = ws.max_row or 0
            max_col = ws.max_column or 0

            # Scan values and formulas up to first 100 rows for analysis
            scan_limit = min(max_row, 100)
            headers = []

            for r_idx in range(1, scan_limit + 1):
                row_vals = []
                for c_idx in range(1, max_col + 1):
                    cell = ws.cell(row=r_idx, column=c_idx)
                    val = str(cell.value) if cell.value is not None else ""
                    if str(cell.value).startswith("="):
                        formulas_count += 1

                    # Typography
                    if cell.font:
                        if cell.font.name:
                            fonts.add(cell.font.name)
                        if cell.font.color and getattr(cell.font.color, "rgb", None):
                            colors.add(f"#{cell.font.color.rgb}")

                    row_vals.append(val)

                if r_idx == 1:
                    headers = [v for v in row_vals if v]
                if any(row_vals):
                    rows_data.append(row_vals)

            sheet_text = f"Worksheet '{sheetname}' ({max_row} rows x {max_col} cols): " + \
                " | ".join([", ".join([c for c in r if c]) for r in rows_data[:10]])
            full_text_parts.append(sheet_text)

            chunks.append({
                "text": sheet_text,
                "metadata": {
                    "sheet_name": sheetname,
                    "rows": max_row,
                    "columns": max_col,
                    "type": "spreadsheet"
                }
            })

            worksheets_data.append({
                "name": sheetname,
                "total_rows": max_row,
                "total_cols": max_col,
                "headers": headers,
                "formulas_count": formulas_count,
                "merged_cells_count": len(merged_ranges),
                "merged_ranges": merged_ranges[:10]
            })

        metadata_summary = {
            "format": "XLSX",
            "sheet_count": len(wb.sheetnames),
            "sheets": worksheets_data,
            "fonts": list(fonts),
            "colors": list(colors)
        }

        return "\n".join(full_text_parts), metadata_summary, chunks

    def _parse_pdf(self, file_path: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        doc = fitz.open(file_path)
        full_text_parts = []
        chunks = []
        pages_data = []
        total_images = 0

        for p_idx, page in enumerate(doc):
            page_no = p_idx + 1
            text = page.get_text("text").strip()
            images = page.get_images(full=True)
            total_images += len(images)

            if text:
                full_text_parts.append(f"Page {page_no}:\n{text}")
                # Chunk every page
                chunks.append({
                    "text": text,
                    "metadata": {
                        "page_number": page_no,
                        "type": "pdf_page"
                    }
                })

            pages_data.append({
                "page_number": page_no,
                "width_pt": page.rect.width,
                "height_pt": page.rect.height,
                "images_count": len(images),
                "text_length": len(text)
            })

        metadata_summary = {
            "format": "PDF",
            "page_count": len(doc),
            "total_images": total_images,
            "pages": pages_data
        }

        return "\n".join(full_text_parts), metadata_summary, chunks

document_parser = DocumentParserService()
