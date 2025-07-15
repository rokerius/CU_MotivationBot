import csv
import re

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
        if not isinstance(post_id, int) or post_id <= 0:
            raise ValueError("post_id must be a positive integer")
        url_pattern = re.compile(r'^https?://')
        if not url_pattern.match(image_url):
            raise ValueError("image_url must be a valid URL starting with http:// or https://")

        async with self.pool.acquire() as conn:
            try:
                await conn.execute('''
                    INSERT INTO post_images (post_id, image_url)
                    VALUES ($1, $2)
                ''', post_id, image_url)
            except Exception as e:
                raise RuntimeError("Database error occurred") from e

