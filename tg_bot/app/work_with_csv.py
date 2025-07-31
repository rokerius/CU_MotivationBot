import csv
import os
import tempfile

from .database.db import Database
from .utils import convert_drive_url


async def import_csv_to_quizzes_db(db: Database, csv_file_path: str):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            module = int(row['module'])
            question = row['question']
            option_1 = row['option_1']
            option_2 = row['option_2']
            option_3 = row.get('option_3')
            option_4 = row.get('option_4')
            option_5 = row.get('option_5')
            description = row.get('description')
            correct_answer = row['correct_answer']

            await db.add_quiz(
                module, question, option_1, option_2, option_3, option_4,
                option_5, correct_answer, description)


async def import_csv_to_questions_db(db: Database, csv_file_path: str):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            module = int(row['module'])
            question = row['question']
            await db.add_question(module, question)


async def import_csv_to_posts_db(db: Database, csv_file_path: str):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user_id = int(row['user_id'])
            module = int(row['module'])
            theme = int(row['theme'])
            title = row['title']
            content = row['content']
            await db.set_post(user_id, module, theme, title, content)


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


async def dicts_to_csv(dict_list, filename_telegram):
    tmp_path = None
    try:
        tmp_file = tempfile.NamedTemporaryFile(mode='w+', newline='', suffix='.csv', delete=False, encoding='utf-8')
        tmp_path = tmp_file.name

        writer = csv.DictWriter(tmp_file, fieldnames=list(dict_list[0].keys()))
        writer.writeheader()
        writer.writerows(dict_list)
        tmp_file.close()

        return tmp_path, filename_telegram
    except Exception as e:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise e
