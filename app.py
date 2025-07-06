# from flask import Flask, request, jsonify, render_template, send_from_directory
# from flask_cors import CORS
# from pymongo import MongoClient
# from bson import ObjectId
# from datetime import datetime, timedelta
# import os
# import json
# import re
# from werkzeug.utils import secure_filename
# import easyocr
# import PyPDF2
# from PIL import Image
# import cv2
# import numpy as np
# import io
# import base64

# app = Flask(__name__)
# CORS(app)

# # MongoDB Configuration
# client = MongoClient('mongodb://localhost:27017/')
# db = client['personal_finance']
# transactions_collection = db['transactions']

# # File upload configuration
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'pdf'}
# MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# # Initialize EasyOCR reader globally for better performance
# try:
#     ocr_reader = easyocr.Reader(['en'])
#     print("EasyOCR initialized successfully")
# except Exception as e:
#     print(f"Error initializing EasyOCR: {e}")
#     ocr_reader = None

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def serialize_transaction(transaction):
#     """Convert MongoDB document to JSON serializable format"""
#     if transaction:
#         transaction['_id'] = str(transaction['_id'])
#         if 'date' in transaction and isinstance(transaction['date'], datetime):
#             transaction['date'] = transaction['date'].isoformat()
#     return transaction

# def preprocess_image(image_path):
#     """Preprocess image for better OCR accuracy"""
#     try:
#         # Read image
#         img = cv2.imread(image_path)
#         if img is None:
#             return image_path
        
#         # Convert to grayscale
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
#         # Apply Gaussian blur to reduce noise
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
#         # Apply adaptive threshold for better text detection
#         thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
#                                      cv2.THRESH_BINARY, 11, 2)
        
#         # Remove noise using morphological operations
#         kernel = np.ones((1, 1), np.uint8)
#         processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
#         # Save preprocessed image
#         processed_path = image_path.replace('.', '_processed.')
#         cv2.imwrite(processed_path, processed)
        
#         return processed_path
#     except Exception as e:
#         print(f"Error preprocessing image: {e}")
#         return image_path

# def extract_text_from_image(image_path):
#     """Extract text from image using EasyOCR"""
#     try:
#         if ocr_reader is None:
#             return "EasyOCR not initialized"
        
#         # Preprocess image for better accuracy
#         processed_path = preprocess_image(image_path)
        
#         # Extract text using EasyOCR
#         results = ocr_reader.readtext(processed_path, detail=0)
        
#         # Clean up processed image if it was created
#         if processed_path != image_path and os.path.exists(processed_path):
#             os.remove(processed_path)
        
#         # Join all detected text
#         extracted_text = ' '.join(results)
        
#         print(f"EasyOCR extracted text: {extracted_text[:100]}...")
#         return extracted_text
        
#     except Exception as e:
#         print(f"Error extracting text from image with EasyOCR: {e}")
#         return f"Error: {str(e)}"

# def extract_text_from_pdf(pdf_path):
#     """Extract text from PDF using PyPDF2"""
#     try:
#         text = ""
        
#         with open(pdf_path, 'rb') as file:
#             pdf_reader = PyPDF2.PdfReader(file)
            
#             # Extract text from all pages
#             for page_num in range(len(pdf_reader.pages)):
#                 page = pdf_reader.pages[page_num]
#                 page_text = page.extract_text()
#                 text += page_text + "\n"
        
#         # If we got substantial text, return it
#         if len(text.strip()) > 50:
#             print(f"PyPDF2 extracted text: {text[:100]}...")
#             return text.strip()
        
#         # If text extraction failed (scanned PDF), try OCR on PDF
#         print("PDF appears to be scanned, attempting OCR...")
#         return extract_text_from_scanned_pdf(pdf_path)
        
#     except Exception as e:
#         print(f"Error extracting text from PDF with PyPDF2: {e}")
#         return f"Error: {str(e)}"

# def extract_text_from_scanned_pdf(pdf_path):
#     """Extract text from scanned PDF using EasyOCR"""
#     try:
#         if ocr_reader is None:
#             return "EasyOCR not initialized for scanned PDF"
        
