# Medical Telegram Warehouse — Final Project README

Comprehensive end-to-end ELT data product that scrapes public Telegram channels for medical and health product information, ingests raw data into a Postgres-backed data warehouse, transforms the data with dbt into a dimensional star schema, enriches images with YOLOv8 object detection, and exposes analytical endpoints via a FastAPI service. This repository contains the code, models, and orchestration used for the 10 Academy: Artificial Intelligence Mastery Week 8 challenge (14–20 Jan 2026).

**Project goals**
- Build a reproducible, testable ELT pipeline for Telegram-sourced data.
- Provide reliable analytical models (dbt) and tests to ensure data quality.
- Enrich visual data using object detection and integrate results into the warehouse.
- Serve business-facing analytical endpoints answering product-mentions, channel activity, message search, and visual content statistics.

## Architecture (high level)

- Extract: `src/scraper.py` (Telethon) collects messages and images into `data/raw/`.
- Load: `src/loader.py` reads raw JSON and writes to Postgres (`raw_telegram_data`).
- Transform: `medical_warehouse/` is a dbt project (staging -> marts) to produce `dim_` and `fct_` tables.
- Enrich: `src/yolo_detect.py` runs YOLOv8 over downloaded images and emits `data/yolo_detections.csv` to be loaded via dbt into `fct_image_detections`.
- Serve: `api/main.py` exposes FastAPI endpoints backed by SQL queries against the warehouse.
- Orchestration: `pipeline.py` defines a Dagster job that runs the full flow (scrape -> load -> dbt -> yolo).

## What’s in this repository

- `src/` — Scraper, loader, YOLO detection, and helpers
- `api/` — FastAPI app, database connection, Pydantic schemas
- `medical_warehouse/` — dbt project (models, tests, docs, profiles.yml)
- `pipeline.py` — Dagster job definition
- `data/` — Raw JSON and images; results like `yolo_detections.csv`
- `requirements.txt` — Python dependencies
- `yolov8n.pt` — YOLOv8-nano model (local copy for convenience)

## Quick Reproduction Guide

Prerequisites
- Python 3.10+ (virtualenv recommended)
- PostgreSQL (user with create DB privileges)
- dbt-core + dbt-postgres
- Optional: GPU drivers + dependencies for faster YOLO inference

1) Create virtual environment and install deps

```powershell
python -m venv venv
& venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Add secrets (create `.env` at repo root — DO NOT COMMIT)

- `TG_API_ID`, `TG_API_HASH` — from my.telegram.org
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

3) Scrape Telegram (extract)

```powershell
python -m src.scraper
```

Output: JSON files in `data/raw/telegram_messages/YYYY-MM-DD/{channel}.json` and images in `data/raw/images/{channel}/{date}/`.

4) Load raw JSON into Postgres (load)

```powershell
python -m src.loader
```

This creates/populates `raw_telegram_data` in your configured DB.

5) Run dbt transformations (transform)

```powershell
cd medical_warehouse
dbt deps
dbt run
dbt test
dbt docs generate
```

Notes:
- `profiles.yml` in `medical_warehouse/` is included — ensure credentials match or set `DBT_PROFILES_DIR`.

6) Run YOLO enrichment (optional)

```powershell
python -m src.yolo_detect
```

This produces `data/yolo_detections.csv` which the dbt model `fct_image_detections` can ingest.

7) Start the API

```powershell
uvicorn api.main:app --reload
```

Open docs at `http://127.0.0.1:8000/docs`.

8) Orchestrate & monitor via Dagster

```powershell
dagster dev -f pipeline.py
# visit http://localhost:3000 to run/monitor
```

## FastAPI Endpoints (summary)

- `GET /api/reports/top-products?limit=10` — top mentioned product terms
- `GET /api/channels/{channel_name}/activity` — channel-level posting activity and aggregates
- `GET /api/search/messages?query=...&limit=20` — search text in messages
- `GET /api/reports/visual-content` — image usage counts and average views by category

Schemas are defined in `api/schemas.py` and responses validated via Pydantic.

## Testing

- Run dbt tests:

```powershell
cd medical_warehouse
dbt test
```

- Unit tests (if present) live in `tests/` and can be executed with `pytest`.

## Observability & Logs

- Scraper logs are produced in `logs/` (Loguru). Dagster captures op logs in the UI. dbt prints execution output; `pipeline.py` captures and logs dbt stdout/stderr when run under Dagster.

## Design decisions & results (summary)

- Dimensional modeling: standard Kimball-style star schema with `dim_channels`, `dim_dates`, and `fct_messages` to make analytics performant and simple.
- Image enrichment: YOLOv8-nano was used to infer object classes and classify images into `promotional`, `product_display`, `lifestyle`, or `other` categories; these categories surface visual-content trends and engagement analysis.
- Trade-offs: Pre-trained YOLO models detect generic objects — domain-specific product recognition requires fine-tuning or a product classifier.

## Known issues & troubleshooting

