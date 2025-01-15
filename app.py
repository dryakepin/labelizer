from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from labels.label_design_1 import LabelDesign1
from labels.label_design_2 import LabelDesign2
from database.schema import init_db
from database.db_manager import DBManager

app = Flask(__name__, static_url_path='', static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the database
init_db()
db_manager = DBManager()

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    # Get all labels from database
    labels = db_manager.get_all_beer_labels()
    return render_template('list.html', labels=labels)

@app.route('/editor/<uuid>')
def editor(uuid):
    # Get label data from database if it exists
    label_data = db_manager.get_beer_label(uuid)
    
    # Convert database row to dictionary if it exists
    initial_data = {}
    if label_data:
        initial_data = {
            'beer_name': label_data[1],
            'subtitle': label_data[2],
            'abv': label_data[3],
            'beer_size': label_data[4],
            'border_color': label_data[5],
            'text_color': label_data[6],
            'font': label_data[7],
            'font_size': label_data[8],
            'image_scale': label_data[9],
            'image_rotation': label_data[10],
            'image_x': label_data[11],
            'image_y': label_data[12],
            'crop_x': label_data[13],
            'crop_y': label_data[14],
            'description': label_data[15],
            'design_type': label_data[16]
        }
    
    return render_template('index.html', uuid=uuid, initial_data=initial_data)

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
            'subtitle': request.form.get('subtitle', ''),
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
        
        # Ensure we have an absolute URL path starting with /uploads/
        preview_url = '/uploads/' + os.path.basename(preview_path)
        
        print(f"Generated preview path: {preview_path}")  # Debug print
        print(f"Generated preview URL: {preview_url}")    # Debug print
        
        return jsonify({
            'preview_url': preview_url,
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
    init_db()  # Initialize database on startup
    app.run(debug=True) 