from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import asyncio
import os

from keyboards import *
from states import *
from handlers import *
from services import *
from database import init_db
from bot import bot, dp

from data.programs import programs
from data.playlist import playlist

async def keep_alive():
    while True:
        await asyncio.sleep(600)
        print("Keep-alive: бот активен")

async def main():
    init_db()
    asyncio.create_task(keep_alive())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())