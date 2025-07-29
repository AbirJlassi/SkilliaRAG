# modules/loader.py
from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain.schema import Document
import os

def load_pdf(path: str) -> List[Document]:
    """
    Charge un PDF et ajoute un champ 'source' au metadata pour identifier le document.
    """
    loader = PyPDFLoader(path)
    docs = loader.load()

    # Ajoute une clé 'source' dans les métadonnées
    source_name = os.path.basename(path)
    for doc in docs:
        doc.metadata["source"] = source_name

    return docs