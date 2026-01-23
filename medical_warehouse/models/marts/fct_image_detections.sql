{{ config(
    materialized='table'
) }}

with yolo as (
    select
        -- Extract message_id from image_name (e.g., "10.jpg" -> 10)
        case 
            when split_part(image_name, '.', 1) ~ '^[0-9]+$' 
            then (split_part(image_name, '.', 1))::int
            else null
        end as message_id,
        channel_name,
        detected_objects,
        avg_confidence,
        image_category
    from {{ ref('raw_yolo_detections') }}
),

messages as (
    select
        f.message_id,
        f.channel_id,
        f.message_date as date_key,
        f.views
    from {{ ref('fact_telegram_messages') }} f
)

select
    y.message_id,
    m.channel_id,
    m.date_key,
    y.detected_objects,
    y.avg_confidence as confidence_score,
    y.image_category,
    m.views
from yolo y
inner join messages m
    on y.message_id = m.message_id