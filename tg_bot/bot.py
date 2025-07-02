import asyncio

from aiogram import Bot, Dispatcher
from app.handlers import router
import os

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    print("bot started")
    asyncio.run(main())
    # @CU_Motivation_bot
