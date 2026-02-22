# app.py - SIMPLEST UI

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import networkx as nx
import time

st.set_page_config(page_title="Enron Graph", layout="wide")

# Simple CSS
st.markdown("""
<style>
    * { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 0; }
    .stApp { background: #f5f5f5; }
    .main { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    h1 { font-size: 2rem; font-weight: 400; color: #333; margin-bottom: 2rem; }
    .search-box { background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 2rem; }
    .graph-box { background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1rem; }
    .detail-box { background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main">', unsafe_allow_html=True)

# Simple title
st.markdown("<h1>🔍 Enron Graph Search</h1>", unsafe_allow_html=True)

# Simple search
st.markdown('<div class="search-box">', unsafe_allow_html=True)
col1, col2 = st.columns([4,1])
with col1:
    query = st.text_input("", placeholder="e.g., jeff dasovich energy trading", label_visibility="collapsed")
with col2:
    search = st.button("Search", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Simple graph data
G = nx.Graph()
edges = [
    ("jeff.dasovich", "kenneth.lay", 47),
    ("jeff.dasovich", "jeff.skilling", 38),
    ("kenneth.lay", "sherron.watkins", 25),
    ("jeff.skilling", "greg.whalley", 22),
]
for src, tgt, w in edges:
    G.add_edge(src, tgt, weight=w)

# Simple entity mapping
entity_info = {
    "jeff.dasovich": {"role": "Gov. Affairs", "emails": 47, "topics": "Energy"},
    "kenneth.lay": {"role": "CEO", "emails": 42, "topics": "Executive"},
    "jeff.skilling": {"role": "COO", "emails": 38, "topics": "Trading"},
    "sherron.watkins": {"role": "VP", "emails": 25, "topics": "Accounting"},
}

# Determine current entity from query
current_entity = "jeff.dasovich"
if query and search:
    if "kenneth" in query.lower() or "lay" in query.lower():
        current_entity = "kenneth.lay"
    elif "sherron" in query.lower() or "watkins" in query.lower():
        current_entity = "sherron.watkins"
    elif "skilling" in query.lower():
        current_entity = "jeff.skilling"

# Graph section
st.markdown('<div class="graph-box">', unsafe_allow_html=True)
st.markdown("**Network Graph**")

if len(G.nodes()) > 0:
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Edges
    edge_trace = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        color = '#3b82f6' if current_entity in [edge[0], edge[1]] else '#ddd'
        edge_trace.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode='lines', line=dict(width=2, color=color),
            hoverinfo='none'
        ))
    
    # Nodes
    node_x, node_y, node_color, node_size = [], [], [], []
    for node in G.nodes():
        node_x.append(pos[node][0])
        node_y.append(pos[node][1])
        node_color.append('#ef4444' if node == current_entity else '#888')
        node_size.append(30 if node == current_entity else 20)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        text=list(G.nodes()), textposition="top center",
        marker=dict(size=node_size, color=node_color, line=dict(width=1, color='white'))
    )
    
    fig = go.Figure(
        data=edge_trace + [node_trace],
        layout=go.Layout(
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='white'
        )
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
st.markdown('</div>', unsafe_allow_html=True)

# Simple details
st.markdown('<div class="detail-box">', unsafe_allow_html=True)
st.markdown("**Entity Details**")

info = entity_info.get(current_entity, entity_info["jeff.dasovich"])
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"**Name**  \n{current_entity}")
with col2:
    st.markdown(f"**Role**  \n{info['role']}")
with col3:
    st.markdown(f"**Emails**  \n{info['emails']}")
with col4:
    st.markdown(f"**Topics**  \n{info['topics']}")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)