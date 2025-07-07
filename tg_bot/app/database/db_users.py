from .db_base import DatabaseBase

class UsersDatabase(DatabaseBase):

    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (id, username, first_name, last_name, modules)
                VALUES ($1, $2, $3, $4, '00000000')
                ON CONFLICT (id) DO NOTHING
            ''', user_id, username, first_name, last_name)

    async def get_user_by_id(self, user_id: int):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
            if row:
                return dict(row)
            return None

    async def add_goals(self, user_id: int, goals: str):
        async with self.pool.acquire() as conn:
            await conn.execute('UPDATE users SET goals = $1 WHERE id = $2', goals, user_id)

    async def change_modules_done(self, user_id: int, module: int, value: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT modules FROM users WHERE id = $1', user_id)
            if not row:
                return False
            if value not in ["1", "2", "3"]:
                return False

            modules = list(row['modules'])
            modules[module-1] = value
            new_modules = ''.join(modules)

            await conn.execute('UPDATE users SET modules = $1 WHERE id = $2', new_modules, user_id)
            return True

    async def save_answer(self, module: int, user_id: int, answer: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT answers FROM users WHERE id = $1', user_id)
            if not row:
                return False

            old_answers = row['answers'] or ""
            answers = old_answers + "\n" + str(module) + ") " + answer

            await conn.execute('UPDATE users SET answers = $1 WHERE id = $2', answers, user_id)
            return True

    async def save_quiz_answer(self, user_id: int, module: int, quiz: int, answer: str):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT quiz_answers FROM users WHERE id = $1', user_id)
            if not row:
                return False

            old_answers = row['quiz_answers'] or ""
            answers = old_answers + "\n" + str(module) + "." + str(quiz) + ") " + answer

            await conn.execute('UPDATE users SET quiz_answers = $1 WHERE id = $2', answers, user_id)
            return True
