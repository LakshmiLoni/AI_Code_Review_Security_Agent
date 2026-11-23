"""Reports: PDF Report Generator.

Generates formal, professional A4 technical review reports in PDF format.
Adheres strictly to enterprise audit and compliance standards:
- All 6 required sections:
  1. Report Information
  2. Review Summary
  3. Security Findings (grouped Critical/High/Medium/Low)
  4. Code Quality Assessment
  5. Recommendations for Improvement (formatted table: Priority | Recommendation | Reason | Suggested Action)
  6. Final Review Summary
- Strictly NO submitted source code, NO corrected code dumps, NO code snippets, NO raw secrets.
- Full A4 page layout with headers, footers, and page numbers.
"""
import os
import datetime
from typing import Dict, Any, List
from config import Config
from .recommendation_formatter import RecommendationFormatter


class PDFReportGenerator:
    """Generates sanitized, formal A4 PDF review reports."""

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or Config.REPORTS_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, review_data: Dict[str, Any]) -> str:
        """Generate PDF report using ReportLab if installed, otherwise pure-Python generator."""
        review_id = review_data.get("review_id", "REV-UNKNOWN")
        filepath = os.path.join(self.output_dir, f"{review_id}.pdf")

        try:
            import reportlab
            return self._build_reportlab_pdf(filepath, review_data)
        except Exception:
            return self._build_pure_python_pdf(filepath, review_data)

    def _build_reportlab_pdf(self, filepath: str, review_data: Dict[str, Any]) -> str:
        """Build PDF using ReportLab Platypus."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfgen import canvas

        class NumberedCanvas(canvas.Canvas):
            """Canvas that performs a two-pass calculation of total page numbers."""
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._saved_page_states = []

            def showPage(self):
                self._saved_page_states.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                num_pages = len(self._saved_page_states)
                for state in self._saved_page_states:
                    self.__dict__.update(state)
                    self.draw_page_decorations(num_pages)
                    canvas.Canvas.showPage(self)
                canvas.Canvas.save(self)

            def draw_page_decorations(self, total_pages):
                self.saveState()
                self.setFont("Helvetica", 8)
                self.setFillColor(colors.HexColor("#718096"))
                # Running header
                self.drawString(40, 810, "AI Code Review & Security Analysis Agent — Technical Security Audit")
                self.setStrokeColor(colors.HexColor("#E2E8F0"))
                self.setLineWidth(0.5)
                self.line(40, 804, 555, 804)

                # Running footer
                self.line(40, 42, 555, 42)
                self.drawString(40, 30, "Confidential Technical Audit Report — Zero Code Disclosure Policy.")
                page_str = f"Page {self._pageNumber} of {total_pages}"
                self.drawRightString(555, 30, page_str)
                self.restoreState()

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=50,
            bottomMargin=50,
        )

        styles = getSampleStyleSheet()

        h1_style = ParagraphStyle(
            "DocH1",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#2D3748"),
            spaceAfter=4,
        )
        h2_style = ParagraphStyle(
            "DocH2",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#5F8670"),
            spaceBefore=10,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#2D3748"),
        )
        body_bold = ParagraphStyle(
            "DocBodyBold",
            parent=body_style,
            fontName="Helvetica-Bold",
        )
        table_hdr = ParagraphStyle(
            "TableHdr",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )
        table_cell = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#2D3748"),
        )

        elements = []
        filename = review_data.get("filename", "unknown_file")
        review_id = review_data.get("review_id", "REV-UNKNOWN")
        lang = str(review_data.get("detected_language", "Unknown")).capitalize()
        findings = review_data.get("findings", [])

        # =========================================================================
        # 1. REPORT INFORMATION
        # =========================================================================
        elements.append(Paragraph("Code Review & Security Analysis Report", h1_style))
        info_data = [
            [
                Paragraph("<b>Project:</b> AI Code Review & Security Agent", body_style),
                Paragraph(f"<b>Review ID:</b> {review_id}", body_style)
            ],
            [
                Paragraph(f"<b>Target File:</b> {filename}", body_style),
                Paragraph(f"<b>Language:</b> {lang}", body_style)
            ],
            [
                Paragraph(f"<b>Date Generated:</b> {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body_style),
                Paragraph("<b>Scope:</b> Static Analysis & OWASP Security Audit", body_style)
            ]
        ]
        info_table = Table(info_data, colWidths=[255, 260])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FDFBF7")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 8))

        # =========================================================================
        # 2. REVIEW SUMMARY
        # =========================================================================
        elements.append(Paragraph("2. Review Summary & Health Assessment", h2_style))
        elements.append(Paragraph(review_data.get("executive_summary", "Review completed successfully."), body_style))
        elements.append(Spacer(1, 4))

        summary_rows = [
            ["Metric", "Value", "Technical Assessment"],
            ["Pull Request Status", review_data.get("pr_status", "APPROVED"), "Merge Readiness Verdict"],
            ["Code Health Score", f"{review_data.get('health_score', 100)} / 100", f"Overall Grade {review_data.get('letter_grade', 'A')}"],
            ["Critical Security Vulnerabilities", str(review_data.get("critical_count", 0)), "Immediate Delivery Blocker"],
            ["High Severity Findings", str(review_data.get("high_count", 0)), "Must Remediate Before Production"],
            ["Medium Severity Findings", str(review_data.get("medium_count", 0)), "Security Review Recommended"],
            ["Low Severity / Quality Smells", str(review_data.get("low_count", 0)), "Maintainability Improvement"],
        ]
        sum_table = Table(summary_rows, colWidths=[160, 115, 240])
        sum_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5F8670")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAF9F6")]),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(sum_table)
        elements.append(Spacer(1, 8))

        # =========================================================================
        # 3. SECURITY FINDINGS (Grouped Critical, High, Medium, Low)
        # =========================================================================
        elements.append(Paragraph("3. Security Vulnerability Findings", h2_style))
        sec_findings = [f for f in findings if f.get("finding_type") == "SECURITY"]
        if not sec_findings:
            elements.append(Paragraph("No security vulnerabilities were identified in the analyzed code.", body_style))
        else:
            for sev_tier in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                tier_items = [f for f in sec_findings if str(f.get("severity", "")).upper() == sev_tier]
                if not tier_items:
                    continue

                badge_color = "#DC2626" if sev_tier == "CRITICAL" else ("#EA580C" if sev_tier == "HIGH" else ("#D97706" if sev_tier == "MEDIUM" else "#2563EB"))
                elements.append(Paragraph(f"<b><font color='{badge_color}'>[{sev_tier}] Findings ({len(tier_items)})</font></b>", body_style))

                for item in tier_items:
                    loc = f"Line {item.get('line_number', 1)} in {filename}"
                    item_text = (
                        f"• <b>{item.get('title')}</b> — <i>{item.get('category')}</i><br/>"
                        f"&nbsp;&nbsp;<b>Affected Location:</b> {loc}<br/>"
                        f"&nbsp;&nbsp;<b>Explanation:</b> {item.get('description')}<br/>"
                        f"&nbsp;&nbsp;<b>Potential Impact:</b> {item.get('risk_explanation')}<br/>"
                        f"&nbsp;&nbsp;<b>Remediation:</b> {item.get('remediation_recommendation')}"
                    )
                    elements.append(Paragraph(item_text, body_style))
                    elements.append(Spacer(1, 3))

        elements.append(Spacer(1, 6))

        # =========================================================================
        # 4. CODE QUALITY ASSESSMENT
        # =========================================================================
        elements.append(Paragraph("4. Code Quality & Maintainability Assessment", h2_style))
        qual_findings = [f for f in findings if f.get("finding_type") == "QUALITY"]
        if not qual_findings:
            elements.append(Paragraph("No significant code quality or maintainability issues identified.", body_style))
        else:
            for item in qual_findings:
                loc = f"Line {item.get('line_number', 1)} in {filename}"
                item_text = (
                    f"• <b>{item.get('title')}</b> [{item.get('severity')}] — {loc}<br/>"
                    f"&nbsp;&nbsp;<b>Observation:</b> {item.get('description')}<br/>"
                    f"&nbsp;&nbsp;<b>Maintainability Advice:</b> {item.get('remediation_recommendation')}"
                )
                elements.append(Paragraph(item_text, body_style))
                elements.append(Spacer(1, 2))

        elements.append(Spacer(1, 6))

        # =========================================================================
        # 5. RECOMMENDATIONS FOR IMPROVEMENT (TABLE)
        # =========================================================================
        elements.append(Paragraph("5. Recommendations for Improvement", h2_style))
        rec_rows = RecommendationFormatter.format_recommendations_table(findings)
        if not rec_rows:
            elements.append(Paragraph("No improvement recommendations recorded.", body_style))
        else:
            table_content = [
                [
                    Paragraph("Priority", table_hdr),
                    Paragraph("Recommendation", table_hdr),
                    Paragraph("Reason", table_hdr),
                    Paragraph("Suggested Action", table_hdr),
                ]
            ]
            for r in rec_rows:
                p_color = "#DC2626" if r["priority"] == "High" else ("#D97706" if r["priority"] == "Medium" else "#2563EB")
                table_content.append([
                    Paragraph(f"<b><font color='{p_color}'>{r['priority']}</font></b>", table_cell),
                    Paragraph(f"<b>{r['recommendation']}</b>", table_cell),
                    Paragraph(r["reason"], table_cell),
                    Paragraph(r["suggested_action"], table_cell),
                ])

            rec_table = Table(table_content, colWidths=[55, 140, 160, 160])
            rec_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2D3748")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FDFBF7")]),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elements.append(rec_table)

        elements.append(Spacer(1, 8))

        # =========================================================================
        # 6. FINAL REVIEW SUMMARY
        # =========================================================================
        elements.append(Paragraph("6. Final Review Summary & Technical Conclusion", h2_style))
        conclusion = (
            f"Static security and code quality analysis was completed for '{filename}' ({lang}). "
            f"The final review status has been designated as <b>{review_data.get('pr_status', 'APPROVED')}</b> "
            f"with a calculated Code Health Score of <b>{review_data.get('health_score', 100)}/100 (Grade {review_data.get('letter_grade', 'A')})</b>. "
            f"A total of {review_data.get('total_findings', len(findings))} findings were detected "
            f"({review_data.get('critical_count', 0)} Critical, {review_data.get('high_count', 0)} High). "
            f"Implementing the prioritized recommendations in Section 5 will elevate the security posture "
            f"and satisfy production release standards."
        )
        elements.append(Paragraph(conclusion, body_style))

        # Build document with running headers/footers
        doc.build(elements, canvasmaker=NumberedCanvas)
        return filepath

    def _build_pure_python_pdf(self, filepath: str, review_data: Dict[str, Any]) -> str:
        """Robust, pure-Python A4 PDF generator conforming to PDF-1.4 specification."""
        # Sanitize data
        filename = review_data.get("filename", "unknown_file")
        review_id = review_data.get("review_id", "REV-UNKNOWN")
        lang = str(review_data.get("detected_language", "Unknown")).capitalize()
        findings = review_data.get("findings", [])
        health = review_data.get("health_score", 100)
        grade = review_data.get("letter_grade", "A")
        pr_status = review_data.get("pr_status", "APPROVED")

        crit_count = review_data.get("critical_count", 0)
        high_count = review_data.get("high_count", 0)
        med_count = review_data.get("medium_count", 0)
        low_count = review_data.get("low_count", 0)

        rec_rows = RecommendationFormatter.format_recommendations_table(findings)

        # Build textual flow lines for pagination
        flow_lines = []
        flow_lines.append(("HEADER", "AI Code Review & Security Analysis Agent"))
        flow_lines.append(("TITLE", "CODE REVIEW & SECURITY ANALYSIS REPORT"))
        flow_lines.append(("INFO", f"Review ID: {review_id}  |  File: {filename}  |  Language: {lang}"))
        flow_lines.append(("INFO", f"Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  |  PR Verdict: {pr_status}"))
        flow_lines.append(("LINE", ""))

        flow_lines.append(("H2", "1. Review Summary & Health Assessment"))
        flow_lines.append(("TEXT", f"Code Health Score: {health}/100 (Grade {grade})  |  Status: {pr_status}"))
        flow_lines.append(("TEXT", f"Findings Summary: {crit_count} Critical, {high_count} High, {med_count} Medium, {low_count} Low"))
        flow_lines.append(("TEXT", review_data.get("executive_summary", "Review complete.")))
        flow_lines.append(("LINE", ""))

        flow_lines.append(("H2", "2. Security Vulnerability Findings"))
        sec_findings = [f for f in findings if f.get("finding_type") == "SECURITY"]
        if not sec_findings:
            flow_lines.append(("TEXT", "No security vulnerabilities were identified in the source code."))
        else:
            for f in sec_findings:
                sev = f.get("severity", "LOW")
                loc = f"Line {f.get('line_number', 1)} in {filename}"
                flow_lines.append(("FINDING", f"[{sev}] {f.get('title')} — {loc}"))
                flow_lines.append(("SUBTEXT", f"Category: {f.get('category')}"))
                flow_lines.append(("SUBTEXT", f"Explanation: {f.get('description')}"))
                flow_lines.append(("SUBTEXT", f"Potential Impact: {f.get('risk_explanation')}"))
                flow_lines.append(("SUBTEXT", f"Remediation: {f.get('remediation_recommendation')}"))

        flow_lines.append(("LINE", ""))
        flow_lines.append(("H2", "3. Code Quality Assessment"))
        qual_findings = [f for f in findings if f.get("finding_type") == "QUALITY"]
        if not qual_findings:
            flow_lines.append(("TEXT", "No significant code quality or maintainability issues identified."))
        else:
            for f in qual_findings:
                loc = f"Line {f.get('line_number', 1)} in {filename}"
                flow_lines.append(("FINDING", f"[{f.get('severity')}] {f.get('title')} — {loc}"))
                flow_lines.append(("SUBTEXT", f"Observation: {f.get('description')}"))
                flow_lines.append(("SUBTEXT", f"Remediation: {f.get('remediation_recommendation')}"))

        flow_lines.append(("LINE", ""))
        flow_lines.append(("H2", "4. Recommendations for Improvement"))
        flow_lines.append(("REC_HEADER", "Priority | Recommendation | Reason | Suggested Action"))
        for r in rec_rows:
            flow_lines.append(("REC_ROW", f"[{r['priority']}] {r['recommendation']} : {r['reason']} -> {r['suggested_action']}"))

        flow_lines.append(("LINE", ""))
        flow_lines.append(("H2", "5. Final Review Summary"))
        flow_lines.append(("TEXT", f"Analysis concluded with status {pr_status} and {len(findings)} total findings."))
        flow_lines.append(("TEXT", "Report generated automatically by static analysis and heuristic evaluation models."))

        # Paginate flow_lines onto A4 pages
        # A4 height: 842 pt. Printable area ~ 720 pt. Lines per page ~ 45.
        lines_per_page = 42
        pages = []
        cur_page = []
        for item in flow_lines:
            cur_page.append(item)
            if len(cur_page) >= lines_per_page:
                pages.append(cur_page)
                cur_page = []
        if cur_page or not pages:
            pages.append(cur_page)

        total_pages = len(pages)

        # Generate standard PDF stream
        pdf_objs = []
        # obj 1: Catalog
        # obj 2: Outlines
        # obj 3: Pages
        # Then for each page: Page obj, Content stream obj

        page_obj_ids = []
        # Page objects start at obj 4. Each page has a page obj and a content stream obj.
        for idx in range(total_pages):
            p_obj_id = 4 + (idx * 2)
            page_obj_ids.append(p_obj_id)

        # Assemble PDF
        pdf_bytes = bytearray()
        pdf_bytes.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = {}

        def add_obj(obj_id, content_bytes):
            offsets[obj_id] = len(pdf_bytes)
            pdf_bytes.extend(f"{obj_id} 0 obj\n".encode("ascii"))
            pdf_bytes.extend(content_bytes)
            pdf_bytes.extend(b"\nendobj\n")

        # 1. Catalog
        add_obj(1, b"<< /Type /Catalog /Pages 3 0 R >>")
        # 2. Outlines
        add_obj(2, b"<< /Type /Outlines /Count 0 >>")
        # 3. Pages
        kids_str = " ".join([f"{pid} 0 R" for pid in page_obj_ids])
        add_obj(3, f"<< /Type /Pages /Kids [{kids_str}] /Count {total_pages} >>".encode("ascii"))

        # For each page, draw contents
        for idx, page_lines in enumerate(pages):
            page_num = idx + 1
            page_obj_id = 4 + (idx * 2)
            stream_obj_id = page_obj_id + 1

            # Build stream content
            stream_commands = []
            # Setup fonts and colors
            stream_commands.append("BT")
            # Running header
            stream_commands.append("/F1 8 Tf 0.44 0.50 0.58 rg")
            stream_commands.append("40 812 Td (AI Code Review & Security Analysis Agent - Technical Security Audit) Tj")
            stream_commands.append("ET")

            # Header line
            stream_commands.append("0.88 0.90 0.93 RG 0.5 w 40 806 m 555 806 l S")

            # Running footer
            stream_commands.append("0.88 0.90 0.93 RG 0.5 w 40 40 m 555 40 l S")
            stream_commands.append("BT")
            stream_commands.append("/F1 8 Tf 0.44 0.50 0.58 rg")
            stream_commands.append(f"40 28 Td (Confidential Technical Security Audit Report - Strict Zero-Code Privacy) Tj")
            stream_commands.append("ET")

            stream_commands.append("BT")
            stream_commands.append("/F1 8 Tf 0.44 0.50 0.58 rg")
            stream_commands.append(f"505 28 Td (Page {page_num} of {total_pages}) Tj")
            stream_commands.append("ET")

            # Main content text
            y = 785
            for kind, text in page_lines:
                # Sanitize text for PDF string literals
                safe_text = (
                    text.replace("\\", "\\\\")
                    .replace("(", "\\(")
                    .replace(")", "\\)")
                    .encode("ascii", "replace")
                    .decode("ascii")
                )
                if len(safe_text) > 105:
                    safe_text = safe_text[:102] + "..."

                if kind == "TITLE":
                    stream_commands.append(f"BT /F2 14 Tf 0.17 0.21 0.28 rg 40 {y} Td ({safe_text}) Tj ET")
                    y -= 18
                elif kind == "H2":
                    stream_commands.append(f"BT /F2 11 Tf 0.37 0.52 0.44 rg 40 {y} Td ({safe_text}) Tj ET")
                    y -= 15
                elif kind == "INFO":
                    stream_commands.append(f"BT /F2 8.5 Tf 0.25 0.30 0.38 rg 40 {y} Td ({safe_text}) Tj ET")
                    y -= 13
                elif kind == "FINDING":
                    stream_commands.append(f"BT /F2 8.5 Tf 0.17 0.21 0.28 rg 45 {y} Td ({safe_text}) Tj ET")
                    y -= 13
                elif kind == "SUBTEXT":
                    stream_commands.append(f"BT /F1 7.5 Tf 0.35 0.40 0.48 rg 55 {y} Td ({safe_text}) Tj ET")
                    y -= 11
                elif kind == "REC_HEADER":
                    stream_commands.append(f"BT /F2 8 Tf 0.17 0.21 0.28 rg 40 {y} Td ({safe_text}) Tj ET")
                    y -= 13
                elif kind == "REC_ROW":
                    stream_commands.append(f"BT /F1 7.5 Tf 0.25 0.30 0.38 rg 45 {y} Td ({safe_text}) Tj ET")
                    y -= 12
                elif kind == "LINE":
                    stream_commands.append(f"0.88 0.90 0.93 RG 0.5 w 40 {y} m 555 {y} l S")
                    y -= 10
                else:
                    stream_commands.append(f"BT /F1 8 Tf 0.25 0.30 0.38 rg 40 {y} Td ({safe_text}) Tj ET")
                    y -= 12

            content_stream = "\n".join(stream_commands).encode("ascii")

            # Write page obj
            page_dict = (
                f"<< /Type /Page /Parent 3 0 R "
                f"/MediaBox [0 0 595.28 841.89] "
                f"/Contents {stream_obj_id} 0 R "
                f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> "
                f"/F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> >> >> >>"
            ).encode("ascii")
            add_obj(page_obj_id, page_dict)

            # Write stream obj
            stream_dict = f"<< /Length {len(content_stream)} >>\nstream\n".encode("ascii") + content_stream + b"\nendstream"
            add_obj(stream_obj_id, stream_dict)

        # xref
        xref_offset = len(pdf_bytes)
        num_objects = len(offsets) + 1
        pdf_bytes.extend(f"xref\n0 {num_objects}\n0000000000 65535 f \n".encode("ascii"))
        for oid in range(1, num_objects):
            offset = offsets[oid]
            pdf_bytes.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

        # trailer
        trailer_str = f"trailer\n<< /Size {num_objects} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
        pdf_bytes.extend(trailer_str.encode("ascii"))

        with open(filepath, "wb") as f:
            f.write(pdf_bytes)

        # Cross copy to legacy directory if different
        if Config.LEGACY_REPORTS_DIR and os.path.abspath(Config.LEGACY_REPORTS_DIR) != os.path.abspath(self.output_dir):
            try:
                legacy_file = os.path.join(Config.LEGACY_REPORTS_DIR, f"{review_id}.pdf")
                with open(legacy_file, "wb") as lf:
                    lf.write(pdf_bytes)
            except Exception:
                pass

        return filepath
