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
    
    async def update_data(self, df):
        logs = []
        db_posts = await self.get_all_posts()
        db_index = {(int(p['module']), int(p['theme'])): p for p in db_posts}
        added, updated = 0, 0
        for i, row in df.iterrows():
            try:
                logs.append('Считываем строку номер ', i+1)
                user_id = int(row['user_id'])
                module = int(row['module'])
                theme = int(row['theme'])
                title = str(row['title'])
                content = str(row['content'])
            except Exception as e:
                logs.append(f"Ошибка в строке: {i+1} — {e}. Полученные данные: \n\n{row} \n\nПереходим к следующей")
                continue
            key = (module, theme)
            db_post = db_index.get(key)
            if not db_post:
                logs.append(f"Добавляем тему {theme} в модуль {module}")
                try:
                    await self.add_post(user_id, module, theme, title, content)
                except e:
                    logs.append(f"Ошибка: {e}")
                added += 1
            else:
                if db_post['title'] != title or db_post['content'] != content or db_post['user_id'] != user_id:
                    logs.append(f"Обновляем тему {theme} в модуле {module}")
                    try:
                        await self.add_post(user_id, module, theme, title, content)
                    except e:
                        logs.append(f"Ошибка: {e}")
                    updated += 1
        logs.append(f"Синхронизация завершена. Добавлено: {added}, обновлено: {updated}")

        return logs

