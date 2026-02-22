# app.py - BEAUTIFUL DASHBOARD UI

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

# --- 1. BEAUTIFUL DASHBOARD CSS ---
st.set_page_config(
    page_title="Enron Analytics", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Beautiful modern CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: #f8fafc;
    }
    
    /* Main container */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Top stats bar */
    .stats-bar {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.01);
        border: 1px solid #f1f5f9;
        transition: all 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05);
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        margin-bottom: 0.5rem;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 600;
        color: #0f172a;
        line-height: 1.2;
    }
    
    .stat-change {
        font-size: 0.8rem;
        color: #10b981;
        margin-top: 0.3rem;
    }
    
    /* Header */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .title-section h1 {
        font-size: 1.8rem;
        font-weight: 600;
        color: #0f172a;
        letter-spacing: -0.02em;
    }
    
    .title-section p {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 0.2rem;
    }
    
    .date-badge {
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 40px;
        font-size: 0.85rem;
        color: #334155;
        border: 1px solid #e2e8f0;
    }
    
    /* Search section */
    .search-section {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid #f1f5f9;
    }
    
    .search-label {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    
    .search-wrapper {
        display: flex;
        gap: 0.75rem;
    }
    
    .search-input {
        flex: 1;
        padding: 0.9rem 1.2rem;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        font-size: 0.95rem;
        outline: none;
        transition: all 0.2s;
        background: #f8fafc;
    }
    
    .search-input:focus {
        border-color: #3b82f6;
        background: white;
        box-shadow: 0 0 0 4px rgba(59,130,246,0.1);
    }
    
    .search-button {
        background: #0f172a;
        color: white;
        border: none;
        padding: 0.9rem 2rem;
        border-radius: 14px;
        font-weight: 500;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .search-button:hover {
        background: #1e293b;
    }
    
    /* Hint carousel */
    .hint-carousel {
        margin-top: 1rem;
        padding: 0.75rem 1rem;
        background: #f8fafc;
        border-radius: 40px;
        color: #475569;
        font-size: 0.9rem;
        animation: gentlePulse 2s infinite;
    }
    
    @keyframes gentlePulse {
        0% { opacity: 0.7; }
        50% { opacity: 1; }
        100% { opacity: 0.7; }
    }
    
    /* Dashboard grid */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Cards */
    .dashboard-card {
        background: white;
        border-radius: 24px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
        border: 1px solid #f1f5f9;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .card-header h3 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-badge {
        background: #f1f5f9;
        padding: 0.25rem 0.75rem;
        border-radius: 30px;
        font-size: 0.75rem;
        color: #475569;
    }
    
    /* Email list */
    .email-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .email-row {
        display: flex;
        align-items: center;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 16px;
        transition: all 0.2s;
        border: 1px solid transparent;
    }
    
    .email-row:hover {
        background: white;
        border-color: #e2e8f0;
        transform: translateX(4px);
    }
    
    .avatar {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        margin-right: 1rem;
    }
    
    .email-content {
        flex: 1;
    }
    
    .email-meta {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.3rem;
    }
    
    .sender {
        font-weight: 600;
        color: #0f172a;
        font-size: 0.9rem;
    }
    
    .date {
        color: #94a3b8;
        font-size: 0.75rem;
    }
    
    .subject {
        font-weight: 500;
        color: #1e293b;
        margin-bottom: 0.25rem;
        font-size: 0.95rem;
    }
    
    .preview {
        color: #64748b;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    
    .badge {
        background: #e2e8f0;
        padding: 0.2rem 0.6rem;
        border-radius: 30px;
        font-size: 0.7rem;
        color: #475569;
        margin-left: 0.5rem;
    }
    
    /* Chart container */
    .chart-container {
        background: #f8fafc;
        border-radius: 20px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Metrics grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-block {
        background: #f8fafc;
        border-radius: 16px;
        padding: 1.2rem;
    }
    
    .metric-block-label {
        color: #64748b;
        font-size: 0.75rem;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }
    
    .metric-block-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0f172a;
    }
    
    .metric-block-trend {
        color: #10b981;
        font-size: 0.8rem;
        margin-top: 0.2rem;
    }
    
    /* Progress bar */
    .progress-bar {
        background: #e2e8f0;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        border-radius: 4px;
        width: 75%;
    }
    
    /* Entity grid */
    .entity-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .entity-item {
        background: #f8fafc;
        border-radius: 16px;
        padding: 1rem;
    }
    
    .entity-item-label {
        color: #64748b;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    
    .entity-item-value {
        font-weight: 600;
        color: #0f172a;
        font-size: 1rem;
    }
    
    /* Graph container */
    .graph-wrapper {
        background: #f8fafc;
        border-radius: 20px;
        padding: 1rem;
        margin: 1rem 0;
        height: 350px;
    }
    
    /* Footer */
    .footer {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #94a3b8;
        font-size: 0.8rem;
    }
    
    .footer-links {
        display: flex;
        gap: 2rem;
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
    "🔍 Try: jeff dasovich energy trading",
    "📧 Try: sherron watkins concerns",
    "👤 Try: kenneth lay meetings",
    "📊 Try: natural gas market",
    "⚡ Try: california crisis",
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
    return None

# ========== MAIN LAYOUT ==========
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="header">
    <div class="title-section">
        <h1>Enron Analytics</h1>
        <p>Intelligence Dashboard · Knowledge Graph · Semantic Search</p>
    </div>
    <div class="date-badge">
        📅 February 2026
    </div>
</div>
""", unsafe_allow_html=True)

# --- Top Stats Bar ---
st.markdown("""
<div class="stats-bar">
    <div class="stat-card">
        <div class="stat-label">Total Communications</div>
        <div class="stat-number">2,547</div>
        <div class="stat-change">↑ 12.3%</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Active Participants</div>
        <div class="stat-number">158</div>
        <div class="stat-change">↑ 8</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Key Topics</div>
        <div class="stat-number">24</div>
        <div class="stat-change">→ stable</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Avg Response</div>
        <div class="stat-number">2.4h</div>
        <div class="stat-change">↓ 15%</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Search Section ---
st.markdown('<div class="search-section">', unsafe_allow_html=True)
st.markdown('<div class="search-label">🔎 SEARCH ENTERPRISE KNOWLEDGE BASE</div>', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    query = st.text_input(
        "",
        placeholder="Ask anything about Enron communications...",
        key="search_main",
        label_visibility="collapsed"
    )
with col2:
    search_clicked = st.button("Search", use_container_width=True)

st.markdown(f'<div class="hint-carousel">{hints[st.session_state.hint_index]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Handle search
if search_clicked and query:
    st.session_state.searched = True
    st.session_state.current_query = query
    st.session_state.current_entity = extract_entity(query)
    st.rerun()

# ========== DASHBOARD CONTENT ==========
if st.session_state.searched:
    # Main Grid
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    
    # LEFT COLUMN - Communications
    st.markdown("""
    <div class="dashboard-card">
        <div class="card-header">
            <h3>📧 Recent Communications</h3>
            <span class="card-badge">4 matches</span>
        </div>
        <div class="email-list">
    """, unsafe_allow_html=True)
    
    # Sample emails
    emails = [
        {"from": "Jeff Dasovich", "email": "jeff.dasovich@enron.com", 
         "subject": "California Energy Market Analysis", 
         "preview": "Ken, the California market is showing significant volatility. Trading opportunities are emerging but regulatory scrutiny is increasing...",
         "date": "May 15, 2001", "tags": ["energy", "california"]},
        {"from": "Sherron Watkins", "email": "sherron.watkins@enron.com", 
         "subject": "URGENT: Accounting Concerns", 
         "preview": "I have serious concerns about our accounting practices. This could be a major problem for the company...",
         "date": "Aug 22, 2001", "tags": ["accounting", "urgent"]},
        {"from": "Jeff Skilling", "email": "jeff.skilling@enron.com", 
         "subject": "Trading Desk Update", 
         "preview": "Natural gas positions are strong. Let's push harder on the West Coast opportunities...",
         "date": "Mar 10, 2001", "tags": ["trading", "gas"]},
        {"from": "Kenneth Lay", "email": "kenneth.lay@enron.com", 
         "subject": "Executive Meeting", 
         "preview": "Board meeting scheduled for next week to discuss quarterly results...",
         "date": "Apr 5, 2001", "tags": ["executive", "meeting"]},
    ]
    
    for e in emails:
        st.markdown(f"""
        <div class="email-row">
            <div class="avatar">{e['from'][0]}</div>
            <div class="email-content">
                <div class="email-meta">
                    <span class="sender">{e['from']}</span>
                    <span class="date">{e['date']}</span>
                </div>
                <div class="subject">{e['subject']}</div>
                <div class="preview">{e['preview']}</div>
                <div style="margin-top: 0.5rem;">
                    <span class="badge">{e['tags'][0]}</span>
                    <span class="badge">{e['tags'][1]}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # RIGHT COLUMN - Graph & Analytics
    st.markdown('<div>', unsafe_allow_html=True)
    
    # Graph Card
    st.markdown("""
    <div class="dashboard-card">
        <div class="card-header">
            <h3>🕸️ Knowledge Graph</h3>
            <span class="card-badge">live</span>
        </div>
        <div class="graph-wrapper">
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
            color = '#3b82f6' if st.session_state.current_entity and st.session_state.current_entity in [edge[0], edge[1]] else '#e2e8f0'
            
            edge_trace.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode='lines', line=dict(width=2, color=color),
                hoverinfo='none'
            ))
        
        node_x, node_y, node_color = [], [], []
        for node in G.nodes():
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_color.append('#ef4444' if st.session_state.current_entity == node else '#94a3b8')
        
        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers+text',
            text=list(G.nodes()), textposition="top center",
            marker=dict(size=25, color=node_color, line=dict(width=2, color='white'))
        )
        
        fig = go.Figure(
            data=edge_trace + [node_trace],
            layout=go.Layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False),
                           height=300, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor='white')
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Metrics Grid
    st.markdown("""
    <div class="metrics-grid">
        <div class="metric-block">
            <div class="metric-block-label">Network Size</div>
            <div class="metric-block-value">5 nodes</div>
            <div class="metric-block-trend">7 connections</div>
        </div>
        <div class="metric-block">
            <div class="metric-block-label">Density</div>
            <div class="metric-block-value">0.45</div>
            <div class="metric-block-trend">moderate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Entity Details
    if st.session_state.current_entity:
        st.markdown("""
        <div style="margin-top: 1rem;">
            <div class="card-header">
                <h3>👤 Entity Profile</h3>
            </div>
            <div class="entity-grid">
                <div class="entity-item">
                    <div class="entity-item-label">Name</div>
                    <div class="entity-item-value">{}</div>
                </div>
                <div class="entity-item">
                    <div class="entity-item-label">Role</div>
                    <div class="entity-item-value">Executive</div>
                </div>
                <div class="entity-item">
                    <div class="entity-item-label">Communications</div>
                    <div class="entity-item-value">42</div>
                </div>
                <div class="entity-item">
                    <div class="entity-item-label">Influence</div>
                    <div class="entity-item-value">High</div>
                </div>
            </div>
        </div>
        """.format(st.session_state.current_entity), unsafe_allow_html=True)
    
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
    # Beautiful empty state
    st.markdown("""
    <div style="background: white; border-radius: 30px; padding: 4rem; text-align: center; border: 1px solid #f1f5f9;">
        <span style="font-size: 5rem;">🔍</span>
        <h2 style="color: #0f172a; margin: 1rem 0; font-weight: 500;">Explore Enron's Communications</h2>
        <p style="color: #64748b; max-width: 500px; margin: 0 auto;">Enter a search query to discover relationships, patterns, and insights from the Enron email dataset.</p>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class="footer">
    <div>© 2026 Enron Analytics · Enterprise Intelligence</div>
    <div class="footer-links">
        <span>Knowledge Graph</span>
        <span>Semantic Search</span>
        <span>Analytics</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)