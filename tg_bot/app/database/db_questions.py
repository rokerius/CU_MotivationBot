from .db_base import DatabaseBase

class QuestionsDatabase(DatabaseBase):
    async def add_question(self, module: int, question: str):
        if len(question) > 1000:
            raise ValueError("question is too long")

        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO module_questions (module, question)
                VALUES ($1, $2)
            ''', module, question)

    async def get_question_by_module(self, module: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT question FROM module_questions
                WHERE module = $1
                LIMIT 1
            ''', module)
            if row:
                return row["question"]
            return None

    async def check_questions_done(self, user_id: int, module: int) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT answers FROM users WHERE id = $1', user_id)
            if not row:
                return False

            answers = row['answers']
            if answers is None:
                return False

            return "$question" + str(module) + "|" in answers