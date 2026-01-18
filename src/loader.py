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

DB_NAME = os.getenv("DB_NAME")  # e.g., medical_warehouse_utf8
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Path to raw JSON files
RAW_DATA_DIR = "../data/raw/telegram_messages"

# -----------------------------
# Create DB engine
# -----------------------------
def get_db_engine():
    try:
        url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(url)
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise

# -----------------------------
# UTF-8 normalization function
# -----------------------------
def normalize_text(text):
    if isinstance(text, str):
        # Encode/decode to safely replace invalid characters
        return text.encode("utf-8", errors="replace").decode("utf-8")
    return text

# -----------------------------
# Load JSON files into Postgres
# -----------------------------
def load_raw_data():
    engine = get_db_engine()

    # Find all JSON files recursively
    json_files = glob.glob(os.path.join(RAW_DATA_DIR, "**", "*.json"), recursive=True)
    if not json_files:
        logger.warning("No JSON files found to load.")
        return

    all_data = []

    for file in json_files:
        try:
            # Try utf-8, fallback to windows-1252 if necessary
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except UnicodeDecodeError:
                with open(file, "r", encoding="windows-1252") as f:
                    data = json.load(f)

            if isinstance(data, list):
                all_data.extend(data)
            else:
                logger.warning(f"File {file} does not contain a list of messages")
        except Exception as e:
            logger.error(f"Error reading file {file}: {e}")

    if not all_data:
        logger.warning("No data found in JSON files.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    logger.info(f"Loaded {len(df)} rows from JSON files.")

    # -----------------------------
    # Normalize text columns
    # -----------------------------
    text_columns = ['content', 'channel', 'media_path']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)

    # -----------------------------
    # Rename columns to match dbt staging
    # -----------------------------
    df.rename(columns={
        'id': 'message_id',
        'content': 'message_text',
        'channel': 'channel_name',
        'media_path': 'image_path',
        'date': 'message_date'
    }, inplace=True)

    # -----------------------------
    # Load into Postgres
    # -----------------------------
    try:
        with engine.begin() as conn:
            inspector = inspect(conn)
            if "raw_telegram_data" not in inspector.get_table_names():
                logger.info("'raw_telegram_data' table does not exist. Creating...")
                df.to_sql(
                    "raw_telegram_data",
                    conn,
                    if_exists="fail",  # create table
                    index=False,
                    method="multi"
                )
                logger.success("Created 'raw_telegram_data' table and inserted data.")
            else:
                # Table exists — truncate & reload
                conn.execute(text("TRUNCATE TABLE raw_telegram_data RESTART IDENTITY;"))
                df.to_sql(
                    "raw_telegram_data",
                    conn,
                    if_exists="append",
                    index=False,
                    method="multi"
                )
                logger.success("Successfully reloaded normalized data into 'raw_telegram_data'.")
    except Exception as e:
        logger.error(f"Error writing to database: {e}")

# -----------------------------
# Run loader
# -----------------------------
if __name__ == "__main__":
    load_raw_data()
