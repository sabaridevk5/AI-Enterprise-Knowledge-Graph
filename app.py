# app.py - SIMPLE CLEAN DASHBOARD

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

# --- 1. SIMPLE CLEAN CSS ---
st.set_page_config(
    page_title="Enron Knowledge Graph", 
    layout="wide", 
    page_icon="🔍"
)

# Minimal, clean CSS
st.markdown("""
<style>
    /* Simple fonts */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Clean header */
    .clean-header {
        padding: 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #eaeef2;
    }
    
    .title {
        font-size: 1.8rem;
        font-weight: 500;
        color: #1a2639;
        letter-spacing: -0.01em;
    }
    
    .subtitle {
        font-size: 0.9rem;
        color: #5d6d7e;
        margin-top: 0.2rem;
    }
    
    /* Simple search */
    .search-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Clean cards */
    .clean-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #edf2f7;
        margin-bottom: 1rem;
    }
    
    /* Simple email items */
    .email-item {
        padding: 1rem;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .email-item:last-child {
        border-bottom: none;
    }
    
    .email-sender {
        font-size: 0.85rem;
        color: #4a5568;
    }
    
    .email-subject {
        font-weight: 500;
        color: #1e293b;
        margin: 0.3rem 0;
    }
    
    .email-preview {
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.5;
    }
    
    .email-meta {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    /* Simple metrics */
    .simple-metric {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .metric-number {
        font-size: 1.8rem;
        font-weight: 500;
        color: #1e293b;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.2rem;
    }
    
    /* Status dot */
    .dot {
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.4rem;
    }
    
    /* Rotating hint */
    .hint {
        background: #f1f5f9;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #475569;
        display: inline-block;
        margin-top: 0.8rem;
    }
    
    /* Divider */
    .divider {
        margin: 1.5rem 0;
        border: 0;
        height: 1px;
        background: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CREDENTIALS ---
if "PINECONE_API_KEY" in st.secrets:
    os.environ['PINECONE_API_KEY'] = st.secrets["PINECONE_API_KEY"]
    NEO4J_URI = st.secrets.get("NEO4J_URI", "")
    NEO4J_USER = st.secrets.get("NEO4J_USER", "")
    NEO4J_PASSWORD = st.secrets.get("NEO4J_PASSWORD", "")
else:
    os.environ['PINECONE_API_KEY'] = 'pcsk_2Z2XfF_2fHGYkbAZRLjxFZcYZB7RW6cFSr9WrKxdR5pYpqkawSEKJdpxnA4UcnY3jTu7dp'

PINECONE_INDEX = "enron-enterprise-kg"

# --- 3. SESSION STATE ---
if 'search_value' not in st.session_state:
    st.session_state.search_value = ""
if 'current_entity' not in st.session_state:
    st.session_state.current_entity = "jeff.dasovich"
if 'hint_index' not in st.session_state:
    st.session_state.hint_index = 0

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
    "Try: natural gas market analysis",
    "Try: jeff dasovich california",
    "Try: sherron watkins concerns",
    "Try: energy trading strategies",
    "Try: kenneth lay meetings",
]

if 'last_hint_time' not in st.session_state:
    st.session_state.last_hint_time = time.time()
    st.session_state.hint_index = 0

current_time = time.time()
if current_time - st.session_state.last_hint_time > 3:
    st.session_state.hint_index = (st.session_state.hint_index + 1) % len(hints)
    st.session_state.last_hint_time = current_time

# --- 6. SIMPLE ENTITY EXTRACTION ---
def get_entity_from_query(query):
    q = query.lower()
    if 'jeff' in q or 'dasovich' in q:
        return "jeff.dasovich"
    elif 'kenneth' in q or 'lay' in q:
        return "kenneth.lay"
    elif 'skilling' in q:
        return "jeff.skilling"
    elif 'sherron' in q or 'watkins' in q:
        return "sherron.watkins"
    return st.session_state.current_entity

# ========== MAIN LAYOUT ==========

# --- Simple Header ---
st.markdown('<div class="clean-header">', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="title">🔍 Enron Knowledge Graph</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Semantic search · Relationship discovery</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div style="text-align: right; padding-top: 0.5rem;"><span class="dot"></span> <span style="color:#4a5568;">connected</span></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Simple Search ---
st.markdown('<div class="search-section">', unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "Search",
        value=st.session_state.search_value,
        placeholder="Ask about Enron communications...",
        key="search_input",
        label_visibility="collapsed"
    )
with col2:
    search_button = st.button("Search", use_container_width=True)

# Update on Enter or button click
if search_button or (query and query != st.session_state.search_value):
    st.session_state.search_value = query
    if query:
        st.session_state.current_entity = get_entity_from_query(query)

st.markdown(f'<div class="hint">{hints[st.session_state.hint_index]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Main Content: Two Columns ---
col_left, col_right = st.columns([1, 1.2])

# ========== LEFT COLUMN: SEARCH RESULTS ==========
with col_left:
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.markdown("**📄 Communications**")
    
    if st.session_state.search_value and vectorstore:
        try:
            docs = vectorstore.similarity_search(st.session_state.search_value, k=4)
            if docs:
                for doc in docs:
                    st.markdown(f"""
                    <div class="email-item">
                        <div class="email-sender">📧 {doc.metadata.get('From', 'Unknown')}</div>
                        <div class="email-subject">{doc.metadata.get('Subject', 'No Subject')}</div>
                        <div class="email-preview">{doc.page_content[:150]}...</div>
                        <div class="email-meta">{doc.metadata.get('Date', 'Unknown')[:10]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No results found")
        except:
            st.info("Search unavailable")
    else:
        # Simple placeholder
        for i in range(3):
            st.markdown(f"""
            <div class="email-item">
                <div class="email-sender">📧 jeff.dasovich@enron.com</div>
                <div class="email-subject">California Energy Market Analysis</div>
                <div class="email-preview">The California market is showing significant volatility. Trading opportunities are emerging...</div>
                <div class="email-meta">2001-05-15</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== RIGHT COLUMN: GRAPH ==========
with col_right:
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.markdown("**🕸️ Relationship Graph**")
    
    # Simple graph
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
            if st.session_state.current_entity in [edge[0], edge[1]]:
                color = '#3b82f6'
                width = 2
            else:
                color = '#cbd5e1'
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
            
            if node == st.session_state.current_entity:
                node_color.append('#ef4444')
            else:
                node_color.append('#94a3b8')
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            textfont=dict(size=9),
            marker=dict(size=25, color=node_color, line=dict(width=1, color='white')),
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
        
        # Simple metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="simple-metric">
                <div class="metric-number">{G.number_of_nodes()}</div>
                <div class="metric-label">people</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="simple-metric">
                <div class="metric-number">{G.number_of_edges()}</div>
                <div class="metric-label">connections</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="simple-metric">
                <div class="metric-number">{G.degree(st.session_state.current_entity)}</div>
                <div class="metric-label">your connections</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Simple Entity Details ---
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

entity_data = {
    "jeff.dasovich": {"role": "Gov. Affairs", "emails": 47, "topics": "Energy Trading"},
    "kenneth.lay": {"role": "CEO", "emails": 42, "topics": "Executive"},
    "jeff.skilling": {"role": "COO", "emails": 38, "topics": "Trading"},
    "sherron.watkins": {"role": "VP", "emails": 25, "topics": "Accounting"},
}

current = entity_data.get(st.session_state.current_entity, entity_data["jeff.dasovich"])

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="clean-card"><span style="color:#4a5568;">Entity</span><br><b>{st.session_state.current_entity}</b></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="clean-card"><span style="color:#4a5568;">Role</span><br><b>{current["role"]}</b></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="clean-card"><span style="color:#4a5568;">Communications</span><br><b>{current["emails"]}</b></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="clean-card"><span style="color:#4a5568;">Main Topic</span><br><b>{current["topics"]}</b></div>', unsafe_allow_html=True)

# --- Simple Footer ---
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #94a3b8; font-size: 0.75rem; padding: 1rem;">Enron Knowledge Graph · Simple · Clean · Functional</div>', unsafe_allow_html=True)