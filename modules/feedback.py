# modules/feedback.py
from fpdf import FPDF
import os
import datetime
from modules.vector_store import store_generated_proposal

def handle_feedback(query: str, proposal_text: str):
    """
    Gère le feedback positif en sauvegardant la proposition.
    """
    print("✅ handle_feedback() called")
    print(f"📝 Query reçue: {len(query)} caractères")
    print(f"📄 Proposal reçue: {len(proposal_text)} caractères")
    
    # Vérifications préliminaires
    if not query or not query.strip():
        raise ValueError("Query vide ou nulle")
    
    if not proposal_text or not proposal_text.strip():
        raise ValueError("Proposal text vide ou nul")
    
    try:
        print("🔄 Appel de store_generated_proposal...")
        filepath = store_generated_proposal(
            proposal_text=proposal_text,
            index_path="vector_store/propales_index",
            metadata={"query": query, "source": "generated"}
        )
        
        if filepath:
            print(f"📁 Feedback enregistré avec succès à : {filepath}")
            
            # Vérification finale
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"✅ Fichier confirmé - Taille: {file_size} bytes")
            else:
                print(f"⚠️ Fichier introuvable après création: {filepath}")
                
            return filepath
        else:
            raise Exception("store_generated_proposal a retourné None")
            
    except Exception as e:
        print(f"❌ Erreur dans handle_feedback: {e}")
        import traceback
        print("🔍 Stack trace complète:")
        print(traceback.format_exc())
        raise e