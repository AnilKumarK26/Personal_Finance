from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from bson import ObjectId
from datetime import datetime
import os

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

