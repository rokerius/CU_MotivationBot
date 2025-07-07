# tg_bot/app/database/db_base.py
from abc import ABC, abstractmethod
import asyncpg
import os

class DatabaseBase(ABC):
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432))
        )

    async def init_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    modules TEXT,
                    answers TEXT,
                    goals TEXT,
                    quiz_answers TEXT,
                    created_at TIMESTAMP DEFAULT now()
                );
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    module BIGINT NOT NULL,
                    theme BIGINT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS post_images (
                    id SERIAL PRIMARY KEY,
                    post_id INT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                    image_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS module_questions (
                    id SERIAL PRIMARY KEY,
                    module BIGINT NOT NULL,
                    question TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            ''')
            await conn.execute('''
                 CREATE TABLE IF NOT EXISTS quizzes (
                     id SERIAL PRIMARY KEY,
                     module BIGINT NOT NULL,
                     question TEXT NOT NULL,
                     option_1 TEXT NOT NULL,
                     option_2 TEXT NOT NULL,
                     option_3 TEXT,
                     option_4 TEXT,
                     option_5 TEXT,
                     correct_answer TEXT NOT NULL,
                     created_at TIMESTAMP DEFAULT NOW()
                 );
            ''')

    async def disconnect(self):
        await self.pool.close()

    @abstractmethod
    async def import_csv_to_posts_db(self, csv_file_path: str):
        pass

    @abstractmethod
    async def import_csv_to_pictures_db(self, csv_file_path: str):
        pass

    @abstractmethod
    async def import_csv_to_questions_db(self, csv_file_path: str):
        pass

    @abstractmethod
    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str):
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int):
        pass

    @abstractmethod
    async def add_post(self, user_id: int, module: int, theme: int, title: str, content: str):
        pass

    @abstractmethod
    async def get_post_by_module_and_theme(self, module: int, theme: int):
        pass

    @abstractmethod
    async def add_image_to_post(self, post_id: int, image_url: str):
        pass

    @abstractmethod
    async def add_goals(self, user_id: int, goals: str):
        pass

    @abstractmethod
    async def change_modules_done(self, user_id: int, module: int, value: str):
        pass

    @abstractmethod
    async def add_question(self, module: int, question: str):
        pass

    @abstractmethod
    async def get_question_by_module(self, module: int):
        pass

    @abstractmethod
    async def save_answer(self, module: int, user_id: int, answer: str):
        pass
