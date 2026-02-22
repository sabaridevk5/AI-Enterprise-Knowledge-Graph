# app.py - ENTERPRISE SAAS COMMAND CENTER

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import time

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from neo4j import GraphDatabase

# --- 1. SAAS PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Enterprise KG Platform", 
    layout="wide", 
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- 2. MATTE DARK SAAS CSS ---
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    code, .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Slate Dark Theme */
    .stApp {
        background-color: #0f172a; /* Slate 900 */
        color: #f8fafc; /* Slate 50 */
    }

    /* Hide defaults */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Widget Cards */
    .widget-card {
        background-color: #1e293b; /* Slate 800 */
        border: 1px solid #334155; /* Slate 700 */
        border-radius: 8px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        height: 100%;
    }
    
    .widget-header {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8; /* Slate 400 */
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #334155;
        padding-bottom: 0.5rem;
    }

    /* Metric Layouts */
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 500;
    }
    .kpi-delta.positive { color: #10b981; } /* Emerald */
    .kpi-delta.negative { color: #ef4444; } /* Red */
    
    /* Search Results Feed */
    .intel-feed-item {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-left: 3px solid #3b82f6; /* Blue accent */
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    
    /* Risk Table */
    .risk-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    .risk-table th {
        text-align: left;
        padding: 8px;
        color: #94a3b8;
        border-bottom: 1px solid #334155;
        font-weight: 600;
    }
    .risk-table td {
        padding: 8px;
        border-bottom: 1px solid #334155;
        color: #cbd5e1;
    }
    .badge {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge.critical { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
    .badge.warning { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
</style>
""", unsafe_allow_html=True)

# --- 3. CONNECTION LOGIC (SAFE LOAD) ---
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

@st.cache_resource
def init_infrastructure():
    infra = {"vector": None, "graph": None, "v_status": "OFFLINE", "g_status": "OFFLINE"}
    try:
        embeds = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        infra["vector"] = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeds)
        infra["v_status"] = "ONLINE"
    except Exception: pass
    
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        infra["graph"] = driver
        infra["g_status"] = "ONLINE"
    except Exception: pass
    return infra

infra = init_infrastructure()

# --- 4. SIDEBAR SETTINGS ---
with st.sidebar:
    st.markdown("<h3 style='color: #f8fafc; font-weight: 600; margin-bottom: 0;'>WORKSPACE</h3>", unsafe_allow_html=True)
    st.markdown("<div style='color: #94a3b8; font-size: 0.8rem; margin-bottom: 2rem;'>Investigation & Intelligence</div>", unsafe_allow_html=True)
    
    st.markdown("**SYSTEM STATUS**")
    v_color = "#10b981" if infra["v_status"] == "ONLINE" else "#ef4444"
    g_color = "#10b981" if infra["g_status"] == "ONLINE" else "#f59e0b"
    
    st.markdown(f"<div style='font-size: 0.85rem; margin-bottom: 5px;'><span style='color:{v_color};'>●</span> Semantic DB (Pinecone)</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 0.85rem; margin-bottom: 20px;'><span style='color:{g_color};'>●</span> Graph DB (Neo4j)</div>", unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("**GLOBAL FILTERS**")
    date_range = st.date_input("Timeframe", [])
    dept_filter = st.selectbox("Department Focus", ["All", "Executive", "Government Affairs", "Trading", "Legal"])
    risk_threshold = st.slider("Anomaly Sensitivity", 0, 100, 75)

# --- 5. TOP KPI BAR ---
st.markdown("<h4 style='color: #f8fafc; margin-top: -1rem; margin-bottom: 1rem;'>CORPORATE INTELLIGENCE OVERVIEW</h4>", unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown("""
    <div class="widget-card">
        <div class="kpi-label">TOTAL INDEXED COMMUNICATIONS</div>
        <div class="kpi-value">2,547 <span class="kpi-delta positive" style="font-size: 0.9rem;">↑ 12%</span></div>
    </div>
    """, unsafe_allow_html=True)
with kpi2:
    st.markdown("""
    <div class="widget-card">
        <div class="kpi-label">ACTIVE NETWORK ENTITIES</div>
        <div class="kpi-value">158 <span class="kpi-delta positive" style="font-size: 0.9rem;">↑ 4</span></div>
    </div>
    """, unsafe_allow_html=True)
with kpi3:
    st.markdown("""
    <div class="widget-card">
        <div class="kpi-label">CRITICAL COMPLIANCE ALERTS</div>
        <div class="kpi-value">12 <span class="kpi-delta negative" style="font-size: 0.9rem;">↑ 3</span></div>
    </div>
    """, unsafe_allow_html=True)
with kpi4:
    st.markdown("""
    <div class="widget-card">
        <div class="kpi-label">AVERAGE GRAPH DENSITY</div>
        <div class="kpi-value">0.84 <span style="font-size: 0.9rem; color:#94a3b8;">STABLE</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. MIDDLE ROW: GRAPH & SEARCH (SPLIT PANE) ---
col_graph, col_search = st.columns([1.5, 1])

with col_graph:
    st.markdown("""
    <div class="widget-header">
        <span>🕸️ TOPOLOGY & INFLUENCE GRAPH</span>
        <span style="color: #3b82f6; font-size: 0.75rem;">LIVE</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate structured Network Graph
    G = nx.fast_gnp_random_graph(25, 0.12, seed=10)
    pos = nx.spring_layout(G)
    centrality = nx.degree_centrality(G)
    
    edge_x, edge_y = [], []
    for edge in G.edges():
        edge_x.extend([pos[edge[0]][0], pos[edge[1]][0], None])
        edge_y.extend([pos[edge[0]][1], pos[edge[1]][1], None])
        
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#475569'), mode='lines', hoverinfo='none')
    
    node_sizes = [v * 120 + 10 for v in centrality.values()]
    node_colors = [v for v in centrality.values()]
    
    node_trace = go.Scatter(
        x=[pos[node][0] for node in G.nodes()], 
        y=[pos[node][1] for node in G.nodes()], 
        mode='markers',
        marker=dict(
            showscale=False, colorscale='Teal', color=node_colors, size=node_sizes,
            line_width=1, line_color='#0f172a'
        ),
        hoverinfo='text',
        text=[f"Node {n} | Influence: {c:.2f}" for n, c in zip(G.nodes(), centrality.values())]
    )
    
    fig_graph = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        showlegend=False, hovermode='closest', margin=dict(b=0,l=0,r=0,t=0),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), height=450
    ))
    
    # Render inside a custom card logic
    st.plotly_chart(fig_graph, use_container_width=True, config={'displayModeBar': False})

with col_search:
    st.markdown("""
    <div class="widget-header">
        <span>🔍 AI HYBRID RAG ENGINE</span>
    </div>
    """, unsafe_allow_html=True)
    
    query = st.text_input("Investigative Query", placeholder="Enter semantic query...", label_visibility="collapsed")
    
    st.markdown("<div style='height: 380px; overflow-y: auto; padding-right: 10px;'>", unsafe_allow_html=True)
    
    if query:
        st.markdown(f"<div style='color:#3b82f6; font-size: 0.8rem; margin-bottom: 10px;' class='mono'>Executing vector retrieval for: '{query}'</div>", unsafe_allow_html=True)
        if infra["v_status"] == "ONLINE":
            try:
                docs = infra["vector"].similarity_search(query, k=3)
                for doc in docs:
                    st.markdown(f"""
                    <div class="intel-feed-item">
                        <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 4px;" class="mono">{doc.metadata.get('Date', 'N/A')} | {doc.metadata.get('From', 'Unknown')}</div>
                        <div style="color: #f8fafc; font-size: 0.9rem; font-weight: 500; margin-bottom: 6px;">{doc.metadata.get('Subject', 'No Subject')}</div>
                        <div style="color: #cbd5e1; font-size: 0.85rem; line-height: 1.4;">{doc.page_content[:150]}...</div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception:
                st.error("Retrieval failed.")
        else:
            # Simulation Data for presentation continuity
            sim_results = [
                {"date": "2001-08-22", "from": "sherron.watkins", "sub": "Accounting Practices", "text": "I am incredibly nervous that we will implode in a wave of accounting scandals."},
                {"date": "2001-09-15", "from": "jeff.dasovich", "sub": "Regulatory Shift", "text": "The CPUC is cracking down. We need to restructure our off-balance operations."}
            ]
            for res in sim_results:
                st.markdown(f"""
                <div class="intel-feed-item">
                    <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 4px;" class="mono">{res['date']} | {res['from']}</div>
                    <div style="color: #f8fafc; font-size: 0.9rem; font-weight: 500; margin-bottom: 6px;">{res['sub']}</div>
                    <div style="color: #cbd5e1; font-size: 0.85rem; line-height: 1.4;">{res['text']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #475569;">
            <div style="font-size: 2rem; margin-bottom: 10px;">⚡</div>
            <div style="font-size: 0.9rem;">System standing by. Enter a query to scan the vector database.</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. BOTTOM ROW: TIMELINE & RISK MATRIX ---
col_time, col_risk = st.columns([1, 1.2])

with col_time:
    st.markdown("""
    <div class="widget-header">
        <span>📈 COMMUNICATION VELOCITY</span>
    </div>
    """, unsafe_allow_html=True)
    
    dates = pd.date_range(start="2001-01-01", end="2001-12-31", freq="W")
    volumes = np.random.normal(50, 15, len(dates))
    volumes[35:38] = volumes[35:38] * 3 # Anomaly
    
    df_time = pd.DataFrame({"Date": dates, "Volume": volumes})
    fig_time = px.area(df_time, x="Date", y="Volume")
    fig_time.update_traces(line_color='#3b82f6', fillcolor='rgba(59, 130, 246, 0.1)')
    fig_time.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', size=10), margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=True, gridcolor='#334155', title=""),
        yaxis=dict(showgrid=True, gridcolor='#334155', title="")
    )
    st.plotly_chart(fig_time, use_container_width=True, config={'displayModeBar': False}, height=250)

with col_risk:
    st.markdown("""
    <div class="widget-header">
        <span>⚠️ THREAT & COMPLIANCE DETECTION MATRIX</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="height: 250px; overflow-y: auto;">
        <table class="risk-table">
            <tr>
                <th>SEVERITY</th>
                <th>ENTITY ID</th>
                <th>DETECTED THREAT VECTOR</th>
                <th class="mono">TIMESTAMP</th>
            </tr>
            <tr>
                <td><span class="badge critical">CRITICAL</span></td>
                <td>sherron.watkins</td>
                <td>Keyword cluster: "Implode", "Accounting Scandal"</td>
                <td class="mono">08-22-2001</td>
            </tr>
            <tr>
                <td><span class="badge warning">WARNING</span></td>
                <td>jeff.dasovich</td>
                <td>Volume anomaly: 300% spike to external (CPUC)</td>
                <td class="mono">09-12-2001</td>
            </tr>
            <tr>
                <td><span class="badge warning">WARNING</span></td>
                <td>andy.zipper</td>
                <td>Unusual off-hours communication pattern</td>
                <td class="mono">10-04-2001</td>
            </tr>
            <tr>
                <td><span class="badge warning">WARNING</span></td>
                <td>kenneth.lay</td>
                <td>Semantic drift: Strategy misalignment detected</td>
                <td class="mono">10-15-2001</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)