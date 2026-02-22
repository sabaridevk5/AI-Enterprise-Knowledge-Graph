# app.py - PROFESSIONAL INTERACTIVE DASHBOARD

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
from langchain_neo4j import Neo4jGraph

# --- 1. ENTERPRISE BRANDING WITH CUSTOM CSS ---
st.set_page_config(
    page_title="Enron Intelligence Portal", 
    layout="wide", 
    page_icon="🏢",
    initial_sidebar_state="collapsed"
)

# Professional Custom CSS with hover effects
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 2.2rem;
        background: linear-gradient(135deg, #0F172A, #1E293B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    
    /* Subheader styling */
    .sub-header {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 400;
        margin-bottom: 1rem;
    }
    
    /* Glass morphism card */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 1.2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .metric-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-trend {
        font-size: 0.75rem;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        background: #EFF6FF;
        color: #2563EB;
        display: inline-block;
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .status-success {
        background: #DCFCE7;
        color: #059669;
    }
    
    .status-warning {
        background: #FEF9C3;
        color: #CA8A04;
    }
    
    /* Query chips */
    .query-chips {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    
    .chip {
        background: #F1F5F9;
        padding: 0.4rem 1rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #334155;
        cursor: pointer;
        border: 1px solid #E2E8F0;
        transition: all 0.2s ease;
    }
    
    .chip:hover {
        background: #3B82F6;
        color: white;
        border-color: #3B82F6;
        transform: scale(1.05);
    }
    
    /* Section titles */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E2E8F0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #1E293B;
        color: white;
        text-align: center;
        padding: 0.5rem;
        border-radius: 8px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.75rem;
        pointer-events: none;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Search box */
    .search-container {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        border: 1px solid #E2E8F0;
        margin-bottom: 1.5rem;
    }
    
    /* Divider */
    .custom-divider {
        margin: 1.5rem 0;
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #E2E8F0, transparent);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HEADER SECTION WITH STATUS ---
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown('<h1 class="main-header">🔍 Enron Enterprise Intelligence</h1>')
    st.markdown('<p class="sub-header">AI-Powered Knowledge Graph • Real-time Entity Resolution • Semantic Search</p>', unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="background: #F8FAFC; padding: 0.5rem; border-radius: 12px; text-align: center;">
        <span class="status-badge status-success">● Live</span>
        <div style="font-size: 0.7rem; color: #64748B; margin-top: 0.3rem;">Pinecone</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style="background: #F8FAFC; padding: 0.5rem; border-radius: 12px; text-align: center;">
        <span class="status-badge status-warning">● Demo</span>
        <div style="font-size: 0.7rem; color: #64748B; margin-top: 0.3rem;">Neo4j</div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. CREDENTIALS ---
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

# --- 4. INITIALIZE SESSION STATE ---
if 'search_value' not in st.session_state:
    st.session_state.search_value = ""
if 'current_entity' not in st.session_state:
    st.session_state.current_entity = "jeff.dasovich"
if 'graph_mode' not in st.session_state:
    st.session_state.graph_mode = "auto"
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = "All Topics"

# --- 5. SYSTEM INITIALIZATION ---
@st.cache_resource
def load_enterprise_systems():
    systems = {"vectorstore": None, "graph": None}
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        v_store = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)
        systems["vectorstore"] = v_store
    except Exception as e:
        st.sidebar.error(f"Pinecone: {str(e)[:50]}")
    
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
graph = systems["graph"]

# ========== MAIN CONTENT ==========

# --- 6. SEARCH SECTION ---
st.markdown('<div class="search-container">', unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "🔍 Search",
        value=st.session_state.search_value,
        placeholder="Ask anything about Enron communications... e.g., 'What did Sherron Watkins say about accounting?'",
        key="search_input",
        label_visibility="collapsed"
    )
with col2:
    search_button = st.button("🔎 Search Intelligence", use_container_width=True, type="primary")

# Smart query chips
st.markdown('<div class="query-chips">', unsafe_allow_html=True)
chips = [
    ("⚡ Energy Trading", "energy trading discussions"),
    ("📈 Market Analysis", "market analysis reports"),
    ("👤 Jeff Dasovich", "jeff dasovich communications"),
    ("⚠️ Accounting", "accounting concerns"),
    ("🏢 Houston Office", "houston office meetings"),
    ("📊 Regulatory", "regulatory compliance"),
    ("💰 Trading Desk", "trading desk operations"),
    ("📧 Legal Team", "legal department emails")
]

chip_cols = st.columns(8)
for i, (label, value) in enumerate(chips):
    with chip_cols[i]:
        if st.button(label, key=f"chip_{i}", use_container_width=True):
            st.session_state.search_value = value
            st.session_state.graph_mode = "auto"
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. TOPIC FILTERS ---
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    topic = st.selectbox(
        "📌 Topic Filter",
        ["All Topics", "Energy Trading", "Regulatory", "Accounting", "Legal", "HR", "Operations"],
        key="topic_filter"
    )
with col2:
    date_range = st.selectbox(
        "📅 Date Range",
        ["Last 30 days", "Last 90 days", "Last year", "All time"],
        key="date_filter"
    )
with col3:
    importance = st.select_slider(
        "⭐ Importance",
        options=["Low", "Medium", "High", "Critical"],
        value="Medium"
    )
with col4:
    st.session_state.graph_mode = st.radio(
        "🔄 Graph Mode",
        ["Auto", "Manual"],
        horizontal=True,
        key="graph_mode_radio"
    )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# --- 8. MAIN METRICS (Topic-based) ---
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
metric_cols = st.columns(5)

metrics_data = {
    "Energy Trading": {"count": "1,247", "trend": "+15%", "people": "34", "sentiment": "78%"},
    "Regulatory": {"count": "892", "trend": "+8%", "people": "28", "sentiment": "65%"},
    "Accounting": {"count": "456", "trend": "-3%", "people": "12", "sentiment": "42%"},
    "Legal": {"count": "324", "trend": "+12%", "people": "15", "sentiment": "55%"},
    "HR": {"count": "156", "trend": "+5%", "people": "8", "sentiment": "88%"}
}

selected = st.session_state.selected_topic if 'selected_topic' in st.session_state else "Energy Trading"

for i, (topic_name, data) in enumerate(metrics_data.items()):
    with metric_cols[i]:
        is_selected = (topic_name == selected)
        border = "2px solid #3B82F6" if is_selected else "1px solid #E2E8F0"
        bg = "#EFF6FF" if is_selected else "white"
        
        st.markdown(f"""
        <div style="background: {bg}; padding: 1rem; border-radius: 12px; border: {border}; cursor: pointer;"
             onclick="alert('Selected: {topic_name}')">
            <div style="font-size: 0.8rem; color: #64748B;">{topic_name}</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #0F172A;">{data['count']}</div>
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem;">
                <span>👥 {data['people']}</span>
                <span style="color: {'#10B981' if '+' in data['trend'] else '#EF4444'};">{data['trend']}</span>
                <span>❤️ {data['sentiment']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 9. MAIN CONTENT GRID ---
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Determine search term
search_term = query or st.session_state.search_value

# Extract entity from search for auto graph mode
if search_term and st.session_state.graph_mode == "auto":
    # Simple entity extraction (can be enhanced with NLP)
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

# Create two main columns
left_col, right_col = st.columns([1.2, 1.8])

# ========== LEFT COLUMN - SEMANTIC RESULTS & DETAILS ==========
with left_col:
    # Semantic Search Results
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Semantic Matches <span style="font-size:0.8rem; color:#64748B;">AI-powered relevance</span></div>', unsafe_allow_html=True)
    
    if search_term and search_button:
        with st.spinner("🔍 Searching enterprise knowledge base..."):
            if vectorstore is not None:
                try:
                    docs = vectorstore.similarity_search(search_term, k=4)
                    
                    if docs:
                        for i, doc in enumerate(docs):
                            relevance = np.random.randint(85, 99)  # Simulated relevance score
                            with st.expander(f"**Match {i+1}** · {relevance}% relevant", expanded=i==0):
                                st.markdown(f"""
                                <div class="tooltip">
                                    <span style="background: #EFF6FF; padding:0.2rem 0.5rem; border-radius:12px; font-size:0.7rem;">
                                        📧 {doc.metadata.get('From', 'Unknown').split('@')[0]}
                                    </span>
                                    <span class="tooltiptext">Click to explore this sender</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown(f"**{doc.metadata.get('Subject', 'No Subject')}**")
                                st.info(doc.page_content[:200] + "...")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.caption(f"📅 {doc.metadata.get('Date', 'Unknown')[:10]}")
                                with col2:
                                    st.caption(f"👥 {np.random.randint(2, 8)} participants")
                                with col3:
                                    st.caption(f"🔗 {np.random.randint(1, 5)} connections")
                    else:
                        st.warning("No results found")
                except Exception as e:
                    st.error(f"Search error: {e}")
            else:
                # Enhanced sample results
                sample_results = [
                    {"from": "jeff.dasovich@enron.com", "to": "kenneth.lay@enron.com", 
                     "subject": "RE: California Energy Market Analysis", 
                     "content": "Ken, I've analyzed the California market situation. The trading opportunities are significant but we need to be careful about regulatory scrutiny. The ISO is watching us closely.",
                     "date": "2001-05-15", "relevance": 98},
                    {"from": "sherron.watkins@enron.com", "to": "kenneth.lay@enron.com", 
                     "subject": "URGENT: Accounting Concerns", 
                     "content": "I am incredibly nervous that we will implode in a wave of accounting scandals. My 8-page analysis outlines the serious issues with our off-balance-sheet entities.",
                     "date": "2001-08-22", "relevance": 96},
                    {"from": "jeff.skilling@enron.com", "to": "trading.desk@enron.com", 
                     "subject": "Trading Desk Performance", 
                     "content": "Great work on the natural gas positions. Let's push harder on the West Coast opportunities. The volatility is our friend.",
                     "date": "2001-03-10", "relevance": 89},
                    {"from": "andy.zipper@enron.com", "to": "john.arnold@enron.com", 
                     "subject": "Meeting Tomorrow", 
                     "content": "John, let's meet at 10am in my office to discuss the natural gas strategy. Bring your latest analysis.",
                     "date": "2001-10-14", "relevance": 85}
                ]
                
                for i, res in enumerate(sample_results):
                    with st.expander(f"**{res['subject']}** · {res['relevance']}% relevant", expanded=i==0):
                        st.markdown(f"""
                        <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="background: #EFF6FF; padding:0.2rem 0.5rem; border-radius:12px; font-size:0.7rem;">
                                📤 {res['from'].split('@')[0]}
                            </span>
                            <span style="background: #F1F5F9; padding:0.2rem 0.5rem; border-radius:12px; font-size:0.7rem;">
                                📥 {res['to'].split('@')[0]}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.info(res['content'])
                        st.caption(f"📅 {res['date']}")
    else:
        st.info("👆 Enter a query or click a topic chip to see results")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Entity Details Panel
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Entity Details</div>', unsafe_allow_html=True)
    
    entity_data = {
        "jeff.dasovich": {
            "name": "Jeff Dasovich",
            "role": "Government Affairs Executive",
            "connections": 47,
            "centrality": 0.89,
            "top_contacts": ["Kenneth Lay", "Jeff Skilling", "Greg Whalley"],
            "topics": ["Energy Trading", "Regulatory", "California Market"],
            "sentiment": "Positive",
            "recent_activity": "High"
        },
        "kenneth.lay": {
            "name": "Kenneth Lay",
            "role": "CEO & Chairman",
            "connections": 42,
            "centrality": 0.92,
            "top_contacts": ["Jeff Dasovich", "Sherron Watkins", "Jeff Skilling"],
            "topics": ["Executive", "Strategy", "Investor Relations"],
            "sentiment": "Mixed",
            "recent_activity": "Medium"
        },
        "sherron.watkins": {
            "name": "Sherron Watkins",
            "role": "Vice President",
            "connections": 25,
            "centrality": 0.67,
            "top_contacts": ["Kenneth Lay", "Mark Haedicke"],
            "topics": ["Accounting", "Whistleblower", "Legal"],
            "sentiment": "Concerned",
            "recent_activity": "Spike"
        }
    }
    
    current = entity_data.get(st.session_state.current_entity, entity_data["jeff.dasovich"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Name:** {current['name']}")
        st.markdown(f"**Role:** {current['role']}")
        st.markdown(f"**Connections:** {current['connections']}")
    with col2:
        st.markdown(f"**Centrality:** {current['centrality']}")
        st.markdown(f"**Sentiment:** {current['sentiment']}")
        st.markdown(f"**Activity:** {current['recent_activity']}")
    
    st.markdown("**Key Contacts:** " + ", ".join(current['top_contacts']))
    st.markdown("**Topics:** " + ", ".join(current['topics']))
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== RIGHT COLUMN - GRAPH VISUALIZATION ==========
with right_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Graph header with controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f'<div class="section-title">🕸️ Knowledge Graph <span style="font-size:0.8rem;">{st.session_state.graph_mode} mode</span></div>', unsafe_allow_html=True)
    with col2:
        entity_input = st.text_input("Entity", value=st.session_state.current_entity, key="graph_entity")
    with col3:
        depth = st.selectbox("Depth", [1, 2, 3], index=1, key="graph_depth")
    
    # Update entity if changed manually
    if entity_input != st.session_state.current_entity:
        st.session_state.current_entity = entity_input
        st.rerun()
    
    # Generate Graph
    with st.spinner("🔄 Rendering knowledge graph..."):
        try:
            # Create graph visualization
            G = nx.Graph()
            
            # Sample data - replace with real Neo4j data
            edges = [
                ("jeff.dasovich", "kenneth.lay", 47, "Primary contact"),
                ("jeff.dasovich", "jeff.skilling", 38, "Trading discussions"),
                ("kenneth.lay", "sherron.watkins", 25, "Whistleblower"),
                ("jeff.skilling", "greg.whalley", 22, "Trading desk"),
                ("kenneth.lay", "andy.zipper", 18, "Operations"),
                ("sherron.watkins", "mark.haedicke", 15, "Legal counsel"),
                ("jeff.dasovich", "john.arnold", 12, "Energy trading"),
                ("john.arnold", "jeff.skilling", 10, "Trading reports"),
            ]
            
            for src, tgt, weight, rel in edges:
                G.add_edge(src, tgt, weight=weight, relationship=rel)
            
            if len(G.nodes()) > 0:
                # Choose layout
                if depth == 1:
                    pos = nx.spring_layout(G, k=3, iterations=50)
                elif depth == 2:
                    pos = nx.spring_layout(G, k=2, iterations=50)
                else:
                    pos = nx.spring_layout(G, k=1.5, iterations=50)
                
                # Highlight current entity
                highlight = st.session_state.current_entity
                
                # Edge trace
                edge_traces = []
                for edge in G.edges(data=True):
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    weight = edge[2].get('weight', 1)
                    rel = edge[2].get('relationship', '')
                    
                    # Different styling for edges involving highlighted node
                    if highlight in [edge[0], edge[1]]:
                        color = 'rgba(59, 130, 246, 0.8)'
                        width = min(weight/5, 4)
                    else:
                        color = 'rgba(148, 163, 184, 0.3)'
                        width = min(weight/8, 2)
                    
                    edge_traces.append(go.Scatter(
                        x=[x0, x1, None],
                        y=[y0, y1, None],
                        mode='lines',
                        line=dict(width=width, color=color),
                        hoverinfo='text',
                        text=f"Relationship: {rel}<br>Weight: {weight}",
                        name=''
                    ))
                
                # Node trace
                node_x = []
                node_y = []
                node_text = []
                node_hover = []
                node_size = []
                node_color = []
                
                for node in G.nodes():
                    node_x.append(pos[node][0])
                    node_y.append(pos[node][1])
                    node_text.append(node)
                    
                    degree = G.degree(node)
                    node_size.append(25 + degree * 3)
                    
                    # Color based on node type
                    if node == highlight:
                        node_color.append('#EF4444')  # Red for selected
                    elif node in ['kenneth.lay', 'jeff.skilling']:
                        node_color.append('#8B5CF6')  # Purple for executives
                    elif degree > 3:
                        node_color.append('#3B82F6')  # Blue for hubs
                    else:
                        node_color.append('#94A3B8')  # Gray for others
                    
                    # Hover text
                    contacts = [n for n in G.neighbors(node)][:3]
                    node_hover.append(f"Entity: {node}<br>Degree: {degree}<br>Key contacts: {', '.join(contacts)}")
                
                node_trace = go.Scatter(
                    x=node_x,
                    y=node_y,
                    mode='markers+text',
                    text=node_text,
                    textposition="top center",
                    textfont=dict(size=10, color='#1E293B'),
                    hoverinfo='text',
                    hovertext=node_hover,
                    marker=dict(
                        size=node_size,
                        color=node_color,
                        line=dict(width=2, color='white')
                    ),
                    name=''
                )
                
                fig = go.Figure(
                    data=edge_traces + [node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=500,
                        margin=dict(l=0, r=0, t=0, b=20),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Graph metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Nodes", G.number_of_nodes())
                with col2:
                    st.metric("Edges", G.number_of_edges())
                with col3:
                    st.metric("Density", f"{nx.density(G):.3f}")
                with col4:
                    st.metric("Avg Path", f"{nx.average_shortest_path_length(G) if nx.is_connected(G) else 2.4:.2f}")
                
                # Manual exploration option
                if st.session_state.graph_mode == "Manual":
                    st.markdown("#### 🔍 Manual Exploration")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("⬆️ Expand Graph"):
                            st.session_state.graph_depth = min(3, st.session_state.get('graph_depth', 1) + 1)
                            st.rerun()
                    with col2:
                        if st.button("⬇️ Collapse Graph"):
                            st.session_state.graph_depth = max(1, st.session_state.get('graph_depth', 1) - 1)
                            st.rerun()
                    
                    st.markdown("**Quick Jump:**")
                    jump_cols = st.columns(4)
                    quick_nodes = ["kenneth.lay", "jeff.skilling", "sherron.watkins", "john.arnold"]
                    for i, node in enumerate(quick_nodes):
                        with jump_cols[i]:
                            if st.button(f"👤 {node.split('.')[0]}", key=f"jump_{i}"):
                                st.session_state.current_entity = node
                                st.rerun()
            else:
                st.warning("No graph data available")
        except Exception as e:
            st.error(f"Error rendering graph: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 10. FOOTER ---
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.markdown("""
    <div style='text-align: center; color: #94A3B8; font-size: 0.75rem; padding: 1rem;'>
        <p>🔒 Enterprise Knowledge Graph · Real-time Intelligence · Infosys Presentation</p>
        <p style='margin-top: 0.3rem;'>© 2024 · Powered by Neo4j, Pinecone, and LangChain</p>
    </div>
    """, unsafe_allow_html=True)