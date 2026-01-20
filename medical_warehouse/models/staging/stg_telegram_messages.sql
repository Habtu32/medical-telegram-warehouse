with raw_data as (

    select
        message_id,
        message_date,
        sender_id,
        coalesce(message_text, '') as message_text,
        channel_name,
        coalesce(image_path, '') as image_path,
        coalesce(views, 0) as views,
        coalesce(forwards, 0) as forwards,
        case when image_path is not null and image_path != '' then true else false end as has_media
    from {{ source('raw_marts', 'raw_telegram_data') }}  -- <-- correct source

)

select * from raw_data