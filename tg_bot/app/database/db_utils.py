import csv
import os
import tempfile
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


async def dicts_to_csv(dict_list, filename_telegram):
    tmp_path = None
    try:
        tmp_file = tempfile.NamedTemporaryFile(mode='w+', newline='', suffix='.csv', delete=False, encoding='utf-8')
        tmp_path = tmp_file.name

        writer = csv.DictWriter(tmp_file, fieldnames=list(dict_list[0].keys())) # Используем ключи первого элемента для fieldnames
        writer.writeheader()
        writer.writerows(dict_list)
        tmp_file.close()

        return tmp_path, filename_telegram
    except Exception as e:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise e