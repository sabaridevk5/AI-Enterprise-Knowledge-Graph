# m4_upload_to_pinecone.py - SECURED & BLINDED
import os
import path_config
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import sys
import hashlib
import time
from dotenv import load_dotenv  # Added for security

# 1. Load the Shield (Environment Variables)
load_dotenv()

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 2. Get Pinecone API Key securely from .env
api_key = os.getenv('PINECONE_API_KEY')

if not api_key:
    print("❌ ERROR: PINECONE_API_KEY not found in .env file.")
    sys.exit(1)

os.environ['PINECONE_API_KEY'] = api_key
index_name = "enron-enterprise-kg"

# Initialize Pinecone with secure key
pc = Pinecone(api_key=api_key)

def create_index_if_not_exists():
    """Create Pinecone index if it doesn't exist"""
    indexes = pc.list_indexes().names()
    print(f"Existing indexes: {indexes}")
    
    if index_name not in indexes:
        print(f"Creating new index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        print("Waiting for index to initialize...")
        time.sleep(15)
        print("✅ Index created successfully!")
    else:
        print(f"ℹ️ Index '{index_name}' already exists")

def remove_duplicate_emails(df):
    """Remove duplicate emails based on content hash"""
    print(f"Initial rows: {len(df)}")
    df['content_hash'] = df['Body'].astype(str).apply(
        lambda x: hashlib.md5(x.encode('utf-8', errors='ignore')).hexdigest()
    )
    df_unique = df.drop_duplicates(subset=['content_hash'], keep='first')
    df_unique = df_unique.drop_duplicates(
        subset=['From', 'To', 'Subject', 'Body'], 
        keep='first'
    )
    print(f"After deduplication: {len(df_unique)} rows")
    return df_unique

def upload_to_cloud():
    print("--- Enterprise Cloud Upload Started ---")
    create_index_if_not_exists()
    
    csv_path = path_config.PROCESSED_EMAILS_CSV
    print(f"Loading data from: {csv_path}")
    
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found at {csv_path}")
        return
    
    print("Loading and deduplicating data...")
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['Body'])
    df = remove_duplicate_emails(df)
    df = df.head(500).fillna("")
    
    print(f"Final upload count: {len(df)} unique emails")
    
    texts = df['Body'].astype(str).tolist()
    metadatas = []
    ids = []
    
    for idx, row in df.iterrows():
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

    print("Loading the all-MiniLM-L6-v2 embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print(f"Uploading {len(texts)} unique vectors to Pinecone index: '{index_name}'...")
    
    vectorstore = PineconeVectorStore.from_texts(
        texts=texts,
        embedding=embeddings,
        index_name=index_name,
        metadatas=metadatas,
        ids=ids
    )
    
    print("\n" + "="*50)
    print("✅ Upload Complete!")
    print("="*50)

if __name__ == "__main__":
    upload_to_cloud()