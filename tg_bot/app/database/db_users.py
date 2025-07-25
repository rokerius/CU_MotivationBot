from .db_base import DatabaseBase

class UsersDatabase(DatabaseBase):

    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str):
        if not (isinstance(user_id, int) and user_id > 0):
            raise ValueError("user_id must be a positive integer")
        for field_name, field_value in [("username", username), ("first_name", first_name), ("last_name", last_name)]:
            if not isinstance(field_value, str):
                raise ValueError(f"{field_name} must be a string")

        async with self.pool.acquire() as conn:
            try:
                await conn.execute('''
                    INSERT INTO users (id, username, first_name, last_name, modules)
                    VALUES ($1, $2, $3, $4, '00000000')
                    ON CONFLICT (id) DO NOTHING
                ''', user_id, username, first_name, last_name)
            except Exception as e:
                raise RuntimeError("Database error occurred while adding user") from e

    async def get_user_by_id(self, user_id: int):
        if not (isinstance(user_id, int) and user_id > 0):
            raise ValueError("user_id must be a positive integer")

        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
                if row:
                    return dict(row)
                return None
            except Exception as e:
                raise RuntimeError("Database error occurred while fetching user") from e

    async def add_goals(self, user_id: int, goals: str):
        if not (isinstance(user_id, int) and user_id > 0):
            raise ValueError("user_id must be a positive integer")
        if not isinstance(goals, str):
            raise ValueError("goals must be a string")

        async with self.pool.acquire() as conn:
            try:
                await conn.execute('UPDATE users SET goals = $1 WHERE id = $2', goals, user_id)
            except Exception as e:
                raise RuntimeError("Database error occurred while updating goals") from e

    async def change_modules_done(self, user_id: int, module: int, value: str):
        if not (isinstance(user_id, int) and user_id > 0):
            raise ValueError("user_id must be a positive integer")
        if not (isinstance(module, int) and module > 0):
            raise ValueError("module must be a positive integer")
        if value not in ["1", "2", "3"]:
            raise ValueError("value must be one of '1', '2', '3'")

        async with self.pool.acquire() as conn:
            try:
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
            except Exception as e:
                raise RuntimeError("Database error occurred while changing modules") from e

    async def save_answer(self, module: int, user_id: int, answer: str):
        if not (isinstance(user_id, int) and user_id > 0):
            raise ValueError("user_id must be a positive integer")
        if not (isinstance(module, int) and module > 0):
            raise ValueError("module must be a positive integer")
        if not isinstance(answer, str):
            raise ValueError("answer must be a string")

        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow('SELECT answers FROM users WHERE id = $1', user_id)
                if not row:
                    return False

                old_answers = row['answers'] or ""
                answers = old_answers + f"$question{module}|{answer}"

                await conn.execute('UPDATE users SET answers = $1 WHERE id = $2', answers, user_id)
                return True
            except Exception as e:
                raise RuntimeError("Database error occurred while saving answer") from e

    async def save_quiz_answer(self, user_id: int, module: int, quiz: int, answer: str):
        if not (isinstance(user_id, int) and user_id > 0):
            raise ValueError("user_id must be a positive integer")
        if not (isinstance(module, int) and module > 0):
            raise ValueError("module must be a positive integer")
        if not (isinstance(quiz, int) and quiz > 0):
            raise ValueError(f"quiz number must a positive integer")
        if not isinstance(answer, str):
            raise ValueError("answer must be a string")

        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow('SELECT answers FROM users WHERE id = $1', user_id)
                if not row:
                    return False

                old_answers = row['answers'] or ""
                answers = old_answers + f"$quiz{module}.{quiz}|{answer}"

                await conn.execute('UPDATE users SET answers = $1 WHERE id = $2', answers, user_id)
                return True
            except Exception as e:
                raise RuntimeError("Database error occurred while saving quiz answer") from e

    async def get_answers(self, user_id: int):
        if not (isinstance(user_id, int) and user_id > 0):
            raise ValueError("user_id must be a positive integer")

        async with self.pool.acquire() as conn:
            try:
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
                    "answer": x.split('|')[1]
                } for x in quiz_answers_list]
                questions_answers = [{
                    "module": x.split('|')[0][8:],
                    "answer": x.split('|')[1]
                } for x in questions_answers_list]
                return {"quizzes": quiz_answers, "questions": questions_answers}
            except Exception as e:
                raise RuntimeError("Database error occurred while fetching answers") from e