#         # For scanned PDFs, we need to convert to images first
#         # This is a simplified approach - in production, you might want to use pdf2image
#         import fitz  # PyMuPDF
        
#         doc = fitz.open(pdf_path)
#         text = ""
        
#         for page_num in range(len(doc)):
#             page = doc.load_page(page_num)
            
#             # Convert page to image
#             pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
#             img_data = pix.tobytes("png")
            
#             # Save temporary image
#             temp_img_path = f"temp_page_{page_num}.png"
#             with open(temp_img_path, "wb") as img_file:
#                 img_file.write(img_data)
            
#             # Extract text using EasyOCR
#             results = ocr_reader.readtext(temp_img_path, detail=0)
#             page_text = ' '.join(results)
#             text += page_text + "\n"
            
#             # Clean up temporary image
#             os.remove(temp_img_path)
        
#         doc.close()
#         return text.strip()
        
#     except ImportError:
#         return "PyMuPDF not installed - cannot process scanned PDFs"
#     except Exception as e:
#         print(f"Error extracting text from scanned PDF: {e}")
#         return f"Error: {str(e)}"

# def parse_receipt_text(text):
#     """Parse receipt text to extract relevant information"""
#     if not text or text.startswith("Error"):
#         return {
#             'merchant': '',
#             'total_amount': 0.0,
#             'date': '',
#             'items': []
#         }
    
#     lines = [line.strip() for line in text.split('\n') if line.strip()]
    
#     # Initialize parsed info
#     parsed_info = {
#         'merchant': '',
#         'total_amount': 0.0,
#         'date': '',
#         'items': []
#     }
    
#     # Extract merchant (usually first few lines that don't contain numbers)
#     for line in lines[:5]:
#         if line and not re.search(r'\d', line) and len(line) > 3:
#             parsed_info['merchant'] = line
#             break
    
#     # Extract total amount with improved patterns
#     amount_patterns = [
#         r'total[:\s]*\$?(\d+\.?\d*)',
#         r'amount[:\s]*\$?(\d+\.?\d*)',
#         r'sum[:\s]*\$?(\d+\.?\d*)',
#         r'balance[:\s]*\$?(\d+\.?\d*)',
#         r'\$(\d+\.\d{2})',
#         r'(\d+\.\d{2})'
#     ]
    
#     for line in lines:
#         line_lower = line.lower()
#         for pattern in amount_patterns:
#             matches = re.findall(pattern, line_lower)
#             for match in matches:
#                 try:
#                     amount = float(match)
#                     # Only consider reasonable amounts (not too small, not too large)
#                     if 0.01 <= amount <= 10000 and amount > parsed_info['total_amount']:
#                         parsed_info['total_amount'] = amount
#                 except ValueError:
#                     continue
    
#     # Extract date with improved patterns
#     date_patterns = [
#         # Label-based patterns (more reliable)
#         r'receipt\s+date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#         r'date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#         r'transaction\s+date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#         r'purchase\s+date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#         r'sale\s+date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        
#         # Label-based patterns with different date formats
#         r'receipt\s+date[:\s]*(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
#         r'date[:\s]*(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
#         r'transaction\s+date[:\s]*(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        
#         # Label-based patterns with text dates
#         r'receipt\s+date[:\s]*(\d{1,2}\s+\w+\s+\d{4})',
#         r'date[:\s]*(\d{1,2}\s+\w+\s+\d{4})',
#         r'date[:\s]*(\w+\s+\d{1,2},?\s+\d{4})',
        
#         # Fallback patterns (original ones)
#         r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
#         r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
#         r'(\d{1,2}\s+\w+\s+\d{4})',
#         r'(\w+\s+\d{1,2},?\s+\d{4})'
#     ]
    
#     for line in lines:
#         for pattern in date_patterns:
#             match = re.search(pattern, line)
#             if match:
#                 parsed_info['date'] = match.group(1)
#                 break
#         if parsed_info['date']:
#             break
    
#     # Extract items (lines with prices but not totals)
#     for line in lines:
#         if re.search(r'\$?\d+\.?\d*', line) and len(line.strip()) > 3:
#             # Skip lines that look like totals
#             if not re.search(r'total|sum|amount|balance', line.lower()):
#                 parsed_info['items'].append(line.strip())
    
