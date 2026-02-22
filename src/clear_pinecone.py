# clear_pinecone.py - Updated for new Pinecone API

import os
from pinecone import Pinecone, ServerlessSpec

# Your API key
api_key = 'pcsk_2Z2XfF_2fHGYkbAZRLjxFZcYZB7RW6cFSr9WrKxdR5pYpqkawSEKJdpxnA4UcnY3jTu7dp'
index_name = "enron-enterprise-kg"

# Initialize Pinecone with new syntax
pc = Pinecone(api_key=api_key)

# List existing indexes
print("Checking existing indexes...")
indexes = pc.list_indexes()
print(f"Found indexes: {indexes.names()}")

# Check if index exists and delete it
if index_name in indexes.names():
    print(f"Deleting existing index: {index_name}")
    pc.delete_index(index_name)
    print("✅ Index deleted successfully!")
else:
    print(f"ℹ️ Index '{index_name}' does not exist.")

print("\nYou can now run m4_upload_to_pinecone.py to create a fresh index.")