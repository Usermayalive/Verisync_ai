import hashlib
from typing import List, Set
from langchain_core.documents import Document
from backend.utils.logger import get_logger
logger = get_logger("RetrievalService.Deduplicator")
def remove_duplicates(docs: List[Document]) -> List[Document]:
    seen_hashes: Set[str] = set()
    unique_docs: List[Document] = []
    for doc in docs:
        content_hash = hashlib.md5(doc.page_content.encode('utf-8')).hexdigest()
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_docs.append(doc)
        else:
            logger.info(f"Duplicate detected and removed: {doc.metadata.get('source', 'unknown')}")
    return unique_docs
