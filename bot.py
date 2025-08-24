
import os, asyncio, time, csv, logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from db import DB
from utils import extract_text_and_media, extract_male_ids
from i18n import t

# --------------- ENV & INIT ---------------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
LANG_DEFAULT = os.getenv("LANG", "ru")
DB_PATH = os.getenv("DB_PATH", "./bot.db")
EXTENSIONS = [m.strip() for m in (os.getenv("EXTENSIONS", "") or "").split(",") if m.strip()]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = DB(DB_PATH)
if OWNER_ID:
    db.add_admin(OWNER_ID)

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

PAGE_SIZE = 5
ADM_PENDING: dict[int, str] = {}

def lang_for(user_id: int) -> str:
    return db.get_user_lang(user_id) or LANG_DEFAULT

def main_menu(user_id: int):
    lang = lang_for(user_id)
    kb = ReplyKeyboardBuilder()
    kb.button(text=t(lang, "menu_search"))
    kb.button(text=t(lang, "menu_mine"))
    kb.button(text=t(lang, "menu_admin"))
    kb.button(text=t(lang, "menu_lang"))
    kb.adjust(2,2)
    return kb.as_markup(resize_keyboard=True)

def is_superadmin(user_id: int) -> bool:
    return user_id == OWNER_ID

def is_admin(user_id: int) -> bool:
    return db.is_admin(user_id)

def has_access(message: Message) -> bool:
    u = message.from_user
    if not u:
        return False
    if is_admin(u.id):
        return True
    return False  # ядро: доступ только админам; пользователей-список можно добавить расширением

# --------------- BASIC ---------------
@dp.message(CommandStart())
async def start(message: Message):
    uid = message.from_user.id
    logger.info("User %s: start", uid)
    db.upsert_user(uid, message.from_user.first_name or "", message.from_user.last_name or "", message.from_user.username or "", None)
    await message.answer(t(lang_for(uid), "start"), reply_markup=main_menu(uid))

@dp.message(F.text.in_({"🌐 Язык: Русский", "🌐 Мова: Українська"}))
async def switch_lang(message: Message):
    uid = message.from_user.id
    logger.info("User %s: switch_lang", uid)
    cur = lang_for(uid)
    new = "uk" if cur == "ru" else "ru"
    db.set_user_lang(uid, new)
    await message.answer(t(new, "menu_lang_set"), reply_markup=main_menu(uid))

# --------------- SEARCH (MEN) ---------------
@dp.message(F.text.in_({"🔍 Поиск по ID (мужчины)", "🔍 Пошук за ID (чоловіки)"}))
async def search_menu_entry(message: Message):
    uid = message.from_user.id
    logger.info("User %s: search_menu_entry", uid)
    if not has_access(message):
        logger.warning("Access denied for user %s in search_menu_entry", uid)
        await message.answer(t(lang_for(uid), "not_authorized"))
        return
    await message.answer(t(lang_for(uid), "search_enter_id"))

@dp.message(F.text.regexp(r"^\d{10}$"))
async def male_search(message: Message):
    uid = message.from_user.id
    logger.info("User %s: male_search", uid)
    if not has_access(message):
        logger.warning("Access denied for user %s in male_search", uid)
        await message.answer(t(lang_for(uid), "not_authorized"))
        return
    if not db.rate_limit_allowed(uid, int(time.time())):
        logger.warning("Rate limit exceeded for user %s", uid)
        await message.answer(t(lang_for(uid), "rate_limited"))
        return
    male = message.text.strip()
    db.log_search(uid, "male", male)
    await send_results(message, male, 0)

async def send_results(message: Message, male_id: str, offset: int):
    uid = message.from_user.id
    logger.info("User %s: send_results male_id=%s offset=%s", uid, male_id, offset)
    lang = lang_for(uid)
    total = db.count_by_male(male_id)
    rows = db.search_by_male(male_id, limit=PAGE_SIZE, offset=offset)
    if not rows:
        await message.answer(t(lang, "search_not_found"))
        return
    for row in rows:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=row["chat_id"], message_id=row["message_id"])
        except Exception:
            logger.error("Failed to copy message for user %s", uid, exc_info=True)
            await message.answer(row["text"] or "(no text)")
    new_offset = offset + PAGE_SIZE
    if new_offset < total:
        kb = InlineKeyboardBuilder()
        kb.button(text=t(lang, "more"), callback_data=f"more:{male_id}:{new_offset}")
        await message.answer(f"{new_offset}/{total}", reply_markup=kb.as_markup())
    else:
        await message.answer(f"{total}/{total}")

