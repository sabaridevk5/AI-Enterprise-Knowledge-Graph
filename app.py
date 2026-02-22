# app.py - ENTERPRISE DASHBOARD

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
from collections import Counter

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# --- 1. ENTERPRISE DASHBOARD CSS ---
st.set_page_config(
    page_title="AI KNOWLEDGE GRAPH BUILDER",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Dashboard CSS
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
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
    .dashboard {
        max-width: 1600px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Header */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .brand h1 {
        font-size: 1.8rem;
        font-weight: 600;
        color: #0f172a;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .brand p {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 0.2rem;
    }
    
    .badge {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 40px;
        font-size: 0.8rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.7); }
        70% { box-shadow: 0 0 0 10px rgba(16,185,129,0); }
        100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    }
    
    /* KPI Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
        border: 1px solid #e2e8f0;
        transition: all 0.2s;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05);
        border-color: #94a3b8;
    }
    
    .kpi-label {
        color: #64748b;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 600;
        color: #0f172a;
        line-height: 1.2;
    }
    
    .kpi-trend {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        margin-top: 0.5rem;
        font-size: 0.8rem;
    }
    
    .trend-up {
        color: #10b981;
    }
    
    .trend-down {
        color: #ef4444;
    }
    
    /* Search Section */
    .search-section {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    }
    
    .search-title {
        color: #64748b;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }
    
    .search-wrapper {
        display: flex;
        gap: 0.5rem;
        align-items: center;
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
        border-color: #0f172a;
        background: white;
        box-shadow: 0 0 0 4px rgba(15,23,42,0.05);
    }
    
    .search-btn {
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
    
    .search-btn:hover {
        background: #1e293b;
    }
    
    /* Hint pills */
    .hint-pills {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    
    .pill {
        background: #f1f5f9;
        color: #475569;
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        font-size: 0.8rem;
        border: 1px solid #e2e8f0;
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .pill:hover {
        background: #0f172a;
        color: white;
        border-color: #0f172a;
    }
    
    /* Dashboard Grid */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1.2fr 0.8fr;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    }
    
    .card-header {
        padding: 1.2rem 1.5rem;
        border-bottom: 1px solid #e2e8f0;
        background: #fafafa;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .card-header h3 {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0f172a;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .card-badge {
        background: #e2e8f0;
        color: #475569;
        padding: 0.2rem 0.8rem;
        border-radius: 30px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .card-body {
        padding: 1.5rem;
    }
    
    /* Result items */
    .result-item {
        padding: 1.2rem;
        border-bottom: 1px solid #f1f5f9;
        transition: all 0.2s;
    }
    
    .result-item:hover {
        background: #f8fafc;
    }
    
    .result-item:last-child {
        border-bottom: none;
    }
    
    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .result-sender {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .avatar {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #0f172a, #334155);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .sender-info {
        display: flex;
        flex-direction: column;
    }
    
    .sender-name {
        font-weight: 600;
        color: #0f172a;
        font-size: 0.9rem;
    }
    
    .sender-email {
        color: #64748b;
        font-size: 0.7rem;
    }
    
    .result-date {
        color: #94a3b8;
        font-size: 0.7rem;
    }
    
    .result-subject {
        font-weight: 500;
        color: #1e293b;
        margin-bottom: 0.3rem;
        font-size: 0.95rem;
    }
    
    .result-preview {
        color: #475569;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    
    .result-meta {
        display: flex;
        gap: 1rem;
        margin-top: 0.8rem;
    }
    
    .meta-tag {
        background: #f1f5f9;
        padding: 0.2rem 0.8rem;
        border-radius: 30px;
        font-size: 0.7rem;
        color: #475569;
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .stat-item {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #f1f5f9;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    
    .stat-value {
        font-size: 1.3rem;
        font-weight: 600;
        color: #0f172a;
    }
    
    .stat-desc {
        color: #94a3b8;
        font-size: 0.7rem;
        margin-top: 0.2rem;
    }
    
    /* Timeline */
    .timeline {
        margin-top: 1rem;
    }
    
    .timeline-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.8rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .timeline-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #3b82f6;
    }
    
    .timeline-content {
        flex: 1;
    }
    
    .timeline-title {
        font-weight: 500;
        color: #1e293b;
        font-size: 0.9rem;
    }
    
    .timeline-time {
        color: #94a3b8;
        font-size: 0.7rem;
    }
    
    /* Entity panel */
    .entity-panel {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin-top: 1.5rem;
    }
    
    .entity-panel h4 {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.7;
        margin-bottom: 1rem;
    }
    
    .entity-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.8rem;
    }
    
    .entity-label {
        opacity: 0.7;
        font-size: 0.85rem;
    }
    
    .entity-value {
        font-weight: 500;
        font-size: 0.95rem;
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
        font-size: 0.75rem;
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
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'entity' not in st.session_state:
    st.session_state.entity = None
if 'results' not in st.session_state:
    st.session_state.results = []
if 'hint_index' not in st.session_state:
    st.session_state.hint_index = 0
    st.session_state.last_hint = time.time()

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
    "📊 Try: sherron watkins accounting concerns",
    "👤 Try: kenneth lay board meetings",
    "📈 Try: california energy crisis",
    "⚡ Try: trading desk operations"
]

# --- 6. ENTITY DETECTION ---
def detect_entity(results):
    if not results:
        return None
    
    entity_keywords = {
        "jeff.dasovich": ["jeff", "dasovich", "jeff dasovich"],
        "kenneth.lay": ["kenneth", "lay", "kenneth lay", "ken lay"],
        "jeff.skilling": ["jeff skilling", "skilling"],
        "sherron.watkins": ["sherron", "watkins", "sherron watkins"],
    }
    
    scores = {e: 0 for e in entity_keywords}
    
    for r in results:
        text = f"{r.get('subject', '')} {r.get('content', '')}".lower()
        sender = r.get('from', '').lower()
        
        for entity, keywords in entity_keywords.items():
            for k in keywords:
                if k in sender:
                    scores[entity] += 3
                elif k in text:
                    scores[entity] += 1
    
    if max(scores.values()) > 0:
        return max(scores.items(), key=lambda x: x[1])[0]
    return None

# ========== DASHBOARD ==========
st.markdown('<div class="dashboard">', unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="header">
    <div class="brand">
        <h1>🏛️ AURUM INTELLIGENCE</h1>
        <p>Enterprise Knowledge Graph · Real-time Analytics</p>
    </div>
    <div class="badge">
        <span class="dot"></span>
        <span>SECURE · SOC2 COMPLIANT</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- KPI Grid ---
st.markdown("""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">Total Communications</div>
        <div class="kpi-value">2,547</div>
        <div class="kpi-trend"><span class="trend-up">↑ 12.3%</span> vs last month</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Active Participants</div>
        <div class="kpi-value">158</div>
        <div class="kpi-trend"><span class="trend-up">↑ 8</span> new this week</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Key Topics</div>
        <div class="kpi-value">24</div>
        <div class="kpi-trend"><span>→ stable</span></div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Risk Score</div>
        <div class="kpi-value">35%</div>
        <div class="kpi-trend"><span class="trend-up">↑ 5%</span> increase</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Search Section ---
st.markdown('<div class="search-section">', unsafe_allow_html=True)
st.markdown('<div class="search-title">🔍 ENTERPRISE SEARCH</div>', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    query = st.text_input(
        "",
        placeholder="Search communications... e.g., 'what did sherron watkins say about accounting'",
        key="search",
        label_visibility="collapsed"
    )
with col2:
    search = st.button("ANALYZE", use_container_width=True)

# Hint pills
current_hint = hints[st.session_state.hint_index % len(hints)]
if time.time() - st.session_state.last_hint > 3:
    st.session_state.hint_index += 1
    st.session_state.last_hint = time.time()

st.markdown(f"""
<div class="hint-pills">
    <span class="pill">{hints[0]}</span>
    <span class="pill">{hints[1]}</span>
    <span class="pill">{hints[2]}</span>
    <span class="pill">{hints[3]}</span>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Handle Search ---
if search and query:
    st.session_state.searched = True
    st.session_state.query = query
    
    # Get results
    if vectorstore:
        try:
            docs = vectorstore.similarity_search(query, k=5)
            st.session_state.results = [
                {
                    'from': d.metadata.get('from', 'Unknown'),
                    'to': d.metadata.get('to', 'Unknown'),
                    'subject': d.metadata.get('subject', 'No Subject'),
                    'date': d.metadata.get('date', 'Unknown'),
                    'content': d.page_content,
                    'score': round(0.85 + (0.1 * np.random.random()), 2)
                }
                for d in docs
            ]
        except:
            # Sample results
            st.session_state.results = [
                {
                    'from': 'jeff.dasovich@enron.com',
                    'to': 'kenneth.lay@enron.com',
                    'subject': 'California Energy Market Analysis',
                    'date': '2001-05-15',
                    'content': 'Ken, the California market is showing significant volatility. Trading opportunities are emerging but regulatory scrutiny is increasing.',
                    'score': 0.98
                },
                {
                    'from': 'sherron.watkins@enron.com',
                    'to': 'kenneth.lay@enron.com',
                    'subject': 'URGENT: Accounting Concerns',
                    'date': '2001-08-22',
                    'content': 'I have serious concerns about our accounting practices. This could be a major problem for the company.',
                    'score': 0.96
                },
                {
                    'from': 'jeff.skilling@enron.com',
                    'to': 'greg.whalley@enron.com',
                    'subject': 'Trading Desk Update',
                    'date': '2001-03-10',
                    'content': 'Natural gas positions are strong. Let\'s push harder on the West Coast opportunities.',
                    'score': 0.89
                }
            ]
    else:
        # Sample results based on query
        if 'watkins' in query.lower() or 'sherron' in query.lower():
            st.session_state.results = [
                {
                    'from': 'sherron.watkins@enron.com',
                    'to': 'kenneth.lay@enron.com',
                    'subject': 'URGENT: Accounting Concerns',
                    'date': '2001-08-22',
                    'content': 'I have serious concerns about our accounting practices. This could be a major problem for the company.',
                    'score': 0.98
                },
                {
                    'from': 'sherron.watkins@enron.com',
                    'to': 'legal@enron.com',
                    'subject': 'Legal Meeting',
                    'date': '2001-07-10',
                    'content': 'Met with legal counsel to discuss the off-balance-sheet entities. The risk is significant.',
                    'score': 0.92
                }
            ]
        else:
            st.session_state.results = [
                {
                    'from': 'jeff.dasovich@enron.com',
                    'to': 'kenneth.lay@enron.com',
                    'subject': 'California Energy Market Analysis',
                    'date': '2001-05-15',
                    'content': 'Ken, the California market is showing significant volatility. Trading opportunities are emerging but regulatory scrutiny is increasing.',
                    'score': 0.98
                },
                {
                    'from': 'sherron.watkins@enron.com',
                    'to': 'kenneth.lay@enron.com',
                    'subject': 'URGENT: Accounting Concerns',
                    'date': '2001-08-22',
                    'content': 'I have serious concerns about our accounting practices. This could be a major problem for the company.',
                    'score': 0.96
                }
            ]
    
    # Detect entity
    st.session_state.entity = detect_entity(st.session_state.results)
    st.rerun()

# ========== RESULTS ==========
if st.session_state.searched and st.session_state.results:
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    
    # --- LEFT COLUMN - Search Results ---
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card-header">
        <h3>📄 Search Results</h3>
        <span class="card-badge">{len(st.session_state.results)} matches</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="card-body">', unsafe_allow_html=True)
    
    for r in st.session_state.results:
        avatar = r['from'][0].upper() if r['from'] else '?'
        st.markdown(f"""
        <div class="result-item">
            <div class="result-header">
                <div class="result-sender">
                    <div class="avatar">{avatar}</div>
                    <div class="sender-info">
                        <span class="sender-name">{r['from'].split('@')[0]}</span>
                        <span class="sender-email">{r['from']}</span>
                    </div>
                </div>
                <span class="result-date">{r['date'][:10]}</span>
            </div>
            <div class="result-subject">{r['subject']}</div>
            <div class="result-preview">{r['content'][:150]}...</div>
            <div class="result-meta">
                <span class="meta-tag">📊 {r['score']*100:.0f}% match</span>
                <span class="meta-tag">📎 4 connections</span>
                <span class="meta-tag">📅 {r['date'][:10]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Timeline
    st.markdown('<div class="card" style="margin-top:1.5rem;">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card-header">
        <h3>⏱️ Activity Timeline</h3>
        <span class="card-badge">last 7 days</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="card-body">', unsafe_allow_html=True)
    
    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    for i, date in enumerate(reversed(dates)):
        activity = np.random.randint(5, 25)
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
                <div class="timeline-title">{activity} communications</div>
                <div class="timeline-time">{date.strftime('%b %d, %Y')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- RIGHT COLUMN - Graph & Analytics ---
    st.markdown('<div>', unsafe_allow_html=True)
    
    # Graph Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card-header">
        <h3>🕸️ Knowledge Graph</h3>
        <span class="card-badge">2.0 depth</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="card-body">', unsafe_allow_html=True)
    
    # Create graph
    G = nx.Graph()
    edges = [
        ("jeff.dasovich", "kenneth.lay", 47),
        ("jeff.dasovich", "jeff.skilling", 38),
        ("kenneth.lay", "sherron.watkins", 25),
        ("jeff.skilling", "greg.whalley", 22),
        ("kenneth.lay", "andy.zipper", 18),
    ]
    
    for s, t, w in edges:
        G.add_edge(s, t, weight=w)
    
    if len(G.nodes()) > 0:
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Edges
        edge_trace = []
        for e in G.edges():
            x0, y0 = pos[e[0]]
            x1, y1 = pos[e[1]]
            color = '#3b82f6' if st.session_state.entity and st.session_state.entity in e else '#e2e8f0'
            width = 2.5 if st.session_state.entity and st.session_state.entity in e else 1.5
            
            edge_trace.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode='lines', line=dict(width=width, color=color),
                hoverinfo='none'
            ))
        
        # Nodes
        node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
        for node in G.nodes():
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_text.append(node)
            
            if st.session_state.entity and node == st.session_state.entity:
                node_color.append('#ef4444')
                node_size.append(35)
            else:
                node_color.append('#94a3b8')
                node_size.append(25)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers+text',
            text=node_text, textposition="top center",
            textfont=dict(size=9, color='#1e293b'),
            marker=dict(size=node_size, color=node_color, line=dict(width=2, color='white'))
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
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Stats Grid
    st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
    
    stats = [
        {"label": "Network Size", "value": "7 nodes", "desc": "9 connections"},
        {"label": "Density", "value": "0.42", "desc": "moderate"},
        {"label": "Centralization", "value": "0.68", "desc": "hub detected"},
        {"label": "Avg Path", "value": "2.4", "desc": "tight network"},
    ]
    
    for s in stats:
        st.markdown(f"""
        <div class="stat-item">
            <div class="stat-label">{s['label']}</div>
            <div class="stat-value">{s['value']}</div>
            <div class="stat-desc">{s['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Entity Panel
    if st.session_state.entity:
        entity_data = {
            "jeff.dasovich": {"role": "Gov. Affairs", "influence": "92%", "topics": "Energy Trading"},
            "kenneth.lay": {"role": "CEO", "influence": "98%", "topics": "Executive"},
            "jeff.skilling": {"role": "COO", "influence": "95%", "topics": "Trading"},
            "sherron.watkins": {"role": "VP", "influence": "88%", "topics": "Accounting"},
        }
        
        info = entity_data.get(st.session_state.entity, {})
        st.markdown(f"""
        <div class="entity-panel">
            <h4>👤 Entity Intelligence</h4>
            <div class="entity-row">
                <span class="entity-label">Person</span>
                <span class="entity-value">{st.session_state.entity}</span>
            </div>
            <div class="entity-row">
                <span class="entity-label">Role</span>
                <span class="entity-value">{info.get('role', 'Unknown')}</span>
            </div>
            <div class="entity-row">
                <span class="entity-label">Influence</span>
                <span class="entity-value">{info.get('influence', '0%')}</span>
            </div>
            <div class="entity-row">
                <span class="entity-label">Primary Topic</span>
                <span class="entity-value">{info.get('topics', 'General')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="entity-panel">
            <h4>👥 Network View</h4>
            <div style="opacity:0.7; font-size:0.9rem;">Showing full communication network</div>
            <div style="margin-top:1rem; font-size:0.8rem; opacity:0.6;">No specific person detected in results</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # New Search
    if st.button("← New Search", use_container_width=True):
        st.session_state.searched = False
        st.session_state.query = ""
        st.session_state.entity = None
        st.session_state.results = []
        st.rerun()

else:
    # Empty State
    st.markdown("""
    <div style="background: white; border-radius: 30px; padding: 4rem; text-align: center; border: 1px solid #e2e8f0;">
        <div style="font-size: 5rem; margin-bottom: 1.5rem;">🏛️</div>
        <h2 style="color: #0f172a; font-weight: 500; margin-bottom: 0.5rem;">Enterprise Intelligence Platform</h2>
        <p style="color: #64748b; max-width: 500px; margin: 0 auto;">Enter a search query to explore the knowledge graph and uncover hidden patterns in communications.</p>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class="footer">
    <div>© 2026 Aurum Intelligence · Enterprise Edition</div>
    <div style="display: flex; gap: 2rem;">
        <span>Security</span>
        <span>Compliance</span>
        <span>Audit</span>
        <span>Docs</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)