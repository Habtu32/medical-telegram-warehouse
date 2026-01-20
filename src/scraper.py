import os
import json
import asyncio
from datetime import datetime
from telethon import TelegramClient
from dotenv import load_dotenv
from loguru import logger

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

API_ID = os.getenv("TG_API_ID")
API_HASH = os.getenv("TG_API_HASH")
SESSION_NAME = "medical_warehouse_session"

# -----------------------------
# Paths
# -----------------------------
RAW_DATA_DIR = os.path.join("data", "raw")
MESSAGES_DIR = os.path.join(RAW_DATA_DIR, "telegram_messages")
IMAGES_DIR = os.path.join(RAW_DATA_DIR, "images")

os.makedirs(MESSAGES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# -----------------------------
# Channels
# -----------------------------
CHANNELS = [
    "CheMed123",
    "lobelia4cosmetics",
    "tikvahpharma",
    "Thequorachannel",
]

# -----------------------------
# Client
# -----------------------------
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


class TelegramScraper:
    def __init__(self, client, channels):
        self.client = client
        self.channels = channels

    async def scrape_channel(self, channel_username, limit=100):
        logger.info(f"Starting scrape for channel: {channel_username}")

        today = datetime.now().strftime("%Y-%m-%d")

        msg_date_dir = os.path.join(MESSAGES_DIR, today)
        os.makedirs(msg_date_dir, exist_ok=True)

        img_channel_date_dir = os.path.join(IMAGES_DIR, channel_username, today)
        os.makedirs(img_channel_date_dir, exist_ok=True)

        data = []

        try:
            entity = await self.client.get_entity(channel_username)

            async for message in self.client.iter_messages(entity, limit=limit):
                msg_data = {
                    "id": message.id,
                    "date": message.date.isoformat() if message.date else None,
                    "sender_id": message.sender_id,
                    "content": message.text,
                    "channel": channel_username,
                    "media_path": None,
                    "views": message.views,
                    "forwards": message.forwards,
                    "has_media": bool(message.media),
                }

                if message.photo:
                    filename = f"{message.id}.jpg"
                    filepath = os.path.join(img_channel_date_dir, filename)

                    await message.download_media(file=filepath)

                    # Normalize path for JSON
                    msg_data["media_path"] = filepath.replace("\\", "/")

                data.append(msg_data)

            # ✅ Write JSON ONCE per channel
            output_file = os.path.join(msg_date_dir, f"{channel_username}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            logger.success(
                f"Successfully scraped {len(data)} messages from {channel_username}"
            )

        except Exception as e:
            logger.error(f"Error scraping {channel_username}: {e}")

    async def run(self):
        await self.client.start()
        logger.info("Telegram client started")

        for channel in self.channels:
            await self.scrape_channel(channel)

        logger.info("Scraping completed")


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    logger.add("logs/scraper.log", rotation="1 MB")

    scraper = TelegramScraper(client, CHANNELS)

    with client:
        client.loop.run_until_complete(scraper.run())