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
        

    async def update_questions_data(self, df):
        logs = []
        updated = 0
        for i, row in df.iterrows():
            try:
                module = int(row['module'])
                question = str(row['question'])
            except Exception as e:
                logs.append(f"Ошибка в строке: {i+1} — {e}. Полученные данные: \n\n{row} \n\nПереходим к следующей")
                continue
            db_question = await self.get_question_by_module(module)
            if db_question != question:
                logs.append(f"Обновляем вопрос в модуле {module}...")
                try:
                    await self.add_question(module, question)
                except Exception as e:
                    logs.append(f"Ошибка при обновлении вопроса в модуле {module}: {e}")
                else:
                    updated += 1
        logs.append(f"Синхронизация вопросов завершена. Обновлено: {updated}")

        return logs