# main.py

import os
import glob
from modules.loader import load_pdf
from modules.splitter import splitdocuments
from modules.embedder import get_embedding_model
from modules.vector_store import build_faiss_index, save_index
from fpdf import FPDF
from pptx import Presentation
from pptx.util import Inches, Pt

def prepare_index_from_directory(data_dir: str, index_path: str):
    """
    Ingestion complète : PDF → chunks → embeddings → FAISS index
    """
    print("🔄 Ingestion des documents depuis :", data_dir)

    all_documents = []

    #pdf_files = glob.glob(os.path.join(data_dir, "**", "*.pdf"), recursive=True)
    pdf_files = glob.glob(os.path.join("data", "**", "*.pdf"), recursive=True)


    print(f"📄 {len(pdf_files)} fichiers PDF trouvés.")

    for pdf_path in pdf_files:
        print(f"📥 Chargement : {pdf_path}")
        docs = load_pdf(pdf_path)
        all_documents.extend(docs)

    print(f"🧾 Total de pages extraites : {len(all_documents)}")

    chunks = splitdocuments(all_documents)
    print(f" Total de chunks générés : {len(chunks)}")

    embedder = get_embedding_model()
    index = build_faiss_index(chunks, embedder)
    save_index(index, index_path)

    print("✅ Index vectoriel FAISS créé et sauvegardé avec succès.")
    



if __name__ == "__main__":
    DATA_DIR = "data"
    INDEX_PATH = "vector_store/propales_index"
    prepare_index_from_directory(DATA_DIR, INDEX_PATH)
