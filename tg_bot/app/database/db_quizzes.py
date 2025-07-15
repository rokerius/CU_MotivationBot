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
                description = row.get('description')
                correct_answer = row['correct_answer']

                await self.add_quiz(
                    module, question, option_1, option_2, option_3, option_4,
                    option_5, correct_answer, description
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
            correct_answer: str = None,
            description: str = None
    ):
        if not (isinstance(module, int) and module > 0):
            raise ValueError("module must be a positive integer")
        for field_name, field_value in [("question", question), ("option_1", option_1), ("option_2", option_2)]:
            if not (isinstance(field_value, str) and field_value.strip()):
                raise ValueError(f"{field_name} must be a non-empty string")

        valid_options = {option_1, option_2}
        if option_3:
            valid_options.add(option_3)
        if option_4:
            valid_options.add(option_4)
        if option_5:
            valid_options.add(option_5)

        if correct_answer and correct_answer not in valid_options:
            raise ValueError("correct_answer must be one of the provided options")

        max_len = 1000
        for field in [question, option_1, option_2, option_3, option_4, option_5, correct_answer, description]:
            if field and len(field) > max_len:
                raise ValueError("One of the input fields exceeds maximum allowed length")

        async with self.pool.acquire() as conn:
            try:
                await conn.execute('''
                    INSERT INTO quizzes (
                        module, question, option_1, option_2, option_3, option_4, 
                        option_5, correct_answer, description
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ''', module, question, option_1, option_2, option_3, option_4,
                                   option_5, correct_answer, description)
            except Exception as e:
                raise RuntimeError("Database error occurred while adding quiz") from e

    async def get_quizzes_by_module(self, module: int):
        if not (isinstance(module, int) and module > 0):
            raise ValueError("module must be a positive integer")

        async with self.pool.acquire() as conn:
            try:
                rows = await conn.fetch('''
                    SELECT id, module, question, option_1, option_2, option_3, option_4, 
                           option_5, correct_answer, description
                    FROM quizzes
                    WHERE module = $1
                ''', module)
                return [dict(row) for row in rows]
            except Exception as e:
                raise RuntimeError("Database error occurred while fetching quizzes") from e


