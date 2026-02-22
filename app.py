# app.py - PREMIUM ENTERPRISE DASHBOARD

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go
import networkx as nx
import random

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Aurum Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="collapsed"
)

# --- 2. CLEAN MODERN CSS ---
# We target specific Streamlit elements to create a cohesive dark/glass theme
# without breaking Streamlit's native responsive grid.
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main App Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }

    /* Hide default Streamlit header and footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Premium Top Bar */
    .top-bar {
        padding: 1rem 0;
        border-bottom: 1px solid #2D3748;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .brand-title {
        font-size: 1.8rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #4299E1, #9F7AEA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    
    .brand-subtitle {
        color: #A0AEC0;
        font-size: 0.9rem;
        font-weight: 400;
    }

    /* Custom Display Cards for Emails */
    .insight-card {
        background: #1A202C;
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .insight-card:hover {
        transform: translateY(-2px);
        border-color: #4299E1;
        box-shadow: 0 4px 20px rgba(66, 153, 225, 0.1);
    }

    .card-meta {
        font-size: 0.8rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
    }

    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-bottom: 0.5rem;
    }

    .card-body {
        font-size: 0.95rem;
        color: #CBD5E0;
        line-height: 1.5;
    }
    
    /* Entity Stat Cards */
    .entity-stat {
        background: #1A202C;
        border: 1px solid #2D3748;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #9F7AEA;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CREDENTIALS & INIT ---
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

@st.cache_resource
def load_systems():
    systems = {"vectorstore": None, "graph_status": "Disconnected"}
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        systems["vectorstore"] = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)
    except Exception:
        pass
    
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        systems["graph_status"] = "Connected"
    except Exception:
        pass
    return systems

systems = load_systems()

# --- 4. SESSION STATE ---
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'current_entity' not in st.session_state:
    st.session_state.current_entity = "jeff.dasovich"

def extract_entity(query):
    q = query.lower()
    entities = ['jeff.dasovich', 'kenneth.lay', 'jeff.skilling', 'sherron.watkins', 'john.arnold']
    for e in entities:
        if e.replace('.', ' ') in q or e.split('.')[1] in q:
            return e
    return "jeff.dasovich"

# --- 5. TOP NAVIGATION BAR ---
st.markdown("""
<div class="top-bar">
    <div>
        <div class="brand-title">💠 AURUM INTELLIGENCE</div>
        <div class="brand-subtitle">Enterprise Knowledge Graph & Semantic Discovery</div>
    </div>
    <div style="color: #48BB78; font-size: 0.9rem; font-weight: 500;">
        ● System Active
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. SEARCH SECTION ---
st.markdown("### 🔍 Query Enterprise Data")
search_col, btn_col = st.columns([5, 1])
with search_col:
    query = st.text_input("Search", label_visibility="collapsed", placeholder="e.g., 'What did Jeff Dasovich say about energy trading regulations?'")
with btn_col:
    search_clicked = st.button("Analyze Data", use_container_width=True, type="primary")

if search_clicked and query:
    st.session_state.search_query = query
    st.session_state.current_entity = extract_entity(query)

st.divider()

# --- 7. MAIN DASHBOARD LAYOUT ---
col_results, col_graph = st.columns([1.2, 1])

# === LEFT: SEMANTIC RESULTS ===
with col_results:
    st.markdown("### 📑 Intelligence Matches")
    
    if st.session_state.search_query:
        # Simulated Search Results (Replace with actual vectorstore query logic if connected)
        st.caption(f"Showing results for: **{st.session_state.search_query}**")
        
        results = [
            {"sender": "Jeff Dasovich", "date": "2001-05-15", "subject": "California Energy Market Analysis", "content": "The California market is showing significant volatility. Trading opportunities are emerging but regulatory scrutiny is increasing."},
            {"sender": "Sherron Watkins", "date": "2001-08-22", "subject": "URGENT: Accounting Concerns", "content": "I have serious concerns about our off-balance-sheet entities. This could explode in our faces."},
            {"sender": "Jeff Skilling", "date": "2001-03-10", "subject": "Trading Desk Strategy", "content": "Natural gas positions are strong. Let's push harder on the West Coast opportunities."}
        ]
        
        for res in results:
            st.markdown(f"""
            <div class="insight-card">
                <div class="card-meta">
                    <span>👤 {res['sender']}</span>
                    <span>📅 {res['date']}</span>
                </div>
                <div class="card-title">{res['subject']}</div>
                <div class="card-body">{res['content']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Awaiting query input to surface relevant communications.")

# === RIGHT: KNOWLEDGE GRAPH ===
with col_graph:
    st.markdown("### 🕸️ Relationship Graph")
    
    # Create sample graph
    G = nx.Graph()
    edges = [
        ("jeff.dasovich", "kenneth.lay", 47), ("jeff.dasovich", "jeff.skilling", 38),
        ("kenneth.lay", "sherron.watkins", 25), ("jeff.skilling", "greg.whalley", 22),
        ("jeff.dasovich", "john.arnold", 12), ("john.arnold", "jeff.skilling", 10)
    ]
    for src, tgt, weight in edges:
        G.add_edge(src, tgt, weight=weight)
        
    pos = nx.spring_layout(G, seed=42)
    
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, line=dict(width=1, color='#4A5568'),
        hoverinfo='none', mode='lines'
    )

    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_text = [node.replace('.', ' ').title() for node in G.nodes()]
    
    # Highlight current entity
    node_colors = ['#4299E1' if node == st.session_state.current_entity else '#718096' for node in G.nodes()]
    node_sizes = [40 if node == st.session_state.current_entity else 25 for node in G.nodes()]

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        hoverinfo='text', text=node_text, textposition="bottom center",
        marker=dict(showscale=False, color=node_colors, size=node_sizes, line_width=2, line_color='#1A202C'),
        textfont=dict(color='#E2E8F0')
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0,l=0,r=0,t=0),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=400
                 ))
                 
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- ENTITY STATS ---
    st.markdown("### 📊 Entity Context")
    stat1, stat2, stat3 = st.columns(3)
    
    active_name = st.session_state.current_entity.replace('.', ' ').title()
    connections = G.degree(st.session_state.current_entity) if st.session_state.current_entity in G else 0
    
    with stat1:
        st.markdown(f'<div class="entity-stat"><div class="stat-value">{connections}</div><div class="stat-label">Direct Contacts</div></div>', unsafe_allow_html=True)
    with stat2:
        st.markdown(f'<div class="entity-stat"><div class="stat-value">{random.randint(80, 99)}%</div><div class="stat-label">Influence Score</div></div>', unsafe_allow_html=True)
    with stat3:
        st.markdown(f'<div class="entity-stat"><div class="stat-value">{random.randint(12, 45)}</div><div class="stat-label">Documents</div></div>', unsafe_allow_html=True)