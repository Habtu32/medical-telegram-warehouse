import os
import json
import glob
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
from loguru import logger

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

DB_NAME = os.getenv("DB_NAME")  # medical_warehouse_utf8
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Compute path relative to project root (one level above `src`)
RAW_DATA_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "data", "raw", "telegram_messages")
)

# -----------------------------
# DB Engine
# -----------------------------
def get_db_engine():
    url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)

# -----------------------------
# Loader
# -----------------------------
def load_raw_data():
    engine = get_db_engine()

    json_files = glob.glob(
        os.path.join(RAW_DATA_DIR, "**", "*.json"), recursive=True
    )

    if not json_files:
        logger.warning("No JSON files found.")
        return

    records = []

    for file in json_files:
        with open(file, "r", encoding="utf-8") as f:
            records.extend(json.load(f))

    df = pd.DataFrame(records)

    # ✅ Column alignment
    df = df.rename(
        columns={
            "id": "message_id",
            "date": "message_date",
            "content": "message_text",
            "channel": "channel_name",
        }
    )

    # ✅ Type cleanup
    df["message_date"] = pd.to_datetime(df["message_date"], errors="coerce")

    logger.info(f"Loaded {len(df)} rows from JSON.")

    with engine.begin() as conn:
        inspector = inspect(conn)

        if "raw_telegram_data" not in inspector.get_table_names():
            df.to_sql(
                "raw_telegram_data",
                conn,
                index=False,
                method="multi"
            )
            logger.success("Created raw_telegram_data table.")
        else:
            conn.execute(text("TRUNCATE TABLE raw_telegram_data"))
            df.to_sql(
                "raw_telegram_data",
                conn,
                if_exists="append",
                index=False,
                method="multi"
            )
            logger.success("Reloaded raw_telegram_data table.")

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    load_raw_data()