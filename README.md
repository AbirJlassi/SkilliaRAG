# Skillia RAG – Proposal Generation Platform


##  Overview
**Skillia RAG** is an internal platform that leverages **Retrieval-Augmented Generation (RAG)** to automatically generate business proposals. It fuses the organization’s knowledge base with a Large Language Model (LLM) to produce high-quality, consistent, and client-oriented documents.

This project was developed during a summer internship at **Skillia** to improve the efficiency and standardization of proposal creation while reusing past work.

---

## Features
- **Document Management** – Upload and manage internal proposals, reports, and deliverables.
- **Taxonomy-based Annotation** – Automatic tagging with a unified taxonomy (sector, scope, technology).
- **RAG Pipeline** – Vector retrieval + LLM generation for context-aware drafting.
- **Interactive Streamlit UI** – Simple, intuitive interface for consultants.
- **Export Options** – Generate and download **PDF** or **PPTX**.
- **Performance Metrics** - Tracks RAG's performance metrics (Relevance score, Response Quality..)
---

##  Architecture
The platform is modular:

1. **Document Loader** → Uploads and parses PDFs.
2. **Splitter** → Splits documents into sections/chunks.
3. **Embedder** → Builds vector embeddings via open-source models.
4. **Vector Store (FAISS)** → Efficient similarity search.
5. **RAG Core** → Orchestrates retrieval + LLM generation.
6. **Metrics Module** → Saves response quality metrics.
7. **Streamlit Frontend** → Interactive UI.

Flow:
User Query → Retriever (FAISS) → Context → LLM → Draft Proposal → Export/Feedback

---
## ⚙️ Tech Stack
- **Language**: Python
- **Frameworks & Libraries**:
  - LangChain – RAG orchestration
  - FAISS – Vector similarity search
  - Hugging Face – Embeddings 
  - Streamlit – Web UI
  - FPDF / python-pptx – Export to PDF & PPTX
- **LLMs**: OpenAI(gpt3.5)
- **Storage**: Local filesystem + FAISS index
---

## 📂 Project Structure
SkilliaRAG/
│── app.py # Main Streamlit app
│── main.py # Index preparation and initialization
│── requirements.txt
│
├── modules/ # Core logic
│ ├── loader.py # PDF loader
│ ├── splitter.py # Text splitting
│ ├── embedder.py # Embedding models
│ ├── vector_store.py # FAISS index mgmt
│ ├── rag_core.py # Full RAG pipeline
│ ├── feedback.py # Feedback handling
│
├── data/ # Uploaded & generated docs
├── vector_store/ # FAISS indexes
└── README.md 

## ▶️ Quickstart

### 1) Clone the repository
```bash
git clone https://github.com/<your-org>/SkilliaRAG.git
cd SkilliaRAG

