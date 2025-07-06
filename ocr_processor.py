import os
import re
import cv2
import numpy as np
import easyocr
import PyPDF2
from datetime import datetime

# Initialize EasyOCR reader globally
try:
    ocr_reader = easyocr.Reader(['en'])
    print("EasyOCR initialized successfully")
except Exception as e:
    print(f"Error initializing EasyOCR: {e}")
    ocr_reader = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    """Preprocess image for better OCR accuracy"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return image_path
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        processed_path = image_path.replace('.', '_processed.')
        cv2.imwrite(processed_path, processed)
        return processed_path
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return image_path

def extract_text_from_image(image_path):
    """Extract text from image using EasyOCR"""
    try:
        if ocr_reader is None:
            return "EasyOCR not initialized"
        
        processed_path = preprocess_image(image_path)
        results = ocr_reader.readtext(processed_path, detail=0)
        
        if processed_path != image_path and os.path.exists(processed_path):
            os.remove(processed_path)
        
        extracted_text = ' '.join(results)
        print(f"EasyOCR extracted text: {extracted_text[:100]}...")
        return extracted_text
        
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return f"Error: {str(e)}"

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyPDF2"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                text += page_text + "\n"
        
        if len(text.strip()) > 50:
            print(f"PyPDF2 extracted text: {text[:100]}...")
            return text.strip()
        
        print("PDF appears to be scanned, attempting OCR...")
        return extract_text_from_scanned_pdf(pdf_path)
        
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return f"Error: {str(e)}"

def extract_text_from_scanned_pdf(pdf_path):
    """Extract text from scanned PDF using EasyOCR"""
    try:
        if ocr_reader is None:
            return "EasyOCR not initialized for scanned PDF"
        
        try:
            import fitz  # PyMuPDF
        except ImportError:
            return "PyMuPDF not installed - cannot process scanned PDFs"
        
        doc = fitz.open(pdf_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            
            temp_img_path = f"temp_page_{page_num}.png"
            with open(temp_img_path, "wb") as img_file:
                img_file.write(img_data)
            
            results = ocr_reader.readtext(temp_img_path, detail=0)
            page_text = ' '.join(results)
            text += page_text + "\n"
            
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
        
        doc.close()
        return text.strip()
        
    except Exception as e:
        print(f"Error extracting text from scanned PDF: {e}")
        return f"Error: {str(e)}"

def parse_receipt_text(text):
    """Parse receipt text to extract relevant information"""
    if not text or text.startswith("Error"):
        return {'merchant': '', 'total_amount': 0.0, 'date': '', 'items': []}
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    parsed_info = {'merchant': '', 'total_amount': 0.0, 'date': '', 'items': []}
    
    # Extract merchant (first few lines without numbers)
    for line in lines[:5]:
        if line and not re.search(r'\d', line) and len(line) > 3:
            parsed_info['merchant'] = line
            break
    
    # Extract total amount
    amount_patterns = [
        r'total[:\s]*\$?(\d+\.?\d*)', r'amount[:\s]*\$?(\d+\.?\d*)',
        r'\$(\d+\.\d{2})', r'(\d+\.\d{2})'
    ]
    
    for line in lines:
        for pattern in amount_patterns:
            matches = re.findall(pattern, line.lower())
            for match in matches:
                try:
                    amount = float(match)
                    if 0.01 <= amount <= 10000 and amount > parsed_info['total_amount']:
                        parsed_info['total_amount'] = amount
                except ValueError:
                    continue
    
    # Extract date
    date_patterns = [
        r'date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    
    for line in lines:
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match:
                parsed_info['date'] = match.group(1)
                break
        if parsed_info['date']:
            break
    
    return parsed_info

def suggest_transaction_from_receipt(parsed_info):
    """Suggest transaction details based on parsed receipt info"""
    merchant = parsed_info['merchant'].lower()
    category = 'General'
    
    # Simple category detection
    if any(word in merchant for word in ['grocery', 'market', 'food']):
        category = 'Groceries'
    elif any(word in merchant for word in ['restaurant', 'cafe', 'pizza']):
        category = 'Dining'
    elif any(word in merchant for word in ['gas', 'fuel', 'shell']):
        category = 'Transportation'
    elif any(word in merchant for word in ['pharmacy', 'cvs', 'medical']):
        category = 'Healthcare'
    
    # Format date
    receipt_date = parsed_info['date']
    if receipt_date and '/' in receipt_date:
        try:
            parts = receipt_date.split('/')
            if len(parts) == 3:
                month, day, year = parts
                if len(year) == 2:
                    year = '20' + year
                receipt_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            receipt_date = datetime.now().strftime('%Y-%m-%d')
    else:
        receipt_date = datetime.now().strftime('%Y-%m-%d')
    
    return {
        'type': 'expense',
        'amount': parsed_info['total_amount'] if parsed_info['total_amount'] > 0 else 0.0,
        'category': category,
        'description': f"Receipt from {parsed_info['merchant']}" if parsed_info['merchant'] else "Receipt purchase",
        'date': receipt_date
    }
