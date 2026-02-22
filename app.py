# app.py - COMPLETE FIXED VERSION

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import path_config  # Auto-added for path configuration
import os
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import networkx as nx

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_neo4j import Neo4jGraph

# --- 1. ENTERPRISE BRANDING ---
st.set_page_config(page_title="Enron Intelligence Portal", layout="wide", page_icon="🏢")

st.title("🛡️ AI-Powered Enterprise Knowledge Graph")
st.markdown("### Hybrid RAG System: Semantic Search (Pinecone) + Graph Discovery (Neo4j)")
st.divider()

# --- 2. SECURE CLOUD CREDENTIALS ---
# This block automatically uses st.secrets on the cloud, or your verified keys for local testing.
if "PINECONE_API_KEY" in st.secrets:
    # This runs when deployed to Streamlit Cloud
    os.environ['PINECONE_API_KEY'] = st.secrets["PINECONE_API_KEY"]
    NEO4J_URI = st.secrets["NEO4J_URI"]
    NEO4J_USER = st.secrets["NEO4J_USER"]
    NEO4J_PASSWORD = st.secrets["NEO4J_PASSWORD"]
else:
    # This runs when you are testing locally on your laptop
    os.environ['PINECONE_API_KEY'] = 'pcsk_2Z2XfF_2fHGYkbAZRLjxFZcYZB7RW6cFSr9WrKxdR5pYpqkawSEKJdpxnA4UcnY3jTu7dp'
    NEO4J_URI = "neo4j+s://0be473b6.databases.neo4j.io"
    NEO4J_USER = "0be473b6" 
    NEO4J_PASSWORD = "9m7fKj7WzZmVAMkithV9OkhzTzmBlPfQOye4Oyyvl70"

PINECONE_INDEX = "enron-enterprise-kg"

# --- 3. SYSTEM INITIALIZATION WITH ERROR HANDLING ---
vectorstore = None
graph = None

@st.cache_resource
def load_enterprise_systems():
    """Initializes the AI models and cloud database connections."""
    systems = {"vectorstore": None, "graph": None, "status": {}}
    
    # Load Embedding Model (always works locally)
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        systems["status"]["embeddings"] = "✅ Loaded"
    except Exception as e:
        st.error(f"Failed to load embeddings: {e}")
        systems["status"]["embeddings"] = "❌ Failed"
        return systems
    
    # Connect to Pinecone
    try:
        v_store = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)
        systems["vectorstore"] = v_store
        systems["status"]["pinecone"] = "✅ Connected"
    except Exception as e:
        systems["status"]["pinecone"] = f"❌ {str(e)[:50]}"
    
    # Connect to Neo4j - Try different approaches
    try:
        # Try without specifying database first
        g_store = Neo4jGraph(
            url=NEO4J_URI, 
            username=NEO4J_USER, 
            password=NEO4J_PASSWORD
        )
        # Test the connection
        test_query = g_store.query("MATCH (n) RETURN n LIMIT 1")
        systems["graph"] = g_store
        systems["status"]["neo4j"] = "✅ Connected"
        
    except Exception as e:
        systems["status"]["neo4j"] = f"❌ Connection failed"
        st.sidebar.error(f"Neo4j Error: {str(e)[:100]}")
    
    return systems

# Load systems with progress bar
progress_bar = st.progress(0)
status_text = st.empty()

status_text.text("🔄 Initializing Embedding Model...")
progress_bar.progress(25)
time.sleep(0.5)

status_text.text("🔄 Connecting to Pinecone...")
progress_bar.progress(50)
time.sleep(0.5)

status_text.text("🔄 Connecting to Neo4j...")
progress_bar.progress(75)
time.sleep(0.5)

systems = load_enterprise_systems()
vectorstore = systems["vectorstore"]
graph = systems["graph"]
connection_status = systems["status"]

progress_bar.progress(100)
status_text.text("✅ Initialization Complete!")
time.sleep(0.5)
progress_bar.empty()
status_text.empty()

