# AI-Powered Enterprise Knowledge Graph

An end-to-end data engineering project focused on building a **Knowledge Graph** for the Enron Email Dataset to uncover hidden organizational relationships and enable **Intelligence Search**.

## 🛠️ Technology Stack
- **Database:** Neo4j (Graph Database)
- **Search Engine:** FAISS (Vector Indexing)
- **AI Model:** Hugging Face `all-MiniLM-L6-v2` (Semantic Embeddings)
- **Orchestration:** Python-based ETL Pipeline

## 📈 Milestones
### Milestone 1: Automated Ingestion
- Processed 495k+ unstructured email records.
- Implemented data cleansing to remove `NaN` and artifacts, creating a "Silver" CSV staging layer.

### Milestone 2: Graph Construction
- Mapped email communications into a Graph Schema (Nodes: `Person`, Edges: `EMAILED`).
- Built corporate hierarchies in **Neo4j** to visualize "hidden relationships".

### Milestone 3: Intelligence Search (GraphRAG)
- Integrated **Hugging Face** transformers to convert email text into semantic vectors.
- Developed an interactive **Intelligence Search** tool that combines Vector Retrieval (FAISS) with Graph Context (Neo4j).

## ⚙️ How to Run
1. Start your **Neo4j** instance.
2. Run `python src/m1_preprocessing.py` to stage data.
3. Run `python src/m2_graph_build.py` to populate the graph.
4. Run `python src/m3_semantic_search.py` for intelligence search.
