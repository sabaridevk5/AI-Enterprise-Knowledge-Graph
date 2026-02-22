# graph_analytics.py
import pandas as pd
from neo4j import GraphDatabase
import networkx as nx
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px

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

# Usage example
if __name__ == "__main__":
    analytics = GraphAnalytics(
        "neo4j+s://0be473b6.databases.neo4j.io",
        "0be473b6",
        "9m7fKj7WzZmVAMkithV9OkhzTzmBlPfQOye4Oyyvl70"
    )
    
    # Get metrics
    degree, centrality = analytics.get_network_metrics()
    print("Top Communicators:", degree[:5])
    
    analytics.close()