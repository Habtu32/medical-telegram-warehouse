import os
import json
import glob
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Database Configuration
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Paths
RAW_DATA_DIR = os.path.join("data", "raw", "telegram_messages")

def get_db_engine():
    try:
        url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(url)
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise

def load_raw_data():
    engine = get_db_engine()
    
    json_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.json"))
    
    all_data = []
    
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure data is a list of dicts
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    logger.warning(f"File {file} does not contain a list of messages")
        except Exception as e:
            logger.error(f"Error reading file {file}: {e}")
    
    if not all_data:
        logger.warning("No data found to load.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Basic cleaning/formatting if necessary for raw load
    # Ensure date is parsed correctly if needed, but for raw load, keeping as string is mostly fine
    # or let pandas handle it.
    
    logger.info(f"Loaded {len(df)} rows from JSON files.")
    
    try:
        # Load to 'raw_telegram_data' table
        # We replace the table for this initial load logic, or append?
        # Let's append, but for idempotency in this demo, 'replace' might be safer for re-runs.
        # But for 'raw' usually we append. I'll use 'replace' for now to allow easy iteration.
        df.to_sql('raw_telegram_data', engine, if_exists='replace', index=False)
        logger.success("Successfully loaded data into 'raw_telegram_data' table.")
    except Exception as e:
        logger.error(f"Error writing to database: {e}")

if __name__ == "__main__":
    load_raw_data()
