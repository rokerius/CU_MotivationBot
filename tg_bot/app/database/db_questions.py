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
        if not (isinstance(module, int) and module > 0):
            raise ValueError("module must be a positive integer")
        if not (isinstance(question, str) and question.strip()):
            raise ValueError("question must be a non-empty string")
        if len(question) > 1000:
            raise ValueError("question is too long")

        async with self.pool.acquire() as conn:
            try:
                await conn.execute('''
                    INSERT INTO module_questions (module, question)
                    VALUES ($1, $2)
                ''', module, question)
            except Exception as e:
                raise RuntimeError("Database error occurred") from e

    async def get_question_by_module(self, module: int):
        if not (isinstance(module, int) and module > 0):
            raise ValueError("module must be a positive integer")

        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow('''
                    SELECT question FROM module_questions
                    WHERE module = $1
                    LIMIT 1
                ''', module)
                if row:
                    return row["question"]
                return None
            except Exception as e:
                raise RuntimeError("Database error occurred") from e

    async def check_questions_done(self, user_id: int, module: int) -> bool:
        if not (isinstance(user_id, int) and user_id > 0):
            raise ValueError("user_id must be a positive integer")
        if not (isinstance(module, int) and module > 0):
            raise ValueError("module must be a positive integer")

        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow('SELECT answers FROM users WHERE id = $1', user_id)
                if not row:
                    return False

                answers = row['answers']
                if answers is None:
                    return False

                return "$question" + str(module) + "|" in answers
            except Exception as e:
                raise RuntimeError(f"Database error occurred while getting answer: {e}") from e