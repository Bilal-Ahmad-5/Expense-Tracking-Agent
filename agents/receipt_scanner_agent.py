"""
Receipt Scanner Agent - Specialized AI agent for OCR processing and data extraction
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
from datetime import datetime
from crewai import Agent, Task
from langchain_groq import ChatGroq
import json


class RecieptObject(BaseModel):
    merchant: str = Field(description="Extracted merchant from reciept text")
    amount: float = Field(description="Extracted amount on reciept")
    date: int = Field(
        description="Extracted date of transaction from reciept text")
    items: str = Field(description="Extracted items from reciept text")
    categery: str = Field(description="Extracted categery from reciept text")


class ReceiptScannerAgent:

    def __init__(self, groq_api_key):
        self.llm = ChatGroq(
            temperature=0.1,
            groq_api_key=groq_api_key,
            model_name="llama-3.1-70b-versatile").bind_tools(RecieptObject)

        self.agent = Agent(
            role='Receipt Processing Specialist',
            goal=
            'Extract structured data from receipt images with maximum accuracy',
            backstory=
            """You are an expert OCR specialist with years of experience in 
                        retail and financial document processing. You excel at extracting 
                        precise information from receipts, invoices, and financial documents.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False)

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

    def ai_enhanced_extraction(self, raw_text):
        """Use AI to enhance and structure the extracted data"""
        task = Task(description=f"""
            Analyze this OCR text from a receipt and extract structured information:
            
            Raw OCR Text:
            {raw_text}
            
            Extract and return a JSON object with these fields:
            - merchant: Store/business name
            - amount: Total amount (as float)
            - date: Date in YYYY-MM-DD format
            - items: List of purchased items
            - category_hints: Likely expense category based on merchant/items
            
            Focus on accuracy. If information is unclear, mark as null.
            Return only valid JSON.
            """,
                    agent=self.agent,
                    expected_output="JSON object with extracted receipt data")

        result = self.agent.execute(task)
        try:
            return {
                "merchant":
                result["merchant"],
                "amount":
                result["amount"],
                "date":
                result["date"],
                "items":
                result["items"],
                "category_hints":
                self._guess_category(result["merchant"], result["items"])
            }
        except Exception as e:
            print(f"AI extraction error: {e}")

    def _guess_category(self, merchant, items):
        """Provide category hints based on merchant and items"""
        merchant_lower = merchant.lower()
        items_text = " ".join(items).lower()

        category_keywords = {
            "Food & Dining": [
                "restaurant", "cafe", "starbucks", "mcdonalds", "pizza",
                "food", "grocery"
            ],
            "Shopping":
            ["walmart", "target", "amazon", "clothing", "mall", "store"],
            "Transportation":
            ["gas", "fuel", "shell", "exxon", "bp", "chevron", "uber", "taxi"],
            "Entertainment":
            ["movie", "theater", "game", "concert", "entertainment"],
            "Healthcare":
            ["pharmacy", "cvs", "walgreens", "hospital", "medical", "health"],
            "Utilities":
            ["electric", "water", "internet", "phone", "cable", "utility"]
        }

        for category, keywords in category_keywords.items():
            if any(keyword in merchant_lower or keyword in items_text
                   for keyword in keywords):
                return category

        return "Other"

    def process_receipt(self, image):
        """Main method to process a receipt image"""
        try:
            # Extract text using OCR
            raw_text = self.extract_text_with_ocr(image)

            if not raw_text:
                return None

            # Use AI to enhance extraction
            structured_data = self.ai_enhanced_extraction(raw_text)

            if structured_data:
                structured_data['raw_text'] = raw_text
                structured_data['processing_method'] = 'ai_enhanced'

            return structured_data

        except Exception as e:
            print(f"Receipt processing error: {e}")
            return None
