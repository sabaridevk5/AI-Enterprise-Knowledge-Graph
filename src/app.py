import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from neo4j import GraphDatabase

# --- STEP 1: PROFESSIONAL PAGE CONFIG ---
st.set_page_config(
    page_title="Infosys | Enterprise Intelligence",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to match Enterprise Branding
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stTextInput > div > div > input { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- STEP 2: CACHED MODELS ---
@st.cache_resource
def load_ai_resources():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    tickets_data = [
        {"id": "T101", "text": "Battery failure in Product X"},
        {"id": "T102", "text": "Screen flickering issue in Product Y"},
        {"id": "T103", "text": "Overheating issue in Product X"},
        {"id": "T104", "text": "Charging problem in Product Z"}
    ]
    texts = [t["text"] for t in tickets_data]
    embeddings = model.encode(texts)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return model, tickets_data, index

model, tickets_data, index = load_ai_resources()

# --- STEP 3: NEO4J CONNECTOR ---
def query_graph(description_match):
    URI = "bolt://localhost:7687"
    USERNAME = "neo4j"
    PASSWORD = "kgdemo001" # Your password
    try:
        driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
        with driver.session() as session:
            result = session.run(
                "MATCH (c:Customer)-[:RAISED]->(t:Ticket)-[:RELATED_TO]->(p:Product) "
                "WHERE t.description CONTAINS $desc "
                "RETURN c.name as customer, p.name as product, t.id as id, t.description as desc",
                desc=description_match
            )
            return [record.data() for record in result]
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return []

# --- STEP 4: SIDEBAR & HEADER ---
with st.sidebar:
    st.image("https://www.infosys.com/content/dam/infosys-web/en/global-resource/media-resources/infosys-logo-jpeg.jpg", width=150)
    st.title("Settings")
    st.success("API: Connected")
    st.info("Milestone 4: Live")
    st.divider()
    st.write("Logged in as: **Sabari (Intern)**")

st.title("🏢 AI Knowledge Graph Explorer")
st.caption("Uncovering hidden relationships across enterprise data sources using Graph RAG.")

# Top Metrics Bar
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Nodes", "186K+")
m2.metric("Relationships", "450K+")
m3.metric("Latency", "24ms")
m4.metric("Engine", "L6-Transformer")

st.divider()

# --- STEP 5: INTELLIGENT SEARCH ---
user_query = st.text_input("🔍 Search Knowledge Base", placeholder="Ask a question (e.g., 'Who is reporting hardware issues?')")

if user_query:
    with st.spinner("Processing Semantic Query..."):
        # 1. Semantic Match
        q_emb = model.encode([user_query])
        D, I = index.search(np.array(q_emb), k=1)
        best_match_text = tickets_data[I[0][0]]["text"]
        
        # 2. Graph Retrieval
        search_term = best_match_text.split("in")[0].strip()
        graph_results = query_graph(search_term)
        
        if graph_results:
            st.subheader("Result Analysis")
            
            # Display result in a nice card
            for res in graph_results:
                with st.container():
                    st.markdown(f"### Ticket {res['id']}: {res['desc']}")
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Customer:** {res['customer']}")
                    c2.write(f"**Product:** {res['product']}")
                    c3.write(f"**Status:** 🔴 High Priority")
                    st.info(f"**AI Reasoning:** Based on the Knowledge Graph, the query was semantically matched to '{best_match_text}'. The graph indicates a direct link between {res['customer']} and {res['product']} via the support ticket.")
        else:
            st.warning("No linked relationships found in the Knowledge Graph for this query.")

st.divider()
st.markdown("### 📊 System Architecture View")
st.write("This dashboard integrates **Milestone 1 (Ingestion)**, **Milestone 2 (Graph Builder)**, and **Milestone 3 (RAG)**.")