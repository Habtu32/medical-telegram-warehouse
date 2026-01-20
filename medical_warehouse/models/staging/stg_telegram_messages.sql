with source as (

    select
        message_id,
        message_date::timestamp as message_date,
        sender_id,
        message_text,
        channel_name,
        views,
        forwards,
        has_media,
        image_path
    from raw_telegram_data

)

select * from source