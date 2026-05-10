import os
import sys

# Ensure the project root is in PYTHONPATH
sys.path.append(os.getcwd())

from backend.retrieval_service.ingestion.loaders import DocumentLoader

audio_file = "backend/samples/[SPOTDOWNLOADER.COM] Udaan (Nadi Mein Talab Hai).mp3.mp3"

print(f"Loading and transcribing: {audio_file}")
docs = DocumentLoader.load_audio(audio_file)

if docs:
    transcription = docs[0].page_content
    with open("parse.txt", "w", encoding="utf-8") as f:
        f.write(transcription)
    print("Successfully wrote transcription to parse.txt")
else:
    print("Failed to transcribe audio.")
