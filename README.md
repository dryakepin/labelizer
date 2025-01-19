# Labelizer

A web application for designing and generating beer labels. Users can upload background images, customize text and design elements, and generate printable PDF labels.

## Features

- Upload and customize background images
- Adjust text positioning, colors, and fonts
- Live preview of label changes
- Save labels for later editing
- Generate PDF output for printing
- Multiple design templates support

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- SQLite3

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/labelizer.git
cd labelizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_db.py
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## Project Structure

```
labelizer/
├── app.py                 # Main Flask application
├── static/
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── uploads/          # Uploaded images
├── templates/            # HTML templates
├── database/            
│   ├── __init__.py
│   ├── db_manager.py     # Database operations
│   └── schema.py         # Database schema
├── labels/
│   ├── __init__.py
│   ├── label_design_1.py # Label design implementations
│   └── label_design_2.py
└── requirements.txt      # Python dependencies
```

## Development

- The application uses Flask for the backend
- SQLite for data persistence
- Pillow (PIL) for image processing
- Bootstrap for frontend styling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
