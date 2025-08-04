from sentence_transformers import SentenceTransformer, util
from difflib import SequenceMatcher
from typing import List, Tuple
from collections import Counter
import re
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from modules.llm_groq import get_llm
from modules.prompt_template import get_proposal_prompt_template

# Modèle pour embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_without_docs(query: str, model: str = "llama3-8b-8192") -> str:
    llm = get_llm(model)
    prompt = f"Rédige une proposition commerciale détaillée EN FRANCAIS en réponse à la demande suivante :\n{query}"
    response = llm.invoke(prompt)
    return response.content if hasattr(response, 'content') else str(response)

def compute_similarity(text1: str, text2: str) -> float:
    emb1 = embedding_model.encode(text1, convert_to_tensor=True)
    emb2 = embedding_model.encode(text2, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2)
    return score.item()

def compute_chunk_coverage(rag_text: str, top_chunks: List[Tuple]) -> float:
    matched_chars = 0
    total_chars = len(rag_text)
    for doc, _ in top_chunks:
        matcher = SequenceMatcher(None, rag_text, doc.page_content)
        match = matcher.find_longest_match(0, len(rag_text), 0, len(doc.page_content))
        matched_chars += match.size
    return matched_chars / total_chars if total_chars > 0 else 0

def highlight_with_chunks(rag_text: str, chunks: List[Tuple], threshold: float = 0.8) -> str:
    highlighted = rag_text
    for chunk, _ in chunks:
        chunk_text = chunk.page_content.strip()
        if not chunk_text:
            continue
        matcher = SequenceMatcher(None, rag_text.lower(), chunk_text.lower())
        match = matcher.find_longest_match(0, len(rag_text), 0, len(chunk_text))
        if match.size > 20:
            matched_str = rag_text[match.a: match.a + match.size]
            highlighted = highlighted.replace(
                matched_str,
                f"<mark style='background-color: #fffa9e;'>{matched_str}</mark>"
            )
    return highlighted

# --- Nouveaux : ngram overlap & semantic similarity chunk par chunk ---

def preprocess_text(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    tokens = text.split()
    return tokens

def ngrams(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
    return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def ngram_overlap(reference: str, candidate: str, n: int = 3) -> float:
    ref_tokens = preprocess_text(reference)
    cand_tokens = preprocess_text(candidate)
    ref_ngrams = Counter(ngrams(ref_tokens, n))
    cand_ngrams = Counter(ngrams(cand_tokens, n))
    if not ref_ngrams:
        return 0.0
    overlap_ngrams = sum((ref_ngrams & cand_ngrams).values())
    total_ngrams = sum(ref_ngrams.values())
    return overlap_ngrams / total_ngrams if total_ngrams > 0 else 0.0

def compute_ngram_overlap_for_chunks(rag_text: str, chunks: List[Tuple], n: int = 3) -> List[Tuple[int, float]]:
    """
    Calcule le recouvrement n-gram (n=3 par défaut) entre rag_text et chaque chunk.
    Retourne une liste de tuples (index_chunk, score_overlap).
    """
    overlaps = []
    for i, (chunk, _) in enumerate(chunks):
        overlap = ngram_overlap(rag_text, chunk.page_content, n=n)
        overlaps.append((i, overlap))
    return overlaps

def semantic_similarity_chunks_response(rag_text: str, chunks: List[Tuple]) -> List[Tuple[int, float]]:
    """
    Calcule la similarité cosinus entre rag_text et chaque chunk (embedding).
    Retourne une liste de tuples (index_chunk, score_similarity).
    """
    chunk_texts = [chunk.page_content for chunk, _ in chunks]
    chunk_embeddings = embedding_model.encode(chunk_texts, convert_to_numpy=True, normalize_embeddings=True)
    rag_embedding = embedding_model.encode([rag_text], convert_to_numpy=True, normalize_embeddings=True)
    sims = cosine_similarity(chunk_embeddings, rag_embedding).flatten()
    return list(enumerate(sims))

# Exemple d’utilisation (à adapter selon ta pipeline)

def evaluate_rag_vs_llm(rag_response: str, llm_response: str, top_chunks: List[Tuple]):
    print("=== Similarité sémantique entre RAG et LLM seul ===")
    sim = compute_similarity(rag_response, llm_response)
    print(f"Similarity score: {sim:.4f}")

    print("\n=== Couverture chunks dans la réponse RAG ===")
    coverage = compute_chunk_coverage(rag_response, top_chunks)
    print(f"Chunk coverage: {coverage:.4%}")

    print("\n=== Recouvrement n-gram par chunk ===")
    ngram_overlaps = compute_ngram_overlap_for_chunks(rag_response, top_chunks)
    for idx, score in ngram_overlaps:
        print(f"Chunk #{idx} : {score:.4f}")

    print("\n=== Similarité sémantique par chunk ===")
    semantic_sims = semantic_similarity_chunks_response(rag_response, top_chunks)
    for idx, score in semantic_sims:
        print(f"Chunk #{idx} : {score:.4f}")

    print("\n=== Texte RAG avec surbrillance des chunks ===")
    highlighted = highlight_with_chunks(rag_response, top_chunks)
    print(highlighted)

    return {
        "similarity_llm_rag": sim,
        "chunk_coverage": coverage,
        "ngram_overlaps": ngram_overlaps,
        "semantic_similarities": semantic_sims,
        "highlighted_text": highlighted
    }
