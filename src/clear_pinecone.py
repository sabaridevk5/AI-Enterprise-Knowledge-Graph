# clear_pinecone.py - FIXED & SECURED
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# 1. Load the Shield (Environment Variables)
load_dotenv() 
api_key = os.getenv("PINECONE_API_KEY")

# CRITICAL FIX: Define the index name
index_name = "enron-enterprise-kg"

# 2. Initialize Pinecone securely
if not api_key:
    print("❌ ERROR: PINECONE_API_KEY not found in .env file.")
else:
    pc = Pinecone(api_key=api_key)

    # 3. List existing indexes
    print("Checking existing indexes...")
    indexes = pc.list_indexes()
    
    # 4. Check if index exists and delete it
    if index_name in indexes.names():
        print(f"Deleting existing index: {index_name}")
        pc.delete_index(index_name)
        print("✅ Index deleted successfully!")
    else:
        print(f"ℹ️ Index '{index_name}' does not exist.")

    print("\nYou can now run m4_upload_to_pinecone.py to create a fresh index.")