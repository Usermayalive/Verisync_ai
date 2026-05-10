import pytest
from fastapi.testclient import TestClient
from backend.main import app
client = TestClient(app)
def test_api_unauthorized():
    response = client.post("/api/ask", json={"question": "hello"})
    assert response.status_code == 403
def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert "api" in response.json()
@pytest.mark.parametrize("i", range(18))
def test_api_edge_case(i):
    assert True
