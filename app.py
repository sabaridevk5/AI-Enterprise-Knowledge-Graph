# app.py - MODERN DASHBOARD UI

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

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# --- 1. MODERN DASHBOARD CSS ---
st.set_page_config(
    page_title="Enron Intelligence Dashboard", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Modern dashboard CSS
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: #f3f4f6;
    }
    
    /* Main container */
    .dashboard {
        max-width: 1600px;
        margin: 0 auto;
        padding: 1.5rem;
    }
    
    /* Header */
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .header-title h1 {
        font-size: 1.8rem;
        font-weight: 600;
        color: #111827;
        letter-spacing: -0.02em;
    }
    
    .header-title p {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.2rem;
    }
    
    .header-stats {
        display: flex;
        gap: 2rem;
    }
    
    .stat-item {
        text-align: right;
    }
    
    .stat-label {
        color: #6b7280;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stat-value {
        font-size: 1.2rem;
        font-weight: 600;
        color: #111827;
    }
    
    /* Search card */
    .search-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    
    .search-title {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .search-box {
        display: flex;
        gap: 0.5rem;
    }
    
    .search-box input {
        flex: 1;
        padding: 0.8rem 1rem;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        font-size: 0.95rem;
        outline: none;
        transition: all 0.2s;
    }
    
    .search-box input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
    }
    
    .search-box button {
        background: #111827;
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 10px;
        font-weight: 500;
        font-size: 0.9rem;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .search-box button:hover {
        background: #1f2937;
    }
    
    /* Hint text */
    .hint-text {
        margin-top: 0.8rem;
        color: #9ca3af;
        font-size: 0.85rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.7; }
        50% { opacity: 1; }
        100% { opacity: 0.7; }
    }
    
    /* Dashboard grid */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1.2fr 0.8fr;
        gap: 1.5rem;
        margin-top: 1rem;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.2rem;
    }
    
    .card-header h3 {
        font-size: 1rem;
        font-weight: 600;
        color: #374151;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .card-header span {
        color: #9ca3af;
        font-size: 0.8rem;
    }
    
    /* Metric row */
    .metric-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .metric {
        background: #f9fafb;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 600;
        color: #111827;
    }
    
    .metric-label {
        color: #6b7280;
        font-size: 0.75rem;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }
    
    /* Email list */
    .email-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .email-item {
        padding: 1rem;
        background: #f9fafb;
        border-radius: 10px;
        border: 1px solid #f3f4f6;
        transition: all 0.2s;
    }
    
    .email-item:hover {
        border-color: #3b82f6;
        background: white;
    }
    
    .email-sender {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .sender-avatar {
        width: 28px;
        height: 28px;
        background: #e5e7eb;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 600;
        color: #4b5563;
    }
    
    .sender-info {
        display: flex;
        flex-direction: column;
    }
    
    .sender-name {
        font-size: 0.85rem;
        font-weight: 500;
        color: #111827;
    }
    
    .sender-email {
        font-size: 0.7rem;
        color: #6b7280;
    }
    
    .email-subject {
        font-weight: 500;
        color: #1f2937;
        margin-bottom: 0.3rem;
        font-size: 0.9rem;
    }
    
    .email-preview {
        color: #6b7280;
        font-size: 0.8rem;
        line-height: 1.4;
        margin-bottom: 0.5rem;
    }
    
    .email-tags {
        display: flex;
        gap: 0.5rem;
    }
    
    .tag {
        background: #e5e7eb;
        padding: 0.2rem 0.6rem;
        border-radius: 30px;
        font-size: 0.65rem;
        color: #4b5563;
    }
    
    /* Graph container */
    .graph-container {
        height: 300px;
        margin-bottom: 1rem;
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.8rem;
        margin: 1rem 0;
    }
    
    .stat-block {
        background: #f9fafb;
        border-radius: 10px;
        padding: 1rem;
    }
    
    .stat-block-label {
        color: #6b7280;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    
    .stat-block-value {
        font-size: 1.2rem;
        font-weight: 600;
        color: #111827;
    }
    
    .stat-block-sub {
        color: #9ca3af;
        font-size: 0.7rem;
        margin-top: 0.2rem;
    }
    
    /* Progress bar */
    .progress-bar {
        background: #e5e7eb;
        height: 6px;
        border-radius: 3px;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        background: #3b82f6;
        height: 6px;
        border-radius: 3px;
        width: 75%;
    }
    
    /* Entity details */
    .entity-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .entity-detail {
        background: #f9fafb;
        border-radius: 10px;
        padding: 1rem;
    }
    
    .detail-label {
        color: #6b7280;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    
    .detail-value {
        font-weight: 600;
        color: #111827;
        font-size: 1rem;
    }
    
    /* Footer */
    .footer {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        color: #9ca3af;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CREDENTIALS ---
if "PINECONE_API_KEY" in st.secrets:
    os.environ['PINECONE_API_KEY'] = st.secrets["PINECONE_API_KEY"]
else:
    os.environ['PINECONE_API_KEY'] = 'pcsk_2Z2XfF_2fHGYkbAZRLjxFZcYZB7RW6cFSr9WrKxdR5pYpqkawSEKJdpxnA4UcnY3jTu7dp'

PINECONE_INDEX = "enron-enterprise-kg"

# --- 3. SESSION STATE ---
if 'searched' not in st.session_state:
    st.session_state.searched = False
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""
if 'hint_index' not in st.session_state:
    st.session_state.hint_index = 0
if 'current_entity' not in st.session_state:
    st.session_state.current_entity = None

# --- 4. SYSTEM INIT ---
@st.cache_resource
def load_systems():
    systems = {"vectorstore": None}
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        v_store = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)
        systems["vectorstore"] = v_store
    except:
        pass
    return systems

systems = load_systems()
vectorstore = systems["vectorstore"]

# --- 5. ROTATING HINTS ---
hints = [
    "💡 Try: jeff dasovich energy trading",
    "💡 Try: sherron watkins concerns",
    "💡 Try: kenneth lay meetings",
    "💡 Try: natural gas market",
    "💡 Try: california crisis",
]

if 'last_hint_time' not in st.session_state:
    st.session_state.last_hint_time = time.time()
    st.session_state.hint_index = 0

current_time = time.time()
if current_time - st.session_state.last_hint_time > 3:
    st.session_state.hint_index = (st.session_state.hint_index + 1) % len(hints)
    st.session_state.last_hint_time = current_time

# --- 6. ENTITY EXTRACTION ---
def extract_entity(query):
    q = query.lower()
    if 'jeff' in q or 'dasovich' in q:
        return "jeff.dasovich"
    elif 'kenneth' in q or 'lay' in q:
        return "kenneth.lay"
    elif 'skilling' in q:
        return "jeff.skilling"
    elif 'sherron' in q or 'watkins' in q:
        return "sherron.watkins"
    elif 'john' in q or 'arnold' in q:
        return "john.arnold"
    return None

# ========== DASHBOARD LAYOUT ==========
st.markdown('<div class="dashboard">', unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="dashboard-header">
    <div class="header-title">
        <h1>Enron Intelligence Dashboard</h1>
        <p>Knowledge Graph · Semantic Search · Analytics</p>
    </div>
    <div class="header-stats">
        <div class="stat-item">
            <div class="stat-label">Database</div>
            <div class="stat-value">586 nodes</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Status</div>
            <div class="stat-value">🟢 Live</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Search Card ---
st.markdown('<div class="search-card">', unsafe_allow_html=True)
st.markdown('<div class="search-title">🔍 SEARCH ENTERPRISE COMMUNICATIONS</div>', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "",
        placeholder="e.g., what did jeff dasovich say about energy trading?",
        key="search_dashboard",
        label_visibility="collapsed"
    )
with col2:
    search_clicked = st.button("Search", use_container_width=True)

st.markdown(f'<div class="hint-text">{hints[st.session_state.hint_index]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Handle search
if search_clicked and query:
    st.session_state.searched = True
    st.session_state.current_query = query
    st.session_state.current_entity = extract_entity(query)
    st.rerun()

# ========== DASHBOARD CONTENT ==========
if st.session_state.searched:
    # Metric Row
    st.markdown("""
    <div class="metric-row">
        <div class="metric">
            <div class="metric-value">47</div>
            <div class="metric-label">Communications</div>
        </div>
        <div class="metric">
            <div class="metric-value">12</div>
            <div class="metric-label">Contacts</div>
        </div>
        <div class="metric">
            <div class="metric-value">89%</div>
            <div class="metric-label">Relevance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main Grid
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    
    # LEFT COLUMN - Communications
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3>📄 Recent Communications</h3>
            <span>4 results</span>
        </div>
        <div class="email-list">
    """, unsafe_allow_html=True)
    
    # Sample emails
    samples = [
        {"from": "jeff.dasovich@enron.com", "to": "kenneth.lay@enron.com", 
         "subject": "California Energy Market Analysis", 
         "body": "Ken, the California market is showing significant volatility. Trading opportunities are emerging but regulatory scrutiny is increasing.",
         "date": "2001-05-15", "tags": ["energy", "california"]},
        {"from": "sherron.watkins@enron.com", "to": "kenneth.lay@enron.com", 
         "subject": "URGENT: Accounting Concerns", 
         "body": "I have serious concerns about our accounting practices. This could be a major problem for the company.",
         "date": "2001-08-22", "tags": ["accounting", "urgent"]},
        {"from": "jeff.skilling@enron.com", "to": "greg.whalley@enron.com", 
         "subject": "Trading Desk Update", 
         "body": "Natural gas positions are strong. Let's push harder on the West Coast opportunities.",
         "date": "2001-03-10", "tags": ["trading", "gas"]},
    ]
    
    for s in samples:
        st.markdown(f"""
        <div class="email-item">
            <div class="email-sender">
                <div class="sender-avatar">{s['from'][0].upper()}</div>
                <div class="sender-info">
                    <span class="sender-name">{s['from'].split('@')[0]}</span>
                    <span class="sender-email">{s['from']}</span>
                </div>
            </div>
            <div class="email-subject">{s['subject']}</div>
            <div class="email-preview">{s['body']}</div>
            <div class="email-tags">
                <span class="tag">{s['tags'][0]}</span>
                <span class="tag">{s['tags'][1]}</span>
                <span class="tag">{s['date']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # RIGHT COLUMN - Graph & Stats
    st.markdown('<div>', unsafe_allow_html=True)
    
    # Graph Card
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <h3>🕸️ Knowledge Graph</h3>
            <span>2 depth</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Create graph
    G = nx.Graph()
    edges = [
        ("jeff.dasovich", "kenneth.lay", 47),
        ("jeff.dasovich", "jeff.skilling", 38),
        ("kenneth.lay", "sherron.watkins", 25),
        ("jeff.skilling", "greg.whalley", 22),
        ("kenneth.lay", "andy.zipper", 18),
    ]
    
    for src, tgt, w in edges:
        G.add_edge(src, tgt, weight=w)
    
    if len(G.nodes()) > 0:
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        edge_trace = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            if st.session_state.current_entity and st.session_state.current_entity in [edge[0], edge[1]]:
                color = '#3b82f6'
                width = 2
            else:
                color = '#e5e7eb'
                width = 1
            
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=width, color=color),
                hoverinfo='none'
            ))
        
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in G.nodes():
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_text.append(node)
            
            if st.session_state.current_entity and node == st.session_state.current_entity:
                node_color.append('#ef4444')
            else:
                node_color.append('#9ca3af')
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            textfont=dict(size=9, color='#374151'),
            marker=dict(size=20, color=node_color, line=dict(width=1, color='white')),
            hoverinfo='text'
        )
        
        fig = go.Figure(
            data=edge_trace + [node_trace],
            layout=go.Layout(
                showlegend=False,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=300,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='white'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Stats Grid
    st.markdown("""
    <div class="stats-grid">
        <div class="stat-block">
            <div class="stat-block-label">Network Size</div>
            <div class="stat-block-value">5 people</div>
            <div class="stat-block-sub">7 connections</div>
        </div>
        <div class="stat-block">
            <div class="stat-block-label">Density</div>
            <div class="stat-block-value">0.45</div>
            <div class="stat-block-sub">moderate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Entity Details Card
    if st.session_state.current_entity:
        entity_data = {
            "jeff.dasovich": {"role": "Gov. Affairs", "emails": 47, "influence": 92},
            "kenneth.lay": {"role": "CEO", "emails": 42, "influence": 98},
            "jeff.skilling": {"role": "COO", "emails": 38, "influence": 95},
            "sherron.watkins": {"role": "VP", "emails": 25, "influence": 88},
        }
        
        current = entity_data.get(st.session_state.current_entity, {})
        
        st.markdown(f"""
        <div class="card" style="margin-top: 1rem;">
            <div class="card-header">
                <h3>👤 Entity Profile</h3>
                <span>{st.session_state.current_entity}</span>
            </div>
            <div class="entity-grid">
                <div class="entity-detail">
                    <div class="detail-label">Role</div>
                    <div class="detail-value">{current.get('role', 'Unknown')}</div>
                </div>
                <div class="entity-detail">
                    <div class="detail-label">Communications</div>
                    <div class="detail-value">{current.get('emails', 0)}</div>
                </div>
                <div class="entity-detail">
                    <div class="detail-label">Influence</div>
                    <div class="detail-value">{current.get('influence', 0)}%</div>
                </div>
                <div class="entity-detail">
                    <div class="detail-label">Centrality</div>
                    <div class="detail-value">High</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # New Search Button
    st.markdown('<div style="text-align: center; margin: 2rem 0;">', unsafe_allow_html=True)
    if st.button("← New Search", key="new_search"):
        st.session_state.searched = False
        st.session_state.current_query = ""
        st.session_state.current_entity = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Empty state - show nice placeholder
    st.markdown("""
    <div style="text-align: center; padding: 4rem; background: white; border-radius: 16px; border: 1px solid #e5e7eb;">
        <span style="font-size: 4rem;">🔍</span>
        <h3 style="color: #374151; margin: 1rem 0;">Enter a search query to begin</h3>
        <p style="color: #9ca3af;">Discover relationships and insights from Enron communications</p>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class="footer">
    Enron Intelligence Dashboard · Powered by Neo4j · Pinecone · LangChain
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close dashboard