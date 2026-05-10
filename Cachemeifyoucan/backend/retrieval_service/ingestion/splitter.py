from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from backend.retrieval_service.utils import normalize_metadata
def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    split_docs = splitter.split_documents(docs)
    for i, doc in enumerate(split_docs):
        doc.metadata["chunk_id"] = f"chunk_{i}"
        doc = normalize_metadata(doc)
    return split_docs
