# import easyocr
# reader = easyocr.Reader(['en'])
# results = reader.readtext(r"C:\Users\anilk\OneDrive\Desktop\receipt-template-us-classic-white-750px.png")
# for result in results:
#     print(result[1])

# from PyPDF2 import PdfReader
# reader = PdfReader(r"C:\Users\anilk\Downloads\receipt-template-us-classic-white-750px (1).pdf")
# text = reader.pages[0].extract_text()
# for line in text.split('\n'):
#     if line.strip():  # Check if the line is not empty
#         print(line.strip())
# # This code reads a PDF file and prints each non-empty line of text.

from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

def test_atlas_connection():
    username = os.getenv('MONGODB_USERNAME')
    password = os.getenv('MONGODB_PASSWORD')
    cluster = os.getenv('MONGODB_CLUSTER')
    database_name = os.getenv('MONGODB_DATABASE')
    
    print(f"Connecting to cluster: {cluster}")
    print(f"Database: {database_name}")
    print(f"Username: {username}")
    
    connection_string = f"mongodb+srv://{username}:{password}@{cluster}.wt5v2.mongodb.net/?retryWrites=true&w=majority&appName={database_name}"
    
    try:
        client = MongoClient(connection_string)
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Test database access
        db = client[database_name]
        collections = db.list_collection_names()
        print(f"Available collections: {collections}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_atlas_connection()


