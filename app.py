# app.py - SIMPLE UI (Shows results only after search)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import networkx as nx
import time

st.set_page_config(page_title="Enron Graph Explorer", layout="wide")

# Clean modern CSS
st.markdown("""
<style>
    * { 
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif; 
        margin: 0; 
        padding: 0; 
        box-sizing: border-box;
    }
    
    .stApp { 
        background: #f8fafc; 
    }
    
    .main { 
        max-width: 1200px; 
        margin: 0 auto; 
        padding: 3rem 2rem; 
    }
    
    /* Header */
    .header {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .header h1 {
        font-size: 2.5rem;
        font-weight: 500;
        color: #0f172a;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        color: #64748b;
        font-size: 1rem;
    }
    
    /* Search container */
    .search-container {
        max-width: 700px;
        margin: 0 auto 3rem auto;
    }
    
    .search-box {
        display: flex;
        gap: 0.5rem;
        background: white;
        padding: 0.25rem;
        border-radius: 50px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .search-box input {
        flex: 1;
        padding: 0.8rem 1.2rem;
        border: none;
        border-radius: 50px;
        font-size: 1rem;
        outline: none;
        background: transparent;
    }
    
    .search-box button {
        background: #0f172a;
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-size: 0.95rem;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .search-box button:hover {
        background: #1e293b;
    }
    
    /* Hint text */
    .hint {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 1rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    /* Results section */
    .results {
        margin-top: 2rem;
    }
    
    .query-badge {
        background: #e2e8f0;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        font-size: 0.85rem;
        color: #334155;
        display: inline-block;
        margin-bottom: 1.5rem;
    }
    
    /* Graph card */
    .graph-card {
        background: white;
        border-radius: 24px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    .graph-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .graph-header h3 {
        font-size: 1rem;
        font-weight: 600;
        color: #0f172a;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    
    .graph-badge {
        background: #f1f5f9;
        padding: 0.2rem 0.8rem;
        border-radius: 30px;
        font-size: 0.7rem;
        color: #475569;
    }
    
    /* Details grid */
    .details-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .detail-card {
        background: #f8fafc;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #e2e8f0;
    }
    
    .detail-label {
        color: #64748b;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        margin-bottom: 0.3rem;
    }
    
    .detail-value {
        font-size: 1.1rem;
        font-weight: 500;
        color: #0f172a;
    }
    
    /* Stats row */
    .stats-row {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .stat {
        background: #f1f5f9;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        font-size: 0.8rem;
        color: #334155;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 4rem;
        background: white;
        border-radius: 24px;
        border: 1px solid #e2e8f0;
    }
    
    .empty-state span {
        font-size: 4rem;
        display: block;
        margin-bottom: 1rem;
    }
    
    .empty-state h3 {
        font-size: 1.2rem;
        font-weight: 500;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
    
    .empty-state p {
        color: #64748b;
    }
    
    /* New search button */
    .new-search {
        text-align: center;
        margin-top: 2rem;
    }
    
    .new-search button {
        background: transparent;
        border: 1px solid #e2e8f0;
        padding: 0.6rem 2rem;
        border-radius: 30px;
        font-size: 0.9rem;
        color: #64748b;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .new-search button:hover {
        border-color: #0f172a;
        color: #0f172a;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e2e8f0;
        color: #94a3b8;
        font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if 'searched' not in st.session_state:
    st.session_state.searched = False
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""
if 'current_entity' not in st.session_state:
    st.session_state.current_entity = "jeff.dasovich"

# ========== DATA ==========
# Graph data
G = nx.Graph()
edges = [
    ("jeff.dasovich", "kenneth.lay", 47),
    ("jeff.dasovich", "jeff.skilling", 38),
    ("kenneth.lay", "sherron.watkins", 25),
    ("jeff.skilling", "greg.whalley", 22),
    ("kenneth.lay", "andy.zipper", 18),
    ("sherron.watkins", "mark.haedicke", 15),
]
for src, tgt, w in edges:
    G.add_edge(src, tgt, weight=w)

# Entity information
entity_info = {
    "jeff.dasovich": {
        "role": "Government Affairs", 
        "emails": 47, 
        "contacts": 12,
        "topics": "Energy Trading, California",
        "influence": 92,
        "sentiment": "Positive"
    },
    "kenneth.lay": {
        "role": "CEO & Chairman", 
        "emails": 42, 
        "contacts": 15,
        "topics": "Executive, Strategy",
        "influence": 98,
        "sentiment": "Mixed"
    },
    "jeff.skilling": {
        "role": "COO", 
        "emails": 38, 
        "contacts": 10,
        "topics": "Trading, Operations",
        "influence": 95,
        "sentiment": "Positive"
    },
    "sherron.watkins": {
        "role": "Vice President", 
        "emails": 25, 
        "contacts": 6,
        "topics": "Accounting, Legal",
        "influence": 88,
        "sentiment": "Concerned"
    },
    "greg.whalley": {
        "role": "President", 
        "emails": 22, 
        "contacts": 8,
        "topics": "Trading, Energy",
        "influence": 86,
        "sentiment": "Neutral"
    },
    "andy.zipper": {
        "role": "CEO (Enron Europe)", 
        "emails": 18, 
        "contacts": 7,
        "topics": "Operations, Europe",
        "influence": 82,
        "sentiment": "Neutral"
    }
}

# Sample search results
search_results = {
    "jeff dasovich": [
        {"subject": "California Energy Market", "date": "2001-05-15", "preview": "Ken, the California market is showing significant volatility..."},
        {"subject": "Trading Strategy", "date": "2001-03-22", "preview": "We should increase our positions in the natural gas market..."},
    ],
    "sherron watkins": [
        {"subject": "URGENT: Accounting Concerns", "date": "2001-08-22", "preview": "I have serious concerns about our accounting practices..."},
        {"subject": "Legal Meeting", "date": "2001-07-10", "preview": "Met with legal counsel to discuss the off-balance-sheet entities..."},
    ],
    "kenneth lay": [
        {"subject": "Board Meeting Agenda", "date": "2001-04-05", "preview": "Quarterly results presentation prepared for the board..."},
        {"subject": "Investor Relations", "date": "2001-02-18", "preview": "Need to prepare talking points for the investor call..."},
    ],
    "jeff skilling": [
        {"subject": "Trading Desk Update", "date": "2001-03-10", "preview": "Natural gas positions are strong. Let's push harder..."},
        {"subject": "Operations Review", "date": "2001-01-25", "preview": "Quarterly operations review scheduled for next week..."},
    ]
}

# ========== HELPER FUNCTIONS ==========
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
    elif 'greg' in q or 'whalley' in q:
        return "greg.whalley"
    elif 'andy' in q or 'zipper' in q:
        return "andy.zipper"
    return "jeff.dasovich"

def get_results_for_query(query):
    q = query.lower()
    for key in search_results:
        if key in q:
            return search_results[key]
    return search_results["jeff dasovich"]  # Default

# ========== MAIN UI ==========
st.markdown('<div class="main">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <h1>🔍 Enron Graph Explorer</h1>
    <p>Search communications · Discover relationships</p>
</div>
""", unsafe_allow_html=True)

