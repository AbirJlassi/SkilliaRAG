# modules/rag_core.py
import time  # AJOUT pour mesurer le temps
from itertools import chain
from modules.vector_store import load_index
from modules.embedder import get_embedding_model
from modules.llm_openai import get_llm
from modules.prompt_template import get_proposal_prompt_template
from modules.reranker import rerank
from modules.metrics import rag_metrics  # AJOUT du module métriques
from langchain.schema import Document
from typing import List, Tuple
from langchain.chains import LLMChain

def full_rag_pipeline(query: str, index_path: str = "vector_store/propales_index", faiss_k: int = 20, final_k: int = 4) -> Tuple[str, List[Tuple[Document, float]]]:
    """
    Pipeline complet : recherche FAISS → reranking → génération LLaMA3 (avec contrôle du contexte)
    AJOUT : Intégration des métriques de performance
    """
    
    # AJOUT : Mesure du temps de départ
    start_time = time.time()
    
    try:
        # 1. Index + Recherche
        embedder = get_embedding_model()
        index = load_index(index_path, embedder)
        retrieved_docs = index.similarity_search(query, k=faiss_k)
        print(f"🔍 {len(retrieved_docs)} documents récupérés par FAISS.")
        
        reranked_docs = rerank(query, retrieved_docs, top_k=final_k)
        print(f"🏅 {len(reranked_docs)} documents après reranking.")
        
        # 2. Préparation du contexte
        docs = [doc for doc, *_ in reranked_docs]
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
        
        # AJOUT : Calcul du temps de traitement
        processing_time = time.time() - start_time
        print(f"⏱️ Temps de traitement total : {processing_time:.2f}s")
        
        # AJOUT : Enregistrement des métriques
        try:
            metrics_data = rag_metrics.log_metrics(
                query=query,
                response=result,
                chunks=reranked_docs,
                processing_time=processing_time
            )
            print(f"📊 Métriques enregistrées - Pertinence: {metrics_data['relevance_score']:.3f}, Qualité: {metrics_data['quality_score']:.3f}")
        except Exception as metrics_error:
            print(f"⚠️ Erreur enregistrement métriques: {metrics_error}")
        
        return result, reranked_docs
        
    except Exception as e:
        # AJOUT : Gestion d'erreur avec métriques
        processing_time = time.time() - start_time
        error_msg = f"❌ Erreur dans le pipeline RAG : {str(e)}"
        print(f"Erreur RAG: {e}")
        
        # Enregistrer l'erreur dans les métriques
        try:
            rag_metrics.log_metrics(
                query=query,
                response=error_msg,
                chunks=[],
                processing_time=processing_time,
                relevance_score=0.0,
                quality_score=0.0
            )
        except:
            pass  # Ignorer les erreurs de logging si critiques
            
        return error_msg, []


# AJOUT : Fonction utilitaire pour analyser les performances d'une requête
def analyze_query_performance(query: str, **kwargs) -> dict:
    """
    Analyse les performances d'une requête spécifique
    
    Args:
        query: La requête à analyser
        **kwargs: Arguments pour full_rag_pipeline
        
    Returns:
        Dictionnaire avec les métriques détaillées
    """
    start_time = time.time()
    
    # Exécuter le pipeline
    result, chunks = full_rag_pipeline(query, **kwargs)
    
    # Calculer métriques détaillées
    processing_time = time.time() - start_time
    
    # Évaluer la qualité de récupération
    if chunks:
        chunk_scores = [score for _, score in chunks]
        retrieval_quality = {
            "avg_chunk_score": sum(chunk_scores) / len(chunk_scores),
            "min_chunk_score": min(chunk_scores),
            "max_chunk_score": max(chunk_scores),
            "num_chunks": len(chunks)
        }
    else:
        retrieval_quality = {
            "avg_chunk_score": 0.0,
            "min_chunk_score": 0.0,
            "max_chunk_score": 0.0,
            "num_chunks": 0
        }
    
    # Calculer scores avec le module métriques
    relevance_score = rag_metrics.calculate_relevance_score(query, chunks)
    quality_score = rag_metrics.calculate_response_quality(query, result)
    
    return {
        "query": query,
        "processing_time": processing_time,
        "response_length": len(result),
        "relevance_score": relevance_score,
        "quality_score": quality_score,
        "retrieval_quality": retrieval_quality,
        "response": result,
        "chunks": chunks
    }


# AJOUT : Fonction pour comparer plusieurs requêtes
def benchmark_queries(queries: List[str], **kwargs) -> dict:
    """
    Effectue un benchmark sur plusieurs requêtes
    
    Args:
        queries: Liste des requêtes à tester
        **kwargs: Arguments pour full_rag_pipeline
        
    Returns:
        Statistiques globales du benchmark
    """
    results = []
    total_start_time = time.time()
    
    print(f"🚀 Début du benchmark sur {len(queries)} requêtes...")
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Requête {i}/{len(queries)}: {query[:50]}...")
        
        try:
            performance = analyze_query_performance(query, **kwargs)
            results.append(performance)
            print(f"✅ Traitée en {performance['processing_time']:.2f}s - Score: {performance['relevance_score']:.3f}")
        except Exception as e:
            print(f"❌ Erreur sur requête {i}: {e}")
            results.append({
                "query": query,
                "error": str(e),
                "processing_time": 0,
                "relevance_score": 0,
                "quality_score": 0
            })
    
    total_time = time.time() - total_start_time
    
    # Calculer statistiques globales
    valid_results = [r for r in results if "error" not in r]
    
    if valid_results:
        avg_processing_time = sum(r["processing_time"] for r in valid_results) / len(valid_results)
        avg_relevance = sum(r["relevance_score"] for r in valid_results) / len(valid_results)
        avg_quality = sum(r["quality_score"] for r in valid_results) / len(valid_results)
    else:
        avg_processing_time = avg_relevance = avg_quality = 0
    
    benchmark_stats = {
        "total_queries": len(queries),
        "successful_queries": len(valid_results),
        "failed_queries": len(queries) - len(valid_results),
        "total_benchmark_time": total_time,
        "avg_processing_time": avg_processing_time,
        "avg_relevance_score": avg_relevance,
        "avg_quality_score": avg_quality,
        "detailed_results": results
    }
    
    print(f"\n🏁 Benchmark terminé en {total_time:.2f}s")
    print(f"📊 Résultats moyens - Pertinence: {avg_relevance:.3f}, Qualité: {avg_quality:.3f}")
    
    return benchmark_stats