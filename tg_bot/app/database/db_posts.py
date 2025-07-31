from .db_base import DatabaseBase

class PostsDatabase(DatabaseBase):

    async def set_post(self, user_id: int, module: int, theme: int, title: str, content: str) -> int:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                existing_post = await conn.fetchrow('''
                    SELECT id FROM posts WHERE module = $1 AND theme = $2
                ''', module, theme)

                if existing_post:
                    post_id = existing_post['id']
                    await conn.execute('''
                        UPDATE posts
                        SET user_id = $1, title = $2, content = $3
                        WHERE id = $4
                    ''', user_id, title, content, post_id)
                    return post_id
                else:
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

    async def get_all_posts(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM posts')
            return [dict(row) for row in rows]

    async def update_posts_data(self, df):
        logs = []
        db_posts = await self.get_all_posts()
        db_index = {(int(p['module']), int(p['theme'])): p for p in db_posts}
        added, updated = 0, 0
        for i, row in df.iterrows():
            try:
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
                logs.append(f"Добавляем тему {theme} в модуль {module}...")
                try:
                    await self.set_post(user_id, module, theme, title, content)
                except Exception as e:
                    logs.append(f"Ошибка: {e}")
                else:
                    added += 1
            else:
                if db_post['title'] != title or db_post['content'] != content or db_post['user_id'] != user_id:
                    logs.append(f"Обновляем тему {theme} в модуле {module}...")
                    try:
                        await self.set_post(user_id, module, theme, title, content)
                    except Exception as e:
                        logs.append(f"Ошибка: {e}")
                    else:
                        updated += 1
        logs.append(f"Синхронизация постов завершена. Добавлено: {added}, обновлено: {updated}")

        return logs
