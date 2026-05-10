from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from backend.config import settings
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)
def get_vector_store():
    return PGVector(
        embeddings=get_embeddings(),
        collection_name="retrieval_collection",
        connection=settings.DATABASE_URL,
        use_jsonb=True,
    )
def add_documents_to_store(docs, session_id: str = "default"):
    if session_id and session_id != "default":
        from backend.retrieval_service.storage.session_retriever import add_to_session_store
        add_to_session_store(session_id, docs)
    else:
        store = get_vector_store()
        store.add_documents(docs)
def get_retriever():
    return get_vector_store().as_retriever()
