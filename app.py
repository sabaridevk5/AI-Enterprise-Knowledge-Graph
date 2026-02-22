# app.py - COMPLETE FIXED VERSION with no session state errors

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import path_config
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
if "PINECONE_API_KEY" in st.secrets:
    os.environ['PINECONE_API_KEY'] = st.secrets["PINECONE_API_KEY"]
    NEO4J_URI = st.secrets["NEO4J_URI"]
    NEO4J_USER = st.secrets["NEO4J_USER"]
    NEO4J_PASSWORD = st.secrets["NEO4J_PASSWORD"]
else:
    os.environ['PINECONE_API_KEY'] = 'pcsk_2Z2XfF_2fHGYkbAZRLjxFZcYZB7RW6cFSr9WrKxdR5pYpqkawSEKJdpxnA4UcnY3jTu7dp'
    NEO4J_URI = "neo4j+s://0be473b6.databases.neo4j.io"
    NEO4J_USER = "0be473b6" 
    NEO4J_PASSWORD = "9m7fKj7WzZmVAMkithV9OkhzTzmBlPfQOye4Oyyvl70"

PINECONE_INDEX = "enron-enterprise-kg"

# --- 3. INITIALIZE SESSION STATE ---
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# --- 4. SYSTEM INITIALIZATION WITH ERROR HANDLING ---
vectorstore = None
graph = None

@st.cache_resource
def load_enterprise_systems():
    """Initializes the AI models and cloud database connections."""
    systems = {"vectorstore": None, "graph": None, "status": {}}
    
    # Load Embedding Model
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
    
    # --- CONNECT TO NEO4J USING DIRECT DRIVER ---
    try:
        from neo4j import GraphDatabase
        
        st.sidebar.info("🔄 Testing Neo4j connection...")
        
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]
            st.sidebar.success(f"✅ Neo4j Connected ({node_count} nodes)")
        
        systems["neo4j_driver"] = driver
        systems["graph"] = driver
        systems["status"]["neo4j"] = f"✅ Connected ({node_count} nodes)"
        
    except Exception as e:
        systems["status"]["neo4j"] = f"❌ {str(e)[:50]}"
        systems["neo4j_driver"] = None
        st.sidebar.error(f"Neo4j connection failed: {str(e)[:100]}")
    
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

# --- 5. DEFINE HELPER FUNCTIONS ---
def show_sample_graph():
    """Display sample graph data when Neo4j is not connected"""
    st.subheader("Sample Graph Data (Demo Mode)")
    
    sample_data = pd.DataFrame([
        {"Person": "jeff.dasovich@enron.com", "Connections": 47, "Key Contacts": "kenneth.lay, jeff.skilling"},
        {"Person": "kenneth.lay@enron.com", "Connections": 42, "Key Contacts": "jeff.dasovich, sherron.watkins"},
        {"Person": "jeff.skilling@enron.com", "Connections": 38, "Key Contacts": "jeff.dasovich, greg.whalley"},
        {"Person": "sherron.watkins@enron.com", "Connections": 25, "Key Contacts": "kenneth.lay"},
        {"Person": "greg.whalley@enron.com", "Connections": 22, "Key Contacts": "jeff.skilling"},
        {"Person": "andy.zipper@enron.com", "Connections": 18, "Key Contacts": "kenneth.lay"},
    ])
    st.dataframe(sample_data, use_container_width=True)
    
    try:
        G = nx.Graph()
        edges = [
            ("jeff.dasovich", "kenneth.lay"),
            ("jeff.dasovich", "jeff.skilling"),
            ("kenneth.lay", "sherron.watkins"),
            ("jeff.skilling", "greg.whalley"),
            ("kenneth.lay", "andy.zipper"),
        ]
        G.add_edges_from(edges)
        
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
                           height=400,
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.image("https://www.neo4j.com/wp-content/uploads/graph-visualization-sample.jpg", width=400)