#     return parsed_info

# def suggest_transaction_from_receipt(parsed_info):
#     """Suggest transaction details based on parsed receipt info"""
#     # Determine category based on merchant name
#     merchant = parsed_info['merchant'].lower()
#     category = 'General'
    
#     # Enhanced category detection
#     category_keywords = {
#         'Groceries': ['grocery', 'market', 'food', 'supermarket', 'walmart', 'target', 'costco'],
#         'Dining': ['restaurant', 'cafe', 'pizza', 'burger', 'mcdonald', 'subway', 'starbucks'],
#         'Transportation': ['gas', 'fuel', 'shell', 'exxon', 'mobil', 'chevron', 'uber', 'lyft'],
#         'Healthcare': ['pharmacy', 'cvs', 'walgreens', 'hospital', 'clinic', 'medical'],
#         'Shopping': ['store', 'mall', 'amazon', 'ebay', 'shop', 'retail'],
#         'Entertainment': ['movie', 'theater', 'cinema', 'netflix', 'spotify', 'game'],
#         'Utilities': ['electric', 'water', 'gas', 'internet', 'phone', 'cable']
#     }
    
#     for cat, keywords in category_keywords.items():
#         if any(keyword in merchant for keyword in keywords):
#             category = cat
#             break
    
#     # Format date
#     receipt_date = parsed_info['date']
#     if receipt_date:
#         try:
#             # Try to parse and format date
#             if '/' in receipt_date:
#                 parts = receipt_date.split('/')
#                 if len(parts) == 3:
#                     month, day, year = parts
#                     if len(year) == 2:
#                         year = '20' + year
#                     receipt_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
#             elif '-' in receipt_date:
#                 # Already in YYYY-MM-DD format
#                 pass
#         except:
#             receipt_date = datetime.now().strftime('%Y-%m-%d')
#     else:
#         receipt_date = datetime.now().strftime('%Y-%m-%d')
    
#     return {
#         'type': 'expense',
#         'amount': parsed_info['total_amount'] if parsed_info['total_amount'] > 0 else 0.0,
#         'category': category,
#         'description': f"Receipt from {parsed_info['merchant']}" if parsed_info['merchant'] else "Receipt purchase",
#         'date': receipt_date
#     }

# # Keep all your existing routes (transactions, analytics, etc.) unchanged
# @app.route('/api/transactions', methods=['GET'])
# def get_transactions():
#     try:
#         # Get query parameters
#         start_date = request.args.get('start_date')
#         end_date = request.args.get('end_date')
#         transaction_type = request.args.get('type')
#         category = request.args.get('category')
        
#         # Build query
#         query = {}
        
#         if start_date or end_date:
#             date_query = {}
#             if start_date:
#                 date_query['$gte'] = datetime.fromisoformat(start_date)
#             if end_date:
#                 date_query['$lte'] = datetime.fromisoformat(end_date)
#             query['date'] = date_query
        
#         if transaction_type:
#             query['type'] = transaction_type
        
#         if category:
#             query['category'] = category
        
#         # Get transactions
#         transactions = list(transactions_collection.find(query).sort('date', -1))
        
#         # Serialize transactions
#         serialized_transactions = [serialize_transaction(t) for t in transactions]
        
#         return jsonify({
#             'transactions': serialized_transactions,
#             'count': len(serialized_transactions)
#         })
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/transactions', methods=['POST'])
# def create_transaction():
#     try:
#         data = request.get_json()
        
#         # Validate required fields
#         required_fields = ['type', 'amount', 'category', 'description', 'date']
#         for field in required_fields:
#             if field not in data:
#                 return jsonify({'error': f'Missing required field: {field}'}), 400
        
#         # Create transaction document
#         transaction = {
#             'type': data['type'],
#             'amount': float(data['amount']),
#             'category': data['category'],
#             'description': data['description'],
#             'date': datetime.fromisoformat(data['date']),
#             'created_at': datetime.utcnow()
#         }
        
#         # Insert transaction
#         result = transactions_collection.insert_one(transaction)
        
