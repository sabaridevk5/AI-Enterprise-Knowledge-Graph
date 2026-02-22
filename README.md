

```markdown
# 🛡️ AI-Powered Enterprise Knowledge Graph for Semantic Search

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-018bff.svg)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-000000.svg)
![LangChain](https://img.shields.io/badge/LangChain-AI-1C3C3C.svg)

## 📌 Project Overview
This project is an advanced **Hybrid Retrieval-Augmented Generation (RAG) System** designed to analyze corporate communications (specifically utilizing the Enron Email Corpus). It bridges the gap between unstructured text data and structured relationship mapping. 

By combining **Semantic Search** (via Pinecone vector embeddings) with **Graph Discovery** (via Neo4j), this intelligence portal allows investigators to not only find specific conversations based on context but also instantly visualize the network topology of the entities involved.

## ✨ Key Features
* **Hybrid Intelligence:** Merges Vector similarities (what was said) with Graph topologies (who talks to whom).
* **Semantic Vector Retrieval:** Uses HuggingFace `all-MiniLM-L6-v2` embeddings stored in Pinecone to retrieve highly relevant emails based on conversational context, not just keyword matching.
* **Dynamic Network Topology:** Interactive Knowledge Graph powered by NetworkX and Plotly. The graph dynamically rebuilds itself to center around the entities mentioned in your search query.
* **AI Context Extractor:** Automatically highlights the primary investigative context of retrieved documents.
* **Enterprise-Grade UI:** A sleek, responsive, and secure command-center dashboard built with Streamlit.

## 🏗️ Architecture & Pipeline
The project is built on a structured data engineering pipeline:
1. **Milestone 1 (Preprocessing):** Cleaning, parsing, and formatting raw Enron email data into structured datasets.
2. **Milestone 2 (Graph Build):** Extracting entities (Sender, Receiver) and relationships to populate the Neo4j Graph Database.
3. **Milestone 3 & 4 (Vectorization):** Generating semantic embeddings for email bodies and pushing them to the Pinecone Cloud Vector index.
4. **Application Layer:** A Streamlit web application acting as the unified interface for both databases.

## 📂 Repository Structure
```text
├── data/                       # Processed Enron CSV/JSON datasets
├── src/                        # Data engineering pipeline scripts
│   ├── milestone1_preprocessing.py
│   ├── milestone2_graph_build.py
│   ├── milestone3_semantic_search.py
│   └── m4_upload_to_pinecone.py
├── app.py                      # Main Streamlit dashboard application
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation

```

## 🚀 Deployment & Installation

**1. Clone the repository**

```bash
git clone [https://github.com/yourusername/AI-Enterprise-Knowledge-Graph.git](https://github.com/yourusername/AI-Enterprise-Knowledge-Graph.git)
cd AI-Enterprise-Knowledge-Graph

```

**2. Install dependencies**

```bash
pip install -r requirements.txt

```

**3. Environment & Cloud Secrets Management**
To comply with enterprise security standards, API keys and database URIs are strictly excluded from the codebase.

* **For Cloud Deployment (Streamlit Community Cloud):** Navigate to your app's **Advanced Settings > Secrets** and securely inject your environment variables using the TOML format:
```toml
PINECONE_API_KEY = "your_pinecone_key_here"
NEO4J_URI = "bolt+s://your_neo4j_uri"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_neo4j_password"

```


* **For Local Execution:** The application is configured to safely default to a local/simulation mode if cloud secrets are not detected in the environment, preventing accidental credential leaks during testing.

**4. Run the Application**

```bash
streamlit run app.py

```

## 🔍 Usage Examples

Once the dashboard is running, try entering the following investigative queries into the search bar:

* *"natural gas market analysis and trading"*
* *"accounting irregularities sherron watkins"*
* *"california energy crisis regulations"*

## 🛠️ Technology Stack

* **Frontend & Visualization:** Streamlit, Plotly, HTML/CSS
* **AI/NLP:** LangChain, HuggingFace Transformers
* **Databases:** Pinecone (Vector Database), Neo4j AuraDB (Graph Database)
* **Data Processing:** Pandas, NumPy, NetworkX

---

*Developed for Enterprise Analytics & Information Retrieval.*

```
