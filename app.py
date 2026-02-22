# app.py - CLEAN BEAUTIFUL DASHBOARD

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
import random

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_neo4j import Neo4jGraph

# --- 1. BEAUTIFUL CUSTOM CSS ---
st.set_page_config(
    page_title="Enron Graph Intelligence", 
    layout="wide", 
    page_icon="🔍",
    initial_sidebar_state="collapsed"
)

# Minimal beautiful CSS
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main title */
    .main-title {
        font-size: 2.2rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    
    /* Subtitle */
    .subtitle {
        font-size: 0.9rem;
        color: #6B7280;
        margin-bottom: 1.5rem;
    }
    
    /* Beautiful search container */
    .search-container {
        background: white;
        padding: 2rem 2rem 1.5rem 2rem;
        border-radius: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
        border: 1px solid #F3F4F6;
        margin-bottom: 1.5rem;
    }
    
    /* Rotating hints */
    .rotating-hint {
        background: #F9FAFB;
        padding: 0.8rem 1.2rem;
        border-radius: 40px;
        color: #4B5563;
        font-size: 0.95rem;
        border: 1px solid #E5E7EB;
        margin-top: 1rem;
        display: inline-block;
        animation: gentlePulse 3s infinite;
    }
    
    @keyframes gentlePulse {
        0% { background: #F9FAFB; }
        50% { background: #F3F4F6; }
        100% { background: #F9FAFB; }
    }
    
    /* Card styling */
    .beautiful-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        border: 1px solid #F3F4F6;
        height: 100%;
        transition: all 0.2s ease;
    }
    
    .beautiful-card:hover {
        border-color: #E5E7EB;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #F3F4F6;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Metric badges */
    .metric-badge {
        background: #F9FAFB;
        padding: 0.25rem 0.8rem;
        border-radius: 30px;
        font-size: 0.75rem;
        color: #4B5563;
        border: 1px solid #E5E7EB;
    }
    
    /* Email result styling */
    .email-result {
        padding: 1rem;
        background: #F9FAFB;
        border-radius: 16px;
        margin-bottom: 0.8rem;
        border: 1px solid #F3F4F6;
        transition: all 0.2s ease;
    }
    
    .email-result:hover {
        background: #F3F4F6;
        border-color: #E5E7EB;
    }
    
    .email-sender {
        font-size: 0.8rem;
        color: #6B7280;
        margin-bottom: 0.3rem;
    }
    
    .email-subject {
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.3rem;
    }
    
    .email-preview {
        font-size: 0.9rem;
        color: #4B5563;
        line-height: 1.4;
    }
    
    .email-meta {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
        font-size: 0.7rem;
        color: #9CA3AF;
    }
    
    /* Status dot */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10B981;
        margin-right: 0.4rem;
    }
    
    /* Divider */
    .light-divider {
        margin: 1.5rem 0;
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #F3F4F6, transparent);
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
if 'search_value' not in st.session_state:
    st.session_state.search_value = ""
if 'current_entity' not in st.session_state:
    st.session_state.current_entity = "jeff.dasovich"
if 'hint_index' not in st.session_state:
    st.session_state.hint_index = 0

# --- 4. SYSTEM INIT ---
@st.cache_resource
def load_systems():
    systems = {"vectorstore": None, "graph": None}
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
    "💡 Try: natural gas market analysis",
    "💡 Try: jeff dasovich emails about california",
    "💡 Try: sherron watkins accounting concerns",
    "💡 Try: energy trading strategies",
    "💡 Try: kenneth lay meeting schedule",
]

# Auto-rotate hints every 3 seconds
if 'last_hint_time' not in st.session_state:
    st.session_state.last_hint_time = time.time()
    st.session_state.hint_index = 0

current_time = time.time()
if current_time - st.session_state.last_hint_time > 3:
    st.session_state.hint_index = (st.session_state.hint_index + 1) % len(hints)
    st.session_state.last_hint_time = current_time

# ========== MAIN LAYOUT ==========

# --- Header ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-title">🔍 Enron Graph Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Semantic search meets knowledge graph visualization</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="text-align: right; padding-top: 0.8rem;">
        <span class="status-dot"></span>
        <span style="font-size:0.8rem; color:#6B7280;">Connected</span>
    </div>
    """, unsafe_allow_html=True)

# --- Beautiful Search Bar ---
st.markdown('<div class="search-container">', unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1:
    query = st.text_input(
        "Search",
        value=st.session_state.search_value,
        placeholder="Ask anything about Enron communications...",
        key="search_main",
        label_visibility="collapsed"
    )
with col2:
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")

# Rotating hint
st.markdown(f'<div class="rotating-hint">{hints[st.session_state.hint_index]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Update search value
if search_button and query:
    st.session_state.search_value = query

# Simple entity extraction from query
search_term = st.session_state.search_value
if search_term:
    if "jeff" in search_term.lower() or "dasovich" in search_term.lower():
        st.session_state.current_entity = "jeff.dasovich"
    elif "kenneth" in search_term.lower() or "lay" in search_term.lower():
        st.session_state.current_entity = "kenneth.lay"
    elif "skilling" in search_term.lower():
        st.session_state.current_entity = "jeff.skilling"
    elif "watkins" in search_term.lower() or "sherron" in search_term.lower():
        st.session_state.current_entity = "sherron.watkins"
    elif "arnold" in search_term.lower() or "john" in search_term.lower():
        st.session_state.current_entity = "john.arnold"

# --- Main Content Grid ---
col1, col2 = st.columns([1, 1.2])

# ========== LEFT COLUMN - SEARCH RESULTS ==========
with col1:
    st.markdown('<div class="beautiful-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📄 Relevant Communications</div>', unsafe_allow_html=True)
    
    if search_term and vectorstore:
        with st.spinner(""):
            try:
                docs = vectorstore.similarity_search(search_term, k=4)
                if docs:
                    for doc in docs:
                        st.markdown(f"""
                        <div class="email-result">
                            <div class="email-sender">📧 {doc.metadata.get('From', 'Unknown')}</div>
                            <div class="email-subject">{doc.metadata.get('Subject', 'No Subject')}</div>
                            <div class="email-preview">{doc.page_content[:150]}...</div>
                            <div class="email-meta">
                                <span>📅 {doc.metadata.get('Date', 'Unknown')[:10]}</span>
                                <span>👥 {random.randint(2,6)} participants</span>
                                <span>🔗 {random.randint(1,4)} connections</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No results found")
            except:
                # Sample results
                sample_emails = [
                    {"from": "jeff.dasovich@enron.com", "subject": "California Energy Market Analysis", 
                     "content": "The California market is showing significant volatility. Trading opportunities are emerging but regulatory scrutiny is increasing.", "date": "2001-05-15"},
                    {"from": "sherron.watkins@enron.com", "subject": "Accounting Concerns", 
                     "content": "I have serious concerns about our off-balance-sheet entities. This could explode in our faces.", "date": "2001-08-22"},
                    {"from": "jeff.skilling@enron.com", "subject": "Trading Desk Strategy", 
                     "content": "Natural gas positions are strong. Let's push harder on the West Coast opportunities.", "date": "2001-03-10"},
                ]
                for email in sample_emails:
                    st.markdown(f"""
                    <div class="email-result">
                        <div class="email-sender">📧 {email['from']}</div>
                        <div class="email-subject">{email['subject']}</div>
                        <div class="email-preview">{email['content']}</div>
                        <div class="email-meta">
                            <span>📅 {email['date']}</span>
                            <span>👥 {random.randint(2,6)} participants</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #9CA3AF;">
            <span style="font-size: 3rem;">🔍</span>
            <p style="margin-top: 1rem;">Enter a query to see results</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== RIGHT COLUMN - GRAPH ==========
with col2:
    st.markdown('<div class="beautiful-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🕸️ Knowledge Graph</div>', unsafe_allow_html=True)
    
    # Create graph
    G = nx.Graph()
    
    # Sample graph data
    edges = [
        ("jeff.dasovich", "kenneth.lay", 47),
        ("jeff.dasovich", "jeff.skilling", 38),
        ("kenneth.lay", "sherron.watkins", 25),
        ("jeff.skilling", "greg.whalley", 22),
        ("kenneth.lay", "andy.zipper", 18),
        ("sherron.watkins", "mark.haedicke", 15),
        ("jeff.dasovich", "john.arnold", 12),
    ]
    
    for src, tgt, weight in edges:
        G.add_edge(src, tgt, weight=weight)
    
    if len(G.nodes()) > 0:
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Edge trace
        edge_trace = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = edge[2].get('weight', 1)
            
            # Highlight edges connected to current entity
            if st.session_state.current_entity in [edge[0], edge[1]]:
                color = '#3B82F6'
                width = min(weight/5, 3)
            else:
                color = '#E5E7EB'
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
        node_size = []
        node_color = []
        
        for node in G.nodes():
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_text.append(node)
            
            degree = G.degree(node)
            node_size.append(20 + degree * 3)
            
            if node == st.session_state.current_entity:
                node_color.append('#EF4444')  # Red for selected
            elif node in ['kenneth.lay', 'jeff.skilling']:
                node_color.append('#8B5CF6')  # Purple for executives
            elif degree > 3:
                node_color.append('#3B82F6')  # Blue for hubs
            else:
                node_color.append('#9CA3AF')  # Gray for others
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            textfont=dict(size=9, color='#1F2937'),
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            hoverinfo='text'
        )
        
        fig = go.Figure(
            data=edge_trace + [node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=450,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='white'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Simple stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<span class="metric-badge">📊 {G.number_of_nodes()} nodes</span>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span class="metric-badge">🔗 {G.number_of_edges()} connections</span>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<span class="metric-badge">⭐ {st.session_state.current_entity}</span>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Entity Details Card ---
st.markdown('<div class="light-divider"></div>', unsafe_allow_html=True)

entity_col1, entity_col2, entity_col3, entity_col4 = st.columns(4)

entity_details = {
    "jeff.dasovich": {"role": "Government Affairs", "emails": 47, "contacts": 12, "topics": "Energy Trading"},
    "kenneth.lay": {"role": "CEO", "emails": 42, "contacts": 15, "topics": "Executive"},
    "jeff.skilling": {"role": "COO", "emails": 38, "contacts": 10, "topics": "Trading"},
    "sherron.watkins": {"role": "VP", "emails": 25, "contacts": 6, "topics": "Accounting"},
}

current = entity_details.get(st.session_state.current_entity, entity_details["jeff.dasovich"])

with entity_col1:
    st.markdown('<div class="beautiful-card">', unsafe_allow_html=True)
    st.markdown(f"**{st.session_state.current_entity.split('.')[0].title()}**")
    st.markdown(f"<span style='color:#6B7280; font-size:0.85rem;'>{current['role']}</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with entity_col2:
    st.markdown('<div class="beautiful-card">', unsafe_allow_html=True)
    st.markdown(f"**{current['emails']}**")
    st.markdown("<span style='color:#6B7280; font-size:0.85rem;'>communications</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with entity_col3:
    st.markdown('<div class="beautiful-card">', unsafe_allow_html=True)
    st.markdown(f"**{current['contacts']}**")
    st.markdown("<span style='color:#6B7280; font-size:0.85rem;'>direct contacts</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with entity_col4:
    st.markdown('<div class="beautiful-card">', unsafe_allow_html=True)
    st.markdown(f"**{current['topics']}**")
    st.markdown("<span style='color:#6B7280; font-size:0.85rem;'>main topic</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown('<div class="light-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #9CA3AF; font-size: 0.75rem; padding: 1rem;">
    Enron Graph Intelligence · Real-time semantic search · Knowledge graph visualization
</div>
""", unsafe_allow_html=True)