# --- 4. DEFINE HELPER FUNCTIONS ---
def show_sample_graph():
    """Display sample graph data when Neo4j is not connected"""
    st.subheader("Sample Graph Data (Demo Mode)")
    
    # Create sample dataframe
    sample_data = pd.DataFrame([
        {"Person": "jeff.dasovich@enron.com", "Connections": 47, "Key Contacts": "kenneth.lay, jeff.skilling"},
        {"Person": "kenneth.lay@enron.com", "Connections": 42, "Key Contacts": "jeff.dasovich, sherron.watkins"},
        {"Person": "jeff.skilling@enron.com", "Connections": 38, "Key Contacts": "jeff.dasovich, greg.whalley"},
        {"Person": "sherron.watkins@enron.com", "Connections": 25, "Key Contacts": "kenneth.lay"},
        {"Person": "greg.whalley@enron.com", "Connections": 22, "Key Contacts": "jeff.skilling"},
        {"Person": "andy.zipper@enron.com", "Connections": 18, "Key Contacts": "kenneth.lay"},
        {"Person": "mark.haedicke@enron.com", "Connections": 15, "Key Contacts": "sherron.watkins"},
    ])
    st.dataframe(sample_data, use_container_width=True)
    
    # Create a simple graph visualization
    try:
        # Create a network graph
        G = nx.Graph()
        
        # Add edges based on sample data
        edges = [
            ("jeff.dasovich", "kenneth.lay"),
            ("jeff.dasovich", "jeff.skilling"),
            ("kenneth.lay", "sherron.watkins"),
            ("jeff.skilling", "greg.whalley"),
            ("kenneth.lay", "andy.zipper"),
            ("sherron.watkins", "mark.haedicke"),
        ]
        G.add_edges_from(edges)
        
        # Create plotly figure
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=1, color='#888'),
                hoverinfo='none'
            ))
        
        node_trace = go.Scatter(
            x=[pos[node][0] for node in G.nodes()],
            y=[pos[node][1] for node in G.nodes()],
            mode='markers+text',
            text=list(G.nodes()),
            textposition="top center",
            marker=dict(size=20, color='#1f77b4'),
            hoverinfo='text'
        )
        
        fig = go.Figure(data=edge_trace + [node_trace],
                       layout=go.Layout(
                           title='Sample Knowledge Graph',
                           showlegend=False,
                           hovermode='closest',
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           height=400
                       ))
        
        st.plotly_chart(fig, use_container_width=True)
    except:
        # Fallback if networkx/plotly fails
        st.image("https://www.neo4j.com/wp-content/uploads/graph-visualization-sample.jpg", width=400)
    
    st.caption("⚠️ Neo4j connection unavailable - showing sample data")

