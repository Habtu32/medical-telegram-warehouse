select *
from {{ ref('fact_telegram_messages') }}
where message_date > current_date