# modules/llm_groq.py (adapté pour GPT-3.5 via OpenAI)

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm(model: str = "gpt-3.5-turbo") -> BaseChatModel:
    """
    Initialise un modèle GPT-3.5 via l'API OpenAI.
    """
    if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError("OPENAI_API_KEY non défini dans les variables d'environnement")

    return ChatOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],  # clé OpenAI
        model_name=model,
        temperature=0.1
    )
