{{ config(
    materialized='table'
) }}

with base as (

    select
        row_number() over () as fact_id,  -- Unique fact ID
        s.message_id,
        c.channel_id,
        d.date_value::date as message_date,  -- keep original name for tests
        d.year,
        d.month,
        d.week,
        d.weekday,
        coalesce(s.message_text, '') as message_text,
        coalesce(s.views, 0) as views,
        coalesce(s.forwards, 0) as forwards,
        coalesce(s.has_media, false) as has_media
    from {{ ref('stg_telegram_messages') }} s
    left join {{ ref('dim_channel') }} c
        on s.channel_name = c.channel_name
    left join {{ ref('dim_date') }} d
        on s.message_date::date = d.date_value::date

)

select *
from base