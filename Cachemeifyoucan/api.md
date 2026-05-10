# Self-Auditing RAG API Documentation

All endpoints require the `X-API-Key` header for authentication.

## 1. Ask Question (RAG)
**Endpoint**: `POST /api/ask`
**Description**: Triggers the self-auditing RAG pipeline to answer a question based on ingested knowledge.

### Request
```json
{
  "question": "string"
}
```

### Response
```json
{
  "final_answer": "string",
  "temporal_drift_warning": "string | null",
  "lightweight_judge_result": "string (SUFFICIENT/INSUFFICIENT)",
  "epistemic_judge_result": "string (A/B/UNKNOWN)",
  "judge_reasoning": "string",
  "judge_confidence": 0.98,
  "real_chain": { "claim": "...", "source": "..." },
  "fake_chain": { "claim": "...", "source": "..." },
  "sources": [
    { "source": "project_plan.pdf", "location": "page: 1" }
  ],
  "pii_report": [
    { "entity": "PERSON", "status": "Redacted" }
  ]
}
```

---

## 2. Ingest Multimedia (PDF, TXT, Audio)
**Endpoint**: `POST /api/ingest`
**Description**: Uploads and processes a file into the vector store.
**Supports**: `.pdf`, `.txt`, `.md`, `.csv`, `.jpg`, `.png`, `.mp3`, `.wav`.

### Request (Multipart/Form-Data)
- `file`: Binary data of the file to ingest.

### Response
```json
{
  "status": "success",
  "filename": "report.pdf"
}
```

---

## 3. Health Check
**Endpoint**: `GET /health`
**Description**: Verifies API and Database status.

### Response
```json
{
  "api": "ok",
  "db": "ok"
}
```

## Security
Endpoints are protected by `X-API-Key` middleware. The key is managed via the `API_SECRET_KEY` environment variable in `backend/.env`.
