
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS allowed_chats (
    chat_id INTEGER PRIMARY KEY,
    title TEXT,
    female_id TEXT,
    added_by INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    lang TEXT,
    is_blocked INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    sender_id INTEGER,
    sender_username TEXT,
    sender_first_name TEXT,
    date INTEGER,
    text TEXT,
    media_type TEXT,
    file_id TEXT,
    is_forward INTEGER DEFAULT 0,
    UNIQUE(chat_id, message_id)
);

CREATE TABLE IF NOT EXISTS message_male_ids (
    message_id_ref INTEGER NOT NULL,
    male_id TEXT NOT NULL,
    UNIQUE(message_id_ref, male_id),
    FOREIGN KEY(message_id_ref) REFERENCES messages(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_male_id ON message_male_ids(male_id);

CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, message_id);
CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date);

CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    query_type TEXT,
    query_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ratelimits (
    user_id INTEGER PRIMARY KEY,
    last_action_ts INTEGER
);
