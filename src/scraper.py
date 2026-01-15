import os
import json
import asyncio
from datetime import datetime
from telethon import TelegramClient
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Configuration
API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
SESSION_NAME = 'medical_warehouse_session'

# Paths
RAW_DATA_DIR = os.path.join("data", "raw")
MESSAGES_DIR = os.path.join(RAW_DATA_DIR, "telegram_messages")
IMAGES_DIR = os.path.join(RAW_DATA_DIR, "images")

# Ensure directories exist
os.makedirs(MESSAGES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# List of Channels to Scrape (Ethiopian Medical/Health Context)
# You can add more channels here
CHANNELS = [
    'CheMed123',
    'lobelia4cosmetics',
    'tikvahpharma',
    'Thequorachannel'
]

# Initialize Client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

class TelegramScraper:
    def __init__(self, client, channels):
        self.client = client
        self.channels = channels

    async def scrape_channel(self, channel_username, limit=100):
        logger.info(f"Starting scrape for channel: {channel_username}")
        
        data = []
        try:
            # Get entity ensures we have the correct channel reference
            entity = await self.client.get_entity(channel_username)
            
            async for message in self.client.iter_messages(entity, limit=limit):
                msg_data = {
                    "id": message.id,
                    "date": message.date.isoformat(),
                    "sender_id": message.sender_id,
                    "content": message.text,
                    "channel": channel_username,
                    "media_path": None
                }

                # Download Image if present
                if message.photo:
                    filename = f"{channel_username}_{message.id}.jpg"
                    filepath = os.path.join(IMAGES_DIR, filename)
                    await message.download_media(file=filepath)
                    msg_data["media_path"] = filepath
                    logger.debug(f"Downloaded image: {filename}")

                data.append(msg_data)

            # Save Messages to JSON
            output_file = os.path.join(MESSAGES_DIR, f"{channel_username}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            logger.success(f"Successfully scraped {len(data)} messages from {channel_username}")

        except Exception as e:
            logger.error(f"Error scraping {channel_username}: {e}")

    async def run(self):
        await self.client.start()
        logger.info("Client Started")
        
        for channel in self.channels:
            await self.scrape_channel(channel)
            
        logger.info("Scraping Completed")

if __name__ == "__main__":
    # Configure logger
    logger.add("logs/scraper.log", rotation="1 MB")
    
    scraper = TelegramScraper(client, CHANNELS)
    
    with client:
        client.loop.run_until_complete(scraper.run())
