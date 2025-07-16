import csv
import re

from .db_base import DatabaseBase
from ..utils import convert_drive_url

class PicturesDatabase(DatabaseBase):

    async def import_csv_to_pictures_db(self, csv_file_path: str):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                module = int(row['module'])
                theme = int(row['theme'])
                image_url = convert_drive_url(row['picture'])

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


    async def save_file_id_for_post_image(self, image_url: str, file_id: str):
        if not file_id or not isinstance(file_id, str):
            raise ValueError("file_id must be a non-empty string")
        if not image_url or not isinstance(image_url, str):
            raise ValueError("image_url must be a non-empty string")

        async with self.pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE post_images
                SET file_id = $1
                WHERE image_url = $2
            ''', file_id, image_url)
            if result == "UPDATE 0":
                raise RuntimeError(f"No post_images record found for image_url={image_url}")
