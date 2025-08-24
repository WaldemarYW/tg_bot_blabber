
import logging
import random
from aiogram import F
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.types import Message


logger = logging.getLogger(__name__)

def register(dp, bot, db, t, lang_for, OWNER_ID):
    @dp.message(F.text.in_({"➕ Добавить разрешённый чат", "➕ Додати дозволений чат"}))
    async def add_chat_hint(message: Message):
        uid = message.from_user.id
        lang = lang_for(uid)
        if not (db.is_admin(uid) or uid == OWNER_ID):
            await message.answer(t(lang, "add_chat_admins_only"))
            return
        secret = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=8))
        logger.info("Generated auth secret %s for user %s", secret, uid)
        db.set_setting(f"auth_secret:{uid}", secret)
        await message.answer(t(lang, "auth_secret_dm", secret=secret))

    @dp.message(Command("authorize"))
    async def authorize_group(message: Message):
        if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
            return
        uid = message.from_user.id
        lang = lang_for(uid)
        if not (db.is_admin(uid) or uid == OWNER_ID):
            logger.warning("User %s attempted to authorize without admin rights in chat %s", uid, message.chat.id)
            await message.reply(t(lang, "add_chat_admins_only"))
            return
        parts = (message.text or "").strip().split(maxsplit=1)
        if len(parts) < 2:
            logger.warning("User %s did not supply a token for chat %s", uid, message.chat.id)
            await message.reply(t(lang, "authorize_need_token"))
            return
        supplied = parts[1].strip()
        expected = db.get_setting(f"auth_secret:{uid}")
        if not expected or supplied != expected:
            logger.warning("User %s supplied invalid or expired token for chat %s", uid, message.chat.id)
            await message.reply(t(lang, "authorize_bad_or_expired"))
            return
        member = await bot.get_chat_member(message.chat.id, uid)
        if member.status not in ("administrator","creator"):
            logger.warning("User %s is not admin of chat %s", uid, message.chat.id)
            await message.reply(t(lang, "authorize_need_admin"))
            return
        title = message.chat.title or ""
        female_id = db.get_female_id_from_title(title)
        if not female_id:
            logger.warning("Chat %s has no female id for authorization by user %s", message.chat.id, uid)
            await message.reply(t(lang, "group_no_female_id"))
            return
        db.add_allowed_chat(message.chat.id, title, female_id, uid)
        db.del_setting(f"auth_secret:{uid}")
        logger.info("Chat %s authorized with female id %s by user %s", message.chat.id, female_id, uid)
        await message.reply(t(lang, "authorize_ok", fid=female_id))

    @dp.message(Command("unauthorize"))
    async def unauthorize_group(message: Message):
        if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
            return
        uid = message.from_user.id
        lang = lang_for(uid)
        if uid != OWNER_ID:
            logger.warning("User %s attempted to unauthorize chat %s without permission", uid, message.chat.id)
            await message.reply(t(lang, "unauthorize_only_superadmin"))
            return
        db.conn.execute("DELETE FROM allowed_chats WHERE chat_id=?", (message.chat.id,))
        db.conn.commit()
        logger.info("Chat %s unauthorized by user %s", message.chat.id, uid)
        await message.reply(t(lang, "unauthorize_ok"))
