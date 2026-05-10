import re
from typing import Dict, Any, List
from datetime import datetime
from langchain_core.documents import Document
def normalize_metadata(doc: Document) -> Document:
    metadata = doc.metadata
    if "source" not in metadata:
        metadata["source"] = "unknown"
    if "page" in metadata:
        metadata["location"] = f"page:{metadata['page']}"
    elif "timestamp" in metadata:
        metadata["location"] = f"timestamp:{metadata['timestamp']}"
    elif "row" in metadata:
        metadata["location"] = f"row:{metadata['row']}"
    else:
        metadata["location"] = "unknown"
    if "date" not in metadata:
        metadata["date"] = datetime.now().strftime("%Y-%m-%d")
    metadata.setdefault("chunk_id", "pending")
    metadata.setdefault("pii_redacted", False)
    metadata.setdefault("language", "en")
    return doc
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
