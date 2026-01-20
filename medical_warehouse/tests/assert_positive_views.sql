select *
from {{ ref('fact_telegram_messages') }}
where views < 0