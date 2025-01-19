from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

class PDFGenerator:
    def __init__(self, preview_folder='static/uploads'):
        self.preview_folder = preview_folder
        # Define standard sizes in cm, converted to points (1 cm = 28.35 points)
        self.label_sizes = {
            '500ML': {
                'width': 9 * 28.35,   # 9cm
                'height': 10 * 28.35,  # 10cm
            },
            '330ML': {
                'width': 6.3 * 28.35,  # 6.3cm
                'height': 7 * 28.35,   # 7cm
            }
        }

    def add_label_size(self, name, width_cm, height_cm):
        """Add a custom label size (dimensions in centimeters)"""
        self.label_sizes[name] = {
            'width': width_cm * 28.35,
            'height': height_cm * 28.35
        }

    def generate_pdf(self, uuid, bottle_label, keg_label, bottle_size='500ML'):
        """
        Generate PDF with bottle and keg labels
        
        Args:
            bottle_label: PIL Image object for the bottle label
            keg_label: PIL Image object for the keg label
            bottle_size: Size key from label_sizes dict ('500ML' or '330ML')
        """
        if bottle_size not in self.label_sizes:
            raise ValueError(f"Unknown bottle size: {bottle_size}")

        # Get label dimensions
        label_dims = self.label_sizes[bottle_size]
        label_width = label_dims['width']
        label_height = label_dims['height']

        # Create PDF
        pdf_path = os.path.join(self.preview_folder, f'labels_{uuid}.pdf')
        c = canvas.Canvas(pdf_path, pagesize=A4)
        
        # Page 1: Bottle Labels
        page_width, page_height = A4
        margin = 36  # 0.5 inch margin
        spacing = 5  # space between labels
        
        # Calculate how many labels can fit horizontally and vertically
        usable_width = page_width - (2 * margin)
        usable_height = page_height - (2 * margin)
        
        labels_per_row = max(1, int((usable_width + spacing) / (label_width + spacing)))
        rows = max(1, int((usable_height + spacing) / (label_height + spacing)))
        
        # Calculate actual spacing to distribute labels evenly
        if labels_per_row > 1:
            h_spacing = (usable_width - (labels_per_row * label_width)) / (labels_per_row - 1)
        else:
            h_spacing = 0
        
        if rows > 1:
            v_spacing = (usable_height - (rows * label_height)) / (rows - 1)
        else:
            v_spacing = 0

        # Generate positions for all labels
        positions = []
        for row in range(rows):
            for col in range(labels_per_row):
                x = margin + (col * (label_width + h_spacing))
                y = page_height - margin - label_height - (row * (label_height + v_spacing))
                positions.append((x, y))
        
        # Draw bottle labels
        for x, y in positions:
            c.drawInlineImage(bottle_label, x, y, width=label_width, height=label_height)
            c.setFont("Helvetica", 8)
            c.drawString(x, y - 10, f"Bottle Label ({bottle_size})")
        
        # Add page 2 for keg label
        c.showPage()
        
        # Center the keg label on the second page
        keg_size = min(page_width - 2 * margin, page_height - 2 * margin)
        x = (page_width - keg_size) / 2
        y = (page_height - keg_size) / 2
        
        c.drawInlineImage(keg_label, x, y, width=keg_size, height=keg_size)
        c.setFont("Helvetica", 10)
        c.drawString(x, y - 20, "Keg Label (Square)")
        
        c.save()
        return pdf_path 