@dp.callback_query(F.data.startswith("more:"))
async def cb_more(call: CallbackQuery):
    uid = call.from_user.id
    logger.info("User %s: cb_more", uid)
    _, male_id, off = call.data.split(":")
    await send_results(call.message, male_id, int(off))
    await call.answer()

# --------------- MY QUERIES ---------------
@dp.message(F.text.in_({"🧾 Мои запросы", "🧾 Мої запити"}))
async def my_queries(message: Message):
    uid = message.from_user.id
    logger.info("User %s: my_queries", uid)
    if not has_access(message):
        logger.warning("Access denied for user %s in my_queries", uid)
        await message.answer(t(lang_for(uid), "not_authorized"))
        return
    logs = db.get_user_searches(uid, 10)
    if not logs:
        await message.answer("—")
        return
    lines = [f"{r['created_at']} • {r['query_type']} • {r['query_value']}" for r in logs]
    await message.answer("\n".join(lines))

# --------------- ADMIN MENU ---------------
@dp.message(F.text.in_({"⚙️ Админ", "⚙️ Адмін"}))
async def admin_menu(message: Message):
    uid = message.from_user.id
    logger.info("User %s: admin_menu", uid)
    if not is_admin(uid):
        logger.warning("Access denied for user %s in admin_menu", uid)
        await message.answer(t(lang_for(uid), "admin_only"))
        return
    lang = lang_for(uid)
    kb = ReplyKeyboardBuilder()
    kb.button(text=t(lang, "admin_search_female"))
    kb.button(text=t(lang, "admin_add_chat"))
    kb.button(text=t(lang, "admin_stats"))
    kb.button(text=t(lang, "admin_export"))
    kb.button(text=t(lang, "admin_manage"))
    kb.button(text=t(lang, "menu_search"))
    kb.adjust(2,2,2,1)
    await message.answer(t(lang, "admin_menu"), reply_markup=kb.as_markup(resize_keyboard=True))

@dp.message(F.text.in_({"🔎 Поиск по женскому ID (из названия группы)", "🔎 Пошук за жіночим ID (з назви групи)"}))
async def prompt_female(message: Message):
    uid = message.from_user.id
    logger.info("User %s: prompt_female", uid)
    if not is_admin(uid):
        logger.warning("Access denied for user %s in prompt_female", uid)
        await message.answer(t(lang_for(uid), "admin_only"))
        return
    await message.answer(t(lang_for(uid), "enter_female_id"))

@dp.message(F.text.regexp(r"^f:\d{10}$|^\d{10}$"))
async def handle_female_search(message: Message):
    uid = message.from_user.id
    logger.info("User %s: handle_female_search", uid)
    if not is_admin(uid):
        logger.warning("Access denied for user %s in handle_female_search", uid)
        return
    female_id = message.text[-10:]
    chats = [c for c in db.list_allowed_chats() if c["female_id"] == female_id]
    if not chats:
        await message.answer("Нет разрешённых чатов с таким женским ID.")
        return
    lines = [f"{c['title']} (chat_id={c['chat_id']})" for c in chats]
    await message.answer("\n".join(lines))

@dp.message(F.text.in_({"📊 Статистика", "📊 Статистика"}))
async def stats(message: Message):
    uid = message.from_user.id
    logger.info("User %s: stats", uid)
    if not is_admin(uid):
        logger.warning("Access denied for user %s in stats", uid)
        await message.answer(t(lang_for(uid), "admin_only"))
        return
    men, msgs, chats = db.count_stats()
    await message.answer(t(lang_for(uid), "stats", men=men, msgs=msgs, chats=chats))

@dp.message(F.text.in_({"💾 Экспорт", "💾 Експорт"}))
async def export_menu(message: Message):
    uid = message.from_user.id
    logger.info("User %s: export_menu", uid)
    if not is_admin(uid):
        logger.warning("Access denied for user %s in export_menu", uid)
        return
    lang = lang_for(uid)
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "export_male"), callback_data="export:male")
    kb.button(text=t(lang, "export_all"), callback_data="export:all")
    await message.answer(t(lang, "export_menu"), reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("export:"))
