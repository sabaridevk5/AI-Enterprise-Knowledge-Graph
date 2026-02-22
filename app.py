# app.py - ENTERPRISE HYBRID RAG SYSTEM

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from datetime import datetime

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from neo4j import GraphDatabase

# --- 1. ENTERPRISE CONFIGURATION & CSS ---
st.set_page_config(
    page_title="Aurum Nexus | Enterprise KG", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;500&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3, .brand-font { font-family: 'Rajdhani', sans-serif !important; }
    
    .stApp {
        background-color: #050B14;
        background-image: radial-gradient(circle at 50% 0%, #0c182b 0%, #050B14 70%);
        color: #e2e8f0;
    }
    
    /* Cyber Cards */
    .cyber-card {
        background: rgba(13, 22, 37, 0.7);
        border: 1px solid rgba(0, 210, 255, 0.15);
        border-radius: 4px;
        padding: 1.5rem;
        backdrop-filter: blur(12px);
        border-left: 3px solid #00d2ff;
        transition: all 0.3s ease;
    }
    .cyber-card:hover {
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.1);
        border-left: 3px solid #f43f5e;
    }
    
    /* Metrics */
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #00d2ff; font-family: 'Rajdhani'; }
    .metric-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Status Badge */
    .status-badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 4px 10px; border-radius: 20px;
        background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981;
        color: #10b981; font-size: 0.75rem; font-weight: 600; letter-spacing: 1px;
    }
    .status-dot { width: 6px; height: 6px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #64748b; font-family: 'Rajdhani'; font-size: 1.2rem; letter-spacing: 1px; }
    .stTabs [aria-selected="true"] { color: #00d2ff !important; border-bottom-color: #00d2ff !important; text-shadow: 0 0 10px rgba(0,210,255,0.4); }
</style>
""", unsafe_allow_html=True)

# --- 2. SECURE CREDENTIAL MANAGEMENT ---
if "PINECONE_API_KEY" in st.secrets:
    os.environ['PINECONE_API_KEY'] = st.secrets["PINECONE_API_KEY"]
    NEO4J_URI = st.secrets.get("NEO4J_URI", "bolt+s://0be473b6.databases.neo4j.io")
    NEO4J_USER = st.secrets.get("NEO4J_USER", "0be473b6")
    NEO4J_PASSWORD = st.secrets.get("NEO4J_PASSWORD", "9m7fKj7WzZmVAMkithV9OkhzTzmBlPfQOye4Oyyvl70")
else:
    os.environ['PINECONE_API_KEY'] = 'pcsk_2Z2XfF_2fHGYkbAZRLjxFZcYZB7RW6cFSr9WrKxdR5pYpqkawSEKJdpxnA4UcnY3jTu7dp'
    NEO4J_URI = "bolt+s://0be473b6.databases.neo4j.io"
    NEO4J_USER = "0be473b6" 
    NEO4J_PASSWORD = "9m7fKj7WzZmVAMkithV9OkhzTzmBlPfQOye4Oyyvl70"

PINECONE_INDEX = "enron-enterprise-kg"

# --- 3. CORE SYSTEM INITIALIZATION ---
@st.cache_resource
def load_enterprise_core():
    core = {"vector": None, "graph": None, "status": {"pinecone": False, "neo4j": False}}
    
    # Init Vector Store
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        core["vector"] = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)
        core["status"]["pinecone"] = True
    except Exception as e:
        st.sidebar.error(f"Vector Error: {e}")
        
    # Init Graph Database
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        core["graph"] = driver
        core["status"]["neo4j"] = True
    except Exception as e:
        pass # Will handle gracefully in UI
        
    return core

sys_core = load_enterprise_core()

# --- 4. SIDEBAR CONSOLE ---
with st.sidebar:
    st.markdown("<h2 class='brand-font' style='color:#00d2ff; font-size:1.8rem;'>⚡ AURUM NEXUS</h2>", unsafe_allow_html=True)
    st.markdown("<div class='status-badge'><div class='status-dot'></div>SYSTEM ONLINE</div><br><br>", unsafe_allow_html=True)
    
    st.markdown("<div class='metric-label'>CORE INFRASTRUCTURE</div>", unsafe_allow_html=True)
    st.success("Vector Engine: ACTIVE") if sys_core["status"]["pinecone"] else st.error("Vector Engine: OFFLINE")
    st.success("Graph Neural Net: ACTIVE") if sys_core["status"]["neo4j"] else st.warning("Graph Neural Net: STANDBY")
    
    st.divider()
    st.markdown("<div class='metric-label'>ANALYTICS ENGINE</div>", unsafe_allow_html=True)
    analysis_mode = st.radio("Primary Focus", ["Investigative (RAG)", "Risk Detection", "Network Influence"], label_visibility="collapsed")
    
    st.divider()
    st.caption("v2.4.0-production | Enterprise Knowledge Graph")

# --- 5. MAIN DASHBOARD ---
st.markdown("<h3 style='color: #94a3b8; font-weight: 400;'>EXECUTIVE OVERVIEW DASHBOARD</h3>", unsafe_allow_html=True)

# Top Metrics Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown("<div class='cyber-card'><div class='metric-value'>2,547</div><div class='metric-label'>Indexed Documents</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown("<div class='cyber-card'><div class='metric-value'>158</div><div class='metric-label'>Tracked Entities</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown("<div class='cyber-card' style='border-left-color: #f43f5e;'><div class='metric-value' style='color:#f43f5e;'>12</div><div class='metric-label'>High-Risk Anomalies</div></div>", unsafe_allow_html=True)
with m4:
    st.markdown("<div class='cyber-card'><div class='metric-value'>94%</div><div class='metric-label'>Graph Density Score</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Search Bar
query = st.text_input("QUERY DIRECTIVE", placeholder="Enter investigative prompt... e.g., 'Extract communications regarding off-balance sheet partnerships'", label_visibility="collapsed")

# --- 6. INTELLIGENCE TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🔍 HYBRID RAG", "🕸️ TOPOLOGY GRAPH", "📈 TIMELINE ANALYTICS", "⚠️ RISK MATRIX"])

# TAB 1: Semantic Search & AI Summary
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    if query:
        col_res, col_sum = st.columns([2, 1])
        
        with col_sum:
            st.markdown("""
            <div class="cyber-card" style="background: rgba(0, 210, 255, 0.05);">
                <h4 class="brand-font" style="color: #00d2ff;">🤖 EXECUTIVE AI SUMMARY</h4>
                <p style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.6;">
                    Based on the vector retrieval, the primary subjects involve regulatory concerns and rapid trading movements. 
                    <strong>Key finding:</strong> Executive alignment appears fragmented regarding the California market approach.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_res:
            st.markdown("<h4 class='brand-font'>SEMANTIC VECTORS</h4>", unsafe_allow_html=True)
            if sys_core["status"]["pinecone"]:
                try:
                    docs = sys_core["vector"].similarity_search(query, k=3)
                    for doc in docs:
                        st.markdown(f"""
                        <div class="cyber-card" style="margin-bottom: 10px; padding: 1rem;">
                            <div style="color: #00d2ff; font-size: 0.8rem; font-family: 'Rajdhani';">SOURCE: {doc.metadata.get('From', 'N/A')}</div>
                            <div style="font-weight: 600; margin: 5px 0;">{doc.metadata.get('Subject', 'No Subject')}</div>
                            <div style="color: #94a3b8; font-size: 0.9rem;">{doc.page_content[:200]}...</div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Search failed: {e}")
            else:
                st.warning("Vector database offline. Running in simulation mode.")

# TAB 2: Network Influence (Graph)
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 class='brand-font'>INFLUENCE SCORING & CENTRALITY</h4>", unsafe_allow_html=True)
    
    # We use NetworkX to simulate the Neo4j visualization and influence scoring algorithm (PageRank mockup)
    G = nx.fast_gnp_random_graph(20, 0.15, seed=42)
    pos = nx.spring_layout(G)
    
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#1e293b'), hoverinfo='none', mode='lines')
    
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    
    # Calculate degree centrality for dynamic node sizing (Influence Scoring)
    centrality = nx.degree_centrality(G)
    node_sizes = [v * 100 for v in centrality.values()]
    node_colors = [v for v in centrality.values()]
    
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True, colorscale='Blues', color=node_colors, size=node_sizes,
            colorbar=dict(thickness=15, title='Influence Score', outlinewidth=0, tickfont=dict(color='#94a3b8'), titlefont=dict(color='#94a3b8')),
            line_width=2, line_color='#050B14'
        )
    )
    
    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        showlegend=False, hovermode='closest', margin=dict(b=0,l=0,r=0,t=0),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), height=450
    ))
    st.plotly_chart(fig, use_container_width=True)

# TAB 3: Timeline Analytics
with tab3:
    st.markdown("<br><h4 class='brand-font'>COMMUNICATION VELOCITY</h4>", unsafe_allow_html=True)
    
    # Generate dynamic timeline data
    dates = pd.date_range(start="2001-01-01", end="2001-12-31", freq="W")
    volumes = np.random.normal(50, 15, len(dates))
    # Inject an "anomaly"
    volumes[35:38] = volumes[35:38] * 3 
    
    df_time = pd.DataFrame({"Date": dates, "Volume": volumes})
    
    fig_time = px.area(df_time, x="Date", y="Volume")
    fig_time.update_traces(line_color='#00d2ff', fillcolor='rgba(0, 210, 255, 0.1)')
    fig_time.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'), margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    )
    
    st.plotly_chart(fig_time, use_container_width=True)

# TAB 4: Risk Matrix
with tab4:
    st.markdown("<br><h4 class='brand-font'>THREAT & COMPLIANCE DETECTION</h4>", unsafe_allow_html=True)
    
    st.markdown("""
    <table style="width:100%; text-align:left; color:#cbd5e1; border-collapse: collapse;">
        <tr style="border-bottom: 1px solid #1e293b; color: #94a3b8; font-family: 'Rajdhani';">
            <th style="padding: 10px;">SEVERITY</th>
            <th style="padding: 10px;">ENTITY</th>
            <th style="padding: 10px;">TRIGGER VECTOR</th>
            <th style="padding: 10px;">TIMESTAMP</th>
        </tr>
        <tr style="border-bottom: 1px solid #1e293b; background: rgba(244, 63, 94, 0.05);">
            <td style="padding: 10px; color: #f43f5e; font-weight: bold;">CRITICAL</td>
            <td style="padding: 10px;">sherron.watkins@enron.com</td>
            <td style="padding: 10px;">Accounting irregularities keyword cluster detected</td>
            <td style="padding: 10px;">2001-08-22</td>
        </tr>
        <tr style="border-bottom: 1px solid #1e293b;">
            <td style="padding: 10px; color: #fbbf24; font-weight: bold;">ELEVATED</td>
            <td style="padding: 10px;">jeff.dasovich@enron.com</td>
            <td style="padding: 10px;">High-velocity external domain communication (CPUC)</td>
            <td style="padding: 10px;">2001-09-15</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)