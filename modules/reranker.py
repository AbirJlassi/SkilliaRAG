# modules/re_ranker.py

from sentence_transformers import CrossEncoder
from langchain.schema import Document
from typing import List, Tuple

# Charge un modèle CrossEncoder (précis et rapide)
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query: str, documents: List[Document], top_k: int = 4) -> List[Tuple[Document, float]]:
    """
    Classe les documents selon leur pertinence avec la requête via CrossEncoder.
    Retourne les top_k meilleurs documents avec leur score.
    """
    pairs = [(query, doc.page_content) for doc in documents]
    scores = reranker.predict(pairs)

    # Associe chaque document à son score
    doc_scores = list(zip(documents, scores))

    # Trie par score décroissant
    doc_scores.sort(key=lambda x: x[1], reverse=True)

    return doc_scores[:top_k]
