# modules/embedder.py

from sentence_transformers import SentenceTransformer # type: ignore
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import Any

def get_embedding_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> Any:
    """
    Retourne un encodeur de type HuggingFace compatible LangChain.
    """
    return HuggingFaceEmbeddings(model_name=model_name) # type: ignore
