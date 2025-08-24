
from typing import Literal

Lang = Literal["ru","uk"]

RU = {
    "start": "Привіт! / Привет!\nВиберіть дію нижче / Выберите действие ниже.",
    "menu_search": "🔍 Поиск по ID (мужчины)",
    "menu_mine": "🧾 Мои запросы",
    "menu_admin": "⚙️ Админ",
    "menu_lang": "🌐 Язык: Русский",
    "menu_lang_set": "Язык переключён.",
    "search_enter_id": "Введи 10-значный ID мужчины.",
    "search_not_found": "Ничего не найдено по этому ID.",
    "more": "Показать ещё",
    "admin_only": "Только для админов.",
    "admin_menu": "Админ-меню",
    "admin_search_female": "🔎 Поиск по женскому ID (из названия группы)",
    "admin_add_chat": "➕ Добавить разрешённый чат",
    "admin_stats": "📊 Статистика",
    "admin_export": "💾 Экспорт",
    "admin_manage": "👤 Админы",
    "admin_add_admin": "➕ Добавить админа",
    "admin_remove_admin": "➖ Удалить админа",
    "prompt_user_id": "Отправьте user_id в формате id:123456789 (только цифры после id:), чтобы выдать/забрать права администратора.",
    "done": "Готово.",
    "authorize_hint": "Зайди в целевую группу и отправь там команду /authorize <пароль>.",
    "authorize_ok": "Чат разрешён. Женский ID: {fid}",
    "authorize_need_admin": "Требуются права администратора группы.",
    "group_no_female_id": "В названии группы нет 10-значного женского ID.",
    "stats": "Мужчин (уникальных ID): {men}\nСообщений: {msgs}\nЧатов: {chats}",
    "export_menu": "Выбери, что экспортировать",
    "export_male": "Экспорт по мужскому ID",
    "export_all": "Полный экспорт",
    "enter_female_id": "Введи 10-значный женский ID.",
    "enter_male_id": "Введи 10-значный мужской ID.",
    "bad_id": "Нужно ровно 10 цифр.",
    "rate_limited": "Слишком часто. Подожди пару секунд.",
    "prompt_add_user": "Отправьте @username пользователя (без ссылки), которого нужно ДОБАВИТЬ к использованию бота.",
    "prompt_del_user": "Отправьте @username пользователя (без ссылки), которого нужно УДАЛИТЬ из доступа к боту.",
    "admin_manage_users": "👥 Пользователи",
    "admin_add_user": "➕ Добавить пользователя",
    "admin_remove_user": "➖ Удалить пользователя",
    "not_authorized": "У вас нет доступа. Обратитесь к администратору бота.",
    "only_superadmin": "Это действие доступно только суперадмину.",

    "add_chat_admins_only": "Добавлять чаты могут только админы или суперадмин.",
    "auth_secret_dm": "Пароль для авторизации чата: <b>{secret}</b>\nПерейдите в нужную группу и отправьте: <code>/authorize {secret}</code>",
    "authorize_need_token": "Нужно использовать формат: /authorize <пароль>, полученный в личке от бота.",
    "authorize_bad_or_expired": "Пароль не подходит или устарел. Сгенерируйте новый в личке.",
    "unauthorize_ok": "Чат удалён из разрешённых.",
    "unauthorize_only_superadmin": "Удалять чаты может только суперадмин."
}

UK = {
    "start": "Привіт! / Привет!\nВиберіть дію нижче / Выберите действие нижче.",
    "menu_search": "🔍 Пошук за ID (чоловіки)",
    "menu_mine": "🧾 Мої запити",
    "menu_admin": "⚙️ Адмін",
    "menu_lang": "🌐 Мова: Українська",
    "menu_lang_set": "Мову перемкнено.",
    "search_enter_id": "Введи 10-значний ID чоловіка.",
    "search_not_found": "Нічого не знайдено за цим ID.",
    "more": "Показати ще",
    "admin_only": "Лише для адміністраторів.",
    "admin_menu": "Адмін-меню",
    "admin_search_female": "🔎 Пошук за жіночим ID (з назви групи)",
    "admin_add_chat": "➕ Додати дозволений чат",
    "admin_stats": "📊 Статистика",
    "admin_export": "💾 Експорт",
    "admin_manage": "👤 Адміни",
    "admin_add_admin": "➕ Додати адміна",
    "admin_remove_admin": "➖ Удалити адміна",
    "prompt_user_id": "Надішліть user_id у форматі id:123456789 (лише цифри після id:), щоб видати/забрати права адміністратора.",
    "done": "Готово.",
    "authorize_hint": "Зайди в цільову групу і надішли там команду /authorize <пароль>.",
    "authorize_ok": "Чат дозволено. Жіночий ID: {fid}",
    "authorize_need_admin": "Потрібні права адміністратора групи.",
    "group_no_female_id": "У назві групи немає 10-значного жіночого ID.",
    "stats": "Чоловіків (унікальних ID): {men}\nПовідомлень: {msgs}\nЧатів: {chats}",
    "export_menu": "Оберіть, що експортувати",
    "export_male": "Експорт за чоловічим ID",
    "export_all": "Повний експорт",
    "enter_female_id": "Введи 10-значний жіночий ID.",
    "enter_male_id": "Введи 10-значний чоловічий ID.",
    "bad_id": "Потрібно рівно 10 цифр.",
    "rate_limited": "Занадто часто. Зачекай кілька секунд.",
    "prompt_add_user": "Надішліть @username користувача (без посилання), якого потрібно ДОДАТИ до використання бота.",
    "prompt_del_user": "Надішліть @username користувача (без посилання), якого потрібно ВИДАЛИТИ з доступу до бота.",
    "admin_manage_users": "👥 Користувачі",
    "admin_add_user": "➕ Додати користувача",
    "admin_remove_user": "➖ Удалити користувача",
    "not_authorized": "У вас немає доступу. Зверніться до адміністратора бота.",
    "only_superadmin": "Ця дія доступна лише суперадміну.",

    "add_chat_admins_only": "Додавати чати можуть лише адміни або суперадмін.",
    "auth_secret_dm": "Пароль для авторизації чату: <b>{secret}</b>\nПерейдіть у потрібну групу та надішліть: <code>/authorize {secret}</code>",
    "authorize_need_token": "Потрібно використати формат: /authorize <пароль>, отриманий у особистих повідомленнях від бота.",
    "authorize_bad_or_expired": "Пароль не підходить або застарів. Згенеруйте новий в особистих.",
    "unauthorize_ok": "Чат видалено зі списку дозволених.",
    "unauthorize_only_superadmin": "Видаляти чати може лише суперадмін."
}

def t(lang: Lang, key: str, **kwargs) -> str:
    data = RU if lang == "ru" else UK
    msg = data.get(key, key)
    if kwargs:
        try:
            return msg.format(**kwargs)
        except Exception:
            return msg
    return msg
