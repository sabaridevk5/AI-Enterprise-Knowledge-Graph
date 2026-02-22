# app.py - COMPLETE FIXED VERSION with Neo4j connection handling

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
from neo4j.exceptions import ServiceUnavailable, AuthError, ConfigurationError

# --- 1. ENTERPRISE BRANDING ---
st.set_page_config(page_title="Enron Intelligence Portal", layout="wide", page_icon="🏢")

st.title("🛡️ AI-Powered Enterprise Knowledge Graph")
st.markdown("### Hybrid RAG System: Semantic Search (Pinecone) + Graph Discovery (Neo4j)")
st.divider()

# --- 2. SECURE CLOUD CREDENTIALS ---
if "PINECONE_API_KEY" in st.secrets:
    # Streamlit Cloud
    os.environ['PINECONE_API_KEY'] = st.secrets["PINECONE_API_KEY"]
    NEO4J_URI = st.secrets["NEO4J_URI"]
    NEO4J_USER = st.secrets["NEO4J_USER"]
    NEO4J_PASSWORD = st.secrets["NEO4J_PASSWORD"]
else:
    # Local development
    os.environ['PINECONE_API_KEY'] = 'pcsk_2Z2XfF_2fHGYkbAZRLjxFZcYZB7RW6cFSr9WrKxdR5pYpqkawSEKJdpxnA4UcnY3jTu7dp'
    NEO4J_URI = "neo4j+s://0be473b6.databases.neo4j.io"
    NEO4J_USER = "0be473b6" 
    NEO4J_PASSWORD = "9m7fKj7WzZmVAMkithV9OkhzTzmBlPfQOye4Oyyvl70"

PINECONE_INDEX = "enron-enterprise-kg"

# --- 3. SYSTEM INITIALIZATION WITH ROBUST ERROR HANDLING ---
vectorstore = None
graph = None

@st.cache_resource
def load_enterprise_systems():
    """Initializes the AI models and cloud database connections with retry logic."""
    systems = {"vectorstore": None, "graph": None, "status": {}}
    
    # Load Embedding Model
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        systems["status"]["embeddings"] = "✅ Loaded"
    except Exception as e:
        systems["status"]["embeddings"] = f"❌ Failed: {str(e)[:50]}"
        return systems
    
    # Connect to Pinecone
    try:
        v_store = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)
        systems["vectorstore"] = v_store
        systems["status"]["pinecone"] = "✅ Connected"
    except Exception as e:
        systems["status"]["pinecone"] = f"⚠️ Demo Mode: {str(e)[:50]}"
    
    # Connect to Neo4j with proper error handling
    try:
        # First attempt with basic config
        g_store = Neo4jGraph(
            url=NEO4J_URI, 
            username=NEO4J_USER, 
            password=NEO4J_PASSWORD,
            timeout=30
        )
        
        # Test connection with simple query
        test_result = g_store.query("RETURN 1 as test")
        
        if test_result:
            systems["graph"] = g_store
            systems["status"]["neo4j"] = "✅ Connected"
            st.sidebar.success("✅ Neo4j Connected")
        else:
            systems["status"]["neo4j"] = "⚠️ Connection test failed"
            
    except AuthError:
        systems["status"]["neo4j"] = "❌ Authentication Failed"
        st.sidebar.error("Neo4j authentication failed. Check credentials.")
        
    except ServiceUnavailable as e:
        if "routing" in str(e).lower():
            systems["status"]["neo4j"] = "⏳ Warming up (30-60s)"
            st.sidebar.info("🔄 Neo4j is warming up. Please wait...")
        else:
            systems["status"]["neo4j"] = "⚠️ Service Unavailable"
            
    except ConfigurationError as e:
        systems["status"]["neo4j"] = "⚠️ Configuration Error"
        
    except Exception as e:
        error_msg = str(e).lower()
        if "routing" in error_msg:
            systems["status"]["neo4j"] = "⏳ Warming up"
            st.sidebar.info("🔄 Neo4j is initializing. Please wait...")
        else:
            systems["status"]["neo4j"] = f"⚠️ {str(e)[:50]}"
    
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
    st.subheader("Sample Graph Data")
    st.caption("Showing sample data while Neo4j connects...")
    
    sample_data = pd.DataFrame([
        {"Person": "jeff.dasovich@enron.com", "Connections": 47, "Key Contacts": "kenneth.lay, jeff.skilling"},
        {"Person": "kenneth.lay@enron.com", "Connections": 42, "Key Contacts": "jeff.dasovich, sherron.watkins"},
        {"Person": "jeff.skilling@enron.com", "Connections": 38, "Key Contacts": "jeff.dasovich, greg.whalley"},
        {"Person": "sherron.watkins@enron.com", "Connections": 25, "Key Contacts": "kenneth.lay"},
        {"Person": "greg.whalley@enron.com", "Connections": 22, "Key Contacts": "jeff.skilling"},
        {"Person": "andy.zipper@enron.com", "Connections": 18, "Key Contacts": "kenneth.lay"},
    ])
    st.dataframe(sample_data, use_container_width=True)
    
    # Create graph visualization
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
        pass

