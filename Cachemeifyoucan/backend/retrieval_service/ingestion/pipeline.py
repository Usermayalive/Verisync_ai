import sys
import argparse
from typing import List
from langchain_core.documents import Document
from backend.retrieval_service.ingestion.loaders import load_documents
from backend.retrieval_service.ingestion.splitter import split_documents
from backend.retrieval_service.tools.pii_redactor import pii_redact
from backend.retrieval_service.tools.duplicate_detector import remove_duplicates
from backend.retrieval_service.tools.translator import detect_and_translate
from backend.retrieval_service.storage.vector_store import add_documents_to_store
from backend.retrieval_service.storage.postgres_tables import init_tables, store_table_data, update_source_telemetry
from backend.utils.logger import get_logger
logger = get_logger("RetrievalService.Ingestion")
def full_ingest_pipeline(sources: List[str], session_id: str = "default"):
    init_tables()
    raw_docs = []
    all_raw_count = 0
    for source in sources:
        try:
            docs, tables = load_documents(source)
            if docs:
                raw_docs.extend(docs)
                all_raw_count += len(docs)
            for table in tables:
                store_table_data(session_id, source, table["table_id"], table["rows"])
        except Exception as e:
            logger.error(f"Error {source}: {e}")
            raise e
    if not raw_docs:
        return
    unique_docs = remove_duplicates(raw_docs)
    translated_docs = detect_and_translate(unique_docs)
    duplicates_removed = [d.metadata.get("source") for d in raw_docs if d not in unique_docs]
    redacted_docs = pii_redact(translated_docs)
    if sources:
        update_source_telemetry(session_id, sources[0], {
            "duplicates": duplicates_removed,
            "pii": {"redacted": True, "count": len(redacted_docs)}
        })
    chunks = split_documents(redacted_docs)
    for chunk in chunks:
        chunk.metadata["session_id"] = session_id
    add_documents_to_store(chunks, session_id=session_id)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", nargs="+", required=True)
    parser.add_argument("--session_id", default="default")
    args = parser.parse_args()
    full_ingest_pipeline(args.sources, args.session_id)
