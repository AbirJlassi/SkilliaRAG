# modules/metrics.py

import time
import json
import os
from datetime import datetime
import streamlit as st
from typing import List, Tuple, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class RAGMetrics:
    """
    Classe simple pour évaluer les performances du système RAG
    """
    
    def __init__(self):
        self.metrics_file = "metrics_data.json"
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Modèle léger pour les embeddings
        
    def calculate_relevance_score(self, query: str, retrieved_chunks: List[Tuple[Any, float]]) -> float:
        """
        Calcule un score de pertinence moyen entre la query et les chunks récupérés
        
        Args:
            query: La requête utilisateur
            retrieved_chunks: Liste des (document, score) récupérés
            
        Returns:
            Score de pertinence moyen (0-1)
        """
        try:
            if not retrieved_chunks:
                return 0.0
            
            # Encoder la query
            query_embedding = self.model.encode([query])
            
            # Encoder les chunks
            chunk_texts = [doc.page_content for doc, _ in retrieved_chunks]
            chunk_embeddings = self.model.encode(chunk_texts)
            
            # Calculer la similarité cosinus
            similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]
            
            # Retourner la moyenne
            return float(np.mean(similarities))
            
        except Exception as e:
            print(f"Erreur calcul relevance_score: {e}")
            return 0.0
    
    def calculate_response_quality(self, query: str, response: str) -> float:
        """
        Calcule la qualité de la réponse basée sur la cohérence sémantique avec la query
        
        Args:
            query: La requête utilisateur
            response: La réponse générée
            
        Returns:
            Score de qualité (0-1)
        """
        try:
            if not response.strip():
                return 0.0
            
            # Encoder query et réponse
            embeddings = self.model.encode([query, response])
            
            # Calculer similarité
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            # Bonus pour la longueur (réponse substantielle)
            length_bonus = min(len(response) / 1000, 0.2)  # Max 20% bonus
            
            return float(min(similarity + length_bonus, 1.0))
            
        except Exception as e:
            print(f"Erreur calcul response_quality: {e}")
            return 0.0
    
    def log_metrics(self, query: str, response: str, chunks: List[Tuple[Any, float]], 
                   processing_time: float, relevance_score: float = None, 
                   quality_score: float = None) -> Dict[str, Any]:
        """
        Enregistre les métriques d'une requête
        
        Args:
            query: La requête utilisateur
            response: La réponse générée
            chunks: Les chunks récupérés
            processing_time: Temps de traitement en secondes
            relevance_score: Score de pertinence (calculé si non fourni)
            quality_score: Score de qualité (calculé si non fourni)
            
        Returns:
            Dictionnaire contenant toutes les métriques
        """
        
        # Calculer les scores si non fournis
        if relevance_score is None:
            relevance_score = self.calculate_relevance_score(query, chunks)
        
        if quality_score is None:
            quality_score = self.calculate_response_quality(query, response)
        
        # Préparer les données
        metrics_data = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:100] + "..." if len(query) > 100 else query,  # Tronquer pour l'espace
            "response_length": len(response),
            "num_chunks_retrieved": len(chunks),
            "processing_time_seconds": round(processing_time, 3),
            "relevance_score": round(relevance_score, 4),
            "quality_score": round(quality_score, 4),
            "chunk_scores": [round(score, 4) for _, score in chunks[:5]]  # Top 5 seulement
        }
        
        # Sauvegarder dans le fichier
        try:
            # Charger les données existantes
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    all_metrics = json.load(f)
            else:
                all_metrics = []
            
            # Ajouter les nouvelles métriques
            all_metrics.append(metrics_data)
            
            # Garder seulement les 100 dernières entrées pour éviter un fichier trop gros
            if len(all_metrics) > 100:
                all_metrics = all_metrics[-100:]
            
            # Sauvegarder
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(all_metrics, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erreur sauvegarde métriques: {e}")
        
        return metrics_data
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques pour le dashboard
        
        Returns:
            Dictionnaire avec les stats globales
        """
        try:
            if not os.path.exists(self.metrics_file):
                return {
                    "total_queries": 0,
                    "avg_relevance": 0.0,
                    "avg_quality": 0.0,
                    "avg_processing_time": 0.0,
                    "recent_queries": []
                }
            
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                all_metrics = json.load(f)
            
            if not all_metrics:
                return {
                    "total_queries": 0,
                    "avg_relevance": 0.0,
                    "avg_quality": 0.0,
                    "avg_processing_time": 0.0,
                    "recent_queries": []
                }
            
            # Calculer les moyennes
            relevance_scores = [m["relevance_score"] for m in all_metrics]
            quality_scores = [m["quality_score"] for m in all_metrics]
            processing_times = [m["processing_time_seconds"] for m in all_metrics]
            
            stats = {
                "total_queries": len(all_metrics),
                "avg_relevance": round(np.mean(relevance_scores), 3),
                "avg_quality": round(np.mean(quality_scores), 3),
                "avg_processing_time": round(np.mean(processing_times), 3),
                "recent_queries": all_metrics[-5:]  # 5 dernières queries
            }
            
            return stats
            
        except Exception as e:
            print(f"Erreur récupération stats: {e}")
            return {
                "total_queries": 0,
                "avg_relevance": 0.0,
                "avg_quality": 0.0,
                "avg_processing_time": 0.0,
                "recent_queries": []
            }

# Instance globale
rag_metrics = RAGMetrics()

def display_metrics_dashboard():
    stats = rag_metrics.get_dashboard_stats()

    with st.expander("📊 Métriques de performance du RAG – Voir les statistiques"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="🔍 Requêtes traitées",
                value=stats['total_queries']
            )

        with col2:
            st.metric(
                label="🎯 Score pertinence (Query-Chunks)",
                value=f"{stats['avg_relevance']:.3f}"
            )

        with col3:
            st.metric(
                label="✨ Qualité de réponse",
                value=f"{stats['avg_quality']:.3f}"
            )

        with col4:
            st.metric(
                label="⚡ Temps de réponse moyen",
                value=f"{stats['avg_processing_time']:.2f} s"
            )
