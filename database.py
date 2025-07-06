from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Atlas Configuration using environment variables
MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_CLUSTER = os.getenv('MONGODB_CLUSTER')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'personal_finance')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'transactions')

# Construct connection string
connection_string = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName=personal_finance"

# Initialize MongoDB connection
try:
    client = MongoClient(connection_string)
    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
    db = client[MONGODB_DATABASE]
    transactions_collection = db[MONGODB_COLLECTION]
    print("Database and collection initialized successfully")
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {e}")
    db = None
    transactions_collection = None

def serialize_transaction(transaction):
    """Convert MongoDB document to JSON serializable format"""
    if transaction:
        transaction['_id'] = str(transaction['_id'])
        if 'date' in transaction and isinstance(transaction['date'], datetime):
            transaction['date'] = transaction['date'].isoformat()
    return transaction

def get_transactions(filters=None):
    """Get transactions with optional filters"""
    if transactions_collection is None:
        raise Exception("Database not connected")
    
    query = {}
    
    if filters:
        if filters.get('start_date') or filters.get('end_date'):
            date_query = {}
            if filters.get('start_date'):
                date_query['$gte'] = datetime.fromisoformat(filters['start_date'])
            if filters.get('end_date'):
                date_query['$lte'] = datetime.fromisoformat(filters['end_date'])
            query['date'] = date_query
        
        if filters.get('type'):
            query['type'] = filters['type']
        if filters.get('category'):
            query['category'] = filters['category']
    
    transactions = list(transactions_collection.find(query).sort('date', -1))
    return [serialize_transaction(t) for t in transactions]

def create_transaction(data):
    """Create new transaction"""
    if transactions_collection is None:
        raise Exception("Database not connected")
    
    transaction = {
        'type': data['type'],
        'amount': float(data['amount']),
        'category': data['category'],
        'description': data['description'],
        'date': datetime.fromisoformat(data['date']),
        'created_at': datetime.utcnow()
    }
    result = transactions_collection.insert_one(transaction)
    created_transaction = transactions_collection.find_one({'_id': result.inserted_id})
    return serialize_transaction(created_transaction)

def update_transaction(transaction_id, data):
    """Update transaction"""
    if transactions_collection is None:
        raise Exception("Database not connected")
    
    update_data = {}
    if 'type' in data:
        update_data['type'] = data['type']
    if 'amount' in data:
        update_data['amount'] = float(data['amount'])
    if 'category' in data:
        update_data['category'] = data['category']
    if 'description' in data:
        update_data['description'] = data['description']
    if 'date' in data:
        update_data['date'] = datetime.fromisoformat(data['date'])
    
    update_data['updated_at'] = datetime.utcnow()
    
    result = transactions_collection.update_one(
        {'_id': ObjectId(transaction_id)},
        {'$set': update_data}
    )
    
    if result.matched_count == 0:
        return None
    
    updated_transaction = transactions_collection.find_one({'_id': ObjectId(transaction_id)})
    return serialize_transaction(updated_transaction)

def delete_transaction(transaction_id):
    """Delete transaction"""
    if transactions_collection is None:
        raise Exception("Database not connected")
    
    result = transactions_collection.delete_one({'_id': ObjectId(transaction_id)})
    return result.deleted_count > 0

def get_categories():
    """Get unique categories"""
    if transactions_collection is None:
        raise Exception("Database not connected")
    
    return sorted(transactions_collection.distinct('category'))