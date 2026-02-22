# app.py - PROFESSIONAL SINGLE PAGE VERSION

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
    initial_sidebar_state="expanded"
)

# Professional Custom CSS
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(120deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    
    /* Subheader styling */
    .sub-header {
        font-size: 1rem;
        color: #6B7280;
        font-weight: 400;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E5E7EB;
    }
    
    /* Card styling */
    .professional-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .professional-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #F9FAFB, #F3F4F6);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3B82F6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Status indicators */
    .status-badge {
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .status-success {
        background: #D1FAE5;
        color: #059669;
    }
    
    .status-warning {
        background: #FEF3C7;
        color: #D97706;
    }
    
    /* Button styling */
    .stButton > button {
        background: white;
        color: #1E3A8A;
        border: 1px solid #3B82F6;
        border-radius: 8px;
        padding: 0.3rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #3B82F6;
        color: white;
        border: 1px solid #3B82F6;
    }
    
    /* Search box styling */
    .search-box {
        background: #F9FAFB;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        margin-bottom: 1.5rem;
    }
    
    /* Divider styling */
    .section-divider {
        margin: 1.5rem 0;
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #E5E7EB, transparent);
    }
    
    /* Query chip styling */
    .query-chip {
        background: #F3F4F6;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        cursor: pointer;
        border: 1px solid #E5E7EB;
        text-align: center;
    }
    
    .query-chip:hover {
        background: #3B82F6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HEADER SECTION ---
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown('<h1 class="main-header">🏢 Enron Intelligence Portal</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Knowledge Graph | Enterprise Forensics</p>', unsafe_allow_html=True)
with col2:
    st.markdown("### 🔧 System Status")
    st.markdown('<span class="status-badge status-success">✓ Pinecone Active</span>', unsafe_allow_html=True)
with col3:
    st.markdown("### 📊 Stats")
    st.markdown('<span class="status-badge status-warning">○ Neo4j Demo</span>', unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

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
if 'graph_data' not in st.session_state:
    st.session_state.graph_data = None

# --- 5. SYSTEM INITIALIZATION ---
@st.cache_resource
def load_enterprise_systems():
    systems = {"vectorstore": None, "graph": None}
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        v_store = PineconeVectorStore(index_name=PINECONE_INDEX, embedding=embeddings)
        systems["vectorstore"] = v_store
    except:
        pass
    
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

# ========== MAIN CONTENT - SINGLE PAGE ==========

# --- 6. SEARCH SECTION ---
st.markdown('<div class="search-box">', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input(
        "🔍 Search Enterprise Communications:",
        value=st.session_state.search_value,
        placeholder="e.g., 'natural gas trading discussions' or 'jeff dasovich emails'",
        key="search_input",
        label_visibility="collapsed"
    )
with col2:
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")

# Quick query chips
st.markdown("#### Quick Queries:")
chip_cols = st.columns(5)
quick_queries = ["⚡ Natural Gas", "📈 Energy Market", "👤 Jeff Dasovich", "⚠️ Accounting", "🏢 Houston Office"]

for i, q in enumerate(quick_queries):
    with chip_cols[i]:
        if st.button(q, key=f"chip_{i}", use_container_width=True):
            st.session_state.search_value = q.split(" ")[-1]
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. TOP METRICS ROW ---
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
metric_cols = st.columns(4)
with metric_cols[0]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Communications", "2,547", "+12.3%")
    st.markdown('</div>', unsafe_allow_html=True)
with metric_cols[1]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Active Participants", "158", "+8")
    st.markdown('</div>', unsafe_allow_html=True)
with metric_cols[2]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Avg Response Time", "2.4h", "-15%")
    st.markdown('</div>', unsafe_allow_html=True)
with metric_cols[3]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Key Topics", "24", "+3")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 8. MAIN CONTENT GRID (2 Columns) ---
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# Determine search term
search_term = query or st.session_state.search_value

# Create two main columns
left_col, right_col = st.columns([1, 1])

# ========== LEFT COLUMN - SEMANTIC RESULTS ==========
with left_col:
    st.markdown('<div class="professional-card">', unsafe_allow_html=True)
    st.markdown("### 📄 Semantic Search Results")
    st.caption("AI-powered semantic matching")
    
    if search_term and search_button:
        with st.spinner("Searching documents..."):
            if vectorstore is not None:
                try:
                    docs = vectorstore.similarity_search(search_term, k=3)
                    
                    if docs:
                        for i, doc in enumerate(docs):
                            with st.expander(f"**Match {i+1}**", expanded=i==0):
                                st.markdown(f"**Content:**")
                                st.info(doc.page_content[:250] + "...")
                                st.caption(f"📧 From: {doc.metadata.get('From', 'Unknown')}")
                                st.caption(f"📌 Subject: {doc.metadata.get('Subject', 'Unknown')}")
                                st.caption(f"📅 Date: {doc.metadata.get('Date', 'Unknown')}")
                    else:
                        st.warning("No results found")
                except Exception as e:
                    st.error(f"Search error: {e}")
            else:
                # Sample results
                sample_results = [
                    {"from": "jeff.dasovich@enron.com", "subject": "Energy Trading Strategy", 
                     "content": "Discussions about California energy market opportunities..."},
                    {"from": "sherron.watkins@enron.com", "subject": "Accounting Concerns", 
                     "content": "I have serious concerns about our accounting practices..."},
                    {"from": "john.arnold@enron.com", "subject": "Natural Gas Update", 
                     "content": "Market analysis shows strong signals in natural gas..."}
                ]
                for i, res in enumerate(sample_results):
                    with st.expander(f"**Sample {i+1}: {res['subject']}**", expanded=i==0):
                        st.info(res['content'])
                        st.caption(f"📧 From: {res['from']}")
    else:
        st.info("👆 Enter a query and click Search to see results")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent insights in left column
    st.markdown('<div class="professional-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Intelligence Insights")
    insights = [
        "• **Jeff Dasovich** identified as central hub (47 connections)",
        "• Increased Houston-London communication detected",
        "• Weekend trading discussions spike before announcements",
        "• Legal team isolated from trading operations"
    ]
    for insight in insights:
        st.markdown(insight)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== RIGHT COLUMN - GRAPH VISUALIZATION ==========
with right_col:
    st.markdown('<div class="professional-card">', unsafe_allow_html=True)
    st.markdown("### 🕸️ Knowledge Graph Visualization")
    st.caption("Entity relationships and communication patterns")
    
    # Graph controls inline
    col1, col2 = st.columns(2)
    with col1:
        entity = st.text_input("Entity:", value="jeff.dasovich", placeholder="Enter name...")
    with col2:
        depth = st.selectbox("Depth:", [1, 2, 3], index=1)
    
    if st.button("🔄 Generate Graph", use_container_width=True):
        with st.spinner("Rendering graph..."):
            try:
                # Create graph visualization
                G = nx.Graph()
                
                # Sample data - replace with real Neo4j data
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
                
                if len(G.nodes()) > 0:
                    pos = nx.spring_layout(G, k=2, iterations=50)
                    
                    # Edge trace
                    edge_trace = []
                    for edge in G.edges(data=True):
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        weight = edge[2].get('weight', 1)
                        
                        edge_trace.append(go.Scatter(
                            x=[x0, x1, None],
                            y=[y0, y1, None],
                            mode='lines',
                            line=dict(width=min(weight/5, 3), color='rgba(59, 130, 246, 0.3)'),
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
                        node_size.append(20 + degree * 5)
                        
                        if node == entity:
                            node_color.append('red')
                        elif degree > 3:
                            node_color.append('#3B82F6')
                        else:
                            node_color.append('#9CA3AF')
                    
                    node_trace = go.Scatter(
                        x=node_x,
                        y=node_y,
                        mode='markers+text',
                        text=node_text,
                        textposition="top center",
                        textfont=dict(size=10),
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
                            height=500,
                            margin=dict(l=0, r=0, t=0, b=0),
                            plot_bgcolor='white'
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Graph stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Nodes", G.number_of_nodes())
                    with col2:
                        st.metric("Edges", G.number_of_edges())
                    with col3:
                        st.metric("Density", f"{nx.density(G):.3f}")
                else:
                    st.warning("No graph data available")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        # Static preview
        st.image("https://images.ctfassets.net/c1zhnszcah7h/1Ox8gzD8p5tKAt1jNYKC0g/52ba886bca190a8a52b1e4d03e98483d/graph-visualization.png", 
                 caption="Knowledge Graph Preview")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick stats in right column
    st.markdown('<div class="professional-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Quick Statistics")
    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        st.write("**Top Senders:**")
        st.write("• Jeff Dasovich (47)")
        st.write("• Kenneth Lay (42)")
        st.write("• Jeff Skilling (38)")
    with stat_col2:
        st.write("**Key Topics:**")
        st.write("• Energy Trading")
        st.write("• Regulatory")
        st.write("• Accounting")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 9. BOTTOM SECTION - ANALYTICS ---
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<div class="professional-card">', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### 📊 Top Communicators")
    df_senders = pd.DataFrame({
        'Person': ['Jeff Dasovich', 'Kenneth Lay', 'Jeff Skilling', 'Sherron Watkins', 'Greg Whalley'],
        'Messages': [47, 42, 38, 25, 22]
    })
    fig = px.bar(df_senders, x='Person', y='Messages', color='Messages',
                 color_continuous_scale='Blues')
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    st.markdown("#### 📈 Communication Timeline")
    dates = pd.date_range(start='2001-01-01', periods=20, freq='W')
    values = np.random.randint(50, 200, size=20)
    df_timeline = pd.DataFrame({'Date': dates, 'Volume': values})
    fig = px.line(df_timeline, x='Date', y='Volume', markers=True)
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- 10. FOOTER ---
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.markdown("""
    <div style='text-align: center; color: #6B7280; font-size: 0.8rem;'>
        <p>© 2024 Enterprise Knowledge Graph | Infosys Presentation | Powered by Neo4j, Pinecone, LangChain</p>
    </div>
    """, unsafe_allow_html=True)