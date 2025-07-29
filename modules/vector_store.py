# modules/vector_store.py

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import os
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS

from modules.loader import load_pdf
from .embedder import get_embedding_model
import datetime
from fpdf import FPDF


def build_faiss_index(documents: list[Document], embedding_model: HuggingFaceEmbeddings) -> FAISS:
    """
    Crée un index FAISS à partir des chunks vectorisés.
    """
    return FAISS.from_documents(documents, embedding_model) 
    #vectorise tous les documents (chunks) automatiquement
    #stocke dans un index FAISS les vecteurs + le contenu texte original

def save_index(index: FAISS, path: str):
    """
    Sauvegarde l’index FAISS localement.
    """
    index.save_local(path)

def load_index(path: str, embedding_model: HuggingFaceEmbeddings) -> FAISS:
    """
    Recharge un index FAISS depuis le disque, avec validation explicite de la désérialisation.
    """
    return FAISS.load_local(
        path,
        embedding_model,
        allow_dangerous_deserialization=True  
    )




def store_generated_proposal(proposal_text: str, index_path: str, metadata: dict = None):
    """
    Sauvegarde une proposition générée en PDF et dans l’index FAISS.
    """
    if metadata is None:
        metadata = {}

    output_dir = "data/generated"
    os.makedirs(output_dir, exist_ok=True)
    print("📁 Dossier créé ou déjà existant :", output_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"propale_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    # Sauvegarde en PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in proposal_text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf.output(filepath)
    print(f"✅ PDF sauvegardé dans : {filepath}")

    # Lecture du PDF et ajout à l'index FAISS
    doc = load_pdf(filepath)[0]
    doc.metadata.update(metadata)
    doc.metadata["source"] = filename
    doc.metadata["generated_at"] = datetime.datetime.now().isoformat()

    embedder = get_embedding_model()

    try:
        index = FAISS.load_local(index_path, embedder, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"⚠️ FAISS index introuvable. Nouveau créé. Raison : {e}")
        index = FAISS.from_documents([], embedder)

    index.add_documents([doc])
    index.save_local(index_path)

    print("💾 Propale indexée et sauvegardée FAISS.")
    return filepath