# Search section
st.markdown('<div class="search-container">', unsafe_allow_html=True)
st.markdown('<div class="search-box">', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    query = st.text_input(
        "",
        placeholder="e.g., jeff dasovich energy trading",
        key="search_input",
        label_visibility="collapsed"
    )
with col2:
    search = st.button("Search", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="hint">💡 Try: jeff dasovich · sherron watkins · kenneth lay · energy trading</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Handle search
if search and query:
    st.session_state.searched = True
    st.session_state.current_query = query
    st.session_state.current_entity = extract_entity(query)
    st.rerun()

# ========== RESULTS (only shown after search) ==========
if st.session_state.searched:
    st.markdown('<div class="results">', unsafe_allow_html=True)
    
    # Query badge
    st.markdown(f'<div class="query-badge">🔍 Showing results for: "{st.session_state.current_query}"</div>', unsafe_allow_html=True)
    
    # Graph card
    st.markdown('<div class="graph-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="graph-header">
        <h3>🕸️ Knowledge Graph</h3>
        <span class="graph-badge">2.0 depth</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Render graph
    if len(G.nodes()) > 0:
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Edge trace
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            color = '#3b82f6' if st.session_state.current_entity in [edge[0], edge[1]] else '#e2e8f0'
            width = 2.5 if st.session_state.current_entity in [edge[0], edge[1]] else 1.5
            
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
            
            if node == st.session_state.current_entity:
                node_color.append('#ef4444')
                node_size.append(35)
            else:
                node_color.append('#94a3b8')
                node_size.append(25)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers+text',
            text=node_text, textposition="top center",
            textfont=dict(size=10, color='#1e293b'),
            marker=dict(size=node_size, color=node_color, line=dict(width=2, color='white'))
        )
        
        fig = go.Figure(
            data=edge_trace + [node_trace],
            layout=go.Layout(
                showlegend=False,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Entity details
    info = entity_info.get(st.session_state.current_entity, entity_info["jeff.dasovich"])
    
    st.markdown('<div class="details-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="detail-card">
            <div class="detail-label">Entity</div>
            <div class="detail-value">{st.session_state.current_entity}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="detail-card">
            <div class="detail-label">Role</div>
            <div class="detail-value">{info['role']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="detail-card">
            <div class="detail-label">Communications</div>
            <div class="detail-value">{info['emails']} emails</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="detail-card">
            <div class="detail-label">Influence</div>
            <div class="detail-value">{info['influence']}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Stats row
    results_list = get_results_for_query(st.session_state.current_query)
    
    st.markdown('<div class="stats-row">', unsafe_allow_html=True)
    st.markdown(f'<span class="stat">📧 {len(results_list)} relevant emails</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="stat">👥 {info["contacts"]} direct contacts</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="stat">📊 {info["topics"]}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="stat">💬 {info["sentiment"]} sentiment</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sample emails
    if results_list:
        st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
        st.markdown("**📧 Recent communications**")
        for r in results_list:
            st.markdown(f"""
            <div style="background: #f8fafc; padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; border: 1px solid #e2e8f0;">
                <div style="font-weight: 500;">{r['subject']}</div>
                <div style="color: #64748b; font-size: 0.85rem; margin: 0.2rem 0;">{r['preview']}</div>
                <div style="color: #94a3b8; font-size: 0.7rem;">{r['date']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # New search button
    st.markdown('<div class="new-search">', unsafe_allow_html=True)
    if st.button("← New Search", use_container_width=True):
        st.session_state.searched = False
        st.session_state.current_query = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Empty state - shown when no search has been performed
    st.markdown("""
    <div class="empty-state">
        <span>🔍</span>
        <h3>Search to begin</h3>
        <p>Enter a query above to explore the Enron knowledge graph</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    Enron Graph Explorer · Simple · Focused
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)