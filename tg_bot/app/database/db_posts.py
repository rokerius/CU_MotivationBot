import csv
from .db_base import DatabaseBase

class PostsDatabase(DatabaseBase):

    async def import_csv_to_posts_db(self, csv_file_path: str):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_id = int(row['user_id'])
                module = int(row['module'])
                theme = int(row['theme'])
                title = row['title']
                content = row['content']
                await self.add_post(user_id, module, theme, title, content)

    async def add_post(self, user_id: int, module: int, theme: int, title: str, content: str):
        if not (isinstance(user_id, int) and user_id > 0):
            raise ValueError("user_id must be a positive integer")
        if not (isinstance(module, int) and module > 0):
            raise ValueError("module must be a positive integer")
        if not (isinstance(theme, int) and theme > 0):
            raise ValueError("theme must be a positive integer")
        if not isinstance(title, str) or not isinstance(content, str):
            raise ValueError("title and content must be strings")

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute('''
                        DELETE FROM posts WHERE module = $1 AND theme = $2
                    ''', module, theme)

                    post_id = await conn.fetchval('''
                        INSERT INTO posts (user_id, module, theme, title, content)
                        VALUES ($1, $2, $3, $4, $5)
                        RETURNING id
                    ''', user_id, module, theme, title, content)
                    return post_id
                except Exception as e:
                    raise RuntimeError("Database operation failed") from e

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
