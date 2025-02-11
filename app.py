from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from labels.label_design_1 import LabelDesign1
from labels.label_design_2 import LabelDesign2
from database.schema import init_db
from database.db_manager import DBManager
import json

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

def generate_preview_image(uuid, filepath, label_data):
    """Generate a preview image and return its URL path"""
    # Get design type
    design_type = label_data.get('design_type', 'design1')
    
    # Select label design based on design_type
    label_class = {
        'design1': LabelDesign1,
        'design2': LabelDesign2
    }.get(design_type)
    
    if not label_class:
        raise ValueError('Invalid design type')
    
    # Generate preview using selected design
    generator = label_class(filepath, label_data)
    preview_path = generator.generate_preview(uuid)
    
    # Ensure we have an absolute URL path starting with /uploads/
    preview_url = '/uploads/' + os.path.basename(preview_path)
    
    print("preview url: " + preview_url)

    return preview_url

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
            'image_x': label_data[10],
            'image_y': label_data[11],
            'crop_x': label_data[12],
            'crop_y': label_data[13],
            'description': label_data[14],
            'design_type': label_data[15]
        }

        # If we have image data, save it to a temporary file and pass the URL
        if label_data[17]:  # label_image is at index 17
            # Use .png as default extension for the temporary file
            temp_filename = f"{uuid}.png"
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            
            # Make sure we're writing bytes, not string
            if isinstance(label_data[17], str):
                image_data = label_data[17].encode('utf-8')
            else:
                image_data = label_data[17]
                
            with open(temp_filepath, 'wb') as f:
                f.write(image_data)
            
            # Add the filename to initial_data for the file input
            initial_data['filename'] = temp_filename
            
            # Generate preview image
            try:
                preview_url = generate_preview_image(uuid, temp_filepath, initial_data)
                initial_data['background'] = preview_url
            except Exception as e:
                print(f"Error generating preview: {e}")
    
    return render_template('index.html', uuid=uuid, initial_data=initial_data)

@app.route('/upload/<uuid>', methods=['POST'])
def upload_file(uuid):
    print("upload file")
    print(uuid)

    if 'background' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['background']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = f"{uuid}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print (filepath)
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
            'image_x': float(request.form.get('image_x', 50)),
            'image_y': float(request.form.get('image_y', 50)),
            'crop_x': float(request.form.get('crop_x', 50)),
            'crop_y': float(request.form.get('crop_y', 50)),
            'description': request.form.get('description', ''),
            'design_type': request.form.get('design_type', 'design1')
        }

        print(label_data)
        
        try:
            preview_url = generate_preview_image(uuid, filepath, label_data)
            return jsonify({
                'preview_url': preview_url,
                'original_file': filename
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/generate-pdf/<uuid>', methods=['POST'])
def generate_pdf(uuid):
    print("generate pdf")
    print(request.form)
    label_data = json.loads(request.form.get('label_data'))
    design_type = label_data.get('design_type', 'design1')  # Add design type parameter

    print("design_type: ", design_type)

    # Select label design based on design_type
    label_class = {
        'design1': LabelDesign1,
        'design2': LabelDesign2
    }.get(design_type)
    
    if not label_class:
        return jsonify({'error': 'Invalid design type'}), 400

    bottle_size = label_data.get('beer_size', '500ML')
    beer_name = label_data.get('beer_name', 'Beer Name')

    print("beer_name: ", beer_name)
    print("bottle_size: ", bottle_size)

    temp_filename = f"{uuid}.png"
    temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

    generator = label_class(temp_filepath, label_data)

    #uuid = label_data.get('uuid')
    pdf_path = generator.generate_pdf(uuid, beer_name, bottle_size=bottle_size)
    

    print("pdf_path: ", pdf_path)

    return send_file(pdf_path, as_attachment=True, download_name='beer_label.pdf')

@app.route('/save-label/<uuid>', methods=['POST'])
def save_label(uuid):
    try:
        # Get label data from form
        label_data = json.loads(request.form.get('label_data'))
        
        # Get the background file if it exists
        background_file = None
        if 'background' in request.files:
            background_file = request.files['background']
        
        # If we have a file, read it into binary data
        image_data = None
        if background_file and background_file.filename:
            image_data = background_file.read()
        
        # Save to database
        success = db_manager.save_beer_label(
            uuid=uuid,
            beer_name=label_data.get('beer_name', ''),
            subtitle=label_data.get('subtitle', ''),
            abv=label_data.get('abv', ''),
            beer_size=label_data.get('beer_size', ''),
            border_color=label_data.get('border_color', '#000000'),
            text_color=label_data.get('text_color', '#000000'),
            font=label_data.get('font', 'Arial'),
            font_size=label_data.get('font_size', 32),
            image_scale=label_data.get('image_scale', 100),
            image_x=label_data.get('image_x', 50),
            image_y=label_data.get('image_y', 50),
            crop_x=label_data.get('crop_x', 50),
            crop_y=label_data.get('crop_y', 50),
            description=label_data.get('description', ''),
            design_type=label_data.get('design_type', 'design1'),
            image_data=image_data
        )
        
        if success:
            return jsonify({'message': 'Label saved successfully'})
        else:
            return jsonify({'error': 'Failed to save label'}), 500
            
    except Exception as e:
        print(f"Error saving label: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()  # Initialize database on startup
    app.run(debug=True) 