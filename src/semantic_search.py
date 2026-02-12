#semantic_search.py


from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# 1️⃣ Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2️⃣ Sample ticket descriptions
tickets = [
    "Battery failure in Product X",
    "Screen flickering issue in Product Y",
    "Overheating issue in Product X",
    "Charging problem in Product Z"
]

# 3️⃣ Generate embeddings
embeddings = model.encode(tickets)

# 4️⃣ Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

print("FAISS index created successfully!")

# 5️⃣ Query input
query = input("Ask your question: ")

query_embedding = model.encode([query])
D, I = index.search(np.array(query_embedding), k=2)

print("\nTop matching tickets:\n")
for idx in I[0]:
    print(tickets[idx])
