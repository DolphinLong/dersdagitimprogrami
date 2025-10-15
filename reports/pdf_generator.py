"""
PDF generator for the Class Scheduling Program using ReportLab Platypus.
"""

import logging

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle


class PDFGenerator:
    """Handles PDF report generation with styled tables."""

    def __init__(self, db_manager=None):
        self.db_manager = db_manager

    def generate_pdf(self, title, headers, data, filename="report.pdf"):
        """
        Generates a PDF with a styled table from structured data.
        """
        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
            elements = []
            styles = getSampleStyleSheet()

            # Title
            elements.append(Paragraph(title, styles["h1"]))

            # Table Data
            table_data = [headers] + data

            # Create Table
            table = Table(table_data, repeatRows=1)

            # Table Style
            style = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("BOX", (0, 0), (-1, -1), 2, colors.black),
                ]
            )

            # Alternating row colors
            for i, row in enumerate(data):
                if i % 2 == 0:
                    style.add("BACKGROUND", (0, i + 1), (-1, i + 1), colors.HexColor("#e0e0e0"))

            table.setStyle(style)  # Apply again after modification
            elements.append(table)

            doc.build(elements)
            return f"PDF raporu başarıyla oluşturuldu: {filename}"

        except Exception as e:
            error_msg = f"PDF oluşturma hatası: {str(e)}"
            logging.error(error_msg)
            return error_msg
