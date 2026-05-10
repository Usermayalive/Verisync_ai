from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from rank_bm25 import BM25Okapi
from backend.retrieval_service.storage.vector_store import get_vector_store
from backend.retrieval_service.retrieval.hybrid_retriever import HybridRetriever
from backend.retrieval_service.storage.postgres_tables import get_table_cell_value, get_all_source_names, get_global_telemetry
from backend.retrieval_service.tools.temporal_drift import calculate_drift
from backend.retrieval_service.schemas import TemporalDriftOutput
from backend.retrieval_service.storage.session_retriever import (
    get_session_retriever as _get_session_retriever,
    add_to_session_store as _add_to_session_store,
)

def get_hybrid_retriever() -> BaseRetriever:
    vector_store = get_vector_store()
    try:
        all_docs = vector_store.similarity_search("", k=1000)
    except Exception:
        all_docs = []
    if not all_docs or not isinstance(all_docs, list) or len(all_docs) == 0:
        return vector_store.as_retriever()
    tokenized_corpus = [doc.page_content.lower().split() for doc in all_docs]
    if not any(tokenized_corpus):
        return vector_store.as_retriever()
    bm25 = BM25Okapi(tokenized_corpus)
    return HybridRetriever(
        vector_store=vector_store,
        bm25=bm25,
        all_docs=all_docs
    )

hybrid_retriever = get_hybrid_retriever()

def get_session_retriever(session_id: str) -> BaseRetriever:
    global_store = get_vector_store()
    return _get_session_retriever(session_id, global_store)

def add_to_session_store(session_id: str, docs: List[Document]) -> None:
    _add_to_session_store(session_id, docs)

def get_source_manifest(session_id: str = "default") -> List[str]:
    return get_all_source_names(session_id)

def detect_temporal_drift(docs: List[Document]) -> Optional[str]:
    return calculate_drift(docs)

def get_table_cell(session_id: str, source: str, table_id: str, row: int, col: int) -> str:
    return get_table_cell_value(session_id, source, table_id, row, col)

def get_duplicate_sources(session_id: str = "default") -> List[str]:
    return get_global_telemetry(session_id).get("duplicate_sources", [])

def get_pii_report(session_id: str = "default") -> List[dict]:
    return get_global_telemetry(session_id).get("pii_entities", [])
