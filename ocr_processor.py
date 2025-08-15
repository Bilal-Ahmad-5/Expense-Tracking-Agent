import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
from datetime import datetime
import numpy as np

class OCRProcessor:
    def __init__(self):
        # Common merchant patterns
        self.merchant_patterns = [
            r'(?i)(walmart|target|costco|amazon|starbucks|mcdonalds|subway)',
            r'(?i)(home depot|lowes|best buy|cvs|walgreens)',
            r'(?i)(shell|exxon|bp|chevron|mobil)',
        ]
        
        # Amount patterns
        self.amount_patterns = [
            r'\$\s*(\d+\.\d{2})',  # $XX.XX
            r'total[:\s]*\$?\s*(\d+\.\d{2})',  # Total: $XX.XX
            r'amount[:\s]*\$?\s*(\d+\.\d{2})',  # Amount: $XX.XX
        ]
        
        # Date patterns
        self.date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',    # YYYY/MM/DD or YYYY-MM-DD
            r'(\w{3,9}\s+\d{1,2},?\s+\d{4})',    # Month DD, YYYY
        ]
    
    def preprocess_image(self, image):
        """Enhance image quality for better OCR results"""
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.MedianFilter())
            
            return image
        except Exception as e:
            print(f"Image preprocessing error: {e}")
            return image
    
    def extract_text(self, image):
        """Extract text from image using OCR"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # OCR configuration
            custom_config = r'--oem 3 --psm 6'
            
            # Extract text
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            return text.strip()
        except Exception as e:
            print(f"OCR extraction error: {e}")
            return ""
    
    def extract_amount(self, text):
        """Extract monetary amount from text"""
        amounts = []
        
        for pattern in self.amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            amounts.extend([float(match) for match in matches])
        
        # Look for any dollar amounts
        dollar_matches = re.findall(r'\$\s*(\d+(?:\.\d{2})?)', text)
        amounts.extend([float(match) for match in dollar_matches])
        
        if amounts:
            # Return the largest amount (likely to be the total)
            return max(amounts)
        
        return None
    
    def extract_date(self, text):
        """Extract date from text"""
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Try different date parsing approaches
                    date_formats = [
                        '%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y',
                        '%Y/%m/%d', '%Y-%m-%d',
                        '%B %d, %Y', '%b %d, %Y', '%B %d %Y', '%b %d %Y'
                    ]
                    
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(match, fmt)
                            return parsed_date.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                except:
                    continue
        
        # Default to today if no date found
        return datetime.now().strftime('%Y-%m-%d')
    
    def extract_merchant(self, text):
        """Extract merchant/store name from text"""
        lines = text.split('\n')
        
        # Look for known merchant patterns first
        for pattern in self.merchant_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0].title()
        
        # Try to find merchant in first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and not re.match(r'^\d+$', line):
                # Clean up the line
                cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', line).strip()
                if len(cleaned.split()) <= 4 and len(cleaned) > 3:
                    return cleaned.title()
        
        return "Unknown Merchant"
    
    def extract_items(self, text):
        """Extract item list from text (basic implementation)"""
        lines = text.split('\n')
        items = []
        
        for line in lines:
            line = line.strip()
            # Look for lines that might be items (contain letters and possibly amounts)
            if (len(line) > 3 and 
                any(c.isalpha() for c in line) and 
                not re.match(r'^[\d\s\$\.\-\/]+$', line)):
                items.append(line)
        
        return items[:10]  # Return first 10 items to avoid clutter
    
    def extract_receipt_data(self, image):
        """Main method to extract all receipt data"""
        try:
            # Extract text from image
            text = self.extract_text(image)
            
            if not text:
                return None
            
            # Extract individual components
            amount = self.extract_amount(text)
            date = self.extract_date(text)
            merchant = self.extract_merchant(text)
            items = self.extract_items(text)
            
            return {
                'amount': amount or 0.0,
                'date': date,
                'merchant': merchant,
                'items': items,
                'raw_text': text
            }
            
        except Exception as e:
            print(f"Receipt processing error: {e}")
            return None
