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
                INSERT INTO users (id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO NOTHING
            ''', user_id, username, first_name, last_name)

    async def get_user_by_id(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
            if row:
                return dict(row)
            return None

db = Database()
