from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.database import get_db
from api.schemas import (
    TopProductsResponse,
    ChannelActivityResponse,
    MessageSearchResponse,
    VisualContentStatsResponse,
)

app = FastAPI(
    title="Medical Telegram Analytics API",
    version="1.0",
)

# --------------------------------------------------
# Endpoint 1: Top Products
# --------------------------------------------------
@app.get("/api/reports/top-products", response_model=TopProductsResponse)
def top_products(
    limit: int = Query(10, gt=0),
    db: Session = Depends(get_db),
):
    query = text("""
        SELECT detected_objects, COUNT(*) AS mention_count
        FROM raw.raw_yolo_detections
        WHERE detected_objects IS NOT NULL
        GROUP BY detected_objects
        ORDER BY mention_count DESC
        LIMIT :limit
    """)
    results = db.execute(query, {"limit": limit}).fetchall()

    return {
        "top_products": [
            {"detected_objects": r[0], "mention_count": r[1]}
            for r in results
        ]
    }

# --------------------------------------------------
# Endpoint 2: Channel Activity
# --------------------------------------------------
@app.get("/api/channels/{channel_id}/activity", response_model=ChannelActivityResponse)
def channel_activity(
    channel_id: int,
    db: Session = Depends(get_db),
):
    query = text("""
    SELECT detected_objects, COUNT(*) AS mention_count
    FROM raw.raw_yolo_detections
    WHERE detected_objects IS NOT NULL
    GROUP BY detected_objects
    ORDER BY mention_count DESC
    LIMIT :limit
""")
    results = db.execute(query, {"channel_id": channel_id}).fetchall()

    return {
        "channel_id": channel_id,
        "activity": [
            {
                "date": r[0],
                "total_posts": r[1],
                "total_views": r[2],
            }
            for r in results
        ],
    }

# --------------------------------------------------
# Endpoint 3: Message Search
# --------------------------------------------------
@app.get("/api/search/messages", response_model=MessageSearchResponse)
def search_messages(
    message_id: int | None = None,
    limit: int = Query(20, gt=0),
    db: Session = Depends(get_db),
):
    query = text("""
        SELECT message_id, channel_id, views
        FROM raw.raw_yolo_detections
        WHERE (:message_id IS NULL OR message_id = :message_id)
        ORDER BY views DESC
        LIMIT :limit
    """)
    results = db.execute(
        query,
        {"message_id": message_id, "limit": limit},
    ).fetchall()

    return {
        "messages": [
            {
                "message_id": r[0],
                "channel_id": r[1],
                "views": r[2],
            }
            for r in results
        ]
    }

# --------------------------------------------------
# Endpoint 4: Visual Content Stats
# --------------------------------------------------
@app.get("/api/reports/visual-content", response_model=VisualContentStatsResponse)
def visual_content_stats(db: Session = Depends(get_db)):
    query = text("""
        SELECT image_category, COUNT(*) AS image_count, AVG(views) AS avg_views
        FROM raw.raw_yolo_detections
        GROUP BY image_category
        ORDER BY image_count DESC
    """)
    results = db.execute(query).fetchall()

    return {
        "visual_content_stats": [
            {
                "image_category": r[0],
                "image_count": r[1],
                "avg_views": float(r[2] or 0),
            }
            for r in results
        ]
    }
