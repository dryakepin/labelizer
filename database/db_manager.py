import sqlite3
from datetime import datetime

class DBManager:
    def __init__(self, db_path='database/beer_labels.db'):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def save_beer_label(self, uuid, label_data, design_type, description, image_blob):
        """Save a new beer label to the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO BeerLabel (
                uuid,
                beer_name,
                subtitle,
                abv,
                beer_size,
                border_color,
                text_color,
                font,
                font_size,
                image_scale,
                image_x,
                image_y,
                crop_x,
                crop_y,
                description,
                design_type,
                label_image
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                uuid,
                label_data.get('beer_name'),
                label_data.get('subtitle'),
                label_data.get('abv'),
                label_data.get('beer_size'),
                label_data.get('border_color'),
                label_data.get('text_color'),
                label_data.get('font'),
                label_data.get('font_size'),
                label_data.get('image_scale'),
                label_data.get('image_x'),
                label_data.get('image_y'),
                label_data.get('crop_x'),
                label_data.get('crop_y'),
                description,
                design_type,
                image_blob
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving beer label: {e}")
            return False
            
        finally:
            conn.close()
    
    def get_beer_label(self, uuid):
        """Retrieve a beer label by UUID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM BeerLabel WHERE uuid = ?', (uuid,))
            return cursor.fetchone()
        finally:
            conn.close()
    
    def get_all_beer_labels(self):
        """Retrieve all beer labels (without image blobs)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT 
                uuid, beer_name, subtitle, abv, beer_size, 
                description, design_type, created_at 
            FROM BeerLabel
            ORDER BY created_at DESC
            ''')
            return cursor.fetchall()
        finally:
            conn.close() 