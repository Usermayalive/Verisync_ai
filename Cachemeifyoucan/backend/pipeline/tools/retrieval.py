from langchain_core.tools import tool
from typing import List, Optional
from backend.retrieval_service.interfaces import hybrid_retriever

@tool
def deep_search(query: str) -> str:
    """Performs a deep search across all indexed PDFs, TXT, and MD files. Use this if the initial context is insufficient or ambiguous."""
    docs = hybrid_retriever.invoke(query)
    if not docs:
        return "No further information found."
    return "\n\n".join([f"Source: {d.metadata.get('source')} - Content: {d.page_content}" for d in docs])

@tool
def get_audio_transcript(source_path: str) -> str:
    """Fetches the full transcript of a specific audio file. Useful for verifying details mentioned in meeting recordings or memos."""
    docs = hybrid_retriever.invoke(source_path)
    audio_docs = [d for d in docs if d.metadata.get("type") == "audio" or source_path in d.metadata.get("source", "")]
    if not audio_docs:
        return f"Could not find transcript for {source_path}."
    return "\n\n".join([d.page_content for d in audio_docs])
