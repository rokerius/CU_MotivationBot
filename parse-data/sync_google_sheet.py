import os
import asyncio
import gspread
from gspread_dataframe import get_as_dataframe
from tg_bot.app.database.db import db

GOOGLE_SHEET_NAME = 'Учебные материалы'
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')
REQUIRED_FIELDS = ['user_id', 'module', 'theme', 'title', 'content']

async def main():
    await db.connect()
    try:
        gc = gspread.service_account(filename=CREDENTIALS_PATH)
    except Exception as e:
        print('Не удалось подключиться к гугл api')
        print(e)
    try:
        worksheet = gc.open(GOOGLE_SHEET_NAME).sheet1
    except Exception as e:
        print('Не нашлась таблица. Возможно неправильное имя')
    df = get_as_dataframe(worksheet, evaluate_formulas=True).dropna(how='all')
    df = df.reset_index(drop=True)
    df = df.dropna(subset=REQUIRED_FIELDS)
    db_posts = await db.get_all_posts()
    db_index = {(int(p['module']), int(p['theme'])): p for p in db_posts}
    added, updated = 0, 0
    for _, row in df.iterrows():
        try:
            user_id = int(row['user_id'])
            module = int(row['module'])
            theme = int(row['theme'])
            title = str(row['title'])
            content = str(row['content'])
        except Exception as e:
            print(f"Ошибка в строке: {row} — {e}")
            continue
        key = (module, theme)
        db_post = db_index.get(key)
        if not db_post:
            await db.add_post(user_id, module, theme, title, content)
            added += 1
        else:
            if db_post['title'] != title or db_post['content'] != content or db_post['user_id'] != user_id:
                await db.add_post(user_id, module, theme, title, content)
                updated += 1
    print(f"Синхронизация завершена. Добавлено: {added}, обновлено: {updated}")

if __name__ == '__main__':
    asyncio.run(main()) 