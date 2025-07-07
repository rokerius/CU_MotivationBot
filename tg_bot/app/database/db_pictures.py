import csv
from .db_base import DatabaseBase

class PicturesDatabase(DatabaseBase):

    async def import_csv_to_pictures_db(self, csv_file_path: str):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                module = int(row['module'])
                theme = int(row['theme'])
                image_url = row['picture']

                post = await self.get_post_by_module_and_theme(module, theme)
                if not post:
                    return
                await self.add_image_to_post(post_id=int(post['id']), image_url=image_url)

    async def add_image_to_post(self, post_id: int, image_url: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO post_images (post_id, image_url)
                VALUES ($1, $2)
            ''', post_id, image_url)
