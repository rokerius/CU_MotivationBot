import asyncio
from aiogram import Bot, Dispatcher
import os
import logging

from app.database.db import db
from app.handlers import all_routers
from app.work_with_csv import import_csv_to_posts_db, import_csv_to_pictures_db, \
    import_csv_to_quizzes_db, import_csv_to_questions_db

TOKEN = os.getenv("TOKEN")

LOG_FILE = 'app.log'
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(f'logs/{LOG_FILE}', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



async def main():
    logger.info("Bot starting...")
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    await db.connect()
    await db.init_tables()

    for router in all_routers:
        dp.include_router(router)

    try:
        await import_csv_to_posts_db(db, 'data/posts.csv')
        await import_csv_to_pictures_db(db, 'data/pictures.csv')
        await import_csv_to_questions_db(db, 'data/questions.csv')
        await import_csv_to_quizzes_db(db, 'data/quizzes.csv')
        logger.info("Data from tables successfully imported")
        await dp.start_polling(bot)
    finally:
        await db.disconnect()
        logger.info("Disconnecting from the database and shutting down")


if __name__ == '__main__':
    asyncio.run(main())
    # @CU_Motivation_bot
