# 💰 Personal Finance Assistant

A modern, full-stack web application for tracking personal finances with advanced features including receipt scanning, analytics, and intelligent categorization.

## ✨ Features

### Core Functionality
- **Transaction Management**: Add, edit, delete, and view income/expense transactions
- **Smart Categorization**: Automatic categorization with custom category support
- **Advanced Filtering**: Filter transactions by date range, type, and category
- **Real-time Analytics**: Interactive charts and financial summaries

### Advanced Features
- **Receipt Scanner**: OCR-powered receipt processing with automatic transaction extraction
- **Dashboard Analytics**: Visual insights with Chart.js integration
- **Responsive Design**: Modern UI with glassmorphism effects and smooth animations
- **Data Export**: Export transactions for external analysis
- **Pagination**: Efficient handling of large transaction datasets

### Technical Features
- **REST API**: Complete backend API with MongoDB integration
- **File Upload**: Support for multiple image formats and PDFs
- **Error Handling**: Comprehensive error handling and user feedback
- **Real-time Updates**: Auto-refresh functionality

## 🛠️ Tech Stack

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Vanilla JS with ES6+ features
- **Chart.js**: Interactive data visualizations
- **CSS Grid/Flexbox**: Advanced layout system

### Backend
- **Python 3.8+**: Core backend language
- **Flask**: Web framework
- **MongoDB**: NoSQL database
- **PyMongo**: MongoDB Python driver

### Additional Libraries
- **Flask-CORS**: Cross-origin resource sharing
- **Werkzeug**: File handling utilities
- **Pillow**: Image processing
- **PyPDF2**: PDF text extraction
- **EasyOCR**: OCR functionality

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running
- Tesseract OCR engine (for receipt scanning)

### Step 1: Clone the Repository
```bash
git clone https://github.com/AnilKumarK26/Personal_Finance.git
cd Personal_Finance
```

### Step 2: Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure MongoDB
Ensure MongoDB is running on `localhost:27017` (default port).

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
personal-finance-assistant/
├── app.py                 # Main Flask application
├── database.py
├── ocr_processor.py
├── analytics.py   
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── uploads/              # Receipt upload directory
├── templates/
│   ├── index.html        # Main frontend application
│   └── styles.css        # Additional styles (optional)

```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=personal_finance

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes

```

### Database Setup
The application will automatically create the necessary collections in MongoDB:
- `transactions`: Stores all financial transactions
- `categories`: Stores transaction categories (auto-generated)

## 📊 API Documentation

### Transactions

#### Get All Transactions
```http
GET /api/transactions
```

**Query Parameters:**
- `start_date` (optional): Filter by start date (YYYY-MM-DD)
- `end_date` (optional): Filter by end date (YYYY-MM-DD)
- `type` (optional): Filter by type (income/expense)
- `category` (optional): Filter by category

#### Create Transaction
```http
POST /api/transactions
```

**Request Body:**
```json
{
  "type": "expense",
  "amount": 25.50,
  "category": "Food",
  "description": "Lunch at restaurant",
  "date": "2024-01-15"
}
```

#### Update Transaction
```http
PUT /api/transactions/{id}
```

#### Delete Transaction
```http
DELETE /api/transactions/{id}
```

### Analytics

#### Get Summary
```http
GET /api/analytics/summary
```

**Response:**
```json
{
  "total_income": 5000.00,
  "total_expenses": 3500.00,
  "net_balance": 1500.00,
  "income_count": 12,
  "expense_count": 45
}
```

#### Get Expenses by Category
```http
GET /api/analytics/expenses-by-category
```

### Receipt Processing

#### Upload Receipt
```http
POST /api/upload-receipt
```

**Request:** Multipart form data with file

**Response:**
```json
{
  "extracted_text": "Receipt text...",
  "parsed_info": {
    "merchant": "Store Name",
    "total_amount": 25.50,
    "date": "2024-01-15",
    "items": ["Item 1", "Item 2"]
  },
  "suggested_transaction": {
    "type": "expense",
    "amount": 25.50,
    "category": "Shopping",
    "description": "Purchase at Store Name",
    "date": "2024-01-15"
  }
}
```

### 🐛 Known Issues
- Receipt OCR accuracy depends on image quality

- Large file uploads may take time to process

- Charts require modern browser support

