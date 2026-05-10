import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
# Add project root to sys.path to allow absolute imports of 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.retrieval_service.ingestion.pipeline import full_ingest_pipeline
from backend.retrieval_service.storage.postgres_tables import init_tables
from backend.utils.logger import get_logger

logger = get_logger("DemoIngestion")

DEMO_DIR = os.path.join(os.path.dirname(__file__), "demo_sources")

def main():
    logger.info("Initializing database tables...")
    init_tables()

    sources = []
    if os.path.isdir(DEMO_DIR):
        for fname in os.listdir(DEMO_DIR):
            fpath = os.path.join(DEMO_DIR, fname)
            if os.path.isfile(fpath):
                sources.append(fpath)

    if not sources:
        logger.warning(f"No files found in {DEMO_DIR}. Add PDF, CSV, TXT, or image files to demo_sources/ and re-run.")
        return

    logger.info(f"Found {len(sources)} source files: {[os.path.basename(s) for s in sources]}")
    full_ingest_pipeline(sources)
    logger.info("Demo ingestion complete.")

if __name__ == "__main__":
    main()
