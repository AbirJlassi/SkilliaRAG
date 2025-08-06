from sentence_transformers import SentenceTransformer, util
from difflib import SequenceMatcher
from typing import List, Tuple
from collections import Counter
import re
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from modules.llm_groq import get_llm
from modules.prompt_template import get_proposal_prompt_template
from typing import List
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
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



#--------------------------------------------------------
#COMPUTING chunk coverage based on semantic similarity
#--------------------------------------------------------


embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def compute_chunk_coverage(generated_text: str, chunks: List[tuple[Document, float]]) -> float:
    """
    Calcule la couverture sémantique entre la propale générée et les chunks utilisés (via embeddings).
    """
    # Embedding du texte généré
    generated_embedding = embedder.embed_query(generated_text)

    # Embedding des chunks (leur texte seulement)
    chunk_embeddings = [embedder.embed_query(doc.page_content) for doc, _ in chunks]

    # Similarité cosinus entre la proposition et chaque chunk
    similarities = cosine_similarity([generated_embedding], chunk_embeddings)[0]

    # Moyenne des similarités
    coverage_score = float(np.mean(similarities))
    return coverage_score
