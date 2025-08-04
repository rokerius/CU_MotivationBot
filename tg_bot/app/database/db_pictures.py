from .db_base import DatabaseBase

class PicturesDatabase(DatabaseBase):

    async def add_image_to_post(self, post_id: int, image_url: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO post_images (post_id, image_url)
                VALUES ($1, $2)
            ''', post_id, image_url)


    async def save_file_id_for_post_image(self, image_url: str, file_id: str):
        async with self.pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE post_images
                SET file_id = $1
                WHERE image_url = $2
            ''', file_id, image_url)
            if result == "UPDATE 0":
                raise RuntimeError(f"No post_images record found for image_url={image_url}")
    
    async def update_image_url(self, post_id: int, image_url: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE post_images
                SET image_url = $1
                WHERE post_id = $2
            ''', image_url, post_id)

    async def clear_post_images(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM post_images
            ''')

    async def get_all_post_images(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM post_images')
            return [dict(row) for row in rows]

    async def update_images_data(self, df):
        logs = []
        await self.clear_post_images()
        for i, row in df.iterrows():
            try:
                module = int(row['module'])
                theme = int(row['theme'])
                post = await self.get_post_by_module_and_theme(module, theme)
                if not post:
                    logs.append(f"Пост модуля {module} темы {theme} не найден. Переходим к следующему")
                    continue
                post_id = post['id']
                image_url = str(row['image_url'])
            except Exception as e:
                logs.append(f"Ошибка в строке: {i+1} — {e}. Полученные данные: \n\n{row} \n\nПереходим к следующей")
                continue

            try:
                await self.add_image_to_post(post_id, image_url)
            except Exception as e:
                logs.append(f"Ошибка при добавлении картинки к посту модуля {module} темы {theme}: {e}")

        logs.append(f"Синхронизация картинок завершена")

        return logs
