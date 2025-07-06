from aiogram import types
from aiogram.types import InputMediaPhoto
import os

ADMINS = os.getenv("ADMINS").split()


async def show_post_with_images(message: types.Message, module: int, theme: int, db):
    post = await db.get_post_by_module_and_theme(module, theme)
    if not post:
        await message.answer("Пост с таким модулем и темой не найден.")
        return

    async with db.pool.acquire() as conn:
        rows = await conn.fetch('SELECT image_url FROM post_images WHERE post_id = $1', post['id'])
    if not rows:
        await message.answer(f"<b>{post['title']}</b>\n\n{post['content']}", parse_mode="HTML")
        return

    media = []
    caption = f"<b>{post['title']}</b>\n\n{post['content']}"
    first = True
    for row in rows:
        if first:
            media.append(InputMediaPhoto(media=row['image_url'], caption=caption, parse_mode="HTML"))
            first = False
        else:
            media.append(InputMediaPhoto(media=row['image_url']))

    await message.answer_media_group(media=media)


def is_admin(username: str) -> bool:
    return username in ADMINS
