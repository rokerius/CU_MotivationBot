import pytest
from sync_google_sheet import main, REQUIRED_FIELDS
from tg_bot.app.database.db import db

@pytest.mark.asyncio
async def test_sync_google_sheet():
    await db.connect()
    await db.init_tables()

    async with db.pool.acquire() as conn:
        await conn.execute('DELETE FROM posts')

    await main()

    posts = await db.get_all_posts()
    assert len(posts) > 0, "В базе должны появиться посты после синхронизации"

    for post in posts:
        for field in REQUIRED_FIELDS:
            assert post.get(field) is not None, f"Поле {field} должно быть заполнено"

    await db.disconnect() 