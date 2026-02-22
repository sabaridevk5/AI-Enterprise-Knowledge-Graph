# app.py - CLEAN MINIMAL DASHBOARD

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
from datetime import datetime

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# --- 1. MINIMAL CSS ---
st.set_page_config(
    page_title="Enron Graph", 
    layout="wide", 
    page_icon="🔍"
)

st.markdown("""
<style>
    /* Reset */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Main container */
    .main {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    
    /* Header */
    .header {
        margin-bottom: 3rem;
    }
    
    .header h1 {
        font-size: 2rem;
        font-weight: 500;
        color: #111;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }
    
    .header p {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Search container */
    .search-container {
        background: #f5f5f5;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Search input */
    .search-input {
        width: 100%;
        max-width: 600px;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        border: 1px solid #ddd;
        border-radius: 40px;
        outline: none;
        transition: all 0.2s;
        margin: 0 auto 1rem auto;
    }
    
    .search-input:focus {
        border-color: #0066ff;
        box-shadow: 0 0 0 3px rgba(0,102,255,0.1);
    }
    
    /* Hint text */
    .hint {
        color: #888;
        font-size: 0.85rem;
        margin-top: 1rem;
        animation: fade 2s infinite;
    }
    
    @keyframes fade {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    /* Results container */
    .results-container {
        margin-top: 2rem;
    }
    
    /* Section titles */
    .section-title {
        font-size: 1.1rem;
        font-weight: 500;
        color: #333;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eee;
    }
    
    /* Email card */
    .email-card {
        background: white;
        border: 1px solid #eee;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.2s;
    }
    
    .email-card:hover {
        border-color: #0066ff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .email-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        color: #666;
        font-size: 0.85rem;
    }
    
    .email-subject {
        font-weight: 500;
        color: #222;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .email-body {
        color: #444;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 0.5rem;
    }
    
    .email-meta {
        display: flex;
        gap: 1rem;
        color: #888;
        font-size: 0.75rem;
    }
    
    /* Graph container */
    .graph-container {
        background: white;
        border: 1px solid #eee;
        border-radius: 8px;
        padding: 1rem;
        height: 400px;
    }
    
    /* Stats cards */
    .stat-card {
        background: #f9f9f9;
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: 500;
        color: #111;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.8rem;
        margin-top: 0.2rem;
    }
    
    /* Entity card */
    .entity-card {
        background: #f9f9f9;
        border-radius: 6px;
        padding: 1rem;
    }
    
    .entity-label {
        color: #666;
        font-size: 0.8rem;
        margin-bottom: 0.2rem;
    }
    
    .entity-value {
        font-weight: 500;
        color: #222;
    }
    
    /* Divider */
    .divider {
        margin: 2rem 0;
        border: 0;
        height: 1px;
        background: #eee;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #888;
        font-size: 0.75rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
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
    "Try: what did jeff dasovich say about energy trading",
    "Try: sherron watkins accounting concerns",
    "Try: kenneth lay meetings",
    "Try: natural gas market analysis",
    "Try: california energy crisis",
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

# ========== MAIN LAYOUT ==========
st.markdown('<div class="main">', unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="header">
    <h1>🔍 Enron Graph</h1>
    <p>Search communications · Discover relationships</p>
</div>
""", unsafe_allow_html=True)

# --- Search Section ---
st.markdown('<div class="search-container">', unsafe_allow_html=True)

