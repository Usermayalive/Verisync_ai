import pytest
import os
import sys
from unittest.mock import MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
@pytest.fixture(autouse=True)
def mock_db_global(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setattr("psycopg2.connect", lambda **kwargs: mock_conn)
    import backend.retrieval_service.storage.postgres_tables as pg_tables
    monkeypatch.setattr(pg_tables, "init_tables", lambda: None)
    import backend.retrieval_service.storage.vector_store as vs
    monkeypatch.setattr(vs, "get_vector_store", lambda: MagicMock())
@pytest.fixture
def mock_document():
    from langchain_core.documents import Document
    return Document(page_content="Test content", metadata={"source": "test.txt"})
@pytest.fixture
def api_headers():
    from backend.config import settings
    return {"X-API-Key": settings.API_SECRET_KEY}
