import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings
client = TestClient(app)
def test_auth_missing_header():
    response = client.post("/api/ask", json={"question": "test"})
    assert response.status_code == 403
def test_auth_invalid_key():
    response = client.post("/api/ask", json={"question": "test"}, headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 403
def test_auth_valid_key():
    response = client.post("/api/ask", json={"question": "test"}, headers={"X-API-Key": settings.API_SECRET_KEY})
    assert response.status_code != 403
def test_pii_redaction_flow():
    from backend.retrieval_service.ingestion.pipeline import full_ingest_pipeline
    import os
    test_file = "/tmp/pii_test.txt"
    with open(test_file, "w") as f:
        f.write("My name is John Doe and my email is john.doe@example.com. My phone is 555-123-4567.")
    try:
        manifest = full_ingest_pipeline([test_file])
        from backend.retrieval_service.storage.postgres_tables import get_global_telemetry
        telemetry = get_global_telemetry()
        assert len(telemetry.get("pii_entities", [])) > 0
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
def test_sql_injection_probe():
    headers = {"X-API-Key": settings.API_SECRET_KEY}
    malicious_query = "'; DROP TABLE sources; --"
    response = client.post("/api/ask", json={"question": malicious_query}, headers=headers)
    assert response.status_code in [200, 500] 
    from backend.retrieval_service.storage.postgres_tables import get_all_source_names
    sources = get_all_source_names()
    assert isinstance(sources, list)
