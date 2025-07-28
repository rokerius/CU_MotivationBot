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
