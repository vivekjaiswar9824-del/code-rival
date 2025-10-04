from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, gold
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
from django.http import HttpResponse
from django.conf import settings
import os
from datetime import datetime
import io

class CertificateGenerator:
    def __init__(self, certification):
        self.certification = certification
        self.user = certification.user
        self.course = certification.course
        
    def generate_certificate_pdf(self):
        """Generate a professional certificate PDF"""
        buffer = io.BytesIO()
        
        # Create the PDF object using ReportLab
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Set up colors
        primary_color = HexColor('#1e3a8a')  # Dark blue
        accent_color = HexColor('#f59e0b')   # Gold
        text_color = HexColor('#374151')     # Dark gray
        
        # Draw border
        p.setStrokeColor(primary_color)
        p.setLineWidth(3)
        p.rect(30, 30, width-60, height-60)
        
        # Draw inner decorative border
        p.setStrokeColor(accent_color)
        p.setLineWidth(1)
        p.rect(50, 50, width-100, height-100)
        
        # Header - Certificate Title
        p.setFont("Helvetica-Bold", 36)
        p.setFillColor(primary_color)
        p.drawCentredText(width/2, height-120, "CERTIFICATE OF COMPLETION")
        
        # Decorative line under title
        p.setStrokeColor(accent_color)
        p.setLineWidth(2)
        p.line(150, height-140, width-150, height-140)
        
        # Subtitle
        p.setFont("Helvetica", 16)
        p.setFillColor(text_color)
        p.drawCentredText(width/2, height-170, "This is to certify that")
        
        # Student Name
        p.setFont("Helvetica-Bold", 28)
        p.setFillColor(primary_color)
        p.drawCentredText(width/2, height-220, self.user.name.upper())
        
        # Underline for name
        name_width = p.stringWidth(self.user.name.upper(), "Helvetica-Bold", 28)
        p.setStrokeColor(primary_color)
        p.setLineWidth(1)
        p.line((width-name_width)/2, height-235, (width+name_width)/2, height-235)
        
        # Course completion text
        p.setFont("Helvetica", 16)
        p.setFillColor(text_color)
        p.drawCentredText(width/2, height-270, "has successfully completed the course")
        
        # Course Name
        p.setFont("Helvetica-Bold", 22)
        p.setFillColor(primary_color)
        p.drawCentredText(width/2, height-310, self.course.title)
        
        # Course Domain
        p.setFont("Helvetica-Oblique", 14)
        p.setFillColor(text_color)
        p.drawCentredText(width/2, height-335, f"in {self.course.domain}")
        
        # Level and Score
        p.setFont("Helvetica", 14)
        level_score_text = f"Level: {self.certification.level} | Score: {self.certification.score}%"
        p.drawCentredText(width/2, height-365, level_score_text)
        
        # Date
        p.setFont("Helvetica", 12)
        date_text = f"Issued on: {self.certification.issued_at.strftime('%B %d, %Y')}"
        p.drawCentredText(width/2, height-420, date_text)
        
        # Certificate ID
        cert_id = f"Certificate ID: CERT-{self.certification.id:06d}"
        p.setFont("Helvetica", 10)
        p.setFillColor(HexColor('#6b7280'))
        p.drawCentredText(width/2, height-450, cert_id)
        
        # Footer - Company/Organization info
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(primary_color)
        p.drawCentredText(width/2, 150, "CODE RIVAL LEARNING PLATFORM")
        
        p.setFont("Helvetica", 10)
        p.setFillColor(text_color)
        p.drawCentredText(width/2, 130, "Professional Development & Certification Authority")
        
        # Signature area
        p.setFont("Helvetica", 10)
        p.drawString(100, 80, "Authorized Signature")
        p.line(100, 95, 250, 95)
        
        p.drawString(width-250, 80, "Date of Issue")
        p.line(width-250, 95, width-100, 95)
        
        # Save the PDF
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer
    
    def get_filename(self):
        """Generate a filename for the certificate"""
        safe_name = "".join(c for c in self.user.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_course = "".join(c for c in self.course.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return f"Certificate_{safe_name}_{safe_course}_{self.certification.id}.pdf"
