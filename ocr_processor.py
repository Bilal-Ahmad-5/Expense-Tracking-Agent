import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
from datetime import datetime


pytesseract.pytesseract.tesseract_cmd = r"C:\codehub\Gen AI Projects\tesseract.exe"
print(pytesseract.get_tesseract_version())

class OCRProcessor:    
    def preprocess_image(self, image):
        """Advanced image preprocessing for better OCR results"""
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Multiple enhancement passes
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.8)

            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.2)

            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)

            # Noise reduction
            image = image.filter(ImageFilter.MedianFilter(size=3))

            return image
        except Exception as e:
            print(f"Image preprocessing error: {e}")
            return image

    def extract_text_with_ocr(self, image):
        """Extract text using advanced OCR configuration"""
        try:
            processed_image = self.preprocess_image(image)

            # Multiple OCR passes with different configurations
            configs = [
                r'--oem 3 --psm 6',  # Uniform text block
                r'--oem 3 --psm 4',  # Single column text
                r'--oem 3 --psm 3',  # Fully automatic
            ]

            texts = []
            for config in configs:
                try:
                    text = pytesseract.image_to_string(processed_image,
                                                       config=config)
                    if text.strip():
                        texts.append(text.strip())
                except:
                    continue

            # Combine and deduplicate text
            combined_text = "\n".join(texts)
            return combined_text

        except Exception as e:
            print(f"OCR extraction error: {e}")
            return ""

