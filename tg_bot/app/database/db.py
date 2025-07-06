import csv
import os

import asyncpg


class Database:
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

    async def disconnect(self):
        await self.pool.close()

    async def import_csv_to_posts_db(self, csv_file_path: str):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_id = int(row['user_id'])
                module = int(row['module'])
                theme = int(row['theme'])
                title = row['title']
                content = row['content']
                await db.add_post(user_id, module, theme, title, content)

    async def import_csv_to_pictures_db(self, csv_file_path: str):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                module = int(row['module'])
                theme = int(row['theme'])
                image_url = row['picture']

                post = await db.get_post_by_module_and_theme(module, theme)
                if not post:
                    return
                await db.add_image_to_post(post_id=int(post['id']), image_url=image_url)

    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (id, username, first_name, last_name, modules)
                VALUES ($1, $2, $3, $4, '00000000')
                ON CONFLICT (id) DO NOTHING
            ''', user_id, username, first_name, last_name)

    async def get_user_by_id(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
            if row:
                return dict(row)
            return None

    async def add_post(self, user_id: int, module: int, theme: int, title: str, content: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM posts WHERE module = $1 AND theme = $2
            ''', module, theme)

            post_id = await conn.fetchval('''
                INSERT INTO posts (user_id, module, theme, title, content)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            ''', user_id, module, theme, title, content)
            return post_id

    async def get_post_by_module_and_theme(self, module: int, theme: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM posts
                WHERE module = $1 AND theme = $2
                LIMIT 1
            ''', module, theme)
            if row:
                return dict(row)
            return None

    async def add_image_to_post(self, post_id: int, image_url: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO post_images (post_id, image_url)
                VALUES ($1, $2)
            ''', post_id, image_url)


    async def change_modules_done(self, user_id: int, module: int, value: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT modules FROM users WHERE id = $1', user_id)
            if not row:
                return False
            if value not in ["1", "2", "3"]:
                return False

            modules = list(row['modules'])
            modules[module-1] = value
            new_modules = ''.join(modules)

            await conn.execute('UPDATE users SET modules = $1 WHERE id = $2', new_modules, user_id)
            return True



db = Database()
