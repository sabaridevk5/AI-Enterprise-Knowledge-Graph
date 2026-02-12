from neo4j import GraphDatabase
import pandas as pd



class EnronGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_relationships(self, csv_path):
        df = pd.read_csv(csv_path).head(1000) # Process in chunks for efficiency
        with self.driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MERGE (s:Person {email: $sender})
                    MERGE (r:Person {email: $receiver})
                    CREATE (s)-[:EMAILED {subject: $sub, date: $date}]->(r)
                """, sender=row['From'], receiver=row['To'], sub=row['Subject'], date=row['Date'])
        print("Milestone 2 Complete: Graph nodes and edges created.")

if __name__ == "__main__":
    builder = EnronGraphBuilder("bolt://localhost:7687", "neo4j", "kgdemo001")
    builder.create_relationships('data/processed_emails.csv')
    builder.close()