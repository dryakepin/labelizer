from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from label_generator import BeerLabelGenerator
import uuid
from labels.label_design_1 import LabelDesign1
from labels.label_design_2 import LabelDesign2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'background' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['background']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(file.filename)[1])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get form data
        label_data = {
            'beer_name': request.form.get('beer_name', ''),
            'brewer_name': request.form.get('brewer_name', ''),
            'abv': request.form.get('abv', ''),
            'beer_size': request.form.get('beer_size', ''),
            'border_color': request.form.get('border_color', '#000000'),
            'text_color': request.form.get('text_color', '#000000'),
            'font': request.form.get('font', 'Arial'),
            'font_size': int(request.form.get('font_size', 32)),
            'image_scale': float(request.form.get('image_scale', 100)),
            'image_rotation': float(request.form.get('image_rotation', 0)),
            'image_x': float(request.form.get('image_x', 50)),
            'image_y': float(request.form.get('image_y', 50)),
            'crop_x': float(request.form.get('crop_x', 50)),
            'crop_y': float(request.form.get('crop_y', 50)),
        }
        
        # Get design type
        design_type = request.form.get('design_type', 'design1')
        
        # Select label design based on design_type
        label_class = {
            'design1': LabelDesign1,
            'design2': LabelDesign2
        }.get(design_type)
        
        if not label_class:
            return jsonify({'error': 'Invalid design type'}), 400
        
        # Generate preview using selected design
        generator = label_class(filepath, label_data)
        preview_path = generator.generate_preview()
        
        return jsonify({
            'preview_url': preview_path,
            'original_file': filename
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()
    filename = data.get('filename')
    label_data = data.get('label_data')
    design_type = data.get('design_type', 'design1')  # Add design type parameter
    
    if not filename or not label_data:
        return jsonify({'error': 'Missing required data'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Select label design based on design_type
    label_class = {
        'design1': LabelDesign1,
        'design2': LabelDesign2
    }.get(design_type)
    
    if not label_class:
        return jsonify({'error': 'Invalid design type'}), 400
    
    generator = label_class(filepath, label_data)
    bottle_size = label_data.get('beer_size', '500ML')
    pdf_path = generator.generate_pdf(bottle_size=bottle_size)
    
    return send_file(pdf_path, as_attachment=True, download_name='beer_label.pdf')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True) 