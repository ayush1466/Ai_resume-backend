"""
PDF Report Generation Service
Generates professional resume analysis reports
"""

from io import BytesIO
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

from app.core.logging import logger, log_service_call
from app.schemas.resume import AnalysisResult


class PDFReportService:
    """Service for generating PDF reports from resume analysis results"""

    def __init__(self):
        """Initialize PDF report service with custom styles"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Score style
        self.styles.add(ParagraphStyle(
            name='ScoreText',
            parent=self.styles['Normal'],
            fontSize=48,
            textColor=colors.HexColor('#2e7d32'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=8,
            bulletIndent=10
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))

    def _get_score_color(self, score: int) -> colors.Color:
        """Get color based on ATS score"""
        if score >= 80:
            return colors.HexColor('#2e7d32')  # Green
        elif score >= 60:
            return colors.HexColor('#f57c00')  # Orange
        else:
            return colors.HexColor('#c62828')  # Red

    def _get_score_label(self, score: int) -> str:
        """Get label based on ATS score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"

    def _create_header(self, canvas_obj, doc):
        """Create header for each page"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawString(
            inch,
            doc.height + doc.topMargin + 0.3 * inch,
            "Resume Analysis Report"
        )
        canvas_obj.restoreState()

    def _create_footer(self, canvas_obj, doc):
        """Create footer for each page"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.grey)
        
        # Page number
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.drawRightString(
            doc.width + doc.leftMargin,
            0.5 * inch,
            text
        )
        
        # Generated date
        canvas_obj.drawString(
            inch,
            0.5 * inch,
            f"Generated on {datetime.now().strftime('%B %d, %Y')}"
        )
        canvas_obj.restoreState()

    def generate_report(
        self,
        analysis_result: AnalysisResult,
        filename: Optional[str] = None
    ) -> BytesIO:
        """
        Generate PDF report from analysis results
        
        Args:
            analysis_result: AnalysisResult object with analysis data
            filename: Optional filename for the resume
            
        Returns:
            BytesIO object containing the PDF
        """
        log_service_call(
            "PDFReportService",
            "generate_report",
            f"ATS Score: {analysis_result.atsScore}"
        )

        # Create BytesIO buffer
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Container for PDF elements
        story = []

        # Add title
        title = Paragraph("Resume Analysis Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))

        # Add generation date
        date_text = Paragraph(
            f"<i>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
            self.styles['Normal']
        )
        story.append(date_text)
        story.append(Spacer(1, 0.5 * inch))

        # Add ATS Score Section
        story.append(self._create_score_section(analysis_result.atsScore))
        story.append(Spacer(1, 0.4 * inch))

        # Add Summary Table
        story.append(self._create_summary_table(analysis_result))
        story.append(Spacer(1, 0.4 * inch))

        # Add Strengths Section
        story.append(self._create_section(
            "💪 Strengths",
            analysis_result.strengths,
            colors.HexColor('#2e7d32')
        ))
        story.append(Spacer(1, 0.3 * inch))

        # Add Improvements Section
        story.append(self._create_section(
            "🔧 Areas for Improvement",
            analysis_result.improvements,
            colors.HexColor('#f57c00')
        ))
        story.append(Spacer(1, 0.3 * inch))

        # Add Missing Keywords Section
        if analysis_result.missingKeywords:
            story.append(self._create_section(
                "🔑 Missing Keywords",
                analysis_result.missingKeywords,
                colors.HexColor('#c62828')
            ))
            story.append(Spacer(1, 0.3 * inch))

        # Add Suggestions Section
        story.append(self._create_section(
            "💡 Actionable Suggestions",
            analysis_result.suggestions,
            colors.HexColor('#1976d2')
        ))

        # Add page break before final recommendations
        story.append(PageBreak())

        # Add Final Recommendations
        story.append(self._create_final_recommendations(analysis_result.atsScore))

        # Build PDF
        doc.build(
            story,
            onFirstPage=lambda c, d: self._create_footer(c, d),
            onLaterPages=lambda c, d: self._create_footer(c, d)
        )

        # Reset buffer position
        buffer.seek(0)
        
        logger.info("PDF report generated successfully")
        return buffer

    def _create_score_section(self, score: int) -> KeepTogether:
        """Create the ATS score display section"""
        elements = []
        
        # Score box with color
        score_color = self._get_score_color(score)
        score_label = self._get_score_label(score)

        # Create score table
        score_data = [
            [Paragraph(f'<font size="48" color="{score_color.hexval()}"><b>{score}</b></font>', self.styles['Normal'])],
            [Paragraph(f'<font size="14"><b>ATS Compatibility Score</b></font>', self.styles['Normal'])],
            [Paragraph(f'<font size="12" color="{score_color.hexval()}"><i>{score_label}</i></font>', self.styles['Normal'])]
        ]

        score_table = Table(score_data, colWidths=[6 * inch])
        score_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 2, score_color),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))

        return KeepTogether([score_table])

    def _create_summary_table(self, analysis_result: AnalysisResult) -> Table:
        """Create summary statistics table"""
        data = [
            ['Metric', 'Count'],
            ['Strengths Identified', str(len(analysis_result.strengths))],
            ['Improvement Areas', str(len(analysis_result.improvements))],
            ['Missing Keywords', str(len(analysis_result.missingKeywords))],
            ['Suggestions Provided', str(len(analysis_result.suggestions))],
        ]

        table = Table(data, colWidths=[4 * inch, 2 * inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))

        return table

    def _create_section(self, title: str, items: list, color: colors.Color) -> KeepTogether:
        """Create a section with title and bullet points"""
        elements = []

        # Section title with colored left border
        title_para = Paragraph(f'<b>{title}</b>', self.styles['SectionHeading'])
        elements.append(title_para)

        # Create bullet points
        for item in items:
            bullet = Paragraph(
                f'• {item}',
                self.styles['BulletPoint']
            )
            elements.append(bullet)

        return KeepTogether(elements)

    def _create_final_recommendations(self, score: int) -> KeepTogether:
        """Create final recommendations based on score"""
        elements = []

        title = Paragraph(
            '<b>📋 Final Recommendations</b>',
            self.styles['SectionHeading']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))

        if score >= 80:
            recommendations = [
                "Your resume is in excellent shape! Focus on minor tweaks.",
                "Continue to tailor your resume for each specific job application.",
                "Keep your resume updated with recent achievements and skills.",
                "Consider adding portfolio links or project demonstrations."
            ]
        elif score >= 60:
            recommendations = [
                "Your resume has a solid foundation with room for improvement.",
                "Focus on incorporating the missing keywords identified above.",
                "Quantify your achievements with specific metrics and numbers.",
                "Optimize section headers and formatting for better ATS parsing.",
                "Add more industry-specific technical skills."
            ]
        else:
            recommendations = [
                "Significant improvements are needed for better ATS compatibility.",
                "Restructure your resume using a standard ATS-friendly template.",
                "Add relevant keywords from job descriptions in your target field.",
                "Quantify all achievements with concrete numbers and metrics.",
                "Expand your skills section with industry-relevant technologies.",
                "Consider getting professional resume review services."
            ]

        for rec in recommendations:
            para = Paragraph(f'• {rec}', self.styles['BulletPoint'])
            elements.append(para)

        elements.append(Spacer(1, 0.3 * inch))

        # Add disclaimer
        disclaimer = Paragraph(
            '<i>Note: This analysis is generated by AI and should be used as guidance. '
            'Always review and customize your resume based on specific job requirements.</i>',
            self.styles['Footer']
        )
        elements.append(disclaimer)

        return KeepTogether(elements)


# Global instance
pdf_report_service = PDFReportService()