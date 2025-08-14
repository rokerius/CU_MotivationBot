from aiogram import types
from aiogram.types import InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest
import os
import csv
import logging
import tempfile

logger = logging.getLogger(__name__)
ADMINS = os.getenv("ADMINS", "").split()

async def safe_delete_message(message):
    try:
        await message.delete()
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            pass
        else:
            logger.error(f"Failed to delete message: {e}")


async def show_post_with_images(message: types.Message, module: int, theme: int, db):
    post = await db.get_post_by_module_and_theme(module, theme)
    if not post:
        await message.answer("Пост с таким модулем и темой не найден.")
        return

    title = post.get('title', '').strip()
    content = post.get('content', '').replace('\\n', '\n').strip()
    caption = f"<b>{title}</b>\n\n{content}"
    if not title or title == "nan":
        if not content or content == "nan":
            caption = ""
        else:
            caption = content

    async with db.pool.acquire() as conn:
        rows = await conn.fetch('SELECT image_url, file_id FROM post_images WHERE post_id = $1 ORDER BY id ASC',
                                post['id'])
    if not rows:
        await message.answer(caption, parse_mode="HTML")
        return

    media = []
    first = True
    should_add_file_ides = []
    for row in rows:
        should_add_file_ides.append(False)
        image = row["file_id"]
        if not image:
            image = row['image_url']
            if not image:
                raise ValueError("no image in row")
            should_add_file_ides[-1] = True

        if first:
            media.append(InputMediaPhoto(media=image, caption=caption, parse_mode="HTML"))
            first = False
        else:
            media.append(InputMediaPhoto(media=image))

    sent_messages = await message.answer_media_group(media=media)

    for i in range(len(sent_messages)):
        photo_sizes = sent_messages[i].photo

        if photo_sizes and should_add_file_ides[i]:
            file_id = photo_sizes[-1].file_id
            await db.save_file_id_for_post_image(rows[i]["image_url"], file_id)


def is_admin(username: str) -> bool:
    return username in ADMINS

async def dicts_to_csv(dict_list, filename_telegram):
    tmp_path = None
    try:
        tmp_file = tempfile.NamedTemporaryFile(mode='w+', newline='', suffix='.csv', delete=False, encoding='utf-8')
        tmp_path = tmp_file.name

        writer = csv.DictWriter(tmp_file, fieldnames=list(dict_list[0].keys()))
        writer.writeheader()
        writer.writerows(dict_list)
        tmp_file.close()

        return tmp_path, filename_telegram
    except Exception as e:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise e

