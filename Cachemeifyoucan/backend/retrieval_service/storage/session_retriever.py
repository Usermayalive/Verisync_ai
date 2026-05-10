import hashlib
from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from rank_bm25 import BM25Okapi
from backend.retrieval_service.retrieval.hybrid_retriever import HybridRetriever
from backend.retrieval_service.storage.vector_store import get_embeddings
from langchain_postgres import PGVector
from backend.config import settings

def _session_collection_name(session_id: str) -> str:
    return f"session_{hashlib.sha256(session_id.encode()).hexdigest()[:16]}"

def get_session_vector_store(session_id: str) -> PGVector:
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=_session_collection_name(session_id),
        connection=settings.DATABASE_URL,
        use_jsonb=True,
    )

def add_to_session_store(session_id: str, docs: List[Document]) -> None:
    if not docs:
        return
    store = get_session_vector_store(session_id)
    store.add_documents(docs)

def get_session_retriever(session_id: str, global_store: PGVector, k: int = 10):
    session_store = get_session_vector_store(session_id)
    # Always include global store as fallback for all sessions
    return _MergedVectorStore(global_store, session_store, k=k)


class _MergedVectorStore:
    def __init__(self, global_store: Optional[PGVector], session_store: PGVector, k: int = 10):
        self._global = global_store
        self._session = session_store
        self.k = k

    def similarity_search_with_score(self, query: str, k: Optional[int] = None):
        from backend.utils.logger import get_logger
        logger = get_logger("MergedVectorStore")

        search_k = k or self.k
        g = [] # <--- GLOBAL FALLBACK DISABLED TO ENFORCE ISOLATION
        # if self._global:
        #     try:
        #         g = self._global.similarity_search_with_score(query, k=search_k)
        #         logger.info(f"[DEBUG] Global store returned {len(g)} results")
        #     except Exception as e:
        #         logger.warning(f"[DEBUG] Global store search failed: {e}")
        #         g = []
                
        s = []
        try:
            s = self._session.similarity_search_with_score(query, k=search_k)
            logger.info(f"[DEBUG] Session store returned {len(s)} results")
        except Exception as e:
            logger.warning(f"[DEBUG] Session store search failed: {e}")
            s = []
            
        seen = set()
        merged = []
        for doc, score in s:
            key = doc.metadata.get("chunk_id", doc.page_content[:100])
            if key not in seen:
                seen.add(key)
                merged.append((doc, score))
                
        # Lower distance is better in PGVector
        merged.sort(key=lambda x: x[1])
        logger.info(f"[DEBUG] Merged total: {len(merged)} results")
        return merged[:search_k]

    def invoke(self, query: str):
        results = self.similarity_search_with_score(query)
        return [doc for doc, score in results]
