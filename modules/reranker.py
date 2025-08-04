from sentence_transformers import CrossEncoder
from langchain.schema import Document
from typing import List
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Choisir un modèle puissant et compatible
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def normalize_scores(scores):
    scaler = MinMaxScaler()
    return scaler.fit_transform(np.array(scores).reshape(-1, 1)).flatten().tolist()

def boost_score(doc: Document, score: float) -> float:
    boost_keywords = ["objectif", "sécurité", "gestion de crise", "exercice simulé"]
    content = doc.page_content.lower()
    boost = sum(1 for kw in boost_keywords if kw in content)
    return score + 0.05 * boost

def rerank(query: str, documents: List[Document], top_k: int = 4, min_score: float = 0.3) -> List[Document]:
    pairs = [(query, doc.page_content) for doc in documents]
    scores = reranker.predict(pairs)
    scores = normalize_scores(scores)

    doc_scores = [(doc, boost_score(doc, score)) for doc, score in zip(documents, scores)]
    filtered = [(doc, score) for doc, score in doc_scores if score >= min_score]
    filtered.sort(key=lambda x: x[1], reverse=True)

    for doc, score in filtered:
        doc.metadata["cross_score"] = score

    return filtered[:top_k]  # ✅ une liste de (Document, score)

