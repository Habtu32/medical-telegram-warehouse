# Medical Telegram Warehouse

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file with the following:
    ```env
    TG_API_ID=your_api_id
    TG_API_HASH=your_api_hash
    DB_NAME=medical_warehouse
    DB_USER=postgres
    DB_PASSWORD=your_password
    DB_HOST=localhost
    DB_PORT=5432
    ```

3.  **Database**:
    Create the database in PostgreSQL:
    ```sql
    CREATE DATABASE medical_warehouse;
    ```

## Running the Pipeline

### 1. Scrape Data
Run the scraper to fetch messages and images from Telegram channels.
```bash
python src/scraper.py
```
*Note: First run requires interactive login.*

### 2. Load Data to Database
Load the scraped JSON data into the raw Postgres table.
```bash
python src/loader.py
```

### 3. Object Detection (Optional)
Run YOLO object detection on downloaded images.
```bash
python src/object_detection.py
```

### 4. Transform Data (dbt)
Run dbt models to clean and transform the data.
```bash
cd medical_warehouse
dbt deps
dbt run --profiles-dir .
dbt test --profiles-dir .
```
