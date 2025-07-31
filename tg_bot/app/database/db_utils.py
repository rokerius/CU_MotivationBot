from .db_base import DatabaseBase


class UtilsDatabase(DatabaseBase):

    async def get_all_users(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM users')
            return [dict(row) for row in rows]

    async def get_all_posts(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM posts')
            return [dict(row) for row in rows]

    async def get_all_post_images(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM post_images')
            return [dict(row) for row in rows]

    async def get_all_module_questions(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM module_questions')
            return [dict(row) for row in rows]

    async def get_all_quizzes(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM quizzes')
            return [dict(row) for row in rows]
