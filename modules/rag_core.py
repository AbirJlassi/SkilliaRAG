# modules/rag_core.py
from itertools import chain
from modules.vector_store import load_index
from modules.embedder import get_embedding_model
from modules.llm_openai import get_llm
from modules.prompt_template import get_proposal_prompt_template
from modules.reranker import rerank
from langchain.schema import Document
from typing import List, Tuple
from langchain.chains import LLMChain

def full_rag_pipeline(query: str, index_path: str = "vector_store/propales_index", faiss_k: int = 20, final_k: int = 4) -> Tuple[str, List[Tuple[Document, float]]]:
    """
    Pipeline complet : recherche FAISS → reranking → génération LLaMA3 (avec contrôle du contexte)
    """


    # 1. Index + Recherche
    embedder = get_embedding_model()
    index = load_index(index_path, embedder)

    retrieved_docs = index.similarity_search(query, k=faiss_k)
    print(f"🔍 {len(retrieved_docs)} documents récupérés par FAISS.")

    reranked_docs = rerank(query, retrieved_docs, top_k=final_k)
    print(f"🏅 {len(reranked_docs)} documents après reranking.")

    # 2. Préparation du contexte
    docs = [doc for doc, _ in reranked_docs]

    context = "\n\n".join(doc.page_content.strip() for doc in docs)
    print(f"🧾 Longueur totale du contexte : {len(context)} caractères")

    # Option : tronquer si trop long (selon ton modèle)
    MAX_CONTEXT_CHARS = 12000
    if len(context) > MAX_CONTEXT_CHARS:
        print(f"⚠️ Contexte tronqué à {MAX_CONTEXT_CHARS} caractères.")
        context = context[:MAX_CONTEXT_CHARS]

    # 3. Appel du modèle avec prompt template
    prompt = get_proposal_prompt_template()
    llm = get_llm("gpt-3.5-turbo")

    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    result = chain.run({"context": context, "question": query})

    return result, reranked_docs