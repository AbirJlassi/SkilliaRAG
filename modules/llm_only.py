# modules/llm_only.py
from sentence_transformers import SentenceTransformer, util

from modules.llm_groq import get_llm
from modules.prompt_template import get_proposal_prompt_template


def generate_without_docs(query: str, model: str = "llama3-8b-8192") -> str:
    """
    Génère une propale sans contexte, juste avec la requête utilisateur.
    """
    llm = get_llm(model)

    # Prompt très simple sans template structuré
    prompt = f"Rédige une proposition commerciale détaillée EN FRANCAIS en réponse à la demande suivante :\n{query}"

    response = llm.invoke(prompt)

    # Si c'est un AIMessage, retourne juste le contenu
    return response.content if hasattr(response, 'content') else str(response)

#Calculate similarity between two texts using Sentence Transformers
model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_similarity(text1: str, text2: str) -> float:
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2)
    return score.item()  # Retourne un float


from difflib import SequenceMatcher

def compute_chunk_coverage(rag_text, top_chunks):
    matched_chars = 0
    total_chars = len(rag_text)

    for doc, _ in top_chunks:
        matcher = SequenceMatcher(None, rag_text, doc.page_content)
        match = matcher.find_longest_match(0, len(rag_text), 0, len(doc.page_content))
        matched_chars += match.size

    return matched_chars / total_chars if total_chars > 0 else 0


def highlight_with_chunks(rag_text: str, chunks, threshold: float = 0.8) -> str:
    """
    Met en surbrillance les passages du texte RAG similaires aux chunks utilisés.
    """
    highlighted = rag_text
    for chunk, _ in chunks:
        chunk_text = chunk.page_content.strip()
        if not chunk_text:
            continue

        # Cherche des correspondances proches dans le texte généré
        matcher = SequenceMatcher(None, rag_text.lower(), chunk_text.lower())
        match = matcher.find_longest_match(0, len(rag_text), 0, len(chunk_text))
        
        if match.size > 20:  # ignorer les trop petits bouts
            matched_str = rag_text[match.a: match.a + match.size]
            highlighted = highlighted.replace(
                matched_str,
                f"<mark style='background-color: #fffa9e;'>{matched_str}</mark>"
            )

    return highlighted
