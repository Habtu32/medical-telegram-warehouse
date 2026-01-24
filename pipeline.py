from dagster import job, op, get_dagster_logger
import subprocess
import os


@op
def scrape_telegram_data():
    logger = get_dagster_logger()
    logger.info("Starting Telegram scraping...")
    subprocess.run(
        ["python", "-m", "src.scraper"],
        check=True
    )
    logger.info("Telegram scraping completed.")


@op
def load_raw_to_postgres():
    logger = get_dagster_logger()
    logger.info("Loading raw data into Postgres...")
    subprocess.run(
        ["python", "-m", "src.loader"],
        check=True
    )
    logger.info("Raw data loaded successfully.")


@op
def run_dbt_transformations():
    logger = get_dagster_logger()
    logger.info("Running dbt transformations...")
    # Resolve dbt project directory relative to this file
    dbt_cwd = os.path.normpath(os.path.join(os.path.dirname(__file__), "medical_warehouse"))

    # Ensure dbt picks up the provided profiles.yml inside the project
    env = os.environ.copy()
    env["DBT_PROFILES_DIR"] = dbt_cwd

    proc = subprocess.run(
        ["dbt", "run"],
        cwd=dbt_cwd,
        env=env,
        capture_output=True,
        text=True,
    )

    # Log output for easier debugging
    if proc.stdout:
        logger.debug(proc.stdout)
    if proc.stderr:
        logger.error(proc.stderr)

    if proc.returncode != 0:
        # Raise to let Dagster mark the step as failed and include output
        raise subprocess.CalledProcessError(proc.returncode, proc.args, output=proc.stdout, stderr=proc.stderr)

    logger.info("dbt transformations completed.")


@op
def run_yolo_enrichment():
    logger = get_dagster_logger()
    logger.info("Running YOLO image enrichment...")
    subprocess.run(
        ["python", "-m", "src.yolo_detect"],
        check=True
    )
    logger.info("YOLO enrichment completed.")


@job
def medical_telegram_pipeline():
    scrape_telegram_data()
    load_raw_to_postgres()
    run_dbt_transformations()
    run_yolo_enrichment()
