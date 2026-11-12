"""Module: Report Generator.

Generates comprehensive downloadable code review and security audit reports
in both PDF and JSON formats.
Includes Review ID, timestamp, health metrics, findings breakdown, remediation,
and pull request summaries.
"""
import os
import json
import datetime
from typing import Dict, Any, List
from config import Config


class ReportGenerator:
    """Generates downloadable PDF and JSON code review reports."""

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or Config.REPORTS_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_json_report(self, review_data: Dict[str, Any]) -> str:
        """Generate structured JSON report file."""
        review_id = review_data.get("review_id", "REV-EXPORT")
        filepath = os.path.join(self.output_dir, f"{review_id}.json")

        export_payload = {
            "metadata": {
                "system": "AI Code Review & Security Analysis Agent",
                "version": "1.0.0",
                "review_id": review_id,
                "exported_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "filename": review_data.get("filename", "unknown"),
                "detected_language": review_data.get("detected_language", "unknown"),
            },
            "summary": {
                "health_score": review_data.get("health_score", 100.0),
                "letter_grade": review_data.get("letter_grade", "A"),
                "pr_status": review_data.get("pr_status", "APPROVED"),
                "executive_summary": review_data.get("executive_summary", ""),
                "counts": {
                    "total": review_data.get("total_findings", 0),
                    "critical": review_data.get("critical_count", 0),
                    "high": review_data.get("high_count", 0),
                    "medium": review_data.get("medium_count", 0),
                    "low": review_data.get("low_count", 0),
                },
            },
            "findings": review_data.get("findings", []),
            "remediation_roadmap": review_data.get("roadmap", []),
            "disclaimer": (
                "This report was generated automatically by static analysis and heuristic models. "
                "Scores and findings are analytical indicators and not official security certifications."
            ),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_payload, f, indent=2)

        return filepath

    def generate_pdf_report(self, review_data: Dict[str, Any]) -> str:
        """Generate PDF report using ReportLab if available, or pure-Python PDF writer."""
        review_id = review_data.get("review_id", "REV-EXPORT")
        filepath = os.path.join(self.output_dir, f"{review_id}.pdf")

        try:
            return self._build_reportlab_pdf(filepath, review_data)
        except Exception:
            return self._build_fallback_pdf(filepath, review_data)

    def _build_reportlab_pdf(self, filepath: str, review_data: Dict[str, Any]) -> str:
        """Build professional multi-page PDF document using ReportLab."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceAfter=15,
        )
        h2_style = ParagraphStyle(
            "DocH2",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )
        code_style = ParagraphStyle(
            "DocCode",
            parent=styles["Code"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0f172a"),
            backColor=colors.HexColor("#f1f5f9"),
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("AI Code Review & Security Analysis Report", title_style))
        sub_text = (
            f"Review ID: <b>{review_data.get('review_id')}</b> | "
            f"File: <b>{review_data.get('filename')}</b> | "
            f"Language: <b>{str(review_data.get('detected_language')).capitalize()}</b> | "
            f"Date: <b>{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</b>"
        )
        elements.append(Paragraph(sub_text, subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#ea580c"), spaceAfter=12))

        # 2. Executive Summary & Health Score Table
        elements.append(Paragraph("Executive Summary & Risk Assessment", h2_style))
        elements.append(Paragraph(review_data.get("executive_summary", "No summary available."), body_style))
        elements.append(Spacer(1, 8))

        # Score Summary Table
        score_data = [
            ["Metric", "Value", "Assessment"],
            ["Code Health Score", f"{review_data.get('health_score', 100)}/100", f"Grade {review_data.get('letter_grade', 'A')}"],
            ["Pull Request Status", review_data.get("pr_status", "APPROVED"), "Merge Readiness Verdict"],
            ["Critical Findings", str(review_data.get("critical_count", 0)), "Immediate Blocker"],
            ["High Findings", str(review_data.get("high_count", 0)), "Action Required"],
            ["Medium Findings", str(review_data.get("medium_count", 0)), "Review Recommended"],
            ["Low / Quality Smells", str(review_data.get("low_count", 0)), "Maintainability Advice"],
        ]
        t = Table(score_data, colWidths=[150, 100, 250])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 14))

        # 3. Detailed Findings List
        elements.append(Paragraph("Detailed Security & Code Quality Findings", h2_style))
        findings = review_data.get("findings", [])
        if not findings:
            elements.append(Paragraph("No vulnerabilities or code quality smells were identified.", body_style))
        else:
            for i, f in enumerate(findings[:15], 1):
                sev = f.get("severity", "LOW")
                sev_color = "#dc2626" if sev == "CRITICAL" else ("#ea580c" if sev == "HIGH" else ("#ca8a04" if sev == "MEDIUM" else "#2563eb"))
                header_text = f"<b>{i}. [{sev}] {f.get('title')}</b> (Line {f.get('line_number')}) - <i>{f.get('category')}</i>"
                elements.append(Paragraph(header_text, body_style))

                desc_text = f"<b>Description:</b> {f.get('description')}<br/><b>Remediation:</b> {f.get('remediation_recommendation')}"
                elements.append(Paragraph(desc_text, body_style))

                if f.get("evidence_snippet"):
                    elements.append(Spacer(1, 3))
                    elements.append(Paragraph(f"<b>Evidence:</b> <font face='Courier'>{f.get('evidence_snippet')[:140]}</font>", code_style))

                if f.get("corrected_code"):
                    elements.append(Spacer(1, 3))
                    elements.append(Paragraph(f"<b>Suggested Fix:</b> <font face='Courier'>{f.get('corrected_code')[:160]}</font>", code_style))

                elements.append(Spacer(1, 8))

        # 4. Footer Note
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
        elements.append(Paragraph(
            "Notice: This report is generated by an automated static analysis and heuristic system. "
            "CVSS-inspired metrics are internal scoring heuristics and not official security certifications.",
            subtitle_style
        ))

        doc.build(elements)
        return filepath

    def _build_fallback_pdf(self, filepath: str, review_data: Dict[str, Any]) -> str:
        """Pure-Python standard PDF 1.4 file writer that generates valid readable PDF without dependencies."""
        review_id = review_data.get("review_id", "REV-EXPORT")
        filename = review_data.get("filename", "unknown")
        language = review_data.get("detected_language", "unknown")
        score = review_data.get("health_score", 100.0)
        grade = review_data.get("letter_grade", "A")
        pr_status = review_data.get("pr_status", "APPROVED")
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        # Prepare readable lines
        lines = [
            "AI CODE REVIEW & SECURITY ANALYSIS REPORT",
            "===========================================================",
            f"Review ID        : {review_id}",
            f"Source File      : {filename}",
            f"Language         : {language.upper()}",
            f"Generation Date  : {timestamp}",
            f"Code Health Score: {score}/100 (Grade {grade})",
            f"Pull Request Verdict: {pr_status}",
            "-----------------------------------------------------------",
            "EXECUTIVE SUMMARY:",
            review_data.get("executive_summary", "Review complete."),
            "-----------------------------------------------------------",
            f"Total Findings: {review_data.get('total_findings', 0)} "
            f"(Critical: {review_data.get('critical_count', 0)}, "
            f"High: {review_data.get('high_count', 0)}, "
            f"Medium: {review_data.get('medium_count', 0)}, "
            f"Low: {review_data.get('low_count', 0)})",
            "===========================================================",
            "DETAILED FINDINGS:",
        ]

        for i, f in enumerate(review_data.get("findings", [])[:10], start=1):
            lines.append(f"{i}. [{f.get('severity')}] Line {f.get('line_number')}: {f.get('title')}")
            lines.append(f"   Category: {f.get('category')}")
            lines.append(f"   Remediation: {f.get('remediation_recommendation')}")
            lines.append("")

        lines.append("-----------------------------------------------------------")
        lines.append("Generated by AI Code Review & Security Analysis Agent")

        # Encode text as PDF stream operators
        stream_content = "BT\n/F1 10 Tf\n40 750 Td\n13 TL\n"
        for l in lines:
            safe_l = l.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            stream_content += f"({safe_l}) '\n"
        stream_content += "ET\n"

        stream_bytes = stream_content.encode("latin-1", errors="replace")

        # Standard minimal PDF 1.4 structure
        pdf_objs = []
        pdf_objs.append(b"%PDF-1.4\n")
        pdf_objs.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        pdf_objs.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
        pdf_objs.append(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n")
        pdf_objs.append(f"4 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode("latin-1") + stream_bytes + b"\nendstream\nendobj\n")
        pdf_objs.append(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

        # Compute xref table
        xref = ["xref\n0 6\n0000000000 65535 f \n"]
        offset = len(pdf_objs[0])
        for obj in pdf_objs[1:]:
            xref.append(f"{offset:010d} 00000 n \n")
            offset += len(obj)

        trailer = f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{offset}\n%%EOF\n"

        with open(filepath, "wb") as f:
            for obj in pdf_objs:
                f.write(obj)
            for x in xref:
                f.write(x.encode("latin-1"))
            f.write(trailer.encode("latin-1"))

        return filepath
