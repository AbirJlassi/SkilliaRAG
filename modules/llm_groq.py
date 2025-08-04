# modules/llm_groq.py

from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
import os
from dotenv import load_dotenv


load_dotenv()
def get_llm(model: str = "llama3-8b-8192") -> BaseChatModel:
    """
    Initialise le modèle LLaMA 3 via l'API Groq.
    """
    if "GROQ_API_KEY" not in os.environ:
        raise EnvironmentError("GROQ_API_KEY non défini dans les variables d'environnement")

    return ChatGroq(
        groq_api_key=os.environ["GROQ_API_KEY"],
        model_name=model,
        temperature=0.1
    )


