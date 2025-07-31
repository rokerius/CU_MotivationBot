import asyncio
from aiogram import Bot, Dispatcher
import os
import logging
import json
from dotenv import load_dotenv

from app.database.db import db
from app.handlers import all_routers
from app.work_with_csv import import_csv_to_posts_db, import_csv_to_pictures_db, \
    import_csv_to_quizzes_db, import_csv_to_questions_db

load_dotenv()

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

async def create_credentials_file():

    credentials = {
        "type": "service_account",
        "private_key": os.getenv("PRIVATE_KEY", "").replace("\\n", "\n"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("CLIENT_ID"),
        "auth_uri": os.getenv("AUTH_URI"),
        "token_uri": os.getenv("TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
        "project_id": os.getenv("PROJECT_ID")
    }

    with open("credentials.json", "w", encoding="utf-8") as f:
        json.dump(credentials, f, indent=2)


async def main():
    logger.info("Creating credentials.json...")
    await create_credentials_file()
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
