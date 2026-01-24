from pydantic import BaseModel
from typing import List, Optional

# ------------------------------
# Endpoint 1: Top Products
# ------------------------------
class TopProductItem(BaseModel):
    detected_objects: str
    mention_count: int

class TopProductsResponse(BaseModel):
    top_products: List[TopProductItem]


# ------------------------------
# Endpoint 2: Channel Activity
# ------------------------------
class ChannelActivityItem(BaseModel):
    date: str  # You can use date if the DB returns date type
    total_posts: int
    total_views: int

class ChannelActivityResponse(BaseModel):
    channel_name: str
    activity: List[ChannelActivityItem]


# ------------------------------
# Endpoint 3: Message Search
# ------------------------------
class MessageItem(BaseModel):
    message_id: int
    message_text: str
    channel_id: int
    views: Optional[int] = 0

class MessageSearchResponse(BaseModel):
    messages: List[MessageItem]


# ------------------------------
# Endpoint 4: Visual Content Stats
# ------------------------------
class VisualContentStatItem(BaseModel):
    image_category: str
    image_count: int
    avg_views: float

class VisualContentStatsResponse(BaseModel):
    visual_content_stats: List[VisualContentStatItem]