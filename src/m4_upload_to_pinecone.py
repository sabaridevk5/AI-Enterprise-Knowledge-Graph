# m4_upload_to_pinecone.py - Updated with free tier region

import os
import path_config
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import sys
import hashlib
import time

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 1. Set your Pinecone API Key
api_key = 'pcsk_2Z2XfF_2fHGYkbAZRLjxFZcYZB7RW6cFSr9WrKxdR5pYpqkawSEKJdpxnA4UcnY3jTu7dp'
os.environ['PINECONE_API_KEY'] = api_key
index_name = "enron-enterprise-kg"

# Initialize Pinecone with new syntax
pc = Pinecone(api_key=api_key)

def create_index_if_not_exists():
    """Create Pinecone index if it doesn't exist"""
    # List available indexes
    indexes = pc.list_indexes().names()
    print(f"Existing indexes: {indexes}")
    
    if index_name not in indexes:
        print(f"Creating new index: {index_name}")
        
        # Free tier supported regions:
        # - aws: us-east-1, us-west-1, eu-west-1, etc.
        # Let's use us-east-1 which is commonly supported
        pc.create_index(
            name=index_name,
            dimension=384,  # all-MiniLM-L6-v2 has 384 dimensions
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'  # Changed from us-west-2 to us-east-1 (free tier)
            )
        )
        # Wait for index to be ready
        print("Waiting for index to initialize...")
        time.sleep(15)
        print("✅ Index created successfully!")
    else:
        print(f"ℹ️ Index '{index_name}' already exists")

def remove_duplicate_emails(df):
    """Remove duplicate emails based on content hash"""
    print(f"Initial rows: {len(df)}")
    
    # Create a content hash for deduplication
    df['content_hash'] = df['Body'].astype(str).apply(
        lambda x: hashlib.md5(x.encode('utf-8', errors='ignore')).hexdigest()
    )
    
    # Drop duplicates based on hash
    df_unique = df.drop_duplicates(subset=['content_hash'], keep='first')
    
    # Also drop exact duplicates in From/To/Subject/Body combination
    df_unique = df_unique.drop_duplicates(
        subset=['From', 'To', 'Subject', 'Body'], 
        keep='first'
    )
    
    print(f"After deduplication: {len(df_unique)} rows")
    return df_unique

def upload_to_cloud():
    print("--- Enterprise Cloud Upload Started ---")
    
    # Create index if needed (with correct region)
    create_index_if_not_exists()
    
    # Get the correct path
    csv_path = path_config.PROCESSED_EMAILS_CSV
    print(f"Loading data from: {csv_path}")
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found at {csv_path}")
        return
    
    # 2. Load and deduplicate the data
    print("Loading and deduplicating data...")
    df = pd.read_csv(csv_path)
    
    # Remove rows with missing Body
    df = df.dropna(subset=['Body'])
    
    # Remove duplicates
    df = remove_duplicate_emails(df)
    
    # Take sample (500 unique emails)
    df = df.head(500).fillna("")
    
    print(f"Final upload count: {len(df)} unique emails")
    
    # 3. Prepare the text and metadata
    texts = df['Body'].astype(str).tolist()
    metadatas = []
    ids = []
    
    for idx, row in df.iterrows():
        # Create unique ID
        email_id = hashlib.md5(
            f"{row.get('From', '')}_{row.get('To', '')}_{row.get('Subject', '')}_{idx}".encode()
        ).hexdigest()[:16]
        
        ids.append(email_id)
        metadatas.append({
            'From': str(row.get('From', ''))[:100],
            'To': str(row.get('To', ''))[:100],
            'Subject': str(row.get('Subject', ''))[:100],
            'Date': str(row.get('Date', ''))[:50],
            'email_id': email_id
        })

    # 4. Initialize the Local AI Model
    print("Loading the all-MiniLM-L6-v2 embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 5. Push everything to Pinecone
    print(f"Uploading {len(texts)} unique vectors to Pinecone index: '{index_name}'...")
    print("This might take a minute...")
    
    # Create vector store with unique IDs to prevent duplicates
    vectorstore = PineconeVectorStore.from_texts(
        texts=texts,
        embedding=embeddings,
        index_name=index_name,
        metadatas=metadatas,
        ids=ids  # Use unique IDs
    )
    
    # Verify upload
    print("\n" + "="*50)
    print("✅ Upload Complete!")
    print(f"📊 Uploaded {len(texts)} unique emails to Pinecone")
    print(f"📁 Index name: {index_name}")
    print("="*50)
    
    # Show index stats
    try:
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        print(f"\n📊 Index Statistics:")
        print(f"   Total vectors: {stats.total_vector_count}")
        print(f"   Dimension: {stats.dimension}")
    except:
        print("\nℹ️ Index stats will be available in a few minutes")

if __name__ == "__main__":
    upload_to_cloud()