{{ config(
    materialized='table',
    schema='marts'
) }}

select
    distinct
    date_trunc('day', message_date::timestamp) as date_value,
    extract(year from message_date::timestamp) as year,
    extract(month from message_date::timestamp) as month,
    extract(day from message_date::timestamp) as day,
    extract(week from message_date::timestamp) as week,
    to_char(message_date::timestamp, 'Day') as weekday
from {{ ref('stg_telegram_messages') }}