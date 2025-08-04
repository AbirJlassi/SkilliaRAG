# modules/vector_store.py

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import os
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from modules.loader import load_pdf 
from modules.embedder import get_embedding_model
import datetime
from fpdf import FPDF
import datetime


def build_faiss_index(documents: list[Document], embedding_model: HuggingFaceEmbeddings) -> FAISS:
    """
    Crée un index FAISS à partir des chunks vectorisés.
    """
    return FAISS.from_documents(documents, embedding_model) 
    #vectorise tous les documents (chunks) automatiquement
    #stocke dans un index FAISS les vecteurs + le contenu texte original

def save_index(index: FAISS, path: str):
    """
    Sauvegarde l’index FAISS localement.
    """
    index.save_local(path)

def load_index(path: str, embedding_model: HuggingFaceEmbeddings) -> FAISS:
    """
    Recharge un index FAISS depuis le disque, avec validation explicite de la désérialisation.
    """
    return FAISS.load_local(
        path,
        embedding_model,
        allow_dangerous_deserialization=True  
    )




def store_generated_proposal(proposal_text: str, index_path: str, metadata: dict = None):
    """
    Sauvegarde une proposition générée en PDF et dans l'index FAISS.
    """
   
    print("🛠 store_generated_proposal() is running")
    
    if metadata is None:
        metadata = {}
        
    # Créer le dossier de sortie
    output_dir = "data/generated"
    os.makedirs(output_dir, exist_ok=True)
    print("📁 Dossier créé ou déjà existant :", output_dir)
    
    # Générer nom de fichier avec timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"propale_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    try:
        # Sauvegarde en PDF avec gestion d'erreur
        print("📝 Création du PDF...")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Traiter le texte ligne par ligne
        lines = proposal_text.split('\n')
        for line in lines:
            try:
                # Nettoyer les caractères problématiques pour FPDF
                clean_line = line.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, clean_line)
            except Exception as line_error:
                print(f"⚠️ Erreur sur une ligne: {line_error}")
                pdf.multi_cell(0, 10, "[Ligne non encodable]")
        
        pdf.output(filepath)
        print(f"✅ PDF sauvegardé dans : {filepath}")
        
        # Vérifier que le fichier existe
        if not os.path.exists(filepath):
            raise Exception(f"Le fichier PDF n'a pas été créé : {filepath}")
            
    except Exception as pdf_error:
        print(f"❌ Erreur lors de la création du PDF: {pdf_error}")
        raise pdf_error
    
    try:
        # Lecture du PDF et ajout à l'index FAISS
        print("📖 Chargement du PDF pour indexation...")
        docs = load_pdf(filepath)
        
        if not docs:
            raise Exception("Aucun document chargé depuis le PDF créé")
            
        doc = docs[0]
        
        # Mise à jour des métadonnées
        doc.metadata.update(metadata)
        doc.metadata["source"] = filename
        doc.metadata["generated_at"] = datetime.datetime.now().isoformat()
        doc.metadata["filepath"] = filepath
        
        print(f"📝 Document chargé avec {len(doc.page_content)} caractères")
        print(f"📋 Métadonnées: {doc.metadata}")
        
        # Charger le modèle d'embedding
        print("🤖 Chargement du modèle d'embedding...")
        embedder = get_embedding_model()
        
        # Charger ou créer l'index FAISS
        try:
            print(f"📂 Chargement de l'index FAISS: {index_path}")
            index = FAISS.load_local(index_path, embedder, allow_dangerous_deserialization=True)
            print("✅ Index FAISS existant chargé")
        except Exception as faiss_load_error:
            print(f"⚠️ FAISS index introuvable. Création d'un nouveau. Erreur: {faiss_load_error}")
            # Créer un nouvel index
            from langchain.schema import Document
            temp_doc = Document(page_content="document temporaire", metadata={})
            index = FAISS.from_documents([temp_doc], embedder)
        
        # Ajouter le document à l'index
        print("➕ Ajout du document à l'index...")
        index.add_documents([doc])
        
        # Sauvegarder l'index
        print("💾 Sauvegarde de l'index FAISS...")
        index.save_local(index_path)
        
        print("✅ Propale indexée et sauvegardée dans FAISS.")
        return filepath
        
    except Exception as index_error:
        print(f"❌ Erreur lors de l'indexation: {index_error}")
        print("⚠️ Le PDF a été créé mais l'indexation a échoué")
        # Retourner quand même le filepath du PDF créé
        return filepath

