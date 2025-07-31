from .db_base import DatabaseBase


class QuizzesDatabase(DatabaseBase):

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

        valid_options = {option_1, option_2}
        if option_3:
            valid_options.add(option_3)
        if option_4:
            valid_options.add(option_4)
        if option_5:
            valid_options.add(option_5)

        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO quizzes (
                    module, question, option_1, option_2, option_3, option_4, 
                    option_5, correct_answer, description
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ''', module, question, option_1, option_2, option_3, option_4,
                               option_5, correct_answer, description)

    async def get_quizzes_by_module(self, module: int):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT id, module, question, option_1, option_2, option_3, option_4, 
                       option_5, correct_answer, description
                FROM quizzes
                WHERE module = $1
            ''', module)
            return [dict(row) for row in rows]


    async def check_quizzes_done(self, user_id: int, quiz: int, module: int) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT answers FROM users WHERE id = $1', user_id)
            if row is None:
                return False

            answers = row['answers']
            if answers is None:
                return False

            return "$quiz" + str(module) + "." + str(quiz + 1) in answers
