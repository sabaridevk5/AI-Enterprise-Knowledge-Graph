# milestone2_graph_build.py - FIXED with correct data path

import pandas as pd
import path_config  # Auto-added for path configuration
from neo4j import GraphDatabase
import time
import os
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class EnronGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def build_graph(self, csv_path):
        print(f"Reading data from {csv_path}...")
        
        # Check if file exists
        if not os.path.exists(csv_path):
            print(f"ERROR: File not found at {csv_path}")
            return
            
        df = pd.read_csv(csv_path).dropna(subset=['From', 'To'])
        data_list = df.head(2000).to_dict('records') 

        query = """
        UNWIND $batch AS row
        MERGE (s:Person {email: row.From})
        MERGE (r:Person {email: row.To})
        CREATE (s)-[:SENT {
            subject: toString(row.Subject), 
            date: toString(row.Date),
            thread_id: toString(row.threadId)
        }]->(r)
        """

        with self.driver.session() as session:
            print(f"--- Starting Batch Upload of {len(data_list)} records to Neo4j AuraDB ---")
            start_time = time.time()
            session.run(query, batch=data_list)
            end_time = time.time()
            print(f"Successfully built the Knowledge Graph in {round(end_time - start_time, 2)} seconds.")

if __name__ == "__main__":
    URI = "neo4j+s://0be473b6.databases.neo4j.io"
    USER = "0be473b6" 
    PASSWORD = "9m7fKj7WzZmVAMkithV9OkhzTzmBlPfQOye4Oyyvl70"

    print(f"Attempting connection to Neo4j AuraDB Cloud at {URI}...")
    
    try:
        builder = EnronGraphBuilder(URI, USER, PASSWORD)
        builder.driver.verify_connectivity()
        print("Authentication Successful!")
        
        # Get the correct path - data is in parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(script_dir), 'data')
        csv_path = os.path.join(data_dir, 'processed_emails.csv')
        
        print(f"Looking for data at: {csv_path}")
        builder.build_graph(csv_path)
        builder.close()
        print("\n--- MISSION COMPLETE ---")
        
    except Exception as e:
        print(f"DATABASE ERROR: {e}")