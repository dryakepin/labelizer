import sqlite3
import os

DATABASE_PATH = 'database/beer_labels.db'

def ensure_database_exists():
    """Create the database and tables if they don't exist"""
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create the BeerLabel table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BeerLabel (
        uuid TEXT PRIMARY KEY,
        beer_name TEXT NOT NULL,
        subtitle TEXT NOT NULL,
        abv TEXT,
        beer_size TEXT,
        border_color TEXT,
        text_color TEXT,
        font TEXT,
        font_size INTEGER,
        image_scale REAL,
        image_x REAL,
        image_y REAL,
        crop_x REAL,
        crop_y REAL,
        description TEXT,
        design_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        label_image BLOB
    )
    ''')
    
    conn.commit()
    conn.close()

def init_db():
    """Initialize the database"""
    try:
        ensure_database_exists()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}") 