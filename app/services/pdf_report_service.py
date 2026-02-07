"""
PDF Report Generation Service
Generates professional resume analysis reports
"""

from io import BytesIO
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from app.core.logging import logger, log_service_call
from app.schemas.resume import AnalysisResult


class PDFReportService:
    """Service for generating PDF reports from resume analysis results"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""

        self.styles.add(ParagraphStyle(
            name="CustomTitle",
            parent=self.styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1a237e"),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold"
        ))

        self.styles.add(ParagraphStyle(
            name="SectionHeading",
            parent=self.styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor("#283593"),
            spaceBefore=12,
            spaceAfter=12,
            fontName="Helvetica-Bold"
        ))

        self.styles.add(ParagraphStyle(
            name="BulletPoint",
            parent=self.styles["Normal"],
            fontSize=11,
            leftIndent=18,
            spaceAfter=8
        ))

        self.styles.add(ParagraphStyle(
            name="Footer",
            parent=self.styles["Normal"],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))

    # -------------------- SCORE HELPERS --------------------

    def _get_score_color(self, score: int):
        if score >= 80:
            return colors.HexColor("#2e7d32")
        elif score >= 60:
            return colors.HexColor("#f57c00")
        else:
            return colors.HexColor("#c62828")

    def _get_score_label(self, score: int):
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"

    # -------------------- HEADER / FOOTER --------------------

    def _create_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)

        canvas.drawString(
            inch,
            0.5 * inch,
            f"Generated on {datetime.now().strftime('%B %d, %Y')}"
        )

        canvas.drawRightString(
            doc.width + doc.leftMargin,
            0.5 * inch,
            f"Page {canvas.getPageNumber()}"
        )

        canvas.restoreState()

    # -------------------- MAIN GENERATOR --------------------

    def generate_report(
        self,
        analysis_result: AnalysisResult,
        filename: Optional[str] = None
    ) -> BytesIO:
        """
        Generate PDF report from analysis results
        """

        log_service_call(
            "PDFReportService",
            "generate_report",
            f"ATS Score: {analysis_result.atsScore}"
        )

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        story = []

        # -------- Title --------
        story.append(Paragraph("Resume Analysis Report", self.styles["CustomTitle"]))
        story.append(Spacer(1, 0.3 * inch))

        story.append(Paragraph(
            f"<i>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
            self.styles["Normal"]
        ))
        story.append(Spacer(1, 0.4 * inch))

        # -------- Score --------
        story.append(self._create_score_section(analysis_result.atsScore))
        story.append(Spacer(1, 0.4 * inch))

        # -------- Summary --------
        story.append(self._create_summary_table(analysis_result))
        story.append(Spacer(1, 0.4 * inch))

        # -------- Sections --------
        story.append(self._create_section("💪 Strengths", analysis_result.strengths))
        story.append(Spacer(1, 0.25 * inch))

        story.append(self._create_section("🔧 Areas for Improvement", analysis_result.improvements))
        story.append(Spacer(1, 0.25 * inch))

        if analysis_result.missingKeywords:
            story.append(self._create_section("🔑 Missing Keywords", analysis_result.missingKeywords))
            story.append(Spacer(1, 0.25 * inch))

        story.append(self._create_section("💡 Actionable Suggestions", analysis_result.suggestions))

        story.append(PageBreak())

        story.append(self._create_final_recommendations(analysis_result.atsScore))

        doc.build(
            story,
            onFirstPage=self._create_footer,
            onLaterPages=self._create_footer
        )

        buffer.seek(0)

        logger.info(f"PDF generated successfully ({buffer.getbuffer().nbytes} bytes)")
        return buffer

    # -------------------- SECTIONS --------------------

    def _create_score_section(self, score: int):
        color = self._get_score_color(score)
        label = self._get_score_label(score)

        data = [
            [Paragraph(f'<font size="48" color="{color.hexval()}"><b>{score}</b></font>', self.styles["Normal"])],
            [Paragraph("<b>ATS Compatibility Score</b>", self.styles["Normal"])],
            [Paragraph(f'<i>{label}</i>', self.styles["Normal"])]
        ]

        table = Table(data, colWidths=[6 * inch])
        table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 2, color),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
            ("TOPPADDING", (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ]))

        return KeepTogether([table])

    def _create_summary_table(self, analysis_result: AnalysisResult):
        data = [
            ["Metric", "Count"],
            ["Strengths", len(analysis_result.strengths)],
            ["Improvements", len(analysis_result.improvements)],
            ["Missing Keywords", len(analysis_result.missingKeywords)],
            ["Suggestions", len(analysis_result.suggestions)]
        ]

        table = Table(data, colWidths=[4 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#283593")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 1), (-1, -1), "LEFT"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ]))

        return table

    def _create_section(self, title: str, items: list):
        elements = [Paragraph(title, self.styles["SectionHeading"])]

        for item in items:
            elements.append(Paragraph(f"• {item}", self.styles["BulletPoint"]))

        return KeepTogether(elements)

    def _create_final_recommendations(self, score: int):
        elements = [Paragraph("📋 Final Recommendations", self.styles["SectionHeading"])]

        if score >= 80:
            recs = [
                "Your resume is excellent. Apply confidently.",
                "Continue tailoring for each job role."
            ]
        elif score >= 60:
            recs = [
                "Improve keyword usage.",
                "Quantify achievements with numbers."
            ]
        else:
            recs = [
                "Major resume improvements required.",
                "Use ATS-friendly templates and keywords."
            ]

        for r in recs:
            elements.append(Paragraph(f"• {r}", self.styles["BulletPoint"]))

        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(
            "<i>This AI-generated report is for guidance only.</i>",
            self.styles["Footer"]
        ))

        return KeepTogether(elements)


# ✅ Global instance
pdf_report_service = PDFReportService()
