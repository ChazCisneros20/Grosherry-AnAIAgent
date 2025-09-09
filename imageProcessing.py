import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class ImageProcessor:
    @staticmethod
    #RETURNS A STRING OF A TRANSCRIBED RECEIPT.
    def returnString(imageFilePath):
        return pytesseract.image_to_string(Image.open(imageFilePath)).strip()
    