#         # Return created transaction
#         created_transaction = transactions_collection.find_one({'_id': result.inserted_id})
#         return jsonify({
#             'transaction': serialize_transaction(created_transaction),
#             'message': 'Transaction created successfully'
#         }), 201
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/transactions/<transaction_id>', methods=['PUT'])
# def update_transaction(transaction_id):
#     try:
#         data = request.get_json()
        
#         # Validate ObjectId
#         if not ObjectId.is_valid(transaction_id):
#             return jsonify({'error': 'Invalid transaction ID'}), 400
        
#         # Prepare update data
#         update_data = {}
#         if 'type' in data:
#             update_data['type'] = data['type']
#         if 'amount' in data:
#             update_data['amount'] = float(data['amount'])
#         if 'category' in data:
#             update_data['category'] = data['category']
#         if 'description' in data:
#             update_data['description'] = data['description']
#         if 'date' in data:
#             update_data['date'] = datetime.fromisoformat(data['date'])
        
#         update_data['updated_at'] = datetime.utcnow()
        
#         # Update transaction
#         result = transactions_collection.update_one(
#             {'_id': ObjectId(transaction_id)},
#             {'$set': update_data}
#         )
        
#         if result.matched_count == 0:
#             return jsonify({'error': 'Transaction not found'}), 404
        
#         # Return updated transaction
#         updated_transaction = transactions_collection.find_one({'_id': ObjectId(transaction_id)})
#         return jsonify({
#             'transaction': serialize_transaction(updated_transaction),
#             'message': 'Transaction updated successfully'
#         })
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/transactions/<transaction_id>', methods=['DELETE'])
# def delete_transaction(transaction_id):
#     try:
#         # Validate ObjectId
#         if not ObjectId.is_valid(transaction_id):
#             return jsonify({'error': 'Invalid transaction ID'}), 400
        
#         # Delete transaction
#         result = transactions_collection.delete_one({'_id': ObjectId(transaction_id)})
        
#         if result.deleted_count == 0:
#             return jsonify({'error': 'Transaction not found'}), 404
        
#         return jsonify({'message': 'Transaction deleted successfully'})
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/categories', methods=['GET'])
# def get_categories():
#     try:
#         # Get unique categories
#         categories = transactions_collection.distinct('category')
#         return jsonify({'categories': sorted(categories)})
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/analytics/summary', methods=['GET'])
# def get_summary():
#     try:
#         # Get current month date range
#         now = datetime.now()
#         start_of_month = datetime(now.year, now.month, 1)
        
#         # Aggregate summary data
#         pipeline = [
#             {'$match': {'date': {'$gte': start_of_month}}},
#             {'$group': {
#                 '_id': '$type',
#                 'total': {'$sum': '$amount'},
#                 'count': {'$sum': 1}
#             }}
#         ]
        
#         results = list(transactions_collection.aggregate(pipeline))
        
#         # Process results
#         summary = {
#             'total_income': 0,
#             'total_expenses': 0,
#             'net_balance': 0,
#             'income_count': 0,
#             'expense_count': 0
#         }
        
#         for result in results:
#             if result['_id'] == 'income':
#                 summary['total_income'] = result['total']
#                 summary['income_count'] = result['count']
#             elif result['_id'] == 'expense':
#                 summary['total_expenses'] = result['total']
#                 summary['expense_count'] = result['count']
        
#         summary['net_balance'] = summary['total_income'] - summary['total_expenses']
        
#         return jsonify(summary)
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/analytics/income-vs-expense', methods=['GET'])
# def get_income_vs_expense():
#     try:
#         # Get current month data
#         now = datetime.now()
#         start_of_month = datetime(now.year, now.month, 1)
        
#         pipeline = [
#             {'$match': {'date': {'$gte': start_of_month}}},
#             {'$group': {
#                 '_id': '$type',
#                 'total': {'$sum': '$amount'}
#             }}
#         ]
        
#         results = list(transactions_collection.aggregate(pipeline))
        
#         data = {'income': 0, 'expense': 0}
#         for result in results:
#             data[result['_id']] = result['total']
        
#         return jsonify(data)
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/analytics/monthly-trend', methods=['GET'])
# def get_monthly_trend():
#     try:
#         # Get last 6 months data
#         end_date = datetime.now()
#         start_date = end_date - timedelta(days=180)
        