- Ensure `medical_warehouse/profiles.yml` DB credentials match your environment or set `DBT_PROFILES_DIR` to the folder containing `profiles.yml`.
- If Dagster-run steps fail due to missing `scripts/` files, the pipeline was updated to run `src` modules (module-style execution). Ensure the project root is the Dagster working directory when running.
- Rate limiting from Telegram: add backoff and error handling for production scraping.

## File structure (top-level)

```
medical-telegram-warehouse/
├── medical_warehouse/   # dbt project
├── src/                 # scraper, loader, yolo scripts
├── api/                 # FastAPI app
├── data/                # raw JSON and images, detection CSV
├── pipeline.py          # Dagster job
├── requirements.txt
├── README.md
```

## Reproducibility checklist

- Create `.env` with Telegram and DB credentials
- Run `python -m src.scraper` to populate `data/raw`
- Run `python -m src.loader` to load into Postgres
- Run dbt from `medical_warehouse/` and resolve any connection issues
- Run `python -m src.yolo_detect` to create detections CSV
- Start `uvicorn` to explore API responses

## Next improvements (recommended)

- Add CI steps to run `pytest` and `dbt test` on PRs
- Containerize with `docker-compose` for easier dev/CI parity
- Build a lightweight product-name normalization step (NER) to improve `top-products` accuracy
- Optionally fine-tune or train a domain-specific object detector for product recognition

## License & Attribution

This repository is provided for the Week 8 challenge and learning purposes. Replace with your preferred license for public distribution.

---

If you'd like, I can also:
- add `CONTRIBUTING.md`, a `Makefile`/PowerShell helper script for common tasks, or
- create a short CI workflow that runs `pytest` and `dbt test` on pull requests.

Updated README for final submission.
# Medical Telegram Warehouse

End-to-end ELT pipeline and analytical API for scraping Telegram channels that sell medical and health products, transforming raw data with dbt, enriching images with YOLOv8, and exposing insights via a FastAPI analytical API. Built as part of the 10 Academy: Artificial Intelligence Mastery Week 8 challenge (14–20 Jan 2026).

## Project Summary

- Purpose: Collect public Telegram messages and images from targeted channels, transform and model data into a dimensional warehouse, enrich image data with object-detection, and provide analytical endpoints for business questions (top products, channel activity, message search, visual-content stats).
- Tech stack: Python, Telethon, PostgreSQL, dbt, Dagster, ultralytics (YOLOv8), FastAPI, SQLAlchemy.

## What’s included

- `src/` — Scraper (`src/scraper.py`), loader (`src/loader.py`), YOLO detection (`src/yolo_detect.py`) and helpers.
- `api/` — FastAPI app (`api/main.py`), DB connection (`api/database.py`) and Pydantic schemas (`api/schemas.py`).
- `medical_warehouse/` — dbt project with staging and marts (models, tests, docs).
- `pipeline.py` — Dagster job and ops to orchestrate scraping, loading, dbt runs, and YOLO enrichment.
- `data/` — Data lake (raw JSON + images) and generated detection CSVs.
- `requirements.txt` — Python dependencies.

## Quick Start

Prerequisites
- Python 3.10+ with a virtualenv
- PostgreSQL database
- `dbt` and `dbt-postgres` installed
- Optional: GPU + dependencies for faster YOLO runs (CPU works for small datasets)

1. Create & activate virtualenv

```powershell
python -m venv venv
& venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure environment
- Create a `.env` at repo root (DO NOT COMMIT). Provide at minimum:
  - `TG_API_ID`, `TG_API_HASH` — Telegram API credentials
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

3. Scrape Telegram (extract)

```powershell
python -m src.scraper
```

This writes JSON files to `data/raw/telegram_messages/YYYY-MM-DD/{channel}.json` and downloads images to `data/raw/images/{channel}/{date}/`.

4. Load raw JSON into Postgres (load)

```powershell
python -m src.loader
```

5. Run dbt transformations (transform)

```powershell
cd medical_warehouse
dbt deps
dbt run
dbt test
dbt docs generate
```

6. Run YOLO enrichment (optional)

```powershell
python -m src.yolo_detect
```

7. Start the API

```powershell
uvicorn api.main:app --reload
```

Open API docs at `http://127.0.0.1:8000/docs`.

8. Orchestrate via Dagster

```powershell
dagster dev -f pipeline.py
# then use the Dagster UI at http://localhost:3000 to launch runs
```

## Notable Endpoints

- `GET /api/reports/top-products?limit=10` — most frequently mentioned products
- `GET /api/channels/{channel_name}/activity` — posting activity for a channel
- `GET /api/search/messages?query=...&limit=20` — search messages by keyword
- `GET /api/reports/visual-content` — image usage and categories

## Data Model & Tests

- dbt implements staging models (`models/staging/`) and marts (`models/marts/`) including `dim_channels`, `dim_dates`, and `fct_messages`.
- Tests include schema-level checks and custom tests (e.g., assert no future messages, assert positive view counts).

