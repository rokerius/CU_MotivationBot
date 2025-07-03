import asyncpg
import os

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

    async def disconnect(self):
        await self.pool.close()

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

db = Database()
