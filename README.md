
# TG ID Bot — Core + Extensions

Готовая сборка ядра и механизм расширений (extensions). Ядро минимально, новые функции добавляем отдельными модулями, чтобы не ломать базу.

## Возможности ядра
- Индексация 10-значных ID (мужчины) в группах/супергруппах (privacy OFF).
- Поиск в личке, выдача по 5, «Показать ещё». Если оригинал недоступен — отправляет сохранённый текст **без** служебных меток.
- Белый список чатов (через `allowed_chats`).
- Роли: суперадмин (OWNER_ID) + админы.
- Экспорт: CSV по мужскому ID и дамп SQLite.
- RU/UA локализация, антиспам (1 запрос / 2 сек), «Мои запросы».
- Мягкие KV-настройки через таблицу `settings` (для расширений).

## Расширения
Подключаются через переменную окружения `.env`:
```
EXTENSIONS=auth_secret
```
- `auth_secret`: добавляет одноразовый пароль для `/authorize`: админ генерирует пароль в личке, в группе запускает `/authorize <пароль>`. Также добавляет `/unauthorize` (только суперадмин).

## Быстрый старт (macOS)
```bash
cd /Users/waldemar/Documents/GitHub/tg_bot_blabber
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
open -e .env   # впиши BOT_TOKEN и OWNER_ID (число), при желании EXTENSIONS=auth_secret
python3 bot.py
```
BotFather → `/setprivacy` → **Disable**.

## Git (очень коротко)
1. Инициализация и первый коммит:
```bash
git init
git add .
git commit -m "core: stable baseline"
git tag core-1.0
```
2. Создай пустой репозиторий на GitHub (без README). Допустим, адрес: `https://github.com/ВАШ_ЛОГИН/tg-id-bot.git`  
   Привяжи и запушь:
```bash
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/tg-id-bot.git
git push -u origin main --tags
```
3. Новая фича — отдельная ветка:
```bash
git checkout -b feat/invite-links
# ... правки в extensions/ ...
git commit -am "feat: invite links"
git checkout main
git merge --no-ff feat/invite-links -m "merge: invite links"
git push
```

## Безопасность данных
- Миграции делаем только **добавочные** (CREATE/ALTER ... ADD COLUMN).
- Перед апдейтом: `sqlite3 bot.db ".backup 'backup-$(date +%F-%H%M).db'"`

