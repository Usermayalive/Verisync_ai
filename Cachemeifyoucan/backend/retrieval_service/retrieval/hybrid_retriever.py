from typing import List
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
class HybridRetriever(BaseRetriever):
    vector_store: any
    bm25: BM25Okapi
    all_docs: List[Document]
    k: int = 10
    alpha: float = 0.5
    def _get_relevant_documents(self, query: str) -> List[Document]:
        vector_docs = self.vector_store.similarity_search(query, k=self.k)
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_n_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:self.k]
        bm25_docs = [self.all_docs[i] for i in top_n_indices]
        return self._rrf_fusion(vector_docs, bm25_docs)
    def _rrf_fusion(self, vector_docs: List[Document], bm25_docs: List[Document]) -> List[Document]:
        k_f = 60
        scores = {}
        for rank, doc in enumerate(vector_docs):
            doc_id = doc.metadata.get("chunk_id", doc.page_content)
            scores[doc_id] = scores.get(doc_id, 0) + (1 / (k_f + rank + 1)) * self.alpha
        for rank, doc in enumerate(bm25_docs):
            doc_id = doc.metadata.get("chunk_id", doc.page_content)
            scores[doc_id] = scores.get(doc_id, 0) + (1 / (k_f + rank + 1)) * (1 - self.alpha)
        all_unique_docs = {doc.metadata.get("chunk_id", doc.page_content): doc for doc in (vector_docs + bm25_docs)}
        fused_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:self.k]
        return [all_unique_docs[fid] for fid in fused_ids]
