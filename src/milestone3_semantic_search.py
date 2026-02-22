# milestone3_semantic_search.py - FIXED with correct data path

from sentence_transformers import SentenceTransformer
import path_config  # Auto-added for path configuration
import faiss
import numpy as np
import pandas as pd
import os
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Get the correct path - data is in parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(script_dir), 'data')
csv_path = os.path.join(data_dir, 'processed_emails.csv')

print(f"Loading data from: {csv_path}")

# Check if file exists
if not os.path.exists(csv_path):
    print(f"ERROR: File not found at {csv_path}")
    print(f"Please ensure processed_emails.csv is in: {data_dir}")
    sys.exit(1)

# Load processed data
df = pd.read_csv(csv_path).head(1000)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate Embeddings
print("Generating embeddings...")
embeddings = model.encode(df['Body'].tolist(), show_progress_bar=True)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))
print(f"Indexed {len(df)} documents with {embeddings.shape[1]}-dimension vectors\n")

def ask_intelligence_system(query):
    print(f"\nSearching for: '{query}'")
    q_emb = model.encode([query])
    D, I = index.search(np.array(q_emb), k=1)
    result = df.iloc[I[0][0]]
    print("\n" + "="*60)
    print("TOP MATCH FOUND:")
    print("="*60)
    print(f"From: {result['From']}")
    print(f"Subject: {result['Subject']}")
    print(f"Body: {result['Body'][:200]}...")
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = input("\nEnter your search query: ")
    ask_intelligence_system(query)