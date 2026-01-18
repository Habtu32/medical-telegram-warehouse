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
        
        # Current date for folder structure
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Prepare channel-specific message folder
        msg_date_dir = os.path.join(MESSAGES_DIR, today)
        os.makedirs(msg_date_dir, exist_ok=True)
        
        # Prepare channel and date specific image folder
        img_channel_date_dir = os.path.join(IMAGES_DIR, channel_username, today)
        os.makedirs(img_channel_date_dir, exist_ok=True)

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
                    # Rename to just message_id.jpg as per request since folder has channel name
                    filename = f"{message.id}.jpg"
                    filepath = os.path.join(img_channel_date_dir, filename)
                    await message.download_media(file=filepath)
                    msg_data["media_path"] = filepath
                    logger.debug(f"Downloaded image: {channel_username}/{today}/{filename}")

                data.append(msg_data)

            # Save Messages to JSON: YYYY-MM-DD/channel.json
            output_file = os.path.join(msg_date_dir, f"{channel_username}.json")
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