async def cb_export(call: CallbackQuery):
    uid = call.from_user.id
    logger.info("User %s: cb_export", uid)
    if not is_admin(uid):
        logger.warning("Access denied for user %s in cb_export", uid)
        await call.answer("")
        return
    kind = call.data.split(":")[1]
    if kind == "male":
        ADM_PENDING[uid] = "export_male"
        await call.message.answer(t(lang_for(uid), "enter_male_id"))
        await call.answer("")
    else:
        try:
            await bot.send_document(uid, document=open(DB_PATH, "rb"), caption="DB dump (SQLite)")
        except Exception:
            logger.error("Failed to send DB dump to user %s", uid, exc_info=True)
        await call.answer("OK")

@dp.message(F.text.regexp(r"^\d{10}$"))
async def export_male_csv(message: Message):
    uid = message.from_user.id
    logger.info("User %s: export_male_csv", uid)
    if ADM_PENDING.get(uid) != "export_male":
        logger.warning("Unexpected export_male_csv by user %s", uid)
        return
    ADM_PENDING.pop(uid, None)
    male = message.text.strip()
    rows = db.search_by_male(male, limit=10**9, offset=0)
    if not rows:
        logger.warning("No rows for male %s requested by user %s", male, uid)
        await message.answer(t(lang_for(uid), "search_not_found"))
        return
    fname = f"export_{male}.csv"
    with open(fname, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["chat_id","message_id","date","text","media_type","sender_id","sender_username","male_id"])
        for r in rows:
            w.writerow([r["chat_id"], r["message_id"], r["date"], (r["text"] or "").replace("\n"," "), r["media_type"], r["sender_id"], r["sender_username"], r["male_id"]])
    try:
        await bot.send_document(uid, document=open(fname, "rb"), caption=f"CSV для {male}")
    except Exception:
        logger.error("Failed to send CSV for male %s to user %s", male, uid, exc_info=True)

# --------------- GROUP LISTENERS ---------------
@dp.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def on_group_message(message: Message):
    uid = message.from_user.id if message.from_user else None
    logger.info("Group message user=%s chat=%s", uid, message.chat.id)
    if db.get_allowed_chat(message.chat.id) is None:
        logger.warning("Message in unauthorized chat %s from user %s", message.chat.id, uid)
        return
    text, media_type, file_id, is_forward = extract_text_and_media(message)
    if not text:
        return
    male_ids = extract_male_ids(text)
    if not male_ids:
        return
    msg_db_id = db.save_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        sender_id=message.from_user.id if message.from_user else None,
        sender_username=message.from_user.username if message.from_user else None,
        sender_first_name=message.from_user.first_name if message.from_user else None,
        date=int(message.date.timestamp()),
        text=text,
        media_type=media_type,
        file_id=file_id,
        is_forward=1 if (message.forward_from or message.forward_from_chat) else 0,
    )
    db.link_male_ids(msg_db_id, male_ids)

@dp.edited_message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def on_group_edited(message: Message):
    uid = message.from_user.id if message.from_user else None
    logger.info("Group edit user=%s chat=%s", uid, message.chat.id)
    if db.get_allowed_chat(message.chat.id) is None:
        logger.warning("Edit in unauthorized chat %s from user %s", message.chat.id, uid)
        return
    text, media_type, file_id, is_forward = extract_text_and_media(message)
    msg_row = db.conn.execute("SELECT id FROM messages WHERE chat_id=? AND message_id=?", (message.chat.id, message.message_id)).fetchone()
    if not msg_row:
        return
    msg_db_id = msg_row["id"]
    db.update_message_text(message.chat.id, message.message_id, text or "")
    db.unlink_all_male_ids(msg_db_id)
    male_ids = extract_male_ids(text or "")
    db.link_male_ids(msg_db_id, male_ids)

# --------------- EXTENSIONS LOADER ---------------
def load_extensions():
    import importlib
    for mod in EXTENSIONS:
        try:
            m = importlib.import_module(f"extensions.{mod}")
            if hasattr(m, "register"):
                m.register(dp, bot, db, t, lang_for, OWNER_ID)
                logger.info("[ext] loaded: %s", mod)
        except Exception as e:
            logger.error("[ext] error loading %s: %s", mod, e, exc_info=True)

# --------------- ENTRYPOINT ---------------
async def main():
    load_extensions()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
