from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd

# Load processed data
df = pd.read_csv('data/processed_emails.csv').head(1000)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate Embeddings (Turning text into 'Intelligence' context)
embeddings = model.encode(df['Body'].tolist(), show_progress_bar=True)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

def ask_intelligence_system(query):
    q_emb = model.encode([query])
    D, I = index.search(np.array(q_emb), k=1)
    result = df.iloc[I[0][0]]
    print(f"\nTop Match:\nFrom: {result['From']}\nSubject: {result['Subject']}\nBody: {result['Body'][:200]}...")

if __name__ == "__main__":
    # This makes the script interactive so YOU can type the query!
    user_query = input("\nEnter your search query (e.g., 'What did Mark say about the trial?'): ")
    ask_intelligence_system(user_query)