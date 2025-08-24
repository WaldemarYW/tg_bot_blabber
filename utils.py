
import re
from aiogram.types import Message

ID_RE = re.compile(r'(?<!\d)(\d{10})(?!\d)')

def extract_text_and_media(message: Message):
    text = message.text or message.caption or ""
    media_type = "text"
    file_id = None

    if message.photo:
        media_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        media_type = "video"
        file_id = message.video.file_id
    elif message.document:
        media_type = "document"
        file_id = message.document.file_id
    elif message.voice:
        media_type = "voice"
        file_id = message.voice.file_id
    elif message.audio:
        media_type = "audio"
        file_id = message.audio.file_id
    elif message.sticker:
        media_type = "sticker"
        file_id = message.sticker.file_id

    is_forward = 1 if (message.forward_from or message.forward_from_chat) else 0
    return text, media_type, file_id, is_forward

def extract_male_ids(text: str):
    return list({m.group(1) for m in ID_RE.finditer(text or "")})
