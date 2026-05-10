import streamlit as st
import requests
import uuid

API_URL = "http://localhost:8000/api/ask"
INGEST_URL = "http://localhost:8000/api/ingest"
API_KEY = "change-this-in-prod"
HEADERS = {"x-api-key": API_KEY}

# Track session isolation
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.set_page_config(page_title="Self-Auditing RAG", layout="wide")

st.title("⚖️ Provably Grounded Assistant")
st.markdown("Ask natural language questions. The backend API will adversarially test itself before answering.")

with st.sidebar:
    st.header("📚 Ingestion Portal")
    st.markdown("Upload test documentation directly to the Postgres Vector Store.")
    uploaded_file = st.file_uploader("Select a file", type=["pdf", "csv", "mp3", "png", "txt", "md"])
    
    if uploaded_file is not None:
        if st.button("Ingest to Database"):
            with st.spinner("Ingesting file into PGVector..."):
                # Pass file inside multipart form
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    res = requests.post(INGEST_URL, headers=HEADERS, files=files)
                    if res.status_code == 200:
                        st.success(f"✅ {uploaded_file.name} ingested successfully!")
                    else:
                        st.error(f"Failed to ingest: {res.text}")
                except Exception as e:
                    st.error(f"Local Server Error: Ensure FastAPI is running on :8000\n{e}")

# Main Interface
query = st.text_input("What would you like to know?", "What is the main finding of the research paper?")

if st.button("Ask") and query.strip():
    with st.spinner("Calling FastAPI Backend..."):
        try:
            # Pass session UI parameters and Security Headers
            payload = {"question": query, "session_id": st.session_state.session_id}
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            
            if response.status_code != 200:
                st.error(f"Error from API: {response.text}")
            else:
                data = response.json()
                
                # Sidebar logic after fetch
                st.sidebar.header("Metadata & Data Quality")
                if data.get("duplicate_sources"):
                    st.sidebar.warning(f"⚠️ Duplicates Detected: {', '.join(data['duplicate_sources'])}")
                else:
                    st.sidebar.success("✅ No Duplicate Sources")
                    
                if data.get("pii_report"):
                    for item in data["pii_report"]:
                        st.sidebar.info(f"🔒 PII Redacted: {item.get('entity', 'Unknown')} ({item.get('status', 'Redacted')})")
                
                st.success("API Execution Complete!")
                
                # Answer
                st.write("### Answer")
                st.write(data.get("final_answer", "No answer generated."))
                
                # Drift Indicator
                if data.get("temporal_drift_warning"):
                    st.warning(f"Temporal Drift: {data['temporal_drift_warning']}")
                
                # Show Metrics and Paths
                judge_res = data.get("lightweight_judge_result")
                st.write(f"**Lightweight Judge Decision:** {judge_res}")
                
                if judge_res in ["AMBIGUOUS", "INSUFFICIENT"] and data.get("epistemic_judge_result"):
                    conf = data.get("judge_confidence", 0)
                    epistemic_res = data.get("epistemic_judge_result")
                    st.progress(conf, text=f"Epistemic Judge Confidence Score: {conf*100:.1f}%")
                    
                    with st.expander("⚖️ Epistemic Judge's Reasoning"):
                        st.write(f"**Identified Real Chain:** {epistemic_res}")
                        st.write(data.get("judge_reasoning"))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander("🔗 Real Evidence Chain"):
                            if data.get("real_chain"):
                                st.json(data["real_chain"])
                            else:
                                st.write("Not available.")
                    with col2:
                        with st.expander("🚫 Rejected Hallucinated Chain"):
                            if data.get("fake_chain"):
                                st.json(data["fake_chain"])
                            else:
                                st.write("Not available.")
                                
                with st.expander("📚 Retrieved Grounding Sources"):
                    sources = data.get("sources", [])
                    if sources:
                        for i, d in enumerate(sources):
                            st.write(f"**{i+1}. {d.get('source')}** (Loc: {d.get('location')})")
                    else:
                        st.write("No direct sources cited.")
                        
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to backend. Is the FastAPI server running on localhost:8000?")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
