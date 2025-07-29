# modules/feedback.py

from modules.vector_store import store_generated_proposal


def handle_feedback(query: str, proposal_text: str):
    filepath = store_generated_proposal(
        proposal_text=proposal_text,
        index_path="vector_store/propales_index",
        metadata={"query": query, "source": "generated"}
    )
    return filepath