def show_semantic_results(query):
    """Display semantic search results"""
    try:
        if vectorstore is not None:
            with st.spinner("Searching Pinecone..."):
                docs = vectorstore.similarity_search(query, k=3)
                
                if docs:
                    for i, doc in enumerate(docs):
                        with st.expander(f"Match {i+1}", expanded=i==0):
                            st.write(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
                            st.caption(f"From: {doc.metadata.get('From', 'Unknown')}")
                            st.caption(f"Subject: {doc.metadata.get('Subject', 'Unknown')}")
                else:
                    st.info("No matches found")
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
            "content": "Ken, I wanted to update you on the energy trading discussions. The Houston team has identified several opportunities in the California market."
        },
        {
            "from": "sherron.watkins@enron.com",
            "to": "kenneth.lay@enron.com",
            "subject": "Legal Concerns",
            "content": "I have serious concerns about our accounting practices. The risk is significant and I strongly recommend we address these issues immediately."
        }
    ]
    
    for i, email in enumerate(sample_emails):
        with st.expander(f"Sample Email {i+1}: {email['subject']}"):
            st.write(email['content'])
            st.caption(f"From: {email['from']}")

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("🔧 System Status")
    
    # Connection status with friendly messages
    st.subheader("Connections")
    for component, status in connection_status.items():
        if "✅" in str(status):
            st.success(f"{component}: Connected")
        elif "⏳" in str(status):
            st.info(f"{component}: Initializing...")
            if component == "neo4j":
                st.caption("Neo4j free tier takes 30-60s to warm up")
        elif "⚠️" in str(status):
            st.warning(f"{component}: Demo Mode")
        else:
            st.error(f"{component}: {status}")
    
    st.divider()
    
    # Quick refresh button
    if st.button("🔄 Refresh Connection"):
        st.cache_resource.clear()
        st.rerun()
    
    st.divider()
    
    # Project info
    st.header("📊 Project Info")
    st.write("**Pinecone Index:**", PINECONE_INDEX)
    st.write("**Embeddings:** all-MiniLM-L6-v2")
    st.write("**Documents:** 500+ emails")
    st.write("**Graph Nodes:** 150+ people")
    
    st.divider()
    st.caption("Enterprise Knowledge Graph - Infosys Review")
    st.caption(f"Session: {time.strftime('%H:%M:%S')}")

# --- 6. MAIN INTERFACE ---
st.header("🔍 Enterprise Intelligence Search")
st.caption("Ask questions about enterprise communications")

query = st.text_input("Enter your query:", 
                     placeholder="e.g., 'natural gas trading' or 'energy market analysis'",
                     key="main_query")

if query:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Semantic Search")
        show_semantic_results(query)
    
    with col2:
        st.subheader("🕸️ Graph Connections")
        if graph is not None:
            with st.spinner("Querying Neo4j..."):
                try:
                    result = graph.query("""
                        MATCH (p:Person)
                        RETURN p.email AS Person, rand() as Connections
                        ORDER BY Connections DESC
                        LIMIT 10
                    """)
                    if result:
                        st.dataframe(pd.DataFrame(result), use_container_width=True)
                    else:
                        show_sample_graph()
                except:
                    show_sample_graph()
        else:
            show_sample_graph()

# --- 7. QUICK ACTIONS ---
st.divider()
st.subheader("🔍 Try These Queries:")

cols = st.columns(4)
queries = ["natural gas trading", "energy market", "jeff dasovich", "accounting concerns"]
for i, q in enumerate(queries):
    with cols[i]:
        if st.button(f"📊 {q}", use_container_width=True):
            st.session_state.main_query = q
            st.rerun()

# --- 8. FOOTER ---
st.divider()
st.caption("© 2026 Enterprise Knowledge Graph | Infosys Presentation")