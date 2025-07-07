import csv
from .db_base import DatabaseBase

class QuestionsDatabase(DatabaseBase):

    async def import_csv_to_questions_db(self, csv_file_path: str):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                module = int(row['module'])
                question = row['question']
                await self.add_question(module, question)

    async def add_question(self, module: int, question: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO module_questions (module, question)
                VALUES ($1, $2)
            ''', module, question)

    async def get_question_by_module(self, module: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM module_questions
                WHERE module = $1
                LIMIT 1
            ''', module)
            if row:
                return dict(row)["question"]
            return None
