import sqlite3
from datetime import datetime
import os

class DBManager:
    def __init__(self, db_path='database/beer_labels.db'):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def save_beer_label(self, uuid, beer_name, subtitle, abv, beer_size, 
                       border_color, text_color, font, font_size, image_scale,
                       image_x, image_y, crop_x, crop_y, description, 
                       design_type, image_data):
        """Save or update a beer label in the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if record exists
            cursor.execute('SELECT 1 FROM BeerLabel WHERE uuid = ?', (uuid,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Update existing record
                cursor.execute('''
                UPDATE BeerLabel SET
                    beer_name = ?, subtitle = ?, abv = ?, beer_size = ?,
                    border_color = ?, text_color = ?, font = ?, font_size = ?,
                    image_scale = ?, image_x = ?, image_y = ?,
                    crop_x = ?, crop_y = ?, description = ?, design_type = ?,
                    label_image = ?
                WHERE uuid = ?
                ''', (beer_name, subtitle, abv, beer_size, border_color,
                      text_color, font, font_size, image_scale,
                      image_x, image_y, crop_x, crop_y, description, design_type,
                      image_data, uuid))
            else:
                # Insert new record
                cursor.execute('''
                INSERT INTO BeerLabel (
                    uuid, beer_name, subtitle, abv, beer_size,
                    border_color, text_color, font, font_size,
                    image_scale, image_x, image_y,
                    crop_x, crop_y, description, design_type, label_image
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (uuid, beer_name, subtitle, abv, beer_size, border_color,
                      text_color, font, font_size, image_scale,
                      image_x, image_y, crop_x, crop_y, description, design_type,
                      image_data))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Database error: {e}")
            conn.rollback()
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