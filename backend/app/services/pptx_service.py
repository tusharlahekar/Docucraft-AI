import os
import logging
from typing import Dict, Any, List, Optional
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

logger = logging.getLogger(__name__)

class PptxService:
    """
    Enterprise PowerPoint generation and slide-master/layout-preserving editing service.
    """

    def create_presentation(
        self,
        output_path: str,
        title: str,
        subtitle: Optional[str] = None,
        slides_data: Optional[List[Dict[str, Any]]] = None,
        brand_color_rgb: tuple = (30, 64, 175)  # Executive Navy
    ) -> str:
        """
        Creates a high-impact professional PowerPoint presentation from scratch.
        """
        prs = pptx.Presentation()
        prs.slide_width = Inches(13.333)  # 16:9 widescreen
        prs.slide_height = Inches(7.5)

        # Slide 1: Title Slide
        title_slide_layout = prs.slide_layouts[0]
        slide1 = prs.slides.add_slide(title_slide_layout)
        title_shape = slide1.shapes.title
        subtitle_shape = slide1.placeholders[1] if len(slide1.placeholders) > 1 else None

        if title_shape:
            title_shape.text = title
            p = title_shape.text_frame.paragraphs[0]
            p.font.name = "Calibri"
            p.font.size = Pt(44)
            p.font.bold = True
            p.font.color.rgb = RGBColor(*brand_color_rgb)

        if subtitle_shape and subtitle:
            subtitle_shape.text = subtitle
            p2 = subtitle_shape.text_frame.paragraphs[0]
            p2.font.name = "Calibri"
            p2.font.size = Pt(22)
            p2.font.color.rgb = RGBColor(100, 116, 139)

        # Default slides if none provided
        if not slides_data:
            slides_data = [
                {
                    "title": "Executive Overview & Context",
                    "bullets": [
                        "Strategic vision for AI-driven transformation and automation.",
                        "Seamless document processing across DOCX, PPTX, and XLSX formats.",
                        "Preservation of institutional design systems and styling."
                    ]
                },
                {
                    "title": "Key Milestones & Deliverables",
                    "bullets": [
                        "Phase 1: Multi-Agent cognitive workflow engine deployment.",
                        "Phase 2: High-fidelity document generation & editing pipeline.",
                        "Phase 3: Real-time web intelligence and contextual RAG integration."
                    ]
                },
                {
                    "title": "Conclusion & Next Steps",
                    "bullets": [
                        "Validation of enterprise-grade security and performance.",
                        "Immediate availability for organizational adoption."
                    ]
                }
            ]

        bullet_slide_layout = prs.slide_layouts[1]
        for s_info in slides_data:
            slide = prs.slides.add_slide(bullet_slide_layout)
            t_shape = slide.shapes.title
            body_shape = slide.placeholders[1] if len(slide.placeholders) > 1 else None

            if t_shape:
                t_shape.text = s_info.get("title", "Key Insights")
                p = t_shape.text_frame.paragraphs[0]
                p.font.name = "Calibri"
                p.font.size = Pt(32)
                p.font.bold = True
                p.font.color.rgb = RGBColor(*brand_color_rgb)

            if body_shape:
                tf = body_shape.text_frame
                tf.word_wrap = True
                bullets = s_info.get("bullets", [])
                for idx, b_text in enumerate(bullets):
                    if idx == 0:
                        bp = tf.paragraphs[0]
                    else:
                        bp = tf.add_paragraph()
                    bp.text = b_text
                    bp.font.name = "Calibri"
                    bp.font.size = Pt(18)
                    bp.font.color.rgb = RGBColor(51, 65, 85)
                    bp.level = 0

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        prs.save(output_path)
        logger.info(f"Generated PPTX saved to {output_path}")
        return output_path

    def edit_existing_pptx(
        self,
        source_path: str,
        output_path: str,
        replacements: Optional[Dict[str, str]] = None,
        new_slides: Optional[List[Dict[str, Any]]] = None,
        instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Targeted editing of PowerPoint presentation while preserving layouts, themes,
        slide dimensions, shapes, positions, and formatting.
        Never overwrites source_path.
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source PPTX not found: {source_path}")

        prs = pptx.Presentation(source_path)

        diff_summary = {
            "source_file": os.path.basename(source_path),
            "output_file": os.path.basename(output_path),
            "modified_slides": 0,
            "modified_shapes": 0,
            "added_slides": 0,
            "changes_log": []
        }

        # 1. Targeted text replacement in shapes
        if replacements:
            for s_idx, slide in enumerate(prs.slides):
                slide_modified = False
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for p in shape.text_frame.paragraphs:
                            for r in p.runs:
                                for target, new_val in replacements.items():
                                    if target.lower() in r.text.lower():
                                        start_i = r.text.lower().find(target.lower())
                                        end_i = start_i + len(target)
                                        r.text = r.text[:start_i] + new_val + r.text[end_i:]
                                        slide_modified = True
                                        diff_summary["modified_shapes"] += 1
                                        diff_summary["changes_log"].append({
                                            "type": "shape_text_updated",
                                            "slide": s_idx + 1,
                                            "target": target,
                                            "replacement": new_val
                                        })
                if slide_modified:
                    diff_summary["modified_slides"] += 1

        # 2. Add new slides if requested using existing master slide layouts
        if new_slides:
            # Use standard content layout from existing presentation's master
            layout = prs.slide_layouts[1] if len(prs.slide_layouts) > 1 else prs.slide_layouts[0]
            for ns in new_slides:
                slide = prs.slides.add_slide(layout)
                diff_summary["added_slides"] += 1

                if slide.shapes.title:
                    slide.shapes.title.text = ns.get("title", "New Slide")

                if len(slide.placeholders) > 1:
                    tf = slide.placeholders[1].text_frame
                    bullets = ns.get("bullets", [])
                    for idx, b_text in enumerate(bullets):
                        if idx == 0:
                            p = tf.paragraphs[0]
                        else:
                            p = tf.add_paragraph()
                        p.text = b_text
                        p.level = 0

                diff_summary["changes_log"].append({
                    "type": "slide_added",
                    "title": ns.get("title"),
                    "details": "Added using original presentation master theme"
                })

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        prs.save(output_path)
        logger.info(f"Targeted PPTX edits saved to {output_path}")
        return diff_summary

pptx_service = PptxService()
