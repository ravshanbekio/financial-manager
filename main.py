import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from handlers import start, text_controller, limit

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# register routers
dp.include_router(start.start_router)
#dp.include_router(voice_controller.voice_controller_router)
dp.include_router(text_controller.text_controller_router)
dp.include_router(limit.limit_router)

async def main():
    """Polling the bot"""
    await dp.start_polling(bot)
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())