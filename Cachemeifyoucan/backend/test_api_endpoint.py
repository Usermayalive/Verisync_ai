from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
sys.modules["psycopg2"] = MagicMock()
sys.modules["langchain_postgres"] = MagicMock()
sys.modules["langchain_huggingface"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
import backend.pipeline.graph as graph_mod
graph_mod.build_graph = MagicMock(return_value=MagicMock())
from backend.main import app
from backend.config import settings
client = TestClient(app)
def test_api_call():
    print("=== Automated API Endpoint Test ===")
    mock_result = {
        "final_answer": "The project status is operational. Evidence found in project_plan.pdf.",
        "temporal_drift_warning": "Data is 5 days old.",
        "lightweight_judge_result": "SUFFICIENT",
        "epistemic_judge_result": "A",
        "judge_reasoning": "Chain A is grounded in the provided source manifest.",
        "judge_confidence": 0.98,
        "real_chain": {"claim": "Operational", "source": "project_plan.pdf"},
        "fake_chain": {"claim": "Delayed", "source": "fabricated_report.pdf"},
        "documents": [],
        "duplicate_sources": ["report_v1.pdf", "report_v1_copy.pdf"],
        "pii_report": [{"entity": "Name", "status": "Redacted"}]
    }
    import backend.main as main_mod
    main_mod.pipeline_graph.invoke = MagicMock(return_value=mock_result)
    print("Sending POST /api/ask request...")
    response = client.post(
        "/api/ask",
        json={"question": "What is the project status?"},
        headers={"X-API-Key": settings.API_SECRET_KEY}
    )
    if response.status_code == 200:
        print("SUCCESS! Status Code: 200")
        print("Full JSON Response:")
        import json
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"FAILED! Status Code: {response.status_code}")
        print(response.text)
if __name__ == "__main__":
    test_api_call()
