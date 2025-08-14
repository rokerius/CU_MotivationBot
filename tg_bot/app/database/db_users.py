from datetime import datetime

from .db_base import DatabaseBase

class UsersDatabase(DatabaseBase):

    async def add_user(self, user_id: int, username: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (id, username, modules)
                VALUES ($1, $2, '00000000')
                ON CONFLICT (id) DO NOTHING
            ''', user_id, username)

    async def get_user_by_id(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
            if row:
                return dict(row)
            return None

    async def add_letter(self, user_id: int, letter: str):
        async with self.pool.acquire() as conn:
            await conn.execute('UPDATE users SET letter = $1 WHERE id = $2', letter, user_id)

    async def change_modules_done(self, user_id: int, module: int, value: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT modules FROM users WHERE id = $1', user_id)
            if not row:
                return False

            modules = list(row['modules'])
            if module > len(modules):
                return False

            modules[module - 1] = value
            new_modules = ''.join(modules)

            await conn.execute('UPDATE users SET modules = $1 WHERE id = $2', new_modules, user_id)
            return True

    async def save_answer(self, module: int, user_id: int, answer: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT answers FROM users WHERE id = $1', user_id)
            if not row:
                return False
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            old_answers = row['answers'] or ""
            answers = old_answers + f"$question{module}|{answer}|{now}"

            await conn.execute('UPDATE users SET answers = $1 WHERE id = $2', answers, user_id)
            return True

    async def save_quiz_answer(self, user_id: int, module: int, quiz: int, answer: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT answers FROM users WHERE id = $1', user_id)
            if not row:
                return False

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            old_answers = row['answers'] or ""
            answers = old_answers + f"$quiz{module}.{quiz}|{answer}|{now}"

            await conn.execute('UPDATE users SET answers = $1 WHERE id = $2', answers, user_id)
            return True

    async def get_answers(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT answers FROM users WHERE id = $1', user_id)
            if not row:
                return None
            answers_string = row['answers'] or ""
            answers_list = answers_string.split("$")
            quiz_answers_list = [x for x in answers_list if x.startswith("quiz")]
            questions_answers_list = [x for x in answers_list if x.startswith("question")]
            quiz_answers = [{
                "module": x.split('.')[0][4:],
                "number": x.split('|')[0].split('.')[1],
                "answer": x.split('|')[1],
                "time": x.split('|')[2]
            } for x in quiz_answers_list]
            questions_answers = [{
                "module": x.split('|')[0][8:],
                "answer": x.split('|')[1],
                "time": x.split('|')[2]
            } for x in questions_answers_list]
            return {"quizzes": quiz_answers, "questions": questions_answers}
