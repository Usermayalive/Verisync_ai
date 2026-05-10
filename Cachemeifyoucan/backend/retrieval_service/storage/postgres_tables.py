import psycopg2
import json
from backend.config import settings
from backend.utils.logger import get_logger
logger = get_logger("RetrievalService.Postgres")
def init_tables():
    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                session_id TEXT DEFAULT 'default',
                source_name TEXT,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                document_type TEXT,
                telemetry JSONB DEFAULT '{}'::jsonb,
                PRIMARY KEY (session_id, source_name)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tables (
                id SERIAL PRIMARY KEY,
                session_id TEXT DEFAULT 'default',
                source_name TEXT,
                table_id TEXT,
                row_data JSONB
            );
        """)
        conn.commit()
    except Exception as e:
        logger.error(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
def store_table_data(session_id, source_name, table_id, rows):
    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO sources (session_id, source_name) VALUES (%s, %s) ON CONFLICT (session_id, source_name) DO NOTHING", 
            (session_id, source_name)
        )
        for row in rows:
            cur.execute(
                "INSERT INTO tables (session_id, source_name, table_id, row_data) VALUES (%s, %s, %s, %s)",
                (session_id, source_name, table_id, json.dumps(row))
            )
        conn.commit()
    except Exception as e:
        logger.error(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
def get_table_cell_value(session_id, source, table_id, row, col):
    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT row_data FROM tables WHERE session_id = %s AND source_name = %s AND table_id = %s LIMIT 1 OFFSET %s",
            (session_id, source, table_id, row)
        )
        result = cur.fetchone()
        if result and len(result[0]) > col:
            return str(result[0][col])
        return ""
    except Exception as e:
        logger.error(f"Error: {e}")
        return ""
    finally:
        cur.close()
        conn.close()
def get_all_source_names(session_id="default"):
    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute("SELECT source_name FROM sources WHERE session_id = %s", (session_id,))
        return [r[0] for r in cur.fetchall()]
    except Exception as e:
        logger.error(f"Error: {e}")
        return []
    finally:
        cur.close()
        conn.close()
def update_source_telemetry(session_id, source_name, telemetry):
    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO sources (session_id, source_name, telemetry) VALUES (%s, %s, %s) ON CONFLICT (session_id, source_name) DO UPDATE SET telemetry = sources.telemetry || EXCLUDED.telemetry",
            (session_id, source_name, json.dumps(telemetry))
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
def get_global_telemetry(session_id="default"):
    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute("SELECT telemetry FROM sources WHERE session_id = %s", (session_id,))
        results = cur.fetchall()
        merged = {"duplicate_sources": [], "pii_entities": []}
        for r in results:
            data = r[0]
            if "duplicates" in data: merged["duplicate_sources"].extend(data["duplicates"])
            if "pii" in data: merged["pii_entities"].append(data["pii"])
        return merged
    except Exception as e:
        logger.error(f"Error: {e}")
        return {}
    finally:
        cur.close()
        conn.close()
