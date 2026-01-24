from sqlalchemy import text

def get_top_products(db, limit: int):
    query = text("""
        SELECT detected_objects AS term, COUNT(*) AS count
        FROM marts.fct_image_detections
        WHERE detected_objects IS NOT NULL
        GROUP BY detected_objects
        ORDER BY count DESC
        LIMIT :limit
    """)
    return db.execute(query, {"limit": limit}).fetchall()


def get_channel_activity(db, channel_name: str):
    query = text("""
        SELECT
            c.channel_name,
            COUNT(f.message_id) AS total_messages,
            AVG(f.views) AS avg_views
        FROM marts.fact_telegram_messages f
        JOIN marts.dim_channel c ON f.channel_id = c.channel_id
        WHERE c.channel_name = :channel_name
        GROUP BY c.channel_name
    """)
    return db.execute(query, {"channel_name": channel_name}).fetchone()

def search_messages(db, query_text: str, limit: int):
    query = text("""
        SELECT
            f.message_id,
            c.channel_name,
            f.message_text
        FROM marts.fact_telegram_messages f
        JOIN marts.dim_channel c ON f.channel_id = c.channel_id
        WHERE LOWER(f.message_text) LIKE LOWER(:query)
        LIMIT :limit
    """)
    return db.execute(
        query,
        {"query": f"%{query_text}%", "limit": limit}
    ).fetchall()

def get_visual_content_stats(db):
    query = text("""
        SELECT
            channel_name,
            COUNT(*) AS image_posts,
            AVG(avg_confidence) AS avg_confidence
        FROM marts.fct_image_detections
        GROUP BY channel_name
        ORDER BY image_posts DESC
    """)
    return db.execute(query).fetchall()
