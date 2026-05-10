from pydantic import BaseModel
from typing import Optional, List
from datetime import date
class RetrievalMetadata(BaseModel):
    source: str
    location: str
    date: Optional[str] = None
    table_ids: Optional[List[str]] = None
    chunk_id: str
    pii_redacted: bool = False
    language: str = "en"
class SourceManifest(BaseModel):
    sources: List[str]
class TemporalDriftOutput(BaseModel):
    has_drift: bool
    message: Optional[str] = None
    oldest_date: Optional[str] = None
    newest_date: Optional[str] = None
    days_since_latest: Optional[int] = None
class TableCellRequest(BaseModel):
    source: str
    table_id: str
    row: int
    col: int
