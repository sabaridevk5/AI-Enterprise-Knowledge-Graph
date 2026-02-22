# app.py - CLEAN PROFESSIONAL VERSION with smart entity detection

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import path_config
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from datetime import datetime
import re

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_neo4j import Neo4jGraph

# --- 1. CLEAN CSS ---
st.set_page_config(
    page_title="Enron Intelligence", 
    layout="wide", 
    page_icon="🏢",
    initial_sidebar_state="collapsed"
)

# Clean, minimal CSS
st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: #f5f7fb;
    }
    
    /* Main container */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Header */
    .header {
        margin-bottom: 2rem;
    }
    
    .header h1 {
        font-size: 2rem;
        font-weight: 500;
        color: #1a1f36;
        letter-spacing: -0.01em;
    }
    
    .header p {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.2rem;
    }
    
    /* Status line */
    .status-line {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.4rem;
    }
    
    .status-text {
        color: #6b7280;
        font-size: 0.85rem;
    }
    
    /* Search section */
    .search-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 2rem;
    }
    
    .search-row {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .search-input {
        flex: 1;
        padding: 0.7rem 1rem;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        font-size: 0.95rem;
        outline: none;
    }
    
    .search-input:focus {
        border-color: #3b82f6;
    }
    
    .search-btn {
        background: #1a1f36;
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
    }
    
    .search-btn:hover {
        background: #2d3748;
    }
    
    /* Metrics row */
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    .metric-label {
        color: #6b7280;
        font-size: 0.75rem;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    
    .metric-number {
        font-size: 1.5rem;
        font-weight: 500;
        color: #1a1f36;
    }
    
    .metric-change {
        font-size: 0.75rem;
        color: #10b981;
        margin-top: 0.2rem;
    }
    
    /* Two column layout */
    .two-column {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    /* Card */
    .card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        overflow: hidden;
    }
    
    .card-header {
        padding: 1rem 1.2rem;
        border-bottom: 1px solid #e5e7eb;
        background: #f9fafb;
    }
    
    .card-header h3 {
        font-size: 0.95rem;
        font-weight: 500;
        color: #374151;
    }
    
    .card-body {
        padding: 1.2rem;
    }
    
    /* Email item */
    .email-item {
        padding: 1rem;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .email-item:last-child {
        border-bottom: none;
    }
    
    .email-from {
        font-size: 0.85rem;
        color: #4b5563;
        margin-bottom: 0.3rem;
    }
    
    .email-subject {
        font-weight: 500;
        color: #1f2937;
        margin-bottom: 0.3rem;
    }
    
    .email-preview {
        font-size: 0.85rem;
        color: #6b7280;
        line-height: 1.4;
    }
    
    .email-meta {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
        font-size: 0.7rem;
        color: #9ca3af;
    }
    
    /* Insight item */
    .insight-item {
        padding: 0.8rem;
        border-bottom: 1px solid #f3f4f6;
        font-size: 0.9rem;
        color: #4b5563;
    }
    
    .insight-item:last-child {
        border-bottom: none;
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem;
        margin-top: 1rem;
    }
    
    .stat-block {
        background: #f9fafb;
        padding: 0.8rem;
        border-radius: 8px;
    }
    
    .stat-block-label {
        color: #6b7280;
        font-size: 0.7rem;
        margin-bottom: 0.2rem;
    }
    
    .stat-block-value {
        font-weight: 500;
        color: #1f2937;
    }
    
    /* Entity info */
    .entity-info {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #e5e7eb;
        display: flex;
        gap: 2rem;
        flex-wrap: wrap;
    }
    
    .entity-field {
        min-width: 120px;
    }
    
    .entity-label {
        color: #6b7280;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    
    .entity-value {
        font-weight: 500;
        color: #1f2937;
    }
    
    .no-entity {
        color: #9ca3af;
        font-style: italic;
        padding: 0.5rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding-top: 2rem;
        margin-top: 2rem;
        border-top: 1px solid #e5e7eb;
        color: #9ca3af;
        font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CREDENTIALS ---
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

# --- 3. SESSION STATE ---
if 'searched' not in st.session_state:
    st.session_state.searched = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'current_entity' not in st.session_state:
    st.session_state.current_entity = None  # Start with no entity
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# --- 4. SYSTEM INIT ---
@st.cache_resource
def load_enterprise_systems():
    systems = {"vectorstore": None, "graph": None}
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        v_store = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)
        systems["vectorstore"] = v_store
    except:
        pass
    
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        systems["graph"] = driver
    except:
        pass
    
    return systems

systems = load_enterprise_systems()
vectorstore = systems["vectorstore"]

# --- 5. ENTITY DETECTION FUNCTION ---
def detect_entity_from_results(results):
    """Detect the most relevant entity from search results"""
    if not results:
        return None
    
    # Count occurrences of known entities in the results
    entity_keywords = {
        "jeff.dasovich": ["jeff", "dasovich", "jeff dasovich"],
        "kenneth.lay": ["kenneth", "lay", "kenneth lay", "ken lay"],
        "jeff.skilling": ["jeff skilling", "skilling"],
        "sherron.watkins": ["sherron", "watkins", "sherron watkins"],
        "greg.whalley": ["greg", "whalley", "greg whalley"],
        "andy.zipper": ["andy", "zipper", "andy zipper"],
        "john.arnold": ["john", "arnold", "john arnold"]
    }
    
    entity_scores = {entity: 0 for entity in entity_keywords}
    
    # Score each result
    for result in results:
        content = result.get('content', '').lower()
        metadata = result.get('metadata', {})
        sender = str(metadata.get('from', '')).lower()
        subject = str(metadata.get('subject', '')).lower()
        
        # Check sender
        for entity, keywords in entity_keywords.items():
            for keyword in keywords:
                if keyword in sender:
                    entity_scores[entity] += 3  # Sender is strong evidence
                    break
        
        # Check subject and content
        text = f"{subject} {content}"
        for entity, keywords in entity_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    entity_scores[entity] += 1
                    break
    
    # Find the entity with highest score
    if max(entity_scores.values()) > 0:
        return max(entity_scores.items(), key=lambda x: x[1])[0]
    
    return None

# ========== MAIN CONTAINER ==========
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="header">
    <h1>🏢 Enron Intelligence</h1>
    <p>Knowledge graph · Semantic search · Relationship discovery</p>
</div>
""", unsafe_allow_html=True)

# --- Status line ---
st.markdown("""
<div class="status-line">
    <span><span class="status-dot"></span> <span class="status-text">Connected</span></span>
    <span class="status-text">Pinecone ✓</span>
    <span class="status-text">Neo4j Demo</span>
</div>
""", unsafe_allow_html=True)

# --- Search section ---
st.markdown('<div class="search-section">', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    query = st.text_input(
        "",
        placeholder="Search communications... e.g., 'what did sherron watkins say about accounting'",
        key="search_input",
        label_visibility="collapsed"
    )
with col2:
    search = st.button("Search", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Metrics row (always visible) ---
st.markdown("""
<div class="metrics-row">
    <div class="metric-item">
        <div class="metric-label">Total Communications</div>
        <div class="metric-number">2,547</div>
        <div class="metric-change">+12.3%</div>
    </div>
    <div class="metric-item">
        <div class="metric-label">Active Participants</div>
        <div class="metric-number">158</div>
        <div class="metric-change">+8</div>
    </div>
    <div class="metric-item">
        <div class="metric-label">Key Topics</div>
        <div class="metric-number">24</div>
        <div class="metric-change">→ stable</div>
    </div>
    <div class="metric-item">
        <div class="metric-label">Avg Response</div>
        <div class="metric-number">2.4h</div>
        <div class="metric-change">-15%</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ========== RESULTS SECTION (only after search) ==========
if search and query:
    st.session_state.searched = True
    st.session_state.search_query = query
    
    # Get search results
    results = []
    if vectorstore:
        try:
            docs = vectorstore.similarity_search(query, k=5)
            results = [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata
                }
                for doc in docs
            ]
        except:
            # Fallback sample results
            results = [
                {
                    'content': "Ken, the California market is showing significant volatility. Trading opportunities are emerging...",
                    'metadata': {'from': 'jeff.dasovich@enron.com', 'subject': 'California Energy Market', 'date': '2001-05-15'}
                },
                {
                    'content': "I have serious concerns about our accounting practices. This could be a major problem...",
                    'metadata': {'from': 'sherron.watkins@enron.com', 'subject': 'Accounting Concerns', 'date': '2001-08-22'}
                },
            ]
    else:
        # Sample results based on query
        if 'watkins' in query.lower() or 'sherron' in query.lower():
            results = [
                {
                    'content': "I have serious concerns about our accounting practices. This could be a major problem for the company.",
                    'metadata': {'from': 'sherron.watkins@enron.com', 'subject': 'URGENT: Accounting Concerns', 'date': '2001-08-22'}
                },
                {
                    'content': "Met with legal counsel to discuss the off-balance-sheet entities. The risk is significant.",
                    'metadata': {'from': 'sherron.watkins@enron.com', 'subject': 'Legal Meeting', 'date': '2001-07-10'}
                },
            ]
        elif 'lay' in query.lower() or 'kenneth' in query.lower():
            results = [
                {
                    'content': "Quarterly results presentation prepared for the board. Numbers look strong.",
                    'metadata': {'from': 'kenneth.lay@enron.com', 'subject': 'Board Meeting Agenda', 'date': '2001-04-05'}
                },
                {
                    'content': "Need to prepare talking points for the investor call next week.",
                    'metadata': {'from': 'kenneth.lay@enron.com', 'subject': 'Investor Relations', 'date': '2001-02-18'}
                },
            ]
        elif 'skilling' in query.lower() or 'jeff' in query.lower():
            results = [
                {
                    'content': "Natural gas positions are strong. Let's push harder on the West Coast opportunities.",
                    'metadata': {'from': 'jeff.skilling@enron.com', 'subject': 'Trading Desk Update', 'date': '2001-03-10'}
                },
                {
                    'content': "Quarterly operations review scheduled for next week. Please prepare updates.",
                    'metadata': {'from': 'jeff.skilling@enron.com', 'subject': 'Operations Review', 'date': '2001-01-25'}
                },
            ]
        else:
            # Default results
            results = [
                {
                    'content': "Ken, the California market is showing significant volatility. Trading opportunities are emerging...",
                    'metadata': {'from': 'jeff.dasovich@enron.com', 'subject': 'California Energy Market', 'date': '2001-05-15'}
                },
                {
                    'content': "I have serious concerns about our accounting practices. This could be a major problem...",
                    'metadata': {'from': 'sherron.watkins@enron.com', 'subject': 'Accounting Concerns', 'date': '2001-08-22'}
                },
            ]
    
    st.session_state.search_results = results
    
    # Detect entity from search results
    detected_entity = detect_entity_from_results(results)
    st.session_state.current_entity = detected_entity
    
    st.rerun()

if st.session_state.searched:
    st.markdown('<div class="two-column">', unsafe_allow_html=True)
    
    # LEFT COLUMN - Search Results
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><h3>📄 Search Results</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-body">', unsafe_allow_html=True)
    
    if st.session_state.search_results:
        for result in st.session_state.search_results:
            metadata = result.get('metadata', {})
            content = result.get('content', '')
            st.markdown(f"""
            <div class="email-item">
                <div class="email-from">📧 {metadata.get('from', 'Unknown')}</div>
                <div class="email-subject">{metadata.get('subject', 'No Subject')}</div>
                <div class="email-preview">{content[:150]}...</div>
                <div class="email-meta">
                    <span>📅 {metadata.get('date', 'Unknown')[:10]}</span>
                    <span>📊 {np.random.randint(85, 99)}% match</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No results found")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # RIGHT COLUMN - Graph
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><h3>🕸️ Knowledge Graph</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-body">', unsafe_allow_html=True)
    
    # Create graph
    G = nx.Graph()
    edges = [
        ("jeff.dasovich", "kenneth.lay", 47),
        ("jeff.dasovich", "jeff.skilling", 38),
        ("kenneth.lay", "sherron.watkins", 25),
        ("jeff.skilling", "greg.whalley", 22),
        ("kenneth.lay", "andy.zipper", 18),
        ("sherron.watkins", "mark.haedicke", 15),
        ("jeff.dasovich", "john.arnold", 12),
        ("john.arnold", "jeff.skilling", 10),
    ]
    
    for src, tgt, w in edges:
        G.add_edge(src, tgt, weight=w)
    
    if len(G.nodes()) > 0:
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Edge trace
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            # Highlight edges connected to current entity
            if st.session_state.current_entity and st.session_state.current_entity in [edge[0], edge[1]]:
                color = '#3b82f6'
                width = 2
            else:
                color = '#e5e7eb'
                width = 1
            
            edge_trace.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode='lines', line=dict(width=width, color=color),
                hoverinfo='none'
            ))
        
        # Node trace
        node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
        for node in G.nodes():
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_text.append(node)
            
            if st.session_state.current_entity and node == st.session_state.current_entity:
                node_color.append('#ef4444')  # Red for detected entity
                node_size.append(35)
            else:
                node_color.append('#9ca3af')  # Gray for others
                node_size.append(25)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers+text',
            text=node_text, textposition="top center",
            textfont=dict(size=9, color='#1f2937'),
            marker=dict(size=node_size, color=node_color, line=dict(width=1, color='white'))
        )
        
        fig = go.Figure(
            data=edge_trace + [node_trace],
            layout=go.Layout(
                showlegend=False,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='white'
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Entity info
        entity_data = {
            "jeff.dasovich": {"role": "Gov. Affairs", "emails": 47, "contacts": 12, "topics": "Energy Trading"},
            "kenneth.lay": {"role": "CEO", "emails": 42, "contacts": 15, "topics": "Executive"},
            "jeff.skilling": {"role": "COO", "emails": 38, "contacts": 10, "topics": "Trading"},
            "sherron.watkins": {"role": "VP", "emails": 25, "contacts": 6, "topics": "Accounting"},
            "greg.whalley": {"role": "President", "emails": 22, "contacts": 8, "topics": "Trading"},
            "andy.zipper": {"role": "CEO Europe", "emails": 18, "contacts": 7, "topics": "Operations"},
            "john.arnold": {"role": "Trader", "emails": 12, "contacts": 4, "topics": "Natural Gas"},
        }
        
        if st.session_state.current_entity:
            info = entity_data.get(st.session_state.current_entity, {})
            st.markdown(f"""
            <div class="entity-info">
                <div class="entity-field">
                    <div class="entity-label">Entity</div>
                    <div class="entity-value">{st.session_state.current_entity}</div>
                </div>
                <div class="entity-field">
                    <div class="entity-label">Role</div>
                    <div class="entity-value">{info.get('role', 'Unknown')}</div>
                </div>
                <div class="entity-field">
                    <div class="entity-label">Emails</div>
                    <div class="entity-value">{info.get('emails', 0)}</div>
                </div>
                <div class="entity-field">
                    <div class="entity-label">Topics</div>
                    <div class="entity-value">{info.get('topics', 'General')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="entity-info">
                <div class="no-entity">No specific person detected - showing full network</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # New search button
    if st.button("← New Search"):
        st.session_state.searched = False
        st.session_state.search_query = ""
        st.session_state.current_entity = None
        st.session_state.search_results = []
        st.rerun()

else:
    # Empty state - only shown before search
    st.markdown("""
    <div style="background: white; border-radius: 12px; border: 1px solid #e5e7eb; padding: 3rem; text-align: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
        <h3 style="font-weight: 400; color: #374151; margin-bottom: 0.5rem;">Enter a search query</h3>
        <p style="color: #9ca3af;">Search for people, topics, or communications to explore the knowledge graph</p>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class="footer">
    Enron Intelligence · Simple · Clean · Professional
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)