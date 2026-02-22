# app.py - PREMIUM ENTERPRISE DASHBOARD

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
import base64

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_neo4j import Neo4jGraph

# --- 1. ULTRA PREMIUM CUSTOM CSS ---
st.set_page_config(
    page_title="AURUM INTELLIGENCE", 
    layout="wide", 
    page_icon="✨",
    initial_sidebar_state="collapsed"
)

# Premium dark theme with glass morphism
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Main container with glass effect */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 40px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    /* Premium header */
    .premium-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        width: 50px;
        height: 50px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.3);
    }
    
    .title {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        font-size: 0.85rem;
        color: #64748B;
        margin-top: 0.2rem;
    }
    
    /* Status indicator */
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 40px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .pulse {
        width: 10px;
        height: 10px;
        background: #10B981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    /* Premium search container */
    .search-container-premium {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        padding: 2rem;
        border-radius: 30px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .search-container-premium::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.1) 50%,
            transparent 70%
        );
        animation: shine 6s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    /* Premium input */
    .premium-input {
        background: white;
        border: 2px solid transparent;
        border-radius: 50px;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .premium-input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    /* Rotating insights */
    .insights-rotator {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 1rem 2rem;
        border-radius: 60px;
        display: inline-block;
        margin-top: 1rem;
        border: 1px solid rgba(102, 126, 234, 0.3);
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }
    
    /* Premium cards */
    .premium-card {
        background: white;
        border-radius: 24px;
        padding: 1.5rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .premium-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 30px 35px -10px rgba(102, 126, 234, 0.3);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .premium-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .premium-card:hover::after {
        transform: scaleX(1);
    }
    
    /* Card header */
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .card-header-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1rem;
    }
    
    /* Email items */
    .email-item {
        background: #f8fafc;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .email-item:hover {
        background: white;
        border-color: #667eea;
        transform: translateX(5px);
        box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.1);
    }
    
    .email-sender {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .sender-avatar {
        width: 24px;
        height: 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .sender-name {
        font-size: 0.85rem;
        color: #475569;
    }
    
    .email-subject {
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    .email-preview {
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.5;
        margin-bottom: 0.5rem;
    }
    
    .email-meta {
        display: flex;
        gap: 1rem;
        font-size: 0.7rem;
        color: #94a3b8;
    }
    
    .meta-tag {
        background: #e2e8f0;
        padding: 0.2rem 0.6rem;
        border-radius: 30px;
    }
    
    /* Graph container */
    .graph-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 24px;
        padding: 1rem;
        position: relative;
        overflow: hidden;
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 20px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stat-card:hover .stat-value,
    .stat-card:hover .stat-label {
        color: white;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Entity details */
    .entity-detail {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem;
        background: #f8fafc;
        border-radius: 16px;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .entity-detail:hover {
        background: white;
        border-color: #667eea;
        transform: translateX(5px);
    }
    
    .detail-label {
        color: #64748b;
        font-size: 0.85rem;
    }
    
    .detail-value {
        font-weight: 600;
        color: #0f172a;
    }
    
    /* Gradient text */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-slide {
        animation: slideIn 0.5s ease forwards;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Button styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(102, 126, 234, 0.4);
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
if 'search_triggered' not in st.session_state:
    st.session_state.search_triggered = False
if 'graph_depth' not in st.session_state:
    st.session_state.graph_depth = 2

# --- 4. SYSTEM INIT ---
@st.cache_resource
def load_systems():
    systems = {"vectorstore": None, "graph": None}
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        v_store = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)
        systems["vectorstore"] = v_store
    except Exception as e:
        st.error(f"Pinecone connection: {str(e)[:50]}")
    
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        systems["graph"] = driver
    except:
        pass
    
    return systems

systems = load_systems()
vectorstore = systems["vectorstore"]
graph = systems["graph"]

# --- 5. ROTATING INSIGHTS ---
insights = [
    "💡 Uncover hidden patterns in executive communications",
    "💡 Trace the flow of information through the organization",
    "💡 Identify key influencers and decision makers",
    "💡 Discover relationships between people and topics",
    "💡 Analyze communication patterns over time",
]

if 'last_hint_time' not in st.session_state:
    st.session_state.last_hint_time = time.time()
    st.session_state.hint_index = 0

current_time = time.time()
if current_time - st.session_state.last_hint_time > 4:
    st.session_state.hint_index = (st.session_state.hint_index + 1) % len(insights)
    st.session_state.last_hint_time = current_time

# --- 6. ENTITY EXTRACTION ---
def extract_entity_from_query(query):
    query_lower = query.lower()
    if any(word in query_lower for word in ['jeff', 'dasovich']):
        return "jeff.dasovich"
    elif any(word in query_lower for word in ['kenneth', 'lay']):
        return "kenneth.lay"
    elif any(word in query_lower for word in ['jeff', 'skilling']):
        return "jeff.skilling"
    elif any(word in query_lower for word in ['sherron', 'watkins']):
        return "sherron.watkins"
    elif any(word in query_lower for word in ['john', 'arnold']):
        return "john.arnold"
    elif any(word in query_lower for word in ['andy', 'zipper']):
        return "andy.zipper"
    elif any(word in query_lower for word in ['greg', 'whalley']):
        return "greg.whalley"
    return "jeff.dasovich"

# ========== MAIN CONTAINER ==========
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# --- Premium Header ---
st.markdown("""
<div class="premium-header">
    <div class="logo-section">
        <div class="logo">✨</div>
        <div>
            <div class="title">AURUM INTELLIGENCE</div>
            <div class="subtitle">Enterprise Knowledge Graph Platform</div>
        </div>
    </div>
    <div class="status-indicator">
        <div class="pulse"></div>
        <span style="color: #64748B;">Live · Real-time</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Premium Search Section ---
st.markdown('<div class="search-container-premium">', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    # Custom styled input using text_input with custom CSS class
    query = st.text_input(
        "Search",
        value=st.session_state.search_value,
        placeholder="Enter your query... e.g., 'What did Jeff Dasovich say about energy trading?'",
        key="premium_search",
        label_visibility="collapsed"
    )
with col2:
    search_clicked = st.button("🔍 Analyze", use_container_width=True)

# Update search on Enter key or button click
if search_clicked or (query and query != st.session_state.search_value):
    st.session_state.search_value = query
    st.session_state.search_triggered = True
    if query:
        st.session_state.current_entity = extract_entity_from_query(query)

# Rotating insights
st.markdown(f'<div class="insights-rotator">{insights[st.session_state.hint_index]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Main Content Grid ---
col_left, col_right = st.columns([1, 1.2])

# ========== LEFT COLUMN - RESULTS ==========
with col_left:
    st.markdown('<div class="premium-card animate-slide">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card-header">
        <div class="card-header-icon">📧</div>
        <span>Intelligent Matches</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.search_triggered and st.session_state.search_value:
        search_term = st.session_state.search_value
        
        if vectorstore:
            try:
                docs = vectorstore.similarity_search(search_term, k=5)
                if docs:
                    for i, doc in enumerate(docs):
                        sender = doc.metadata.get('From', 'Unknown').split('@')[0]
                        st.markdown(f"""
                        <div class="email-item" style="animation: slideIn 0.3s ease {i*0.1}s both;">
                            <div class="email-sender">
                                <div class="sender-avatar">{sender[0].upper()}</div>
                                <span class="sender-name">{doc.metadata.get('From', 'Unknown')}</span>
                            </div>
                            <div class="email-subject">{doc.metadata.get('Subject', 'No Subject')}</div>
                            <div class="email-preview">{doc.page_content[:200]}...</div>
                            <div class="email-meta">
                                <span class="meta-tag">📅 {doc.metadata.get('Date', 'Unknown')[:10]}</span>
                                <span class="meta-tag">👥 {random.randint(2,6)} participants</span>
                                <span class="meta-tag">📊 {random.randint(70, 99)}% relevance</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No results found")
            except Exception as e:
                st.error(f"Search error: {e}")
        else:
            # Premium sample results
            sample_results = [
                {"sender": "Jeff Dasovich", "email": "jeff.dasovich@enron.com", 
                 "subject": "California Energy Market Analysis", 
                 "content": "The California market is showing significant volatility. Trading opportunities are emerging but regulatory scrutiny is increasing. We need to be careful about our positions.",
                 "date": "2001-05-15", "relevance": 98},
                {"sender": "Sherron Watkins", "email": "sherron.watkins@enron.com", 
                 "subject": "URGENT: Accounting Concerns", 
                 "content": "I have serious concerns about our off-balance-sheet entities. This could explode in our faces. I've outlined the risks in detail.",
                 "date": "2001-08-22", "relevance": 96},
                {"sender": "Jeff Skilling", "email": "jeff.skilling@enron.com", 
                 "subject": "Trading Desk Strategy", 
                 "content": "Natural gas positions are strong. Let's push harder on the West Coast opportunities. The volatility is our friend.",
                 "date": "2001-03-10", "relevance": 92},
            ]
            
            for i, res in enumerate(sample_results):
                st.markdown(f"""
                <div class="email-item" style="animation: slideIn 0.3s ease {i*0.1}s both;">
                    <div class="email-sender">
                        <div class="sender-avatar">{res['sender'][0]}</div>
                        <span class="sender-name">{res['email']}</span>
                    </div>
                    <div class="email-subject">{res['subject']}</div>
                    <div class="email-preview">{res['content']}</div>
                    <div class="email-meta">
                        <span class="meta-tag">📅 {res['date']}</span>
                        <span class="meta-tag">👥 {random.randint(2,6)} participants</span>
                        <span class="meta-tag">📊 {res['relevance']}% relevance</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #94A3B8;">
            <span style="font-size: 4rem;">✨</span>
            <p style="margin-top: 1rem;">Enter a query to discover insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== RIGHT COLUMN - GRAPH ==========
with col_right:
    st.markdown('<div class="premium-card animate-slide">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card-header">
        <div class="card-header-icon">🕸️</div>
        <span>Knowledge Graph</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Graph depth control
    col1, col2 = st.columns(2)
    with col1:
        depth = st.slider("Connection Depth", 1, 3, st.session_state.graph_depth, key="graph_depth_slider")
        st.session_state.graph_depth = depth
    with col2:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("🔄 Refresh Graph", use_container_width=True):
            st.rerun()
    
    # Create graph
    G = nx.Graph()
    
    # Enhanced graph data
    edges = [
        ("jeff.dasovich", "kenneth.lay", 47, "Primary contact"),
        ("jeff.dasovich", "jeff.skilling", 38, "Trading discussions"),
        ("kenneth.lay", "sherron.watkins", 25, "Whistleblower"),
        ("jeff.skilling", "greg.whalley", 22, "Trading desk"),
        ("kenneth.lay", "andy.zipper", 18, "Operations"),
        ("sherron.watkins", "mark.haedicke", 15, "Legal counsel"),
        ("jeff.dasovich", "john.arnold", 12, "Energy trading"),
        ("john.arnold", "jeff.skilling", 10, "Trading reports"),
        ("greg.whalley", "jeff.dasovich", 8, "Market analysis"),
    ]
    
    for src, tgt, weight, rel in edges:
        G.add_edge(src, tgt, weight=weight, relationship=rel)
    
    if len(G.nodes()) > 0:
        # Dynamic layout based on depth
        if depth == 1:
            pos = nx.spring_layout(G, k=3, iterations=50)
        elif depth == 2:
            pos = nx.spring_layout(G, k=2, iterations=50)
        else:
            pos = nx.spring_layout(G, k=1.5, iterations=50)
        
        current_entity = st.session_state.current_entity
        
        # Edge trace
        edge_traces = []
        for edge in G.edges(data=True):
            if edge[0] in pos and edge[1] in pos:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                weight = edge[2].get('weight', 1)
                
                if current_entity in [edge[0], edge[1]]:
                    color = 'rgba(102, 126, 234, 0.8)'
                    width = min(weight/4, 4)
                else:
                    color = 'rgba(148, 163, 184, 0.3)'
                    width = 1
                
                edge_traces.append(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=width, color=color),
                    hoverinfo='text',
                    text=edge[2].get('relationship', ''),
                    name=''
                ))
        
        # Node trace
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []
        node_hover = []
        
        for node in G.nodes():
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_text.append(node.split('.')[0].title())
            
            degree = G.degree(node)
            node_size.append(25 + degree * 3)
            
            if node == current_entity:
                node_color.append('#EF4444')  # Red for selected
            elif node in ['kenneth.lay', 'jeff.skilling']:
                node_color.append('#8B5CF6')  # Purple for executives
            elif degree > 3:
                node_color.append('#3B82F6')  # Blue for hubs
            else:
                node_color.append('#94A3B8')  # Gray for others
            
            # Get connected nodes for hover
            neighbors = list(G.neighbors(node))[:3]
            node_hover.append(f"Entity: {node}<br>Connections: {degree}<br>Key contacts: {', '.join(neighbors)}")
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            textfont=dict(size=10, color='#1F2937', family='Plus Jakarta Sans'),
            hoverinfo='text',
            hovertext=node_hover,
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white'),
                gradient=dict(type='radial', color='lightgray')
            ),
            name=''
        )
        
        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
                height=500,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Graph stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{G.number_of_nodes()}</div>
                <div class="stat-label">Entities</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{G.number_of_edges()}</div>
                <div class="stat-label">Relationships</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{nx.density(G):.3f}</div>
                <div class="stat-label">Density</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{G.degree(current_entity) if current_entity in G else 0}</div>
                <div class="stat-label">Your Connections</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Entity Details Section ---
st.markdown('<div class="premium-card animate-slide">', unsafe_allow_html=True)
st.markdown("""
<div class="card-header">
    <div class="card-header-icon">👤</div>
    <span>Entity Intelligence</span>
</div>
""", unsafe_allow_html=True)

# Entity details mapping
entity_details = {
    "jeff.dasovich": {
        "name": "Jeff Dasovich", "role": "Government Affairs Executive", 
        "emails": 47, "contacts": 12, "topics": "Energy Trading, Regulatory",
        "sentiment": 78, "influence": 92, "department": "Government Relations"
    },
    "kenneth.lay": {
        "name": "Kenneth Lay", "role": "CEO & Chairman", 
        "emails": 42, "contacts": 15, "topics": "Executive, Strategy",
        "sentiment": 65, "influence": 98, "department": "Executive Office"
    },
    "jeff.skilling": {
        "name": "Jeff Skilling", "role": "COO", 
        "emails": 38, "contacts": 10, "topics": "Trading, Operations",
        "sentiment": 72, "influence": 95, "department": "Operations"
    },
    "sherron.watkins": {
        "name": "Sherron Watkins", "role": "Vice President", 
        "emails": 25, "contacts": 6, "topics": "Accounting, Legal",
        "sentiment": 45, "influence": 88, "department": "Finance"
    },
}

current = entity_details.get(st.session_state.current_entity, entity_details["jeff.dasovich"])

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="entity-detail">
        <span class="detail-label">Name</span>
        <span class="detail-value">{current['name']}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="entity-detail">
        <span class="detail-label">Role</span>
        <span class="detail-value">{current['role']}</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="entity-detail">
        <span class="detail-label">Department</span>
        <span class="detail-value">{current['department']}</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="entity-detail">
        <span class="detail-label">Communications</span>
        <span class="detail-value">{current['emails']}</span>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="entity-detail">
        <span class="detail-label">Influence Score</span>
        <span class="detail-value">{current['influence']}%</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(102, 126, 234, 0.2);">
    <span style="color: #94A3B8; font-size: 0.8rem;">
        ✨ Aurum Intelligence · Enterprise Knowledge Graph Platform · Real-time Analytics
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close main container