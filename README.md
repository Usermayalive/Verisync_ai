# Cache Me If You Can — Multi-Document Intelligence Assistant

> **A self-auditing, trust-aware assistant that proves its own reliability.**

## Problem Statement

Users need to query across diverse public sources (PDFs, YouTube, podcasts, CSVs, images) but face a **trust gap**:
- **Hallucination** — answers drawn from LLM training memory, not from provided documents.
- **No source transparency** — no way to verify which document, page, or timestamp supports a claim.
- **Temporal confusion** — cannot distinguish genuine contradiction from knowledge evolution.
- **No graceful refusal** — the system answers even when the corpus lacks information.

**Our goal:** Build an assistant that is *provably grounded* — it shows its evidence chain, passes its own adversarial hallucination test, or refuses honestly.x

---

## Three-Layer Self-Auditing Pipeline

| Layer | Name | Purpose |
|:---:|:---|:---|
| 0 | **Lightweight Judge** | Fast filter: SUFFICIENT → direct answer, AMBIGUOUS → full audit, INSUFFICIENT → refusal |
| 1 | **Causal Autopsy** | Traces every claim to raw evidence (table cell, timestamp, CSV row) |
| 2 | **Fake Chain Generator** | Creates a plausible hallucinated chain using invented sources |
| 3 | **Epistemic Judge** | Compares real vs fake chain in random order, identifies the grounded one |

**Why unique:** Most RAG systems retrieve and generate once. Ours adversarially tests itself before answering. It's *"trust me"* vs. *"watch me verify."*

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (UI)                        │
│  Chat interface, Audit Trail panel, Confidence bars, Sources    │
└───────────────────────────┬─────────────────────────────────────┘
                            │ POST /api/ask
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (main.py)                       │
│  POST /api/ask · POST /api/ingest · GET /health                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│           LangGraph State Machine (pipeline/)                   │
│  retrieve → lightweight_judge → (conditional routing)           │
│  ├─ SUFFICIENT → direct_answer → END                           │
│  ├─ AMBIGUOUS → causal_autopsy → fake_chain → epistemic_judge  │
│  │              → synthesize_answer / refusal → END             │
│  └─ INSUFFICIENT → refusal → END                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│            Data Layer (retrieval_service/)                      │
│  PostgreSQL + pgvector · Hybrid retriever (Vector + BM25 + RRF)│
│  Loaders: PDF, YouTube, Podcast, CSV, Image                    │
│  Tools: PII (Presidio), Dedup, Temporal Drift, Translation     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11 MVP Requirements

| # | Requirement | Implementation |
|:---:|:---|:---|
| 1 | Multi-source ingestion (≥4 types) | PDF, YouTube, podcast, CSV, image via LangChain loaders |
| 2 | Justified retrieval architecture | Hybrid (vector + BM25 + RRF) |
| 3 | NL Q&A with source citations | Every answer includes citations with source + location |
| 4 | Summarisation & synthesis | Cross-source synthesis via merging evidence chains |
| 5 | Source transparency | RightPanel shows real chain and rejected fake chain |
| 6 | Temporal drift detection | `detect_temporal_drift()` compares dates; warning badge in UI |
| 7 | Knowledge boundary awareness | Lightweight Judge → INSUFFICIENT or Judge fails → refusal |
| 8 | PII detection & redaction | Presidio at ingestion; report shown in UI sidebar |
| 9 | Table & chart understanding | pdfplumber cell extraction; traced to exact cell in chain |
| 10 | Cross-lingual retrieval | Helsinki-NLP translation at ingestion; English answers |
| 11 | Duplicate detection | Cosine similarity >0.95 → flagged in UI |

---

## Quick Start

### Prerequisites
- Python 3.10+, Node.js 18+, Docker

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Edit with your GOOGLE_API_KEY, DATABASE_URL
docker-compose up -d   # Start PostgreSQL + pgvector
python ingest_all_demo_sources.py   # Populate DB with demo data
uvicorn backend.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Visit **http://localhost:3000** and start querying.

---

## Project Structure

```
Cachemeifyoucan/
├── backend/
│   ├── main.py                      # FastAPI server
│   ├── config.py                    # Settings (Pydantic)
│   ├── ingest_all_demo_sources.py   # One-click demo ingestion
│   ├── pipeline/                    # LangGraph orchestration
│   │   ├── graph.py                 # State machine definition
│   │   ├── nodes.py                 # Node functions
│   │   ├── prompts.py              # All LLM prompts
│   │   ├── conditional.py          # Routing logic
│   │   └── state.py                # GraphState schema
│   ├── retrieval_service/           # Data layer
│   │   ├── ingestion/              # Loaders, splitter, pipeline
│   │   ├── retrieval/              # Hybrid retriever
│   │   ├── storage/                # PGVector, Postgres tables
│   │   └── tools/                  # PII, dedup, translation, drift
│   ├── ui/                          # Streamlit fallback client
│   └── tests/                       # Test suites
├── frontend/
│   ├── src/app/dashboard/page.tsx   # Main dashboard
│   ├── src/components/ChatArea.tsx  # Chat interface
│   ├── src/components/RightPanel.tsx # Audit trail panel
│   └── src/components/Sidebar.tsx   # Chat history
└── README.md                        # This file
```

---

## Tech Stack

| Layer | Technology |
|:---|:---|
| LLM | Google Gemini (gemini-3-flash-preview) |
| Orchestration | LangGraph + LangChain |
| Backend API | FastAPI + Uvicorn |
| Vector DB | PostgreSQL + pgvector |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Frontend | Next.js 16 + TailwindCSS |
| PII | Presidio Analyzer + Anonymizer |
| Translation | Helsinki-NLP/opus-mt |
# Verisync_ai
