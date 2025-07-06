import asyncio

from aiogram import Bot, Dispatcher

from app.database.db import db
from app.handlers import router
from app.config import TOKEN


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    await db.connect()
    await db.init_tables()

    dp.include_router(router)
    try:
        # await db.import_csv_to_posts_db('data/posts.csv')
        # await db.import_csv_to_pictures_db('data/pictures.csv')

        await dp.start_polling(bot)
    finally:
        await db.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
    # @CU_Motivation_bot
