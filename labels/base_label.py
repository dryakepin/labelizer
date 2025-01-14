from abc import ABC, abstractmethod

class BaseLabel:
    @abstractmethod
    def __init__(self, image_path, label_data):
        pass

    @abstractmethod
    def generate_preview(self):
        """Generate a preview image of the label"""
        pass

    @abstractmethod
    def generate_pdf(self, bottle_size='500ML'):
        """Generate a PDF with the label layout"""
        pass 