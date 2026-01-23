{{ config(
    materialized='table',
    schema='marts'
) }}
SELECT
    {{ dbt_utils.generate_surrogate_key(['date']) }} AS date_key,
    date AS date_value,
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    EXTRACT(WEEK FROM date) AS week,
    EXTRACT(DOW FROM date) AS weekday
FROM {{ ref('stg_telegram_messages') }}