#         pipeline = [
#             {'$match': {'date': {'$gte': start_date, '$lte': end_date}}},
#             {'$group': {
#                 '_id': {
#                     'year': {'$year': '$date'},
#                     'month': {'$month': '$date'},
#                     'type': '$type'
#                 },
#                 'total': {'$sum': '$amount'}
#             }},
#             {'$sort': {'_id.year': 1, '_id.month': 1}}
#         ]
        
#         results = list(transactions_collection.aggregate(pipeline))
        
#         # Process results into monthly data
#         monthly_data = {}
#         for result in results:
#             month_key = f"{result['_id']['year']}-{result['_id']['month']:02d}"
#             if month_key not in monthly_data:
#                 monthly_data[month_key] = {'income': 0, 'expense': 0}
#             monthly_data[month_key][result['_id']['type']] = result['total']
        
#         return jsonify(monthly_data)
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/analytics/category-breakdown', methods=['GET'])
# def get_category_breakdown():
#     try:
#         pipeline = [
#             {'$match': {'type': 'expense'}},
#             {'$group': {
#                 '_id': '$category',
#                 'total_amount': {'$sum': '$amount'},
#                 'count': {'$sum': 1},
#                 'avg_amount': {'$avg': '$amount'}
#             }},
#             {'$sort': {'total_amount': -1}}
#         ]
        
#         results = list(transactions_collection.aggregate(pipeline))
        
#         return jsonify({
#             'categories': [r['_id'] for r in results],
#             'amounts': [r['total_amount'] for r in results],
#             'counts': [r['count'] for r in results],
#             'averages': [r['avg_amount'] for r in results]
#         })
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/analytics/expenses-by-category', methods=['GET'])
# def get_expenses_by_category():
#     try:
#         # Get date range (default to current month)
#         start_date = request.args.get('start_date')
#         end_date = request.args.get('end_date')
        
#         # Build date query
#         date_query = {}
#         if start_date:
#             date_query['$gte'] = datetime.fromisoformat(start_date)
#         else:
#             # Default to current month
#             now = datetime.now()
#             date_query['$gte'] = datetime(now.year, now.month, 1)
        
#         if end_date:
#             date_query['$lte'] = datetime.fromisoformat(end_date)
        
#         # Aggregate expenses by category
#         pipeline = [
#             {'$match': {
#                 'type': 'expense',
#                 'date': date_query
#             }},
#             {'$group': {
#                 '_id': '$category',
#                 'total_amount': {'$sum': '$amount'},
#                 'count': {'$sum': 1}
#             }},
#             {'$sort': {'total_amount': -1}}
#         ]
        
#         results = list(transactions_collection.aggregate(pipeline))
        
#         # Format data for chart
#         categories = []
#         amounts = []
        
#         for result in results:
#             categories.append(result['_id'])
#             amounts.append(result['total_amount'])
        
#         return jsonify({
#             'categories': categories,
#             'amounts': amounts,
#             'total_categories': len(categories),
#             'total_amount': sum(amounts)
#         })
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @app.route('/api/analytics/daily-expenses', methods=['GET'])
# def get_daily_expenses():
#     try:
#         # Get last 30 days
#         end_date = datetime.now()
#         start_date = end_date - timedelta(days=30)
        
#         pipeline = [
#             {'$match': {
#                 'type': 'expense',
#                 'date': {'$gte': start_date, '$lte': end_date}
#             }},
#             {'$group': {
#                 '_id': {
#                     'year': {'$year': '$date'},
#                     'month': {'$month': '$date'},
#                     'day': {'$dayOfMonth': '$date'}
#                 },
#                 'total_amount': {'$sum': '$amount'}
#             }},
#             {'$sort': {'_id.year': 1, '_id.month': 1, '_id.day': 1}}
#         ]
        
#         results = list(transactions_collection.aggregate(pipeline))
        
#         # Create complete date range with zeros for missing days
#         daily_data = {}
#         current_date = start_date
#         while current_date <= end_date:
#             date_key = current_date.strftime('%Y-%m-%d')
#             daily_data[date_key] = 0
#             current_date += timedelta(days=1)
        
