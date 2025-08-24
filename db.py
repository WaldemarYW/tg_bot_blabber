
import sqlite3, os
from pathlib import Path
from typing import Optional

import re
import logging
import functools
import inspect

logger = logging.getLogger(__name__)


def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = inspect.signature(func).bind(*args, **kwargs)
        bound.apply_defaults()
        params = {k: v for k, v in bound.arguments.items() if k != "self"}
        logger.info("Calling %s with %s", func.__name__, params)
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.exception("Error in %s", func.__name__)
            raise
    return wrapper

class DB:
    @log_call
    def __init__(self, path: str):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.ensure_schema()

    @log_call
    def ensure_schema(self):
        sql = Path("messages.sql").read_text(encoding="utf-8")
        self.conn.executescript(sql)
        self.conn.commit()

    # ---- Admins
    @log_call
    def add_admin(self, user_id: int):
        self.conn.execute("INSERT OR IGNORE INTO admins(user_id) VALUES (?)", (user_id,))
        self.conn.commit()

    @log_call
    def is_admin(self, user_id: int) -> bool:
        r = self.conn.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,)).fetchone()
        return r is not None

    # ---- Users table
    @log_call
    def set_user_lang(self, user_id: int, lang: str):
        self.conn.execute(
            """INSERT INTO users(user_id, lang) VALUES(?,?)
               ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang, updated_at=CURRENT_TIMESTAMP""",
                          (user_id, lang)
        )
        self.conn.commit()

    @log_call
    def get_user_lang(self, user_id: int) -> Optional[str]:
        r = self.conn.execute("SELECT lang FROM users WHERE user_id=?", (user_id,)).fetchone()
        return r["lang"] if r and r["lang"] in ("ru","uk") else None

    @log_call
    def upsert_user(self, user_id: int, first_name: str, last_name: str, username: str, lang: Optional[str]):
        self.conn.execute(
            """INSERT INTO users(user_id, first_name, last_name, username, lang)
               VALUES(?,?,?,?,?)
               ON CONFLICT(user_id) DO UPDATE SET
                 first_name=excluded.first_name,
                 last_name=excluded.last_name,
                 username=excluded.username,
                 updated_at=CURRENT_TIMESTAMP""",
            (user_id, first_name, last_name, username, lang),
        )
        self.conn.commit()

    # ---- Allowed chats (by female id in title)
    @log_call
    def add_allowed_chat(self, chat_id: int, title: str, female_id: str, added_by: int):
        self.conn.execute(
            """INSERT OR REPLACE INTO allowed_chats(chat_id, title, female_id, added_by)
               VALUES(?,?,?,?)""",
            (chat_id, title, female_id, added_by),
        )
        self.conn.commit()

    @log_call
    def get_allowed_chat(self, chat_id: int):
        return self.conn.execute("SELECT * FROM allowed_chats WHERE chat_id=?", (chat_id,)).fetchone()

    @log_call
    def list_allowed_chats(self):
        return self.conn.execute("SELECT * FROM allowed_chats ORDER BY added_at DESC").fetchall()

    @log_call
    def get_female_id_from_title(self, title: str):
        m = re.search(r'(?:^|[^0-9])([0-9]{10})(?:[^0-9]|$)', title or "")
        return m.group(1) if m else None

    # ---- KV settings (for extensions)
    @log_call
    def set_setting(self, key: str, value: str):
        self.conn.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        self.conn.commit()

    @log_call
    def get_setting(self, key: str):
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None

    @log_call
    def del_setting(self, key: str):
        self.conn.execute("DELETE FROM settings WHERE key=?", (key,))
        self.conn.commit()

    # ---- Messages / Linking
    @log_call
    def save_message(self, chat_id: int, message_id: int, sender_id: int, sender_username: str,
                     sender_first_name: str, date: int, text: str, media_type: str,
                     file_id: str, is_forward: int) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """INSERT OR IGNORE INTO messages(chat_id, message_id, sender_id, sender_username,
                    sender_first_name, date, text, media_type, file_id, is_forward)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (chat_id, message_id, sender_id, sender_username, sender_first_name, date, text, media_type, file_id, is_forward),
        )
        self.conn.commit()
        msg_db = cur.execute("SELECT id FROM messages WHERE chat_id=? AND message_id=?", (chat_id, message_id)).fetchone()
        return msg_db["id"]

    @log_call
    def update_message_text(self, chat_id: int, message_id: int, text: str):
        self.conn.execute("""UPDATE messages SET text=? WHERE chat_id=? AND message_id=?""", (text, chat_id, message_id))
        self.conn.commit()

    @log_call
    def link_male_ids(self, message_db_id: int, male_ids: list[str]):
        for mid in set(male_ids):
            try:
                self.conn.execute(
                    """INSERT OR IGNORE INTO message_male_ids(message_id_ref, male_id)
                                     VALUES(?,?)""",
                    (message_db_id, mid),
                )
            except Exception:
                logger.exception(
                    "Failed to link male_id %s for message %s", mid, message_db_id
                )
        self.conn.commit()

    @log_call
    def unlink_all_male_ids(self, message_db_id: int):
        self.conn.execute("DELETE FROM message_male_ids WHERE message_id_ref=?", (message_db_id,))
        self.conn.commit()

    # ---- Search / Stats
    @log_call
    def search_by_male(self, male_id: str, limit: int=5, offset: int=0):
        return self.conn.execute(
            """
            SELECT m.*, mm.male_id FROM messages m
            JOIN message_male_ids mm ON mm.message_id_ref = m.id
            WHERE mm.male_id = ?
            ORDER BY m.date DESC
            LIMIT ? OFFSET ?
        """,
            (male_id, limit, offset),
        ).fetchall()

    @log_call
    def count_by_male(self, male_id: str) -> int:
        r = self.conn.execute(
            """
            SELECT COUNT(*) c FROM messages m
            JOIN message_male_ids mm ON mm.message_id_ref = m.id
            WHERE mm.male_id = ?
        """,
            (male_id,),
        ).fetchone()
        return r["c"] if r else 0

    @log_call
    def count_stats(self):
        men = self.conn.execute("SELECT COUNT(DISTINCT male_id) c FROM message_male_ids").fetchone()["c"]
        msgs = self.conn.execute("SELECT COUNT(*) c FROM messages").fetchone()["c"]
        chats = self.conn.execute("SELECT COUNT(*) c FROM allowed_chats").fetchone()["c"]
        return men, msgs, chats

    # ---- Logs / Rate limit
    @log_call
    def log_search(self, user_id: int, query_type: str, query_value: str):
        self.conn.execute("INSERT INTO searches(user_id, query_type, query_value) VALUES(?,?,?)", (user_id, query_type, query_value))
        self.conn.commit()

    @log_call
    def get_user_searches(self, user_id: int, limit=10):
        return self.conn.execute(
            """SELECT * FROM searches WHERE user_id=? ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()

    @log_call
    def rate_limit_allowed(self, user_id: int, now_ts: int, min_interval: int = 2) -> bool:
        r = self.conn.execute("SELECT last_action_ts FROM ratelimits WHERE user_id=?", (user_id,)).fetchone()
        if r is None:
            self.conn.execute("INSERT OR REPLACE INTO ratelimits(user_id, last_action_ts) VALUES(?,?)", (user_id, now_ts))
            self.conn.commit()
            return True
        last = r["last_action_ts"]
        if now_ts - last < min_interval:
            return False
        self.conn.execute("UPDATE ratelimits SET last_action_ts=? WHERE user_id=?", (now_ts, user_id))
        self.conn.commit()
        return True
