from aiogram import types
from aiogram.types import InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest
import os
import csv
import re
import logging

logger = logging.getLogger(__name__)
ADMINS = os.getenv("ADMINS").split()

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
    caption = f"<b>{title}</b>\n\n{content}" if (title or content) else "Пост не содержит текста"
    async with db.pool.acquire() as conn:
        rows = await conn.fetch('SELECT image_url, file_id FROM post_images WHERE post_id = $1', post['id'])
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


def read_modules_description_from_csv(file_path):
    modules_description = {}
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row or row[0] == "id":
                continue
            key = int(row[0].strip())
            value = row[1].strip()
            modules_description[key] = value
    return modules_description

def convert_drive_url(url: str) -> str:
    pattern = r"https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/view(?:\?.*)?"
    match = re.match(pattern, url)
    if match:
        file_id = match.group(1)
        return f"https://docs.google.com/uc?id={file_id}"
    return url


def is_admin(username: str) -> bool:
    return username in ADMINS
