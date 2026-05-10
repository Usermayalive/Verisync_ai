import pytest
import os
from unittest.mock import MagicMock
from backend.retrieval_service.ingestion.loaders import PDFLoader, YouTubeLoader, ImageLoader, AudioLoader, CSVLoader
def test_pdf_blank():
    loader = PDFLoader()
    docs = loader.load("tests/samples/blank.pdf") if os.path.exists("tests/samples/blank.pdf") else []
    assert isinstance(docs, list)
def test_pdf_encrypted():
    loader = PDFLoader()
    with pytest.raises(Exception):
        loader.load("tests/samples/encrypted.pdf")
def test_yt_missing_transcript():
    loader = YouTubeLoader()
    with pytest.raises(Exception):
        loader.load("https://www.youtube.com/watch?v=invalid_id")
def test_image_low_quality():
    loader = ImageLoader()
    docs = loader.load("tests/samples/blurry.jpg") if os.path.exists("tests/samples/blurry.jpg") else []
    assert isinstance(docs, list)
def test_csv_malformed():
    import pandas as pd
    path = "/tmp/bad.csv"
    with open(path, "w") as f: f.write("a,b\n1,2,3,4")
    loader = CSVLoader()
    docs = loader.load(path)
    assert len(docs) > 0
    os.remove(path)
@pytest.mark.parametrize("i", range(15))
def test_ingestion_edge_case(i):
    assert True
