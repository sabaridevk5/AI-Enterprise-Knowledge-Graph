#graph_rag_final.py

import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from neo4j import GraphDatabase

# 1. Setup Models and Data
model = SentenceTransformer("all-MiniLM-L6-v2")
tickets = ["Battery failure in Product X", "Screen flickering in Product Y", "Overheating in Product X"]

# 2. Build FAISS Index
embeddings = model.encode(tickets)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

# 3. Neo4j Connection
URI = "bolt://localhost:7687"
USER = "neo4j"
PWD = "your_password" # Use your password here
driver = GraphDatabase.driver(URI, auth=(USER, PWD))

def search_rag(query):
    # STEP A: Semantic Search
    q_emb = model.encode([query])
    D, I = index.search(np.array(q_emb), k=1)
    best_match = tickets[I[0][0]]
    print(f"Found via Semantic Search: {best_match}")

    # STEP B: Graph Retrieval
    with driver.session() as session:
        # We find the ticket in the graph and see who raised it
        result = session.run(
            "MATCH (c:Customer)-[:RAISED]->(t:Ticket) "
            "WHERE t.description CONTAINS $desc "
            "RETURN c.name as name, t.id as id", 
            desc="Battery failure" # Hardcoded for demo simplicity
        )
        for record in result:
            print(f"Graph Intelligence: This ticket ({record['id']}) was raised by {record['name']}")

if __name__ == "__main__":
    search_rag("My device has power problems")
    driver.close()