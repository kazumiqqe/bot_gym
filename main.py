from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import os
from dotenv import load_dotenv

from data.programs import programs
from data.playlist import playlist

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not API_TOKEN:
    print("ОШИБКА: Не найден BOT_TOKEN в .env файле!")
    print("Создай файл .env в той же папке и добавь туда: BOT_TOKEN=твой_токен")
    exit(1)

if not CHANNEL_ID:
    print("ВНИМАНИЕ: Не найден CHANNEL_ID в .env файле!")
    print("Добавь в .env: CHANNEL_ID=@username_канала или CHANNEL_ID=-100123456789")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def get_main_menu_keyboard():
    """Главное меню"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💪 Программы тренировок", callback_data="programs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎵 Плейлисты для зала", callback_data="playlists"
                )
            ],
            [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")],
        ]
    )
    return keyboard


async def check_subscription(user_id: int) -> bool:
    """Проверяет подписку пользователя на канал"""
    if not CHANNEL_ID:
        return True

    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return True


def get_subscription_keyboard():
    """Клавиатура с кнопкой подписки"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подписаться на канал",
                    url=f"https://t.me/{CHANNEL_ID.replace('@', '')}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Проверить подписку", callback_data="check_sub"
                )
            ],
        ]
    )
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)

    if not is_subscribed:
        await message.answer(
            "Привет! Чтобы пользоваться ботом, подпишись на наш канал:",
            reply_markup=get_subscription_keyboard(),
        )
        return

    welcome_text = (
        "Добро пожаловать в бота для тренировок!\n" "Выбери нужный раздел в меню ниже:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@dp.callback_query(lambda c: c.data == "check_sub")
async def check_subscription_callback(callback: types.CallbackQuery):
    """Обработка проверки подписки через кнопку"""
    is_subscribed = await check_subscription(callback.from_user.id)

    if is_subscribed:
        welcome_text = (
            "Отлично! Ты подписан на канал.\n\n"
            "Добро пожаловать в бота для тренировок!\n"
            "Выбери нужный раздел в меню ниже:"
        )
        await callback.message.edit_text(
            welcome_text, reply_markup=get_main_menu_keyboard()
        )
        await callback.answer("Подписка подтверждена!")
    else:
        await callback.answer("Ты еще не подписан на канал!", show_alert=True)


def get_programs_keyboard():
    """Клавиатура с программами тренировок"""
    buttons = []
    program_list = list(programs.keys())
    for index, name in enumerate(program_list):
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"prog_{index}")])

    buttons.append(
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_playlist_keyboard():
    """Клавиатура с плейлистами"""
    buttons = []
    playlist_list = list(playlist.keys())

    for index, name in enumerate(playlist_list):
        buttons.append(
            [InlineKeyboardButton(text=name, callback_data=f"playlist_{index}")]
        )

    buttons.append(
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    is_subscribed = await check_subscription(callback.from_user.id)

    if not is_subscribed:
        await callback.message.edit_text(
            "⚠️ Для доступа к боту необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "📋 Главное меню:", reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "programs")
async def show_programs_menu(callback: types.CallbackQuery):
    """Показать меню программ"""
    is_subscribed = await check_subscription(callback.from_user.id)

    if not is_subscribed:
        await callback.message.edit_text(
            "⚠️ Для доступа к функциям бота необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "💪 Выбери программу тренировок:", reply_markup=get_programs_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "playlists")
async def show_playlist_menu(callback: types.CallbackQuery):
    """Показать меню плейлистов"""
    is_subscribed = await check_subscription(callback.from_user.id)

    if not is_subscribed:
        await callback.message.edit_text(
            "⚠️ Для доступа к функциям бота необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "🎵 Выбери плейлист:", reply_markup=get_playlist_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "about")
async def about_bot(callback: types.CallbackQuery):
    """Информация о боте"""
    is_subscribed = await check_subscription(callback.from_user.id)

    if not is_subscribed:
        await callback.message.edit_text(
            "⚠️ Для доступа к функциям бота необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        await callback.answer()
        return

    about_text = (
        "ℹ️ О боте:\n\n"
        "Этот бот создан для помощи в тренировках.\n"
        "Здесь ты найдешь:\n\n"
        "💪 Программы тренировок\n"
        "🎵 Плейлисты для зала\n\n"
        "Используй кнопки для навигации по боту."
    )

    back_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
        ]
    )

    await callback.message.edit_text(about_text, reply_markup=back_button)
    await callback.answer()


@dp.callback_query(F.data.startswith("prog_"))
async def send_program(callback: types.CallbackQuery):
    """Отправка программы тренировок"""
    is_subscribed = await check_subscription(callback.from_user.id)

    if not is_subscribed:
        await callback.message.edit_text(
            "⚠️ Для доступа к программам необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        await callback.answer()
        return

    index = int(callback.data.split("_")[1])
    program_list = list(programs.keys())

    if index < len(program_list):
        program_name = program_list[index]
        program_text = programs[program_name]
        await callback.message.edit_text(
            f"💪 {program_name}\n\n{program_text}", reply_markup=get_programs_keyboard()
        )
    else:
        await callback.answer("❌ Программа не найдена!", show_alert=True)
        return

    await callback.answer()


@dp.callback_query(F.data.startswith("playlist_"))
async def send_playlist(callback: types.CallbackQuery):
    is_subscribed = await check_subscription(callback.from_user.id)

    if not is_subscribed:
        await callback.message.edit_text(
            "⚠️ Для доступа к плейлистам необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        await callback.answer()
        return

    index = int(callback.data.split("_")[1])
    playlist_list = list(playlist.keys())

    if index < len(playlist_list):
        playlist_name = playlist_list[index]
        playlist_link = playlist[playlist_name]

        link_button = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎵 Открыть плейлист", url=playlist_link)],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="playlists")],
            ]
        )

        await callback.message.edit_text(
            f"🎵 {playlist_name}", reply_markup=link_button
        )
    else:
        await callback.answer("❌ Плейлист не найден!", show_alert=True)
        return

    await callback.answer()


async def keep_alive():
    """Предотвращает засыпание бота на хостинге"""
    while True:
        await asyncio.sleep(600)
        print("Keep-alive: бот активен")


async def main():
    asyncio.create_task(keep_alive())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
