import os
import shutil
import tempfile
from fastapi import FastAPI, HTTPException, Header, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Literal
import traceback
import psycopg2
from backend.config import settings
from backend.pipeline.graph import build_graph
from backend.utils.logger import get_logger
from backend.retrieval_service.ingestion.pipeline import full_ingest_pipeline
logger = get_logger("Backend.Main")
app = FastAPI(
    title="Self-Auditing RAG API",
    description="Production-ready API for the self-auditing pipeline.",
    version="1.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
pipeline_graph = build_graph()
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"
    chat_history: Optional[List[Dict[str, str]]] = []
    model: Optional[Literal["gemini", "deepseek"]] = None
class QueryResponse(BaseModel):
    final_answer: str
    temporal_drift_warning: Optional[str] = None
    lightweight_judge_result: str
    epistemic_judge_result: Optional[str] = None
    judge_reasoning: Optional[str] = None
    judge_confidence: float = 0.0
    max_similarity: float = 0.0
    real_chain: Optional[Dict[str, Any]] = None
    fake_chain: Optional[Dict[str, Any]] = None
    sources: List[Dict[str, str]] = []
    source_manifest: List[str] = []
    duplicate_sources: List[str] = []
    pii_report: List[Dict[str, Any]] = []

@app.post("/api/ask", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
async def ask_question(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        # Pass model selection to pipeline_graph
        result_state = pipeline_graph.invoke({
            "question": request.question,
            "session_id": request.session_id,
            "chat_history": request.chat_history or [],
            "model": request.model
        })
        docs = result_state.get("documents", [])
        sources_list = [
            {
                "source": d.metadata.get("source", "Unknown"),
                "location": d.metadata.get("location", "Unknown"),
                "source_type": d.metadata.get("source_type", d.metadata.get("type", "Unknown")),
                "language": d.metadata.get("language", d.metadata.get("source_language", "en")),
            }
            for d in docs
        ]
        return QueryResponse(
            final_answer=result_state.get("final_answer", "No answer generated."),
            temporal_drift_warning=result_state.get("temporal_drift_warning"),
            lightweight_judge_result=result_state.get("lightweight_judge_result", "UNKNOWN"),
            epistemic_judge_result=result_state.get("epistemic_judge_result"),
            judge_reasoning=result_state.get("judge_reasoning"),
            judge_confidence=result_state.get("judge_confidence", 0.0),
            max_similarity=result_state.get("max_similarity", 0.0),
            real_chain=result_state.get("real_chain"),
            fake_chain=result_state.get("fake_chain"),
            sources=sources_list,
            source_manifest=result_state.get("source_manifest", []),
            duplicate_sources=result_state.get("duplicate_sources", []),
            pii_report=result_state.get("pii_report", [])
        )
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error")
@app.get("/health")
def health_check():
    status = {"api": "ok", "db": "unknown"}
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.close()
        status["db"] = "ok"
    except Exception as e:
        status["db"] = f"error: {str(e)}"
    return status
@app.post("/api/ingest_url", dependencies=[Depends(verify_api_key)])
async def ingest_url(request: Dict[str, str]):
    url = request.get("url")
    session_id = request.get("session_id", "default")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        logger.info(f"Ingesting URL: {url} into session {session_id}")
        full_ingest_pipeline([url], session_id=session_id)
        return {"status": "success", "url": url}
    except Exception as e:
        logger.error(f"URL Ingestion Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest", dependencies=[Depends(verify_api_key)])
async def ingest_file(file: UploadFile = File(...), session_id: str = Form("default")):
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        full_ingest_pipeline([file_path], session_id=session_id)
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        logger.error(f"Ingestion Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(temp_dir)
