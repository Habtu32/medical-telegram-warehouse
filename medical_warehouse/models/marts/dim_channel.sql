{{ config(
    materialized='table',
    schema='marts'
) }}

select
    row_number() over (order by channel_name) as channel_id,
    channel_name
from (
    select distinct channel_name
    from {{ ref('stg_telegram_messages') }}
) channels