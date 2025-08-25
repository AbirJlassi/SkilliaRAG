# Skillia RAG – Proposal Generation Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-green)
![License](https://img.shields.io/badge/License-MIT-black)

## 📌 Overview
**Skillia RAG** is an internal platform that leverages **Retrieval-Augmented Generation (RAG)** to automatically generate business proposals and deliverables. It fuses your organization’s knowledge base with a Large Language Model (LLM) to produce high-quality, consistent, and client-oriented documents.

This project was developed during a summer internship at **Skillia** to improve the efficiency and standardization of proposal creation while reusing past work.

---

## 🚀 Features
- **Document Management** – Upload and manage internal proposals, reports, and deliverables.
- **Taxonomy-based Annotation** – Automatic tagging with a unified taxonomy (sector, scope, technology).
- **RAG Pipeline** – Vector retrieval + LLM generation for context-aware drafting.
- **Section-Aware Retrieval** – Retrieves only the relevant sections (e.g., “finance sector case studies”).
- **Dynamic Variables Extraction** – Detects client name, project duration, daily rate, etc.
- **Interactive Streamlit UI** – Simple, intuitive interface for consultants.
- **Export Options** – Generate and download **PDF** or **PPTX**.
- **Feedback Loop** – Store outputs and user feedback to continuously improve (feed-forward learning).

---

## 🏗️ Architecture
The platform is modular:

1. **Document Loader** → Uploads and parses PDFs.
2. **Splitter** → Splits documents into sections/chunks.
3. **Embedder** → Builds vector embeddings via open-source models.
4. **Vector Store (FAISS)** → Efficient similarity search.
5. **RAG Core** → Orchestrates retrieval + LLM generation.
6. **Feedback Module** → Collects user evaluations and saves outputs.
7. **Streamlit Frontend** → Interactive UI.

High-level flow:
