from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu(owner=False):
    buttons = [
        [
            InlineKeyboardButton(
                text="🔍 Поиск",
                callback_data="search"
            ),
            InlineKeyboardButton(
                text="🧠 Глубокий поиск",
                callback_data="deep_search"
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 Профиль",
                callback_data="profile"
            ),
            InlineKeyboardButton(
                text="🎁 Бонус",
                callback_data="bonus"
            )
        ],
        [
            InlineKeyboardButton(
                text="💎 Купить запросы",
                callback_data="buy"
            ),
            InlineKeyboardButton(
                text="🤝 Партнёрка",
                callback_data="ref"
            )
        ]
    ]

    if owner:
        buttons.append([
            InlineKeyboardButton(
                text="👑 Админ-панель",
                callback_data="admin"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def search_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👤 ФИО",
                callback_data="type_name"
            ),
            InlineKeyboardButton(
                text="📱 Телефон",
                callback_data="type_phone"
            )
        ],
        [
            InlineKeyboardButton(
                text="📧 Email",
                callback_data="type_email"
            ),
            InlineKeyboardButton(
                text="💬 Telegram",
                callback_data="type_telegram"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏢 Компания",
                callback_data="type_company"
            ),
            InlineKeyboardButton(
                text="🚗 Автомобиль",
                callback_data="type_auto"
            )
        ],
        [
            InlineKeyboardButton(
                text="📍 Адрес",
                callback_data="type_address"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="back"
            )
        ]
    ])
