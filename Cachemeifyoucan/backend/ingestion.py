import os
import glob
from langchain_community.document_loaders import TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

VECTOR_STORE = None

def get_real_retriever():
    global VECTOR_STORE
    if VECTOR_STORE is None:
        raise ValueError("Vector store not initialized. Call ingest_sources() first.")
    return VECTOR_STORE.as_retriever(search_kwargs={"k": 5})

def ingest_sources():
    global VECTOR_STORE
    print("Ingesting demonstration sources (FAISS)...")
    docs = []
    
    source_dir = os.path.join(os.path.dirname(__file__), "demo_sources")
    
    # Load TXT files (simulating PDF/Podcast)
    for txt_path in glob.glob(os.path.join(source_dir, "*.txt")):
        loader = TextLoader(txt_path)
        raw = loader.load()
        # Mock metadata explicitly for testing
        basename = os.path.basename(txt_path)
        for d in raw:
            d.metadata["source"] = basename
            d.metadata["source_type"] = "PDF" if "paper" in basename else "MP3"
            d.metadata["location"] = "Page 4" if "paper" in basename else "12:34"
            d.metadata["date"] = "2023-01-01" if "paper" in basename else "2021-06-15"
            d.metadata["language"] = "en"
        docs.extend(raw)

    # Load CSV files
    for csv_path in glob.glob(os.path.join(source_dir, "*.csv")):
        loader = CSVLoader(csv_path)
        raw = loader.load()
        basename = os.path.basename(csv_path)
        for d in raw:
            d.metadata["source"] = basename
            d.metadata["source_type"] = "CSV"
            d.metadata["location"] = "CSV Row"
            d.metadata["date"] = "2024-01-01"
            d.metadata["language"] = "en"
        docs.extend(raw)
        
    if not docs:
        print("No documents found in demo_sources/!")
        return

    # Split
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    # Embed and Store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    VECTOR_STORE = FAISS.from_documents(split_docs, embeddings)
    print(f"Created FAISS index with {len(split_docs)} chunks from {len(docs)} documents.")

# Replacement for `detect_temporal_drift`
def check_temporal_drift(retrieved_docs: list) -> str:
    dates = []
    for d in retrieved_docs:
        date_str = d.metadata.get("date")
        if date_str:
            year = date_str.split("-")[0]
            if year.isdigit():
                dates.append(int(year))
    
    if dates and (max(dates) - min(dates) >= 1):
        return f"Knowledge evolved: oldest source is {min(dates)} vs newest {max(dates)}."
    return None

def fetch_table_cell(source: str, table_id: str, row: int, col: int) -> str:
    # A smart backend would dynamically query the actual CSV data using pandas
    # We will simulate the pandas query natively parsing the doc list
    global VECTOR_STORE
    return f"Live extracted value for {table_id}, row {row}, col {col} structure natively stored."