#         # Fill in actual data
#         for result in results:
#             date_key = f"{result['_id']['year']}-{result['_id']['month']:02d}-{result['_id']['day']:02d}"
#             daily_data[date_key] = result['total_amount']
        
#         return jsonify({
#             'dates': list(daily_data.keys()),
#             'amounts': list(daily_data.values())
#         })
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/upload-receipt', methods=['POST'])
# def upload_receipt():
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400
        
#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400
        
#         if not allowed_file(file.filename):
#             return jsonify({'error': 'File type not allowed'}), 400
        
#         # Save file
#         filename = secure_filename(file.filename)
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
#         filename = timestamp + filename
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         try:
#             # Extract text based on file type
#             if filename.lower().endswith('.pdf'):
#                 print(f"Processing PDF: {filename}")
#                 extracted_text = extract_text_from_pdf(filepath)
#             else:
#                 print(f"Processing image: {filename}")
#                 extracted_text = extract_text_from_image(filepath)
            
#             # Parse receipt information
#             parsed_info = parse_receipt_text(extracted_text)
            
#             # Suggest transaction
#             suggested_transaction = suggest_transaction_from_receipt(parsed_info)
            
#             # Clean up uploaded file
#             os.remove(filepath)
            
#             return jsonify({
#                 'extracted_text': extracted_text,
#                 'parsed_info': parsed_info,
#                 'suggested_transaction': suggested_transaction
#             })
        
#         except Exception as e:
#             # Clean up uploaded file on error
#             if os.path.exists(filepath):
#                 os.remove(filepath)
#             raise e
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/')
# def main():
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from bson import ObjectId
from datetime import datetime
import os

# Import our modules
import database
import ocr_processor
import analytics

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Transaction Routes
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        filters = {
            'start_date': request.args.get('start_date'),
            'end_date': request.args.get('end_date'),
            'type': request.args.get('type'),
            'category': request.args.get('category')
        }
        filters = {k: v for k, v in filters.items() if v}  # Remove None values
        
        transactions = database.get_transactions(filters)
        return jsonify({'transactions': transactions, 'count': len(transactions)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()
        required_fields = ['type', 'amount', 'category', 'description', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        transaction = database.create_transaction(data)
        return jsonify({'transaction': transaction, 'message': 'Transaction created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    try:
        if not ObjectId.is_valid(transaction_id):
            return jsonify({'error': 'Invalid transaction ID'}), 400
        
        data = request.get_json()
        transaction = database.update_transaction(transaction_id, data)
        
        if transaction is None:
            return jsonify({'error': 'Transaction not found'}), 404
        
        return jsonify({'transaction': transaction, 'message': 'Transaction updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        if not ObjectId.is_valid(transaction_id):
            return jsonify({'error': 'Invalid transaction ID'}), 400
        
        success = database.delete_transaction(transaction_id)
        if not success:
            return jsonify({'error': 'Transaction not found'}), 404
        
        return jsonify({'message': 'Transaction deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = database.get_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analytics Routes
@app.route('/api/analytics/summary', methods=['GET'])
def get_summary():
    try:
        summary = analytics.get_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/expenses-by-category', methods=['GET'])
def get_expenses_by_category():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        data = analytics.get_expenses_by_category(start_date, end_date)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/monthly-trend', methods=['GET'])
def get_monthly_trend():
    try:
        data = analytics.get_monthly_trend()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Upload Route
@app.route('/api/upload-receipt', methods=['POST'])
def upload_receipt():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '' or not ocr_processor.allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process file
            if filename.lower().endswith('.pdf'):
                extracted_text = ocr_processor.extract_text_from_pdf(filepath)
            else:
                extracted_text = ocr_processor.extract_text_from_image(filepath)
            
            parsed_info = ocr_processor.parse_receipt_text(extracted_text)
            suggested_transaction = ocr_processor.suggest_transaction_from_receipt(parsed_info)
            
            # Clean up
            os.remove(filepath)
            
            return jsonify({
                'extracted_text': extracted_text,
                'parsed_info': parsed_info,
                'suggested_transaction': suggested_transaction
            })
        
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            raise e
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
