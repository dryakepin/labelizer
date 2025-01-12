from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
import os
import uuid

class BeerLabelGenerator:
    def __init__(self, image_path, label_data):
        self.image_path = image_path
        self.label_data = label_data.copy()
        self.label_data['font_size'] = int(self.label_data.get('font_size', 24))
        self.preview_folder = 'static/uploads'
    
    def _resize_and_crop(self, img, target_width, target_height):
        """Resize and crop image to target aspect ratio while maintaining proportions"""
        target_ratio = target_width / target_height
        img_ratio = img.width / img.height
        
        # Get crop position (0-100%)
        crop_x = float(self.label_data.get('crop_x', 50)) / 100
        crop_y = float(self.label_data.get('crop_y', 50)) / 100
        
        if img_ratio > target_ratio:
            # Image is wider than target ratio
            new_width = int(target_ratio * img.height)
            left = int((img.width - new_width) * crop_x)
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            # Image is taller than target ratio
            new_height = int(img.width / target_ratio)
            top = int((img.height - new_height) * crop_y)
            img = img.crop((0, top, img.width, top + new_height))
        
        # Resize to target dimensions
        return img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    def _create_label(self, size, is_preview=True):
        # Define constants
        border_width = 1
        margin = 8
        text_spacing = 8

        # Define fonts
        try:
            beer_name_font = ImageFont.truetype('Arial Bold.ttf', self.label_data['font_size'])
            brewer_font = ImageFont.truetype('Arial.ttf', self.label_data['font_size'] - 4)
            abv_font = ImageFont.truetype('Arial.ttf', self.label_data['font_size'] - 8)
        except:
            beer_name_font = ImageFont.load_default()
            brewer_font = ImageFont.load_default()
            abv_font = ImageFont.load_default()

        # Create or load background image
        if not self.image_path:
            final_img = Image.new('RGB', size, 'blue')
        else:
            img = Image.open(self.image_path)
            rotation = float(self.label_data.get('image_rotation', 0))
            x_pos = float(self.label_data.get('image_x', 50)) / 100
            y_pos = float(self.label_data.get('image_y', 50)) / 100

            is_bottle = size[1] > size[0]

            if is_bottle:
                img = self._resize_and_crop(img, size[0], size[1])
            else:
                square_size = min(size)
                img = self._resize_and_crop(img, square_size, square_size)

            if rotation != 0:
                img = img.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)

            final_img = Image.new('RGB', size, 'white')
            paste_x = int((size[0] - img.width) * x_pos)
            paste_y = int((size[1] - img.height) * y_pos)
            final_img.paste(img, (paste_x, paste_y))

        # Create white box for text
        box_height = size[0] // 5  # 1/5th of the image width
        box_width = size[1] - (2 * border_width)
        box_img = Image.new('RGBA', (box_width, box_height), (255, 255, 255, 255))
        box_draw = ImageDraw.Draw(box_img)

        # Draw text content in the box
        beer_name = self.label_data['beer_name']
        brewer_name = self.label_data['brewer_name']
        beer_size = self.label_data.get('beer_size', '500ML')
        abv_text = f"{beer_size} // {self.label_data['abv']}%/VOL"

        current_x = margin
        current_y = margin

        box_draw.text((current_x, current_y), beer_name, font=beer_name_font, fill=self.label_data['text_color'])
        beer_bbox = box_draw.textbbox((0, 0), beer_name, font=beer_name_font)
        current_y += beer_bbox[3] - beer_bbox[1] + text_spacing

        box_draw.text((current_x, current_y), brewer_name, font=brewer_font, fill=self.label_data['text_color'])
        brewer_bbox = box_draw.textbbox((0, 0), brewer_name, font=brewer_font)
        current_y += brewer_bbox[3] - brewer_bbox[1] + text_spacing

        box_draw.text((current_x, current_y), abv_text, font=abv_font, fill=self.label_data['text_color'])

        # Rotate the box
        box_img = box_img.rotate(90, expand=True)
        rotated_box_width, rotated_box_height = box_img.size

        # Calculate position to paste the rotated box
        box_left = size[0] - rotated_box_width - border_width
        box_top = (size[1] - rotated_box_height) // 2

        # Draw large transparent first letter
        first_letter = self.label_data['beer_name'][0] if self.label_data['beer_name'] else ''
        if first_letter:
            letter_size = 100
            try:
                letter_font = ImageFont.truetype('Arial Bold.ttf', letter_size)
            except:
                letter_font = ImageFont.load_default()

            if letter_font:
                rotated_box_draw = ImageDraw.Draw(box_img)
                letter_bbox = rotated_box_draw.textbbox((0, 0), first_letter, font=letter_font)
                letter_width = letter_bbox[2] - letter_bbox[0]
                letter_height = letter_bbox[3] - letter_bbox[1]
                letter_x = (rotated_box_width - letter_width) // 2
                letter_y = (margin) 

                rotated_box_draw.text(
                    (letter_x, letter_y),
                    first_letter,
                    font=letter_font,
                    fill=(0, 0, 0, 64)
                )

        # Paste the rotated box onto the final image
        final_img.paste(box_img, (box_left, box_top), mask=box_img)

        # Draw border
        draw = ImageDraw.Draw(final_img)
        draw.rectangle(
            [(0, 0), (size[0] - 1, size[1] - 1)],
            outline=self.label_data['border_color'],
            width=border_width
        )

        # Save or return the image
        if is_preview:
            preview_path = os.path.join(self.preview_folder, f'preview_{uuid.uuid4()}.png')
            final_img.save(preview_path)
            return preview_path

        return final_img


    """
    def _create_label(self, size, is_preview=True):
        # Define constants at the start
        border_width = 1
        
        # Define fonts at the start of the method
        try:
            beer_name_font = ImageFont.truetype('Arial Bold.ttf', self.label_data['font_size'])
            brewer_font = ImageFont.truetype('Arial.ttf', self.label_data['font_size'] - 4)
            abv_font = ImageFont.truetype('Arial.ttf', self.label_data['font_size'] - 8)
        except:
            # Fallback to default font if Arial is not available
            beer_name_font = ImageFont.load_default()
            brewer_font = ImageFont.load_default()
            abv_font = ImageFont.load_default()

        # Create a blank canvas if no image is provided
        if not self.image_path:
            final_img = Image.new('RGB', size, 'blue')
        else:
            # Open and process background image as before
            img = Image.open(self.image_path)
            rotation = float(self.label_data.get('image_rotation', 0))
            x_pos = float(self.label_data.get('image_x', 50)) / 100
            y_pos = float(self.label_data.get('image_y', 50)) / 100
            
            is_bottle = size[1] > size[0]
            
            if is_bottle:
                img = self._resize_and_crop(img, size[0], size[1])
            else:
                square_size = min(size)
                img = self._resize_and_crop(img, square_size, square_size)
            
            if rotation != 0:
                img = img.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)
            
            final_img = Image.new('RGB', size, 'white')
            
            # Calculate the position to paste the image
            paste_x = int((size[0] - img.width) * x_pos)
            paste_y = int((size[1] - img.height) * y_pos)
            
            final_img.paste(img, (paste_x, paste_y))

        # Create white box
        box_height = size[0] // 5  # 1/5th of the image width
        box_width = size[1] - (2 * border_width)

        print ("box width, height")
        print(box_width, box_height)
        # Create a separate image for the white box and its contents
        box_img = Image.new('RGBA', (box_width, box_height), (255, 255, 255, 255))
        box_draw = ImageDraw.Draw(box_img)
        
        margin = 8
        text_spacing = 8
        
        # Calculate text heights and prepare text
        beer_name = self.label_data['beer_name']
        brewer_name = self.label_data['brewer_name']
        beer_size = self.label_data.get('beer_size', '500ML')
        abv_text = f"{beer_size} // {self.label_data['abv']}%/VOL"
        
        # Draw all text vertically (since we're pre-rotating)
        current_x = margin
        current_y = margin

        # Draw beer name
        box_draw.text(
            (current_x, current_y),
            beer_name,
            font=beer_name_font,
            fill=self.label_data['text_color']
        )
        
        # Calculate next position
        beer_bbox = box_draw.textbbox((0, 0), beer_name, font=beer_name_font)
        current_y += beer_bbox[3] - beer_bbox[1] + text_spacing
        
        # Draw subtitle (brewer name)
        box_draw.text( 
            (current_x, current_y),
            brewer_name,
            font=brewer_font,
            fill=self.label_data['text_color'],
        )
        
        # Calculate next position
        brewer_bbox = box_draw.textbbox((0, 0), brewer_name, font=brewer_font)
        current_y += brewer_bbox[3] - brewer_bbox[1] + text_spacing
        
        # Draw size and ABV
        box_draw.text(
            (current_x, current_y),
            abv_text,
            font=abv_font,
            fill=self.label_data['text_color']
        )

        # Rotate the box 90 degrees
        box_img = box_img.rotate(90, expand=True)

        # After rotation, box_width and box_height are swapped
        # Calculate position to paste the rotated box
        box_left = size[0] - box_height - border_width  # Use box_height because dimensions are swapped after rotation
        box_top = (size[1] - box_width) // 2  # Use box_width because dimensions are swapped after rotation

        print("box left, top")
        print(box_left, box_top)

        # Draw large transparent first letter (adjusted for horizontal layout)
        first_letter = self.label_data['beer_name'][0] if self.label_data['beer_name'] else ''
        if first_letter:
            # Calculate size to fit width of box
            #target_height = box_height - (2 * margin)
            letter_size = 100  # Starting size
            letter_font = None
            
            try:
                letter_font = ImageFont.truetype('Arial Bold.ttf', letter_size)
            except:
                letter_font = ImageFont.load_default()

            if letter_font:
                letter_bbox = box_draw.textbbox((0, 0), first_letter, font=letter_font)
                letter_width = letter_bbox[2] - letter_bbox[0]
                letter_height = letter_bbox[3] - letter_bbox[1]
                
                # Position at right side
                letter_x = 40
                letter_y = 40
                
                print ("letter x, y")
                print(letter_x, letter_y)

                box_draw.text(
                    (letter_x, letter_y),
                    first_letter,
                    font=letter_font,
                    fill=(0, 0, 0, 64)
                )

        # Paste the rotated box onto the final image
        final_img.paste(box_img, (box_left, box_top), mask=box_img)
        
        # Draw border last
        draw = ImageDraw.Draw(final_img)
        border_width = 1
        draw.rectangle(
            [(0, 0), (size[0]-1, size[1]-1)],
            outline=self.label_data['border_color'],
            width=border_width
        )
        
        if is_preview:
            # Save preview image
            preview_path = os.path.join(self.preview_folder, f'preview_{uuid.uuid4()}.png')
            final_img.save(preview_path)
            return preview_path
        
        return final_img
    """
    
    def generate_preview(self):
        # Generate preview for bottle label (3:4)
        return self._create_label((450, 600), True)  # 3:4 aspect ratio
    
    def generate_pdf(self):
        # Generate both bottle and keg labels
        bottle_label = self._create_label((450, 600), False)  # 3:4 for bottle
        keg_label = self._create_label((600, 600), False)    # Square for keg
        
        # Create PDF
        pdf_path = os.path.join(self.preview_folder, f'labels_{uuid.uuid4()}.pdf')
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Page 1: Bottle Labels (2x2 grid)
        # Calculate dimensions to fit 4 labels on the page with margins
        page_width, page_height = letter  # typically 612 x 792 points
        margin = 36  # 0.5 inch margin
        spacing = 20  # space between labels
        
        # Calculate label size to fit on page
        label_width = (page_width - 2 * margin - spacing) / 2
        label_height = (page_height - 2 * margin - spacing) / 2
        
        # Draw 4 bottle labels in a grid
        positions = [
            (margin, page_height - margin - label_height),                    # top left
            (margin + label_width + spacing, page_height - margin - label_height),  # top right
            (margin, margin),                                                # bottom left
            (margin + label_width + spacing, margin)                         # bottom right
        ]
        
        for x, y in positions:
            c.drawInlineImage(bottle_label, x, y, width=label_width, height=label_height)
            c.setFont("Helvetica", 8)
            c.drawString(x, y - 10, "Bottle Label (3:4)")
        
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