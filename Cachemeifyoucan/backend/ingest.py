import argparse
import os
import sys
from backend.retrieval_service.ingestion.pipeline import full_ingest_pipeline
from backend.retrieval_service.storage.postgres_tables import init_tables
from backend.utils.logger import get_logger
logger = get_logger("Ingest.CLI")
def parse_args():
    parser = argparse.ArgumentParser(description="Multi-Modal Ingestion CLI")
    parser.add_argument("--path", required=True, help="Path to file or directory to ingest")
    parser.add_argument("--init", action="store_true", help="Initialize database tables before ingestion")
    return parser.parse_args()
def main():
    args = parse_args()
    if args.init:
        logger.info("Initializing tables...")
        init_tables()
    if not os.path.exists(args.path):
        logger.error(f"Path not found: {args.path}")
        sys.exit(1)
    logger.info(f"Starting ingestion for: {args.path}")
    try:
        manifest = full_ingest_pipeline([args.path])
        logger.info(f"Ingestion complete. Sources: {manifest}")
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()
