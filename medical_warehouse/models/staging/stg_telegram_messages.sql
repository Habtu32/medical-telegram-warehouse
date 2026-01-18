-- models/staging/stg_telegram_messages.sql

with raw_data as (

    select
        message_id,
        channel_name,
        message_date::timestamp        as message_date,
        message_text,
        length(message_text)           as message_length,
        null::integer                  as view_count,
        null::integer                  as forward_count,
        case
            when image_path is not null then true
            else false
        end                            as has_image,
        image_path
    from {{ source('raw', 'raw_telegram_data') }}

)

select *
from raw_data
