# Cache Me If You Can: Self-Auditing RAG Pipeline ⚖️

This repository contains a production-grade, three-layer self-auditing RAG (Retrieval-Augmented Generation) system. Unlike standard RAG pipelines, this system is **provably grounded**—it adversarially tests its own reasoning chains before presenting an answer to the user to guarantee zero hallucinations.

## 🚀 Key Features (11/11 MVP Met)
- **Three-Layer Orchestration**: Lightweight Judge (Filter), Causal Autopsy (Evidence Tracing), and Epistemic Judge (Adversarial Audit).
- **Multi-Modal Ingestion**: Handles PDFs (with table extraction), YouTube transcripts, MP3 Podcasts (Whisper), CSVs, and Images (OCR).
- **Production Storage**: PGVector (PostgreSQL) + BM25 Hybrid Search with RRF Fusion.
- **Safety & Quality**: Automated PII Redaction (Presidio), Duplicate Detection, and Temporal Drift Detection.
- **Cross-Lingual support**: Automated translation using Helsinki-NLP transformers.

---

## 🏗 System Architecture

The pipeline is built using **LangGraph** for stateful orchestration and **LangChain** for modular retrieval and ingestion.

1. **Lightweight Judge**: Fast-tracks 80% of queries if a direct answer is evident.
2. **Adversarial Audit**: For complex queries, generates a 'Real Chain' of evidence and a 'Fake Chain' (hallucinated).
3. **Epistemic Judge**: A blinded judge adjudicates which chain is grounded in the actual corpus.

---

## 🛠 Setup & Installation

### 1. Prerequisites
- PostgreSQL running locally
- Python 3.9+
- Google Gemini API Key (or OpenAI API Key)

### 2. Setup Database & Dependencies
Ensure your PostgreSQL server is running and you have created a database (e.g. `cache_me_db`). Then install dependencies:
```bash
cd backend
pip install -r requirements.txt
python setup_env.py  # Run the environment setup script
```

### 3. Configuration
Create a `.env` file in the `backend/` directory:
```env
GOOGLE_API_KEY="your-gemini-key"
DATABASE_URL="postgresql://user:password@localhost:5432/cache_me_db"
API_SECRET_KEY="change-this-in-prod"
```

---

## 🚦 Running the System

### Power on the Backend (FastAPI)
```bash
uvicorn main:app --reload
```
*Access API Docs at: http://localhost:8000/docs*

### Power on the Frontend (Streamlit)
```bash
streamlit run ui/app.py
```

### Run Full certification Suite
```bash
python test_requirements.py
```

---

## 🧪 Testing the 11 MVP Requirements
Our automated suite `test_requirements.py` validates:
- **Direct Answer**: "What is the main finding?"
- **Temporal Drift**: "Compare 2021 vs 2023..."
- **Table Extraction**: "What is the value in Table 2, row 3?"
- **PII/Duplicates**: Automatic filtering and reporting.
- **Cross-Lingual**: "What does the French PDF say...?"

---

## 📂 Project Structure
- `backend/main.py`: FastAPI entry point.
- `backend/pipeline/`: LangGraph logic, prompts, and nodes.
- `backend/retrieval_service/`: Ingestion, Storage, and Tooling (PII, Translation).
- `backend/ui/`: Streamlit dashboard.
- `backend/demo_sources/`: Sample data for ingestion.
