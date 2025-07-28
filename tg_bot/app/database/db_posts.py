from .db_base import DatabaseBase

class PostsDatabase(DatabaseBase):

    async def add_post(self, user_id: int, module: int, theme: int, title: str, content: str) -> int:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
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
                SELECT id, title, content FROM posts
                WHERE module = $1 AND theme = $2
                LIMIT 1
            ''', module, theme)
            if row:
                return dict(row)
            return None
