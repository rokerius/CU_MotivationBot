import asyncio
import logging  # Импортируем модуль logging

from aiogram import Bot, Dispatcher

from app.database.db import db
from app.handlers import router
from app.config import TOKEN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    await db.connect()

    dp.include_router(router)
    try:
        try:
            await db.import_csv_to_posts_db('data/posts.csv')
            logger.info("Successfully imported 'data/posts.csv'") # Логируем успешный импорт
        except Exception as e:
            logger.error(f"Failed to import 'data/posts.csv': {e}") # Логируем ошибку при импорте posts.csv

        try:
            await db.import_csv_to_pictures_db('data/pictures.csv')
            logger.info("Successfully imported 'data/pictures.csv'") # Логируем успешный импорт
        except Exception as e:
            logger.error(f"Failed to import 'data/pictures.csv': {e}") # Логируем ошибку при импорте pictures.csv

        await dp.start_polling(bot)
    finally:
        await db.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
    # @CU_Motivation_bot
