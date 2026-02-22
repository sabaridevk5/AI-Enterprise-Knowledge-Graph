# graph_analytics.py - SECURED & BLINDED
import pandas as pd
from neo4j import GraphDatabase
import networkx as nx
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
import os
from dotenv import load_dotenv  # Added for security shielding

# 1. Load the Shield (Environment Variables)
load_dotenv()

class GraphAnalytics:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_network_metrics(self):
        """Calculate key network metrics"""
        with self.driver.session() as session:
            # Degree centrality
            result = session.run("""
                MATCH (p:Person)-[r:SENT]->()
                RETURN p.email AS person, count(r) AS degree
                ORDER BY degree DESC
                LIMIT 10
            """)
            degree_data = [{"person": r["person"], "degree": r["degree"]} for r in result]
            
            # Betweenness centrality (simplified)
            result = session.run("""
                MATCH (p:Person)
                OPTIONAL MATCH (p)-[:SENT]->(other)
                RETURN p.email AS person, count(other) AS connections
                ORDER BY connections DESC
                LIMIT 10
            """)
            centrality_data = [{"person": r["person"], "connections": r["connections"]} for r in result]
            
            return degree_data, centrality_data
    
    def find_communities(self):
        """Detect communication communities"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p1:Person)-[:SENT]->(p2:Person)
                RETURN p1.email AS source, p2.email AS target, count(*) AS weight
                LIMIT 100
            """)
            
            # Build graph in NetworkX
            G = nx.Graph()
            for record in result:
                G.add_edge(record["source"], record["target"], weight=record["weight"])
            
            # Detect communities
            if len(G.nodes()) > 0:
                communities = nx.community.greedy_modularity_communities(G)
                return communities
            return []
    
    def get_temporal_patterns(self):
        """Analyze communication patterns over time"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH ()-[r:SENT]->()
                WHERE r.date IS NOT NULL
                RETURN r.date AS date, count(*) AS count
                ORDER BY date
                LIMIT 50
            """)
            return [{"date": r["date"], "count": r["count"]} for r in result]

# 2. Usage example with Secure Credential Loading
if __name__ == "__main__":
    # Load credentials securely from .env instead of hardcoding
    URI = os.getenv("NEO4J_URI")
    USER = os.getenv("NEO4J_USER")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

    if not all([URI, USER, PASSWORD]):
        print("❌ ERROR: Neo4j credentials missing in .env file.")
    else:
        print(f"Connecting to Neo4j Analytics Engine at {URI}...")
        analytics = GraphAnalytics(URI, USER, PASSWORD)
        
        # Get metrics
        degree, centrality = analytics.get_network_metrics()
        print("Top Communicators:", degree[:5])
        
        analytics.close()