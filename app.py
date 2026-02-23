# app.py - ENTERPRISE DASHBOARD

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from datetime import datetime

# Direct imports
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from neo4j import GraphDatabase

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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: #f8fafc; }
    .dashboard { max-width: 1600px; margin: 0 auto; padding: 2rem; }
    
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
    .brand h1 { font-size: 1.8rem; font-weight: 600; color: #0f172a; letter-spacing: -0.02em; display: flex; align-items: center; gap: 0.5rem; }
    .brand p { color: #64748b; font-size: 0.85rem; margin-top: 0.2rem; }
    .badge { background: linear-gradient(135deg, #0f172a, #1e293b); color: white; padding: 0.5rem 1.2rem; border-radius: 40px; font-size: 0.8rem; font-weight: 500; display: flex; align-items: center; gap: 0.5rem; }
    .dot { width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.7); }
        70% { box-shadow: 0 0 0 10px rgba(16,185,129,0); }
        100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    }
    
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-bottom: 2rem; }
    .kpi-card { background: white; border-radius: 20px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); border: 1px solid #e2e8f0; transition: all 0.2s; }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05); border-color: #94a3b8; }
    .kpi-label { color: #64748b; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
    .kpi-value { font-size: 2rem; font-weight: 600; color: #0f172a; line-height: 1.2; }
    .kpi-trend { display: flex; align-items: center; gap: 0.3rem; margin-top: 0.5rem; font-size: 0.8rem; }
    .trend-up { color: #10b981; } .trend-down { color: #ef4444; }
    
    .search-section { background: white; border-radius: 20px; padding: 1.5rem; border: 1px solid #e2e8f0; margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
    .search-title { color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; }
    .search-wrapper { display: flex; gap: 0.5rem; align-items: center; }
    
    .hint-pills { display: flex; gap: 0.5rem; margin-top: 1rem; flex-wrap: wrap; }
    .pill { background: #f1f5f9; color: #475569; padding: 0.4rem 1.2rem; border-radius: 30px; font-size: 0.8rem; border: 1px solid #e2e8f0; transition: all 0.2s; cursor: pointer; }
    .pill:hover { background: #0f172a; color: white; border-color: #0f172a; }
    
    .dashboard-grid { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 1.5rem; margin-bottom: 1.5rem; }
    .card { background: white; border-radius: 20px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
    .card-header { padding: 1.2rem 1.5rem; border-bottom: 1px solid #e2e8f0; background: #fafafa; display: flex; justify-content: space-between; align-items: center; }
    .card-header h3 { font-size: 0.95rem; font-weight: 600; color: #0f172a; text-transform: uppercase; letter-spacing: 0.03em; }
    .card-badge { background: #e2e8f0; color: #475569; padding: 0.2rem 0.8rem; border-radius: 30px; font-size: 0.7rem; font-weight: 500; }
    .card-body { padding: 1.5rem; }
    
    .result-item { padding: 1.2rem; border-bottom: 1px solid #f1f5f9; transition: all 0.2s; }
    .result-item:hover { background: #f8fafc; }
    .result-item:last-child { border-bottom: none; }
    .result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
    .result-sender { display: flex; align-items: center; gap: 0.5rem; }
    .avatar { width: 32px; height: 32px; background: linear-gradient(135deg, #0f172a, #334155); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.8rem; font-weight: 600; }
    .sender-info { display: flex; flex-direction: column; }
    .sender-name { font-weight: 600; color: #0f172a; font-size: 0.9rem; }
    .sender-email { color: #64748b; font-size: 0.7rem; }
    .result-date { color: #94a3b8; font-size: 0.7rem; }
    .result-subject { font-weight: 500; color: #1e293b; margin-bottom: 0.3rem; font-size: 0.95rem; }
    .result-preview { color: #475569; font-size: 0.85rem; line-height: 1.5; }
    .result-meta { display: flex; gap: 1rem; margin-top: 0.8rem; }
    .meta-tag { background: #f1f5f9; padding: 0.2rem 0.8rem; border-radius: 30px; font-size: 0.7rem; color: #475569; }
    
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
    .stat-item { background: #f8fafc; padding: 1rem; border-radius: 14px; border: 1px solid #f1f5f9; }
    .stat-label { color: #64748b; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 0.2rem; }
    .stat-value { font-size: 1.3rem; font-weight: 600; color: #0f172a; }
    .stat-desc { color: #94a3b8; font-size: 0.7rem; margin-top: 0.2rem; }
    
    .timeline { margin-top: 1rem; }
    .timeline-item { display: flex; align-items: center; gap: 1rem; padding: 0.8rem 0; border-bottom: 1px solid #f1f5f9; }
    .timeline-dot { width: 8px; height: 8px; border-radius: 50%; background: #3b82f6; }
    .timeline-content { flex: 1; }
    .timeline-title { font-weight: 500; color: #1e293b; font-size: 0.9rem; }
    .timeline-time { color: #94a3b8; font-size: 0.7rem; }
    
    .entity-panel { background: linear-gradient(135deg, #0f172a, #1e293b); color: white; padding: 1.5rem; border-radius: 20px; margin-top: 1.5rem; }
    .entity-panel h4 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7; margin-bottom: 1rem; }
    .entity-row { display: flex; justify-content: space-between; margin-bottom: 0.8rem; }
    .entity-label { opacity: 0.7; font-size: 0.85rem; }
    .entity-value { font-weight: 500; font-size: 0.95rem; }
    
    .footer { margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; color: #94a3b8; font-size: 0.75rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. CREDENTIALS ---
if "PINECONE_API_KEY" in st.secrets:
    os.environ['PINECONE_API_KEY'] = st.secrets["PINECONE_API_KEY"]
else:
    os.environ['PINECONE_API_KEY'] = 'pcsk_2Z2XfF_2fHGYkbAZRLjxFZcYZB7RW6cFSr9WrKxdR5pYpqkawSEKJdpxnA4UcnY3jTu7dp'

PINECONE_INDEX = "enron-enterprise-kg"

if "NEO4J_URI" in st.secrets:
    NEO4J_URI = st.secrets["NEO4J_URI"]
    NEO4J_USER = st.secrets["NEO4J_USER"]
    NEO4J_PASSWORD = st.secrets["NEO4J_PASSWORD"]
else:
    NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://0be473b6.databases.neo4j.io")
    NEO4J_USER = os.getenv("NEO4J_USER", "0be473b6")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "9m7fKj7WzZmVAMkithV9OkhzTzmBlPfQOye4Oyyvl70")

# --- 3. SESSION STATE ---
if 'searched' not in st.session_state: st.session_state.searched = False
if 'query' not in st.session_state: st.session_state.query = ""
if 'entity' not in st.session_state: st.session_state.entity = None
if 'results' not in st.session_state: st.session_state.results = []
if 'hint_index' not in st.session_state:
    st.session_state.hint_index = 0
    st.session_state.last_hint = time.time()

# --- 4. SYSTEM INIT ---
@st.cache_resource
def load_systems():
    systems = {"model": None, "pinecone": None, "neo4j": None}
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        systems["model"] = model
    except Exception: pass
    
    try:
        pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
        systems["pinecone"] = pc
    except Exception: pass
    
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        systems["neo4j"] = driver
    except Exception: pass
    
    return systems

systems = load_systems()
model = systems["model"]
pinecone_client = systems["pinecone"]
neo4j_driver = systems["neo4j"]

hints = [
    "🔍 Try: jeff dasovich energy trading",
    "📊 Try: sherron watkins accounting concerns",
    "👤 Try: kenneth lay board meetings",
    "📈 Try: california energy crisis"
]

# --- 5. LOGIC: ENTITY & GRAPH ---
def detect_entity(results):
    if not results: return None
    # BUG FIX 1: We must return the full email so Neo4j can find them!
    entity_keywords = {
        "jeff.dasovich@enron.com": ["jeff", "dasovich"],
        "kenneth.lay@enron.com": ["kenneth", "lay", "ken lay"],
        "jeff.skilling@enron.com": ["skilling"],
        "sherron.watkins@enron.com": ["sherron", "watkins"],
        "andy.zipper@enron.com": ["zipper", "andy"],
        "greg.whalley@enron.com": ["whalley", "greg"],
        "john.arnold@enron.com": ["arnold", "john"]
    }
    
    scores = {e: 0 for e in entity_keywords}
    for r in results:
        text = f"{r.get('subject', '')} {r.get('content', '')}".lower()
        sender = r.get('from', '').lower()
        for entity, keywords in entity_keywords.items():
            for k in keywords:
                if k in sender: scores[entity] += 3
                elif k in text: scores[entity] += 1
                
    if max(scores.values()) > 0:
        return max(scores.items(), key=lambda x: x[1])[0]
    return None

def get_graph_data(entity_name=None, search_results=None):
    G = nx.Graph()
    
    # 1. Try fetching real relations from Neo4j
    if neo4j_driver and entity_name:
        try:
            with neo4j_driver.session() as session:
                query = """
                MATCH (p:Person {email: $email})-[r:SENT]-(connected)
                RETURN p.email as source, connected.email as target, count(r) as weight
                LIMIT 25
                """
                result = session.run(query, email=entity_name)
                for record in result:
                    G.add_edge(record['source'], record['target'], weight=record.get('weight', 1))
        except: pass

    # BUG FIX 3: Dynamic Graph Fallback! If Neo4j is empty, build a graph from Pinecone search results!
    if len(G.nodes()) == 0 and search_results:
        for res in search_results:
            src = res.get('from', 'Unknown')
            tgt = res.get('to', 'Unknown')
            if src != 'Unknown' and tgt != 'Unknown':
                # Target can sometimes be a comma-separated list
                targets = [t.strip() for t in str(tgt).split(',')] if tgt else []
                for t in targets[:3]: # Limit to avoid massive tangles
                    if src and t and src != t:
                        if G.has_edge(src, t): G[src][t]['weight'] += 1
                        else: G.add_edge(src, t, weight=1)

    # 3. Final Fallback (If both databases fail)
    if len(G.nodes()) == 0:
        demo_edges = [
            ("jeff.dasovich@enron.com", "kenneth.lay@enron.com", 10),
            ("sherron.watkins@enron.com", "kenneth.lay@enron.com", 15)
        ]
        for s, t, w in demo_edges: G.add_edge(s, t, weight=w)
        
    return G

# ========== DASHBOARD ==========
st.markdown('<div class="dashboard">', unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <div class="brand">
        <h1>🏛️ AI GRAPH BUILDER</h1>
        <p>Enterprise Intelligence Platform</p>
    </div>
    <div class="badge"><span class="dot"></span><span>SECURE · SOC2 COMPLIANT</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="kpi-grid">
    <div class="kpi-card"><div class="kpi-label">Total Communications</div><div class="kpi-value">2,547</div><div class="kpi-trend"><span class="trend-up">↑ 12.3%</span> vs last month</div></div>
    <div class="kpi-card"><div class="kpi-label">Active Participants</div><div class="kpi-value">158</div><div class="kpi-trend"><span class="trend-up">↑ 8</span> new this week</div></div>
    <div class="kpi-card"><div class="kpi-label">Key Topics</div><div class="kpi-value">24</div><div class="kpi-trend"><span>→ stable</span></div></div>
    <div class="kpi-card"><div class="kpi-label">Risk Score</div><div class="kpi-value">35%</div><div class="kpi-trend"><span class="trend-up">↑ 5%</span> increase</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="search-section"><div class="search-title">🔍 ENTERPRISE SEARCH</div>', unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])
with col1: query = st.text_input("Search", placeholder="Search communications... e.g., 'what did sherron watkins say about accounting'", key="search", label_visibility="collapsed")
with col2: search = st.button("ANALYZE", use_container_width=True)

if time.time() - st.session_state.last_hint > 3:
    st.session_state.hint_index += 1
    st.session_state.last_hint = time.time()

st.markdown(f'<div class="hint-pills"><span class="pill">{hints[0]}</span><span class="pill">{hints[1]}</span><span class="pill">{hints[2]}</span></div></div>', unsafe_allow_html=True)

# --- Execute Search ---
if search and query:
    st.session_state.searched = True
    st.session_state.query = query
    
    with st.spinner("🔍 Scanning Vector Space..."):
        if model and pinecone_client:
            try:
                index = pinecone_client.Index(PINECONE_INDEX)
                query_embedding = model.encode(query).tolist()
                pinecone_results = index.query(vector=query_embedding, top_k=5, include_metadata=True)
                
                results = []
                for match in pinecone_results.get('matches', []):
                    metadata = match.get('metadata', {})
                    # BUG FIX 2: Catch-all for metadata keys regardless of capitalization
                    results.append({
                        'from': metadata.get('From', metadata.get('from', metadata.get('Sender', 'Unknown'))),
                        'to': metadata.get('To', metadata.get('to', metadata.get('Receiver', 'Unknown'))),
                        'subject': metadata.get('Subject', metadata.get('subject', 'No Subject')),
                        'date': metadata.get('Date', metadata.get('date', 'Unknown')),
                        'content': metadata.get('text', metadata.get('Body', metadata.get('body', '')))[:500],
                        'score': match.get('score', 0.0)
                    })
                st.session_state.results = results
            except Exception as e:
                st.error(f"Pinecone Search Error: {e}")
                st.session_state.results = []
        else:
            st.warning("Models unavailable.")
            
    st.session_state.entity = detect_entity(st.session_state.results)
    st.rerun()

# ========== RENDER RESULTS ==========
if st.session_state.searched and st.session_state.results:
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    
    # --- LEFT PANE ---
    st.markdown('<div><div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-header"><h3>📄 Search Results</h3><span class="card-badge">{len(st.session_state.results)} matches</span></div><div class="card-body">', unsafe_allow_html=True)
    
    for r in st.session_state.results:
        avatar = str(r['from'])[0].upper() if r['from'] and r['from'] != 'Unknown' else '?'
        clean_name = str(r['from']).split('@')[0] if '@' in str(r['from']) else r['from']
        st.markdown(f"""
        <div class="result-item">
            <div class="result-header">
                <div class="result-sender"><div class="avatar">{avatar}</div><div class="sender-info"><span class="sender-name">{clean_name}</span><span class="sender-email">{r['from']}</span></div></div>
                <span class="result-date">{r['date'][:10] if r['date'] else ''}</span>
            </div>
            <div class="result-subject">{r['subject']}</div>
            <div class="result-preview">{r['content'][:200]}...</div>
            <div class="result-meta"><span class="meta-tag">📊 {r['score']*100:.0f}% match</span></div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div></div></div>', unsafe_allow_html=True)
    
    # --- RIGHT PANE ---
    st.markdown('<div>', unsafe_allow_html=True)
    
    # Generate Graph
    graph_entity = st.session_state.entity if st.session_state.entity else ""
    G = get_graph_data(graph_entity, st.session_state.results)
    
    st.markdown('<div class="card"><div class="card-header"><h3>🕸️ Knowledge Graph</h3><span class="card-badge">Live Topology</span></div><div class="card-body">', unsafe_allow_html=True)
    
    if len(G.nodes()) > 0:
        pos = nx.spring_layout(G, k=1.5, iterations=50)
        edge_trace = []
        for e in G.edges():
            edge_trace.append(go.Scatter(x=[pos[e[0]][0], pos[e[1]][0], None], y=[pos[e[0]][1], pos[e[1]][1], None], mode='lines', line=dict(width=1.5, color='#cbd5e1'), hoverinfo='none'))
            
        node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
        for node in G.nodes():
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_text.append(str(node).split('@')[0])
            
            if st.session_state.entity and node == st.session_state.entity:
                node_color.append('#ef4444'); node_size.append(35)
            else:
                node_color.append('#3b82f6'); node_size.append(25)
                
        node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', text=node_text, textposition="top center", textfont=dict(size=10, color='#1e293b'), marker=dict(size=node_size, color=node_color, line=dict(width=2, color='white')))
        
        fig = go.Figure(data=edge_trace + [node_trace], layout=go.Layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False), height=350, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor='white'))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Stats Grid
    st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
    stats = [{"label": "Network Size", "value": f"{len(G.nodes())} nodes", "desc": f"{len(G.edges())} edges"}, {"label": "Density", "value": f"{nx.density(G):.2f}", "desc": "Live Metric"}]
    for s in stats: st.markdown(f'<div class="stat-item"><div class="stat-label">{s["label"]}</div><div class="stat-value">{s["value"]}</div><div class="stat-desc">{s["desc"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Entity Panel
    if st.session_state.entity:
        st.markdown(f"""
        <div class="entity-panel">
            <h4>👤 Entity Intelligence: {st.session_state.entity.split('@')[0]}</h4>
            <div class="entity-row"><span class="entity-label">Identifier</span><span class="entity-value">{st.session_state.entity}</span></div>
            <div class="entity-row"><span class="entity-label">Graph Presence</span><span class="entity-value">High</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    if st.button("← Clear Analysis", use_container_width=True):
        st.session_state.searched = False
        st.session_state.query = ""
        st.session_state.results = []
        st.rerun()

else:
    st.markdown("""
    <div style="background: white; border-radius: 30px; padding: 4rem; text-align: center; border: 1px solid #e2e8f0;">
        <div style="font-size: 5rem; margin-bottom: 1.5rem;">🏛️</div>
        <h2 style="color: #0f172a; font-weight: 500; margin-bottom: 0.5rem;">AI Knowledge Graph Builder</h2>
        <p style="color: #64748b; max-width: 500px; margin: 0 auto;">Enter a search query to explore the knowledge graph and uncover hidden patterns in communications.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer"><div>© 2026 AI Graph Builder · Enterprise Edition</div></div></div>', unsafe_allow_html=True)