import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from database import (
    init_db,
    create_user,
    get_user,
    add_queries,
    use_query,
    daily_bonus,
    save_search
)

from keyboards import main_menu, search_menu
from search import search_all


BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "5295393159"))

dp = Dispatcher()

waiting_search = set()


@dp.message(CommandStart())
async def start(message: Message):

    await create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        OWNER_ID
    )

    user = await get_user(message.from_user.id)

    owner = user["role"] == "owner"

    text = (
        "🚀 <b>AHISKA SEARCH</b>\n\n"
        "Приветствую тебя на одном из самых лучших "
        "ботов в Telegram.\n\n"
        "Выбери необходимое действие:"
    )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=main_menu(owner)
    )


@dp.callback_query(F.data == "search")
async def search_button(callback: CallbackQuery):

    await callback.message.edit_text(
        "🔍 <b>ПОИСК</b>\n\n"
        "Выберите тип поиска:",
        parse_mode="HTML",
        reply_markup=search_menu()
    )

    await callback.answer()


@dp.callback_query(F.data == "deep_search")
async def deep_search(callback: CallbackQuery):

    waiting_search.add(callback.from_user.id)

    await callback.message.answer(
        "🧠 <b>ГЛУБОКИЙ ПОИСК</b>\n\n"
        "Отправьте известные данные.\n\n"
        "Например:\n"
        "• имя и фамилия\n"
        "• номер телефона\n"
        "• email\n"
        "• username\n"
        "• компания\n"
        "• автомобиль\n"
        "• адрес",
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("type_"))
async def select_type(callback: CallbackQuery):

    waiting_search.add(callback.from_user.id)

    await callback.message.answer(
        "⌨️ Отправьте данные для поиска."
    )

    await callback.answer()


@dp.message()
async def handle_search(message: Message):

    user_id = message.from_user.id

    if user_id not in waiting_search:
        return

    waiting_search.discard(user_id)

    query = message.text

    if not query:
        await message.answer(
            "❌ Отправьте текстовые данные для поиска."
        )
        return

    user = await get_user(user_id)

    if user["role"] != "owner" and not user["vip"]:

        if user["queries"] <= 0:
            await message.answer(
                "❌ У вас закончились запросы.\n\n"
                "Используйте раздел 💎 Купить запросы."
            )
            return

    if not await use_query(user_id):
        await message.answer(
            "❌ Недостаточно запросов."
        )
        return

    await save_search(user_id, query)

    await message.answer(
        "🔎 Выполняю поиск..."
    )

    results = search_all(query)

    if not results:
        await message.answer(
            "❌ <b>Ничего не найдено.</b>\n\n"
            f"Запрос: <code>{query}</code>",
            parse_mode="HTML"
        )
        return

    text = (
        "✅ <b>РЕЗУЛЬТАТ ПОИСКА</b>\n\n"
        f"🔎 Запрос: <code>{query}</code>\n"
        f"📊 Найдено совпадений: {len(results)}\n\n"
    )

    for index, result in enumerate(results[:20], 1):

        if isinstance(result, dict):
            block = "\n".join(
                f"<b>{k}:</b> {v}"
                for k, v in result.items()
            )
        else:
            block = str(result)

        text += (
            f"━━━━━━━━━━━━━━\n"
            f"#{index}\n"
            f"{block}\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):

    user = await get_user(callback.from_user.id)

    role = {
        "owner": "👑 Владелец",
        "admin": "🛡 Администратор",
        "user": "👤 Пользователь"
    }.get(user["role"], "👤 Пользователь")

    queries = (
        "♾ Безлимит"
        if user["role"] == "owner" or user["vip"]
        else str(user["queries"])
    )

    text = (
        "👤 <b>МОЙ ПРОФИЛЬ</b>\n\n"
        f"🆔 ID: <code>{user['id']}</code>\n"
        f"👑 Статус: {role}\n"
        f"💰 Кошелёк: {user['balance']} ₽\n"
        f"💎 Доступно запросов: {queries}\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📊 Статистика поиска доступна "
        "в истории."
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=main_menu(user["role"] == "owner")
    )

    await callback.answer()


@dp.callback_query(F.data == "bonus")
async def bonus(callback: CallbackQuery):

    success = await daily_bonus(
        callback.from_user.id
    )

    if success:
        text = (
            "🎁 <b>БОНУС ПОЛУЧЕН</b>\n\n"
            "Вам начислен 1 бесплатный запрос.\n\n"
            "Следующий бонус будет доступен через 24 часа."
        )
    else:
        text = (
            "⏳ <b>БОНУС УЖЕ ПОЛУЧЕН</b>\n\n"
            "Следующий бонус будет доступен через 24 часа."
        )

    await callback.message.answer(
        text,
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):

    user = await get_user(callback.from_user.id)

    await callback.message.edit_text(
        "🚀 <b>AHISKA SEARCH</b>\n\n"
        "Главное меню.",
        parse_mode="HTML",
        reply_markup=main_menu(
            user["role"] == "owner"
        )
    )

    await callback.answer()


async def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "Переменная BOT_TOKEN не задана"
        )

    await init_db()

    bot = Bot(BOT_TOKEN)

    print("Ahiska Search запущен.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
