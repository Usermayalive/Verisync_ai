import logging
import os
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import pdfplumber
from langchain_community.document_loaders import (
    PyPDFLoader, 
    YoutubeLoader, 
    CSVLoader,
    UnstructuredImageLoader,
    TextLoader
)
from langchain_core.documents import Document
from backend.utils.logger import get_logger
logger = get_logger("RetrievalService.Loaders")
class DocumentLoader:
    @staticmethod
    def load_pdf(file_path: str) -> Tuple[List[Document], List[Dict[str, Any]]]:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        extracted_tables = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    if tables:
                        for j, table in enumerate(tables):
                            table_id = f"table_{i}_{j}"
                            extracted_tables.append({
                                "table_id": table_id,
                                "rows": table
                            })
                            if i < len(docs):
                                if "table_ids" not in docs[i].metadata:
                                    docs[i].metadata["table_ids"] = []
                                docs[i].metadata["table_ids"].append(table_id)
        except Exception as e:
            logger.warning(f"Error {file_path}: {e}")
        return docs, extracted_tables
    @staticmethod
    def load_youtube(url: str) -> List[Document]:
        import re
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            # Extract video ID from URL
            match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
            if not match:
                logger.error(f"Could not extract video ID from URL: {url}")
                return []
            video_id = match.group(1)
            
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)

            # Bundle transcript into ~500-char segments
            docs = []
            current_text = ""
            current_start = 0.0
            for entry in transcript:
                if not current_text:
                    current_start = entry.start
                current_text += " " + entry.text
                if len(current_text) >= 500:
                    mins = int(current_start // 60)
                    secs = int(current_start % 60)
                    docs.append(Document(
                        page_content=current_text.strip(),
                        metadata={
                            "source": url,
                            "location": f"timestamp {mins:02d}:{secs:02d}",
                            "source_type": "YouTube",
                            "start_seconds": current_start,
                        }
                    ))
                    current_text = ""
            # Flush remaining text
            if current_text.strip():
                mins = int(current_start // 60)
                secs = int(current_start % 60)
                docs.append(Document(
                    page_content=current_text.strip(),
                    metadata={
                        "source": url,
                        "location": f"timestamp {mins:02d}:{secs:02d}",
                        "source_type": "YouTube",
                        "start_seconds": current_start,
                    }
                ))
            logger.info(f"Loaded {len(docs)} transcript segments from YouTube: {url}")
            return docs
        except Exception as e:
            logger.error(f"YouTube load failed for {url}: {e}")
            return []
    @staticmethod
    def load_csv(file_path: str) -> List[Document]:
        loader = CSVLoader(file_path=file_path)
        return loader.load()
    @staticmethod
    def load_txt(file_path: str) -> List[Document]:
        loader = TextLoader(file_path)
        return loader.load()
    @staticmethod
    def load_image(file_path: str) -> List[Document]:
        try:
            loader = UnstructuredImageLoader(file_path)
            return loader.load()
        except:
            return []
    @staticmethod
    def load_audio(file_path: str) -> List[Document]:
        try:
            from transformers import pipeline
            asr = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
            result = asr(file_path, chunk_length_s=30, batch_size=8)
            return [Document(page_content=result["text"], metadata={"source": file_path, "type": "audio"})]
        except Exception as e:
            logger.error(f"Audio Error: {e}")
            return [Document(page_content="[Audio transcription failed]", metadata={"source": file_path, "type": "audio"})]

    @staticmethod
    def load_web_page(url: str) -> List[Document]:
        import requests
        from bs4 import BeautifulSoup
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            # Remove script/style elements
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            # Split into manageable page-like chunks (~2000 chars each)
            pages = []
            chunk_size = 2000
            for i in range(0, len(text), chunk_size):
                page_text = text[i:i+chunk_size]
                if page_text.strip():
                    pages.append(Document(
                        page_content=page_text,
                        metadata={"source": url, "location": f"chars {i}-{i+chunk_size}", "source_type": "web"}
                    ))
            logger.info(f"Loaded {len(pages)} chunks from web page: {url}")
            return pages
        except Exception as e:
            logger.error(f"Web page load error for {url}: {e}")
            return []

def load_documents(source: str) -> Tuple[List[Document], List[Dict[str, Any]]]:
    path = Path(source)
    all_docs = []
    all_tables = []
    if "youtube.com" in source or "youtu.be" in source:
        all_docs = DocumentLoader.load_youtube(source)
    elif source.startswith("http://") or source.startswith("https://"):
        all_docs = DocumentLoader.load_web_page(source)
    elif path.exists():
        ext = path.suffix.lower()
        if ext == ".pdf":
            all_docs, all_tables = DocumentLoader.load_pdf(str(path))
        elif ext == ".csv":
            all_docs = DocumentLoader.load_csv(str(path))
        elif ext in [".txt", ".md"]:
            all_docs = DocumentLoader.load_txt(str(path))
        elif ext in [".jpg", ".jpeg", ".png"]:
            all_docs = DocumentLoader.load_image(str(path))
        elif ext in [".mp3", ".wav", ".m4a"]:
            all_docs = DocumentLoader.load_audio(str(path))
    return all_docs, all_tables