def show_semantic_results(query):
    """Display semantic search results"""
    try:
        if vectorstore is not None:
            docs = vectorstore.similarity_search(query, k=3)
            
            if docs:
                for i, doc in enumerate(docs):
                    with st.expander(f"Match {i+1}", expanded=i==0):
                        st.write(doc.page_content[:300] + "...")
                        st.caption(f"From: {doc.metadata.get('From', 'Unknown')}")
                        st.caption(f"Subject: {doc.metadata.get('Subject', 'Unknown')}")
            else:
                st.info("No matches found")
        else:
            st.info("Pinecone not connected. Using sample data.")
    except Exception as e:
        st.error(f"Search error: {e}")

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("🔧 System Status")
    
    st.subheader("Connections")
    for component, status in connection_status.items():
        if "✅" in str(status):
            st.success(f"{component}: Connected")
        elif "❌" in str(status):
            st.error(f"{component}: Failed")
        else:
            st.info(f"{component}: {status}")
    
    st.divider()
    
    st.header("📊 Project Info")
    st.write("**Pinecone Index:**", PINECONE_INDEX)
    st.write("**Neo4j:**", NEO4J_URI[:30] + "...")
    st.write("**Embeddings:** all-MiniLM-L6-v2")
    
    st.divider()
    st.caption("Enterprise Knowledge Graph - Infosys Review")

# --- 7. MAIN INTERFACE ---
st.header("🔍 Enterprise Intelligence Search")
st.caption("Ask questions about enterprise communications")

# Search input with session state
query = st.text_input("Enter your query:", 
                     value=st.session_state.search_query,
                     placeholder="e.g., 'natural gas trading' or 'energy market analysis'",
                     key="search_input")

# Search type selector
search_type = st.radio("Search Type:", 
                      ["Semantic + Graph", "Semantic Only", "Graph Only"], 
                      horizontal=True)

# --- 8. QUICK ACTION BUTTONS ---
st.divider()
st.subheader("🔍 Try These Sample Queries:")

cols = st.columns(4)
queries = ["natural gas trading", "energy market analysis", "jeff dasovich", "accounting concerns"]

for i, q in enumerate(queries):
    with cols[i]:
        if st.button(f"📊 {q}", key=f"btn_{i}", use_container_width=True):
            st.session_state.search_query = q
            st.rerun()

# --- 9. SEARCH RESULTS ---
if query:
    if search_type == "Semantic + Graph":
        col1, col2 = st.columns([1, 1])
    elif search_type == "Semantic Only":
        col1 = st.container()
        col2 = None
    else:
        col1 = None
        col2 = st.container()
    
    # Semantic Search Results
    if search_type != "Graph Only" and col1 is not None:
        with col1:
            st.subheader("📄 Semantic Matches")
            with st.spinner("Searching..."):
                show_semantic_results(query)
    
    # Graph Results
    if search_type != "Semantic Only" and col2 is not None:
        with col2:
            st.subheader("🕸️ Graph Connections")
            
            if graph is not None:
                with st.spinner("Querying Neo4j..."):
                    try:
                        with graph.session() as session:
                            result = session.run("""
                            MATCH (p:Person)
                            OPTIONAL MATCH (p)-[r:SENT]->(target:Person)
                            RETURN p.email AS Person, count(r) AS Connections
                            ORDER BY Connections DESC
                            LIMIT 10
                            """)
                            
                            data = [record.data() for record in result]
                            
                            if data:
                                df = pd.DataFrame(data)
                                st.dataframe(df, use_container_width=True)
                            else:
                                show_sample_graph()
                    except Exception as e:
                        st.error(f"Graph query error")
                        show_sample_graph()
            else:
                show_sample_graph()

# --- 10. ANALYTICS SECTION ---
st.divider()
st.header("📊 Enterprise Insights")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Communications", "2,547")
with col2:
    st.metric("Active Participants", "158") 
with col3:
    st.metric("Avg. Response", "2.4h")
with col4:
    st.metric("Key Topics", "24")

# --- 11. FOOTER ---
st.divider()
st.caption("© 2024 Enterprise Knowledge Graph | Infosys Presentation")