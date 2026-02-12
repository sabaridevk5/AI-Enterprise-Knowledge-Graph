#neo4j_connect.py

from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "kgdemo001"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


def insert_tickets():
    tickets = [
        ("T101", "John", "Product X", "Battery failure"),
        ("T102", "Alice", "Product Y", "Screen flickering"),
        ("T103", "Mark", "Product X", "Overheating issue"),
        ("T104", "Sarah", "Product Z", "Charging problem")
    ]

    with driver.session() as session:
        for tid, customer, product, issue in tickets:
            session.run("""
                MERGE (c:Customer {name: $customer})
                MERGE (p:Product {name: $product})
                MERGE (t:Ticket {id: $tid, description: $issue})
                MERGE (c)-[:RAISED]->(t)
                MERGE (t)-[:RELATED_TO]->(p)
            """, customer=customer, product=product, tid=tid, issue=issue)

    print("Multiple tickets inserted!")


if __name__ == "__main__":
    insert_tickets()
    driver.close()
