from jinja2 import Template
from datetime import datetime
from typing import Dict
import os


class PDFGenerationService:
    """Service for generating PDF reports.

    ReportLab is used by default because it works on Windows without the
    native GTK/Pango libraries required by WeasyPrint. WeasyPrint remains
    optional and is only imported if explicitly enabled via USE_WEASYPRINT=1.
    """

    @staticmethod
    def generate_pdf(session_data: Dict, organ_scores: Dict, output_path: str) -> str:
        os.makedirs(output_path, exist_ok=True)
        pdf_filename = f"healthscan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(output_path, pdf_filename)
        html_content = PDFGenerationService._generate_html(session_data, organ_scores)

        # Never import WeasyPrint during application startup on Windows.
        if os.getenv("USE_WEASYPRINT", "0") == "1":
            try:
                from weasyprint import HTML
                HTML(string=html_content).write_pdf(pdf_path)
                return pdf_path
            except (ImportError, OSError):
                # Fall back automatically if GTK/Pango DLLs are unavailable.
                pass

        PDFGenerationService._generate_reportlab_pdf(session_data, organ_scores, pdf_path)
        return pdf_path

    @staticmethod
    def _generate_reportlab_pdf(session_data: Dict, organ_scores: Dict, pdf_path: str) -> None:
        """Generate a Windows-friendly PDF using ReportLab."""
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
        from xml.sax.saxutils import escape

        styles = getSampleStyleSheet()
        title = ParagraphStyle("SmartTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#1E88E5"))
        center = ParagraphStyle("Center", parent=styles["BodyText"], alignment=TA_CENTER)
        h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#1E88E5"))
        small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#666666"))

        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
        story = []
        overall_score = organ_scores.get("overall_health_score", 0)
        if overall_score >= 90:
            status = "Excellent Health"
        elif overall_score >= 70:
            status = "Good Health"
        elif overall_score >= 50:
            status = "Attention Needed"
        else:
            status = "Concerning"

        story += [Paragraph("SmartReports Health Analysis", title),
                  Paragraph("AI-Powered Pathology Report Analysis", center),
                  Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", center), Spacer(1, 16)]
        story += [Paragraph("Overall Health Summary", h2),
                  Paragraph(f"<b>{escape(str(overall_score))}/100</b>", center),
                  Paragraph(f"<b>{escape(status)}</b>", center),
                  Paragraph(f"Based on analysis of {len(session_data.get('lab_results', []))} lab tests across {len(organ_scores.get('organ_scores', []))} organ systems", center), Spacer(1, 14)]

        story.append(Paragraph("Lab Test Results", h2))
        rows = [["Test Name", "Value", "Unit", "Normal Range", "Status"]]
        for test in session_data.get("lab_results", []):
            mn, mx = test.get("normal_range_min"), test.get("normal_range_max")
            normal = f"{mn} - {mx}" if mn is not None and mx is not None else "N/A"
            rows.append([str(test.get("test_name", "")), str(test.get("value", "")), str(test.get("unit", "")), normal, str(test.get("status", ""))])
        table = Table(rows, repeatRows=1, colWidths=[5.0*cm, 2.2*cm, 2.0*cm, 3.2*cm, 2.2*cm])
        table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EAF2F8")), ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#1E88E5")), ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#DDDDDD")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("FONTSIZE", (0,0), (-1,-1), 8), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5)]))
        story += [table, Spacer(1, 14), Paragraph("Organ Health Analysis", h2)]

        for organ in organ_scores.get("organ_scores", []):
            related = organ.get("related_tests", [])
            related_text = "<br/>".join(f"• {escape(str(t.get('test_name','')))}: {escape(str(t.get('value','')))} {escape(str(t.get('unit','')))} - {escape(str(t.get('status','')))}" for t in related)
            content = [Paragraph(f"<b>{escape(str(organ.get('organ_name','')))}</b> — <b>{escape(str(organ.get('health_score',0)))}/100</b>", styles["Heading3"]), Paragraph(f"Status: {escape(str(organ.get('status','')))}", styles["BodyText"]), Paragraph(f"Tests Analyzed: {organ.get('test_count',0)} ({organ.get('abnormal_test_count',0)} abnormal)", styles["BodyText"])]
            if organ.get("description"):
                content.append(Paragraph(escape(str(organ["description"])), small))
            if related_text:
                content.append(Paragraph("<b>Related Tests:</b>", styles["BodyText"]))
                content.append(Paragraph(related_text, small))
            story += [KeepTogether(content), Spacer(1, 10)]

        story.append(Paragraph("Health Recommendations", h2))
        recs = organ_scores.get("recommendations", [])
        if recs:
            for rec in recs:
                story.append(Paragraph(f"<b>{escape(str(rec.get('organ_name','')))}:</b> {escape(str(rec.get('text','')))}", styles["BodyText"]))
                story.append(Paragraph(f"Category: {escape(str(rec.get('category','')).replace('_',' ').title())} | Priority: {escape(str(rec.get('severity','')).title())}", small))
                story.append(Spacer(1, 7))
        else:
            story.append(Paragraph("All your test results are within normal ranges. Maintain a healthy lifestyle!", styles["BodyText"]))

        story += [Spacer(1, 20), Paragraph("Disclaimer: This report is generated by AI and is for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult your physician or qualified healthcare provider with any questions about your health.", small), Paragraph("Generated by SmartReports - AI-Powered Health Analysis | © 2025", small)]
        doc.build(story)

    @staticmethod
    def _generate_html(session_data: Dict, organ_scores: Dict) -> str:
        """Generate the original HTML content for optional WeasyPrint use."""
        template_str = """<!DOCTYPE html><html><head><meta charset='UTF-8'><style>body{font-family:Arial;color:#333;line-height:1.6}@page{size:A4;margin:2cm}.header{text-align:center;border-bottom:3px solid #1E88E5;padding-bottom:20px;margin-bottom:30px}.header h1{color:#1E88E5}.section{margin-bottom:30px}table{width:100%;border-collapse:collapse}th,td{padding:10px;border-bottom:1px solid #E0E0E0;text-align:left}th{background:#f5f7fa}.footer{margin-top:40px;padding-top:20px;border-top:2px solid #E0E0E0;text-align:center;color:#666;font-size:12px}</style></head><body><div class='header'><h1>SmartReports Health Analysis</h1><p>AI-Powered Pathology Report Analysis</p><p>Generated on: {{ generation_date }}</p></div><div class='section'><h2>Overall Health Summary</h2><h1 style='text-align:center'>{{ overall_health_score }}/100</h1><p style='text-align:center'><strong>{{ overall_status }}</strong></p><p style='text-align:center'>Based on analysis of {{ total_tests }} lab tests across {{ total_organs }} organ systems</p></div><div class='section'><h2>Lab Test Results</h2><table><tr><th>Test Name</th><th>Value</th><th>Unit</th><th>Normal Range</th><th>Status</th></tr>{% for test in lab_results %}<tr><td>{{ test.test_name }}</td><td>{{ test.value }}</td><td>{{ test.unit }}</td><td>{{ test.normal_range_min }} - {{ test.normal_range_max }}</td><td>{{ test.status }}</td></tr>{% endfor %}</table></div><div class='section'><h2>Organ Health Analysis</h2>{% for organ in organ_scores %}<h3>{{ organ.organ_name }} — {{ organ.health_score }}/100</h3><p>Status: {{ organ.status }}</p><p>Tests Analyzed: {{ organ.test_count }} ({{ organ.abnormal_test_count }} abnormal)</p>{% endfor %}</div><div class='section'><h2>Health Recommendations</h2>{% for rec in recommendations %}<p><strong>{{ rec.organ_name }}:</strong> {{ rec.text }}</p>{% endfor %}</div><div class='footer'><p><strong>Disclaimer:</strong> This report is generated by AI and is for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.</p></div></body></html>"""
        score = organ_scores.get("overall_health_score", 0)
        status = "Excellent Health" if score >= 90 else "Good Health" if score >= 70 else "Attention Needed" if score >= 50 else "Concerning"
        return Template(template_str).render(generation_date=datetime.now().strftime("%B %d, %Y at %I:%M %p"), overall_health_score=score, overall_status=status, total_tests=len(session_data.get("lab_results", [])), total_organs=len(organ_scores.get("organ_scores", [])), lab_results=session_data.get("lab_results", []), organ_scores=organ_scores.get("organ_scores", []), recommendations=organ_scores.get("recommendations", []))
