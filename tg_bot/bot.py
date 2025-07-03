import asyncio

from aiogram import Bot, Dispatcher
from app.handlers import router
from config import TOKEN
from app.database.db import db


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    await db.connect()
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await db.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
    # @CU_Motivation_bot
