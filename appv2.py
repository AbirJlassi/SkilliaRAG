# app.py

import glob
import os
import streamlit as st
from modules.loader import load_pdf
from modules.rag_core import full_rag_pipeline
from modules.feedback import handle_feedback
from modules.splitter import splitdocuments
from modules.vector_store import load_index
from main import prepare_index_from_directory 
from modules.llm_only import generate_without_docs
from modules.llm_only import compute_similarity, compute_chunk_coverage

# -----------------------------------------------
# CONFIGURATION GÉNÉRALE
# -----------------------------------------------
st.set_page_config(
    page_title="Skillia Propales", 
    layout="wide", 
    page_icon="🧠",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------
# CSS PROFESSIONNEL
# -----------------------------------------------

st.markdown("""
    <style>
        /* Variables CSS pour cohérence */
        :root {
            --primary-color: #2e2e9b;
            --secondary-color: #f92a88;
            --accent-color: #00c9ff;
            --background-light: #f8fafc;
            --background-white: #ffffff;
            --text-dark: #1e293b;
            --text-gray: #64748b;
            --border-color: #e2e8f0;
            --shadow-light: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            --shadow-medium: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-large: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }

        /* Background principal */
        .main {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 2rem 0;
        }

        /* Header avec gradient */
        .header-container {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-large);
            text-align: center;
            color: white;
        }

        .header-title {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
            margin-bottom: 0;
        }

        /* Cards modernes */
        .modern-card {
            background: var(--background-white);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: var(--shadow-medium);
            border: 1px solid var(--border-color);
            margin-bottom: 2rem;
            transition: all 0.3s ease;
        }

        .modern-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-large);
        }

        /* Styles pour les boutons */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            font-weight: 600;
            border-radius: 12px;
            padding: 0.75em 2em;
            border: none;
            transition: all 0.3s ease;
            font-size: 1rem;
            box-shadow: var(--shadow-light);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
            background: linear-gradient(135deg, var(--secondary-color) 0%, var(--primary-color) 100%);
        }

        /* Boutons de feedback */
        .feedback-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }

        .btn-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        }

        .btn-warning {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        }

        /* Zone de texte améliorée */
        .stTextArea > div > div > textarea {
            border-radius: 12px;
            border: 2px solid var(--border-color);
            padding: 1rem;
            font-size: 1rem;
            transition: border-color 0.3s ease;
            background: var(--background-white);
        }

        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(46, 46, 155, 0.1);
        }

        /* Section des résultats */
        .result-container {
            background: var(--background-white);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: var(--shadow-medium);
            border-left: 4px solid var(--primary-color);
            margin: 1rem 0;
        }

        /* Chunks avec design amélioré */
        .chunk-container {
            background: var(--background-white);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }

        .chunk-container:hover {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-light);
        }

        .chunk-score {
            background: linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 0.5rem;
        }

        /* Indicateurs de statut */
        .status-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            text-align: center;
            font-weight: 600;
        }

        .status-warning {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            text-align: center;
            font-weight: 600;
        }

        /* Amélioration des expandeurs */
        .streamlit-expanderHeader {
            background: var(--background-light);
            border-radius: 8px;
            padding: 0.5rem;
            font-weight: 600;
        }

        /* Section headers */
        .section-header {
            color: var(--text-dark);
            font-weight: 700;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border-color);
        }

        /* Spinner personnalisé */
        .stSpinner {
            text-align: center;
            padding: 2rem;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .header-title {
                font-size: 2rem;
            }
            
            .modern-card {
                padding: 1rem;
            }
            
            .header-container {
                padding: 2rem 1rem;
            }
        }

        /* Animation de chargement */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .loading-animation {
            animation: pulse 2s infinite;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# HEADER PROFESSIONNEL
# -----------------------------------------------
st.markdown("""
    <div class="header-container">
        <div class="header-title">🧠 SKILLIA</div>
        <div class="header-subtitle">Générateur intelligent de propositions commerciales</div>
        <div style="margin-top: 1rem; font-size: 0.95rem; opacity: 0.8;">
            Solution basée sur les documents internes • Propulsé par LLaMA 3 + CrossEncoder 
        </div>
    </div>
""", unsafe_allow_html=True)

# Bouton admin pour recharger les documents
with st.expander("⚙️ Options avancées – Réindexation des documents"):
    if st.button("🔄 Recharger les documents internes (PDF)"):
        with st.spinner("📥 Lecture des documents, découpage et indexation en cours..."):
            data_dir = "data"
            index_path = "vector_store/propales_index"

            # 1. Charger les PDF
            pdf_files = glob.glob(os.path.join(data_dir, "**", "*.pdf"), recursive=True)
            st.write(f"📄 **{len(pdf_files)} fichiers PDF trouvés dans `{data_dir}`.**")

            all_documents = []
            for pdf_path in pdf_files:
                docs = load_pdf(pdf_path)
                all_documents.extend(docs)

            st.write(f"📚 **{len(all_documents)} pages extraites** avant découpage.")

            # 2. Chunking
            chunks = splitdocuments(all_documents)
            st.write(f"🧩 **{len(chunks)} chunks générés** pour l'indexation.")

            # 3. Ingestion finale
            prepare_index_from_directory(data_dir, index_path)

        st.success("✅ Index vectoriel reconstruit avec succès à partir des nouveaux documents !")

# -------------------
# SECTION PRINCIPALE
# -------------------

st.markdown("""
    <div class="modern-card">
        <h3 class="section-header">💬 Décrivez le besoin client</h3>
    </div>
""", unsafe_allow_html=True)

user_query = st.text_area(
    "Décrivez le besoin client :",
    height=150,
    placeholder="💡 Exemple : Proposer un accompagnement cybersécurité pour une banque publique ou une mission IA pour une société...\n\nDécrivez ici la problématique du client, ses enjeux et ses contraintes.",
    help="Plus votre description est précise, plus la proposition générée sera pertinente et adaptée."
)

# -----------------------------------------------
# BOUTON DE GÉNÉRATION
# -----------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    generate_button = st.button(
        "⚡ Générer la proposition ",
        use_container_width=True,
        type="primary"
    )

# -----------------------------------------------
# TRAITEMENT ET RÉSULTATS
# -----------------------------------------------
if generate_button:
    if user_query.strip():
        st.session_state["proposal_ready"] = True
        
        with st.spinner("🔍 Analyse des documents en cours..."):
            progress_bar = st.progress(0)
            import time
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            result, top_chunks = full_rag_pipeline(user_query)
            st.session_state["last_result"] = result
            st.session_state["last_chunks"] = top_chunks
            st.session_state["last_query"] = user_query

        with st.spinner("✨ Génération via LLM seul (sans contexte)..."):
            result_llm_only = generate_without_docs(user_query)

        similarity_score = compute_similarity(result, result_llm_only)
        coverage_score = compute_chunk_coverage(result, top_chunks)
        #highlighted_rag_result = highlight_with_chunks(result, top_chunks)

        score_color = "#10b981" if similarity_score >= 0.75 else "#f59e0b" if similarity_score >= 0.5 else "#ef4444"

        st.markdown(f"""
            <div class="modern-card">
                <h3 class="section-header">📊 Comparaison RAG vs LLM seul</h3>
                <p style="color: var(--text-gray);">
                    Comparaison entre la réponse enrichie par les documents internes (RAG) et celle générée uniquement par le LLM. Le score de similarité indique leur proximité, tandis que le taux de couverture estime à quel point la réponse RAG reprend des passages des documents.
                </p>
                <div style="display: flex; gap: 2rem;">
                    <div style="flex: 1; background: #f8fafc; border-left: 4px solid #2e2e9b; padding: 1.5rem; border-radius: 12px;">
                        <h4 style="margin-top: 0;">📄 Proposition via RAG</h4>
                        <div style="white-space: pre-wrap; font-size: 0.95rem; font-family: monospace;">
                            {result}
                        </div>
                    </div>
                    <div style="flex: 1; background: #f8fafc; border-left: 4px solid #00c9ff; padding: 1.5rem; border-radius: 12px;">
                        <h4 style="margin-top: 0;">🤖 Proposition LLM seul</h4>
                        <div style="white-space: pre-wrap; font-size: 0.95rem; font-family: monospace;">
                            {result_llm_only}
                        </div>
                    </div>
                </div>
                <div style="margin-top: 1.5rem; display: flex; gap: 2rem;">
                    <div style="flex: 1;">
                        <h4 style="margin-bottom: 0.5rem;">🔄 Score de similarité :</h4>
                        <p style="font-size: 1.3rem; font-weight: bold; color: {score_color};">
                            {similarity_score:.2f} / 1.00
                        </p>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin-bottom: 0.5rem;">📚 Taux de couverture des documents :</h4>
                        <p style="font-size: 1.3rem; font-weight: bold; color: #2e2e9b;">
                            {coverage_score:.2%}
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # -----------------------------------------------
        # DOCUMENTS SOURCES
        # -----------------------------------------------

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="modern-card">
                <h3 class="section-header">📚 Sources utilisées pour la génération (avec RAG) </h3>
                <p style="color: var(--text-gray); margin-bottom: 1.5rem;">
                    Les extraits suivants ont été analysés pour construire votre proposition :
                </p>
            </div>
        """, unsafe_allow_html=True)

        for i, (doc, score) in enumerate(top_chunks):
            score_color = "#10b981" if score > 0.8 else "#f59e0b" if score > 0.6 else "#ef4444"
            
            with st.expander(f"📋 Source {i+1} • Score de pertinence : {score:.4f} • {doc.metadata.get('source', 'Document inconnu')}"):
                col_meta1, col_meta2 = st.columns(2)
                with col_meta1:
                    st.markdown(f"**📄 Source :** `{doc.metadata.get('source', 'N/A')}`")
                with col_meta2:
                    st.markdown(f"**📖 Page :** `{doc.metadata.get('page', '?')}`")
                
                st.markdown(f"""
                    <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        <div class="chunk-score" style="background-color: {score_color};">
                            Score : {score:.4f}
                        </div>
                        <div style="margin-top: 0.5rem; font-family: monospace; white-space: pre-wrap; font-size: 0.9rem;">
                            {doc.page_content[:1000]}{"..." if len(doc.page_content) > 1000 else ""}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    else:
        st.markdown("""
            <div class="status-warning">
                ⚠️ Veuillez décrire le besoin client avant de générer une proposition.
            </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------
# SECTION FEEDBACK - UNE SEULE FOIS !
# -----------------------------------------------
if "last_result" in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="modern-card">
            <h3 class="section-header">🗳️ Évaluation de la proposition</h3>
            <p style="color: var(--text-gray); margin-bottom: 1.5rem;">
                Votre retour nous aide à améliorer la qualité des propositions générées.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_fb1, col_fb2, col_fb3 = st.columns([1, 1, 1])

    with col_fb1:
        if st.button("👍 Excellente proposition", use_container_width=True, key="btn_good"):
            st.write("🔍 DEBUG: Bouton cliqué")
            
            # Vérifier l'état de session
            if "last_result" not in st.session_state:
                st.error("❌ Pas de résultat en session")
                st.stop()
            
            if "last_query" not in st.session_state:
                st.error("❌ Pas de query en session")
                st.stop()
            
            # Afficher les données
            #st.write("📊 Données en session:")
            #st.write(f"- Query: {len(st.session_state['last_query'])} caractères")
            #st.write(f"- Result: {len(st.session_state['last_result'])} caractères")
            
            with st.spinner("📄 Sauvegarde de la proposition dans les données..."):
                try:
                    #st.write("🔄 Appel de handle_feedback...")
                    
                    filepath = handle_feedback(
                        st.session_state["last_query"],
                        st.session_state["last_result"]
                    )
                    
                    
                    if filepath:
                        st.toast("📄 PDF sauvegardé et indexé avec succès.")
                        st.success("✅ Proposition ajoutée à la base documentaire !")
                        st.markdown(f"**Fichier créé :** `{filepath}`")
                        
                        # Vérifications finales
                        if os.path.exists(filepath):
                            file_size = os.path.getsize(filepath)
                            #st.write(f"✅ **Fichier confirmé** - Taille: {file_size:,} bytes")
                            
                            # Lister les fichiers dans le dossier
                            data_dir = "data/generated"
                            if os.path.exists(data_dir):
                                files = os.listdir(data_dir)
                                #st.write(f"📂 **Fichiers dans {data_dir}:** {len(files)}")
                                #for f in files[-3:]:  # Montrer les 3 derniers
                                    #st.write(f"  - {f}")
                        else:
                            st.error(f"❌ **Fichier non trouvé:** {filepath}")
                    else:
                        st.error("❌ **Aucun fichier retourné** par handle_feedback")
                        
                except Exception as e:
                    st.error(f"❌ **Erreur lors de la sauvegarde:** {str(e)}")
                    
                    # Debug détaillé
                    with st.expander("🔍 Détails de l'erreur"):
                        st.code(str(e))
                        import traceback
                        st.code(traceback.format_exc())

    with col_fb2:
        if st.button("⚡️ Bonne, mais à améliorer", use_container_width=True, key="btn_ok"):
            st.markdown("""
                <div style="background: #fef3c7; color: #92400e; padding: 1rem; border-radius: 12px; text-align: center;">
                    📝 Merci pour ce retour constructif !
                </div>
            """, unsafe_allow_html=True)

    with col_fb3:
        if st.button("👎 Non satisfaisante", use_container_width=True, key="btn_bad"):
            st.markdown("""
                <div class="status-warning">
                    🔄 Merci pour votre retour. Essayez de reformuler votre demande pour de meilleurs résultats.
                </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------
# FOOTER INFORMATIF
# -----------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; padding: 2rem; color: var(--text-gray); border-top: 1px solid var(--border-color); margin-top: 3rem;">
         Version 2.0 • © 2025
        <br>
    </div>
""", unsafe_allow_html=True)