## Notes & Caveats

- Secrets: keep `.env` out of git. Use environment variables in production.
- Rate limits: Telethon and Telegram API may rate-limit large scrapes. Add backoff and retry tuning for production.
- YOLO model: `yolov8n.pt` is included for convenience; pre-trained models detect generic objects (bottle, person, etc.) and may not identify brand-specific products.

## Next Steps (optional recommendations)

- Add automated CI to run unit tests and dbt tests on PRs.
- Containerize services with `docker-compose` for reproducible runs.
- Improve schema and product extraction (NER) for better product normalization.
- Add monitoring/alerting for Dagster runs and dbt failures.

## References

- Telethon: https://docs.telethon.dev/
- dbt: https://docs.getdbt.com/
- YOLO/Ultralytics: https://docs.ultralytics.com/
- FastAPI: https://fastapi.tiangolo.com/

---

If you want, I can also:
- add a short `CONTRIBUTING.md`, or
- create a minimal `Makefile`/PowerShell script to run the full pipeline locally.

Created by the Week 8 challenge — deliverables completed as described in the project brief.# Medical Telegram Data Warehouse

## Project Overview

This project builds a **data warehouse pipeline** for medical-related Telegram channels.
The objective is to **extract**, **store**, and **transform** Telegram message data into a structured analytics-ready format using **Python**, **PostgreSQL**, and **dbt**.

This repository covers **Interim Submission Tasks**:

* Task 1: Data Scraping and Collection (Extract & Load)
* Task 2: Data Modeling and Transformation with dbt

---

## Architecture Overview

```
Telegram Channels
        ↓
Raw JSON Files (data/raw)
        ↓
Python Loader (src/loader.py)
        ↓
PostgreSQL (raw_telegram_data)
        ↓
dbt Staging Models
        ↓
Analytics-ready Views
```

---

## Project Structure

```
medical-telegram-warehouse/
├── data/
│   └── raw/
│       └── telegram_messages/      # Raw scraped Telegram JSON files
│
├── src/
│   ├── scraper.py                  # Telegram data scraper
│   ├── loader.py                   # JSON → PostgreSQL loader
│   └── object_detection.py         # Image processing (YOLO)
│
├── medical_warehouse/              # dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       └── staging/
│           ├── stg_telegram_messages.sql
│           └── schema.yml
│
├── logs/
│   └── scraper.log
│
├── notebooks/                      # Analysis notebooks
├── tests/                          # Python tests
│
├── .gitignore
├── .env.example
├── requirements.txt
└── README.md
```

---

## Task 1: Data Scraping and Collection (Extract & Load)

### Data Source

Medical-related Telegram channels (messages and metadata).

### Extraction

* Telegram messages are scraped and saved as **raw JSON files**
* Files are stored under:

  ```
  data/raw/telegram_messages/
  ```

### Loading

* `src/loader.py` reads all JSON files recursively
* Data is loaded into PostgreSQL table:

  ```
  raw_telegram_data
  ```
* Loader behavior:

  * Creates table if it does not exist
  * Truncates and reloads data safely on re-runs
  * Uses UTF-8 encoding
  * Uses environment variables for credentials

### Run the Loader

```bash
cd src
python loader.py
```

---

## Task 2: Data Modeling and Transformation with dbt

### dbt Source

Raw table:

```sql
raw_telegram_data
```

### Staging Model

Model:

```
models/staging/stg_telegram_messages.sql
```

Key transformations:

* Column renaming for consistency
* Type casting (timestamps, integers)
* Derived fields:

  * `message_length`
  * `has_image`

### Run dbt Models

```bash
cd medical_warehouse
dbt run --select stg_telegram_messages
```

### Run dbt Tests

```bash
dbt test
```

### Tests Implemented

* `not_null` on:

  * `message_id`
  * `channel_name`
  * `message_date`
* `unique` on `message_id`

All tests pass successfully.

---

## Database Configuration

This project uses **PostgreSQL**.

Create a `.env` file using the example below:

```env
DB_NAME=medical_warehouse_utf8
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

⚠️ **Do not commit `.env` files** — use `.env.example`.

---

## Technologies Used

* Python 3
* PostgreSQL
* SQLAlchemy
* pandas
* dbt (Data Build Tool)
* Telethon
* Loguru

---

## Interim Submission Status

| Task                 | Status                    |
| -------------------- | ------------------------- |
| Data Scraping & Load | ✅ Completed               |
| dbt Staging Models   | ✅ Completed               |
| dbt Tests            | ✅ Passing                 |
| Repository Structure | ✅ Best Practices Followed |

---

## Notes

* This submission focuses on **raw ingestion and staging**
* Dimensional marts and analytics models will be implemented in the final phase
* Image analytics is prepared but not evaluated in this interim submission

---

## Author

**Habtamu Wendifraw Eshibele**
Data Engineering Project – Interim Submission