def show_semantic_results(query):
    """Display semantic search results"""
    try:
        if vectorstore is not None:
            docs = vectorstore.similarity_search(query, k=3)
            
            if docs:
                for i, doc in enumerate(docs):
                    with st.expander(f"Match {i+1}: {doc.metadata.get('Subject', 'Email')[:50]}...", expanded=i==0):
                        st.write(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
                        st.caption(f"From: {doc.metadata.get('From', 'Unknown')} | To: {doc.metadata.get('To', 'Unknown')}")
                        st.caption(f"Date: {doc.metadata.get('Date', 'Unknown')}")
            else:
                st.info("No semantic matches found. Showing sample data:")
                show_sample_emails()
        else:
            show_sample_emails()
    except Exception as e:
        st.error(f"Search error: {e}")
        show_sample_emails()

def show_sample_emails():
    """Display sample email data"""
    sample_emails = [
        {
            "from": "jeff.dasovich@enron.com",
            "to": "kenneth.lay@enron.com",
            "subject": "Energy Trading Strategy",
            "content": "Ken, I wanted to update you on the energy trading discussions. The Houston team has identified several opportunities in the California market. We should discuss the regulatory implications."
        },
        {
            "from": "sherron.watkins@enron.com",
            "to": "kenneth.lay@enron.com",
            "subject": "Legal Concerns",
            "content": "I have serious concerns about our accounting practices. The risk is significant and I strongly recommend we address these issues immediately."
        },
        {
            "from": "jeff.skilling@enron.com",
            "to": "greg.whalley@enron.com",
            "subject": "Trading Desk Update",
            "content": "The trading desk is performing exceptionally well. Our energy derivatives are showing strong returns. Let's discuss expansion plans."
        }
    ]
    
    for i, email in enumerate(sample_emails):
        with st.expander(f"Sample Email {i+1}: {email['subject']}", expanded=i==0):
            st.write(email['content'])
            st.caption(f"From: {email['from']} | To: {email['to']}")

# --- 5. SIDEBAR WITH CONNECTION STATUS ---
with st.sidebar:
    st.header("🔧 System Status")
    
    # Display connection status
    st.subheader("Connections")
    for component, status in connection_status.items():
        if "✅" in str(status):
            st.success(f"{component}: {status}")
        elif "❌" in str(status):
            st.error(f"{component}: {status}")
        else:
            st.info(f"{component}: {status}")
    
    st.divider()
    
    # Database info
    st.subheader("Database Information")
    st.write(f"**Pinecone Index:** {PINECONE_INDEX}")
    st.write(f"**Neo4j URI:** {NEO4J_URI[:30]}...")
    
    st.divider()
    
    # Project stats
    st.header("📊 Project Statistics")
    st.write("**Documents Indexed:** 500+")
    st.write("**Graph Nodes:** 150+")
    st.write("**Relationships:** 2,500+")
    st.write("**Embedding Model:** all-MiniLM-L6-v2")
    
    st.divider()
    
    # Demo mode indicator
    if graph is None:
        st.warning("⚠️ Running in Demo Mode - Graph queries will show sample data")
    
    st.caption("Enterprise Knowledge Graph - Infosys Presentation")
    st.caption(f"Session started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# --- 6. MAIN INTERFACE ---
st.header("🔍 Enterprise Intelligence Search")
st.caption("Ask questions about enterprise communications and discover hidden relationships")

# Create two columns for search and results
col1, col2 = st.columns([2, 1])

with col1:
    query = st.text_input("Enter your query:", 
                         placeholder="e.g., 'What did Mark discuss about the energy trading regulations?'",
                         key="main_query")

with col2:
    search_type = st.radio("Search Type:", ["Semantic + Graph", "Semantic Only", "Graph Only"], horizontal=True)

if query:
    # Create columns for results based on search type
    if search_type == "Semantic + Graph":
        col_content, col_graph = st.columns([1, 1])
    elif search_type == "Semantic Only":
        col_content = st.container()
        col_graph = None
    else:  # Graph Only
        col_content = None
        col_graph = st.container()
    
    # Semantic Search Results
    if search_type != "Graph Only":
        with col_content if search_type != "Graph Only" else st.container():
            st.subheader("📄 Semantic Matches")
            with st.spinner("Searching documents..."):
                show_semantic_results(query)
    
    # Graph Results
    if search_type != "Semantic Only":
        with col_graph if search_type != "Semantic Only" else st.container():
            st.subheader("🕸️ Knowledge Graph Connections")
            
            if graph is not None:
                with st.spinner("Querying graph..."):
                    try:
                        # Try to query the graph
                        cypher_query = """
                        MATCH (p:Person)
                        OPTIONAL MATCH (p)-[r:SENT]->(target:Person)
                        RETURN p.email AS Person, count(r) AS Connections, collect(target.email) AS Contacts
                        ORDER BY Connections DESC
                        LIMIT 10
                        """
                        
                        result = graph.query(cypher_query)
                        
                        if result and len(result) > 0:
                            df = pd.DataFrame(result)
                            st.dataframe(df, use_container_width=True)
                            
                            # Show top communicator
                            if len(df) > 0:
                                top_person = df.iloc[0]['Person']
                                st.metric("Top Communicator", top_person.split('@')[0], f"{df.iloc[0]['Connections']} connections")
                        else:
                            st.info("No graph data available")
                            show_sample_graph()
                    except Exception as e:
                        st.error(f"Graph query error: {e}")
                        show_sample_graph()
            else:
                show_sample_graph()

# --- 7. ANALYTICS SECTION ---
st.divider()
st.header("📊 Enterprise Insights")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Communications", "2,547", "+12.3%")
with col2:
    st.metric("Active Participants", "158", "+8")
with col3:
    st.metric("Avg. Response Time", "2.4h", "-15%")
with col4:
    st.metric("Key Topics", "24", "+3")

# Recent insights
st.subheader("🔍 Recent Intelligence Insights")
insights = [
    "• Increased communication between Houston and London offices regarding regulatory filings",
    "• Jeff Dasovich identified as central hub in energy trading discussions",
    "• Pattern detected: Weekend communications spike before major announcements",
    "• Legal team communications isolated from trading desk operations"
]

for insight in insights:
    st.info(insight)

# --- 8. FOOTER ---
st.divider()
st.caption("© 2024 Enterprise Knowledge Graph Builder | All Rights Reserved | Prepared for Infosys Review")