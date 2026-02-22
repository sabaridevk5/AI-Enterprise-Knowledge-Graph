# app.py - CYBER-INTELLIGENCE EDITION

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
import networkx as nx

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Aurum Intelligence", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# --- 2. CYBER-INTELLIGENCE CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'Rajdhani', sans-serif !important;
    }

    /* Deep Midnight Background */
    .stApp {
        background-color: #030712;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(0, 210, 255, 0.03), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(159, 122, 234, 0.04), transparent 25%);
        color: #e2e8f0;
    }

    /* Hide defaults */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Brand Header */
    .top-bar {
        padding: 1rem 0;
        border-bottom: 1px solid rgba(0, 210, 255, 0.1);
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .brand-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Neon Cards */
    .cyber-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.1);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        border-left: 3px solid transparent;
    }
    
    .cyber-card:hover {
        transform: translateX(5px);
        border-left: 3px solid #00d2ff;
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.1);
        background: rgba(15, 23, 42, 0.9);
    }

    /* System Metrics */
    .metric-box {
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-top: 2px solid #3a7bd5;
        border-radius: 6px;
        padding: 1.5rem;
        text-align: center;
    }
    .metric-value {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #e2e8f0;
        text-shadow: 0 0 10px rgba(255,255,255,0.1);
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 0.5rem;
    }

    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.2rem;
        letter-spacing: 1px;
    }
    .stTabs [aria-selected="true"] {
        color: #00d2ff !important;
        border-bottom-color: #00d2ff !important;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT ---
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'trigger_search' not in st.session_state:
    st.session_state.trigger_search = False

def set_query(q):
    st.session_state.search_query = q
    st.session_state.trigger_search = True

# --- 4. HEADER ---
st.markdown("""
<div class="top-bar">
    <div>
        <div class="brand-title">⚡ AURUM NEXUS</div>
        <div style="color: #64748b; font-size: 0.9rem; letter-spacing: 1px;">COGNITIVE GRAPH INTERFACE v2.4</div>
    </div>
    <div style="color: #10b981; font-family: 'Rajdhani'; letter-spacing: 1px; display: flex; align-items: center; gap: 8px;">
        <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 10px #10b981;"></div>
        SECURE LINK ACTIVE
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5. SEARCH BAR ---
col_search, col_btn, col_clear = st.columns([6, 1.5, 1])
with col_search:
    query_input = st.text_input("QUERY", value=st.session_state.search_query, label_visibility="collapsed", placeholder="Initialize search protocol... (e.g., 'California energy crisis')")
with col_btn:
    search_clicked = st.button("INITIATE SCAN", use_container_width=True, type="primary")
with col_clear:
    if st.button("CLEAR", use_container_width=True):
        st.session_state.search_query = ""
        st.session_state.trigger_search = False
        st.rerun()

if search_clicked and query_input:
    st.session_state.search_query = query_input
    st.session_state.trigger_search = True

st.divider()

# --- 6. CONDITIONAL UI: EMPTY STATE vs RESULTS ---

if not st.session_state.search_query:
    # --- LANDING PAGE (Empty State) ---
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem; color: #94a3b8;'>SYSTEM AWAITING DIRECTIVES</h2>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="metric-box"><div class="metric-value">586</div><div class="metric-label">Neural Nodes Indexed</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-box"><div class="metric-value">4,000+</div><div class="metric-label">Identified Relationships</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-box"><div class="metric-value">0.94ms</div><div class="metric-label">Vector Latency</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br><br><h4 style='text-align: center; color: #64748b;'>SUGGESTED INTEL PROTOCOLS</h4>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔍 'What did Jeff Dasovich discuss regarding regulations?'", use_container_width=True):
            set_query("What did Jeff Dasovich discuss regarding regulations?")
            st.rerun()
    with c2:
        if st.button("🔍 'Show accounting concerns by Sherron Watkins'", use_container_width=True):
            set_query("Show accounting concerns by Sherron Watkins")
            st.rerun()
    with c3:
        if st.button("🔍 'Analyze West Coast trading desk strategies'", use_container_width=True):
            set_query("Analyze West Coast trading desk strategies")
            st.rerun()

else:
    # --- RESULTS PAGE ---
    st.caption(f"**ACTIVE DIRECTIVE:** `{st.session_state.search_query}`")
    
    tab1, tab2, tab3 = st.tabs(["📄 SEMANTIC INTEL", "🕸️ NEURAL GRAPH", "📊 ENTITY MATRIX"])
    
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        # Dummy data simulating a real semantic search
        results = [
            {"sender": "jeff.dasovich@enron.com", "subject": "California Energy Regulations", "content": "We need to monitor the CPUC rulings closely. The volatility is creating a massive gap in the market.", "date": "2001-09-12"},
            {"sender": "kenneth.lay@enron.com", "subject": "Strategy Alignment", "content": "Please ensure all trading desks are aligned with the new regulatory framework Jeff proposed.", "date": "2001-09-14"}
        ]
        
        for res in results:
            st.markdown(f"""
            <div class="cyber-card">
                <div style="display: flex; justify-content: space-between; color: #64748b; font-size: 0.8rem; margin-bottom: 10px; font-family: 'Rajdhani';">
                    <span>FROM: <span style="color:#00d2ff">{res['sender']}</span></span>
                    <span>TS: {res['date']}</span>
                </div>
                <div style="color: #e2e8f0; font-weight: 600; font-size: 1.1rem; margin-bottom: 8px;">{res['subject']}</div>
                <div style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5;">{res['content']}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        # Create a dynamic-looking graph
        G = nx.Graph()
        edges = [
            ("Jeff Dasovich", "Kenneth Lay", 8),
            ("Jeff Dasovich", "Jeff Skilling", 5),
            ("Kenneth Lay", "Sherron Watkins", 3),
            ("Regulatory Body", "Jeff Dasovich", 7)
        ]
        for src, tgt, weight in edges:
            G.add_edge(src, tgt, weight=weight)
            
        pos = nx.spring_layout(G, seed=42)
        
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y, line=dict(width=2, color='rgba(0, 210, 255, 0.3)'),
            hoverinfo='none', mode='lines'
        )

        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers+text',
            text=list(G.nodes()), textposition="bottom center",
            marker=dict(
                color='#00d2ff', size=30, 
                line=dict(color='#ffffff', width=2)
            ),
            textfont=dict(color='#e2e8f0', size=12, family="Rajdhani")
        )

        fig = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(
                        showlegend=False, hovermode='closest',
                        margin=dict(b=0,l=0,r=0,t=0),
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=500
                     ))
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card">
            <h3 style="color: #00d2ff; margin-bottom: 1rem;">PRIMARY ENTITY TARGET: JEFF DASOVICH</h3>
            <p><strong>Department:</strong> Government Affairs</p>
            <p><strong>Risk Profile:</strong> Elevated (Frequent regulatory communication)</p>
            <p><strong>Key Topics:</strong> CPUC, California Market, Deregulation</p>
        </div>
        """, unsafe_allow_html=True)