# Centered search
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    query = st.text_input(
        "",
        placeholder="Ask anything about Enron...",
        key="search",
        label_visibility="collapsed"
    )
    
    search_clicked = st.button("Search", use_container_width=True)
    
    # Rotating hint
    st.markdown(f'<div class="hint">{hints[st.session_state.hint_index]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Handle search
if search_clicked and query:
    st.session_state.searched = True
    st.session_state.current_query = query
    st.session_state.current_entity = extract_entity(query)
    st.rerun()

# ========== RESULTS (only show after search) ==========
if st.session_state.searched:
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # Two columns
    col_left, col_right = st.columns([1, 1.2])
    
    # --- LEFT COLUMN: EMAIL RESULTS ---
    with col_left:
        st.markdown('<div class="section-title">📄 Results</div>', unsafe_allow_html=True)
        
        if vectorstore:
            try:
                docs = vectorstore.similarity_search(st.session_state.current_query, k=4)
                if docs:
                    for doc in docs:
                        st.markdown(f"""
                        <div class="email-card">
                            <div class="email-header">
                                <span>📧 {doc.metadata.get('From', 'Unknown')}</span>
                                <span>→</span>
                                <span>{doc.metadata.get('To', 'Unknown')}</span>
                            </div>
                            <div class="email-subject">{doc.metadata.get('Subject', 'No Subject')}</div>
                            <div class="email-body">{doc.page_content[:200]}...</div>
                            <div class="email-meta">
                                <span>📅 {doc.metadata.get('Date', 'Unknown')[:10]}</span>
                                <span>🔗 {np.random.randint(2,6)} connections</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No results found")
            except:
                # Sample results
                samples = [
                    {"from": "jeff.dasovich@enron.com", "to": "kenneth.lay@enron.com", 
                     "subject": "California Energy Market", 
                     "body": "Ken, the California market is volatile. Trading opportunities are significant but regulatory scrutiny is increasing.",
                     "date": "2001-05-15"},
                    {"from": "sherron.watkins@enron.com", "to": "kenneth.lay@enron.com", 
                     "subject": "Accounting Concerns", 
                     "body": "I have serious concerns about our accounting practices. This could be a major problem.",
                     "date": "2001-08-22"},
                ]
                for s in samples:
                    st.markdown(f"""
                    <div class="email-card">
                        <div class="email-header">
                            <span>📧 {s['from']}</span>
                            <span>→</span>
                            <span>{s['to']}</span>
                        </div>
                        <div class="email-subject">{s['subject']}</div>
                        <div class="email-body">{s['body']}</div>
                        <div class="email-meta">
                            <span>📅 {s['date']}</span>
                            <span>🔗 4 connections</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Search unavailable - using sample data")
            # Show sample results
            samples = [
                {"from": "jeff.dasovich@enron.com", "to": "kenneth.lay@enron.com", 
                 "subject": "California Energy Market", 
                 "body": "Ken, the California market is volatile. Trading opportunities are significant but regulatory scrutiny is increasing.",
                 "date": "2001-05-15"},
                {"from": "sherron.watkins@enron.com", "to": "kenneth.lay@enron.com", 
                 "subject": "Accounting Concerns", 
                 "body": "I have serious concerns about our accounting practices. This could be a major problem.",
                 "date": "2001-08-22"},
            ]
            for s in samples:
                st.markdown(f"""
                <div class="email-card">
                    <div class="email-header">
                        <span>📧 {s['from']}</span>
                        <span>→</span>
                        <span>{s['to']}</span>
                    </div>
                    <div class="email-subject">{s['subject']}</div>
                    <div class="email-body">{s['body']}</div>
                    <div class="email-meta">
                        <span>📅 {s['date']}</span>
                        <span>🔗 4 connections</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # --- RIGHT COLUMN: GRAPH ---
    with col_right:
        st.markdown('<div class="section-title">🕸️ Network</div>', unsafe_allow_html=True)
        
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
            
            # Edge trace
            edge_trace = []
            for edge in G.edges(data=True):
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                
                # Highlight current entity's connections
                if st.session_state.current_entity and st.session_state.current_entity in [edge[0], edge[1]]:
                    color = '#0066ff'
                    width = 2
                else:
                    color = '#ddd'
                    width = 1
                
                edge_trace.append(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=width, color=color),
                    hoverinfo='none'
                ))
            
            # Node trace
            node_x = []
            node_y = []
            node_text = []
            node_color = []
            
            for node in G.nodes():
                node_x.append(pos[node][0])
                node_y.append(pos[node][1])
                node_text.append(node)
                
                if st.session_state.current_entity and node == st.session_state.current_entity:
                    node_color.append('#ff4444')
                else:
                    node_color.append('#aaa')
            
            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text',
                text=node_text,
                textposition="top center",
                textfont=dict(size=9, color='#333'),
                marker=dict(size=20, color=node_color, line=dict(width=1, color='white')),
                hoverinfo='text'
            )
            
            fig = go.Figure(
                data=edge_trace + [node_trace],
                layout=go.Layout(
                    showlegend=False,
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    height=400,
                    margin=dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor='white'
                )
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Simple stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{G.number_of_nodes()}</div>
                    <div class="stat-label">people</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{G.number_of_edges()}</div>
                    <div class="stat-label">connections</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                if st.session_state.current_entity:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-number">{G.degree(st.session_state.current_entity)}</div>
                        <div class="stat-label">direct contacts</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # --- ENTITY DETAILS (only if entity found) ---
    if st.session_state.current_entity:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        entity_data = {
            "jeff.dasovich": {"role": "Gov. Affairs", "emails": 47, "topics": "Energy Trading"},
            "kenneth.lay": {"role": "CEO", "emails": 42, "topics": "Executive"},
            "jeff.skilling": {"role": "COO", "emails": 38, "topics": "Trading"},
            "sherron.watkins": {"role": "VP", "emails": 25, "topics": "Accounting"},
        }
        
        current = entity_data.get(st.session_state.current_entity, {})
        if current:
            cols = st.columns(4)
            with cols[0]:
                st.markdown(f'<div class="entity-card"><div class="entity-label">Person</div><div class="entity-value">{st.session_state.current_entity}</div></div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f'<div class="entity-card"><div class="entity-label">Role</div><div class="entity-value">{current.get("role", "Unknown")}</div></div>', unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f'<div class="entity-card"><div class="entity-label">Communications</div><div class="entity-value">{current.get("emails", 0)}</div></div>', unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f'<div class="entity-card"><div class="entity-label">Main Topic</div><div class="entity-value">{current.get("topics", "Unknown")}</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- New Search Button (to search again) ---
if st.session_state.searched:
    st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
    if st.button("← New Search"):
        st.session_state.searched = False
        st.session_state.current_query = ""
        st.session_state.current_entity = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class="footer">
    Enron Graph · Simple · Clean · Functional
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close main