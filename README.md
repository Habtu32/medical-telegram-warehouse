# Medical Telegram Data Warehouse

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