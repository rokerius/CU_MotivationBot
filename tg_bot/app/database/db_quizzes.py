import csv
from .db_base import DatabaseBase

class QuizzesDatabase(DatabaseBase):

    async def import_csv_to_quizzes_db(self, csv_file_path: str):
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
                correct_answer = row['correct_answer']

                await self.add_quiz(
                    module, question, option_1, option_2, option_3, option_4, option_5, correct_answer
                )

    async def add_quiz(
        self,
        module: int,
        question: str,
        option_1: str,
        option_2: str,
        option_3: str = None,
        option_4: str = None,
        option_5: str = None,
        correct_answer: str = None
    ):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO quizzes (
                    module, question, option_1, option_2, option_3, option_4, option_5, correct_answer
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ''', module, question, option_1, option_2, option_3, option_4, option_5, correct_answer)

    async def get_quizzes_by_module(self, module: int):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT * FROM quizzes
                WHERE module = $1
            ''', module)
            return [dict(row) for row in rows]

