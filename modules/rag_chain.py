# modules/rag_chain.py
"""
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.prompts import PromptTemplate
from modules.prompt_template import get_proposal_prompt_template

def build_rag_chain(index: FAISS, llm: BaseChatModel) -> RetrievalQA:
    
    #Crée une chaîne RAG personnalisée avec prompt structuré pour propale.
    
    retriever = index.as_retriever(search_kwargs={"k": 4})
    prompt = get_proposal_prompt_template()

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    return rag_chain
"""