from aiogram import Bot, Dispatcher, types
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

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Программы тренировок")],
        [KeyboardButton(text="Плейлисты для зала")],
        [KeyboardButton(text="О боте")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие",
)


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
    await message.answer(welcome_text, reply_markup=main_menu)


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
        await callback.message.edit_text(welcome_text)
        await callback.message.answer("Главное меню:", reply_markup=main_menu)
        await callback.answer("Подписка подтверждена!")
    else:
        await callback.answer("Ты еще не подписан на канал!", show_alert=True)


def get_programs_keyboard():
    buttons = []
    for name in programs.keys():
        buttons.append([KeyboardButton(text=name)])

    buttons.append([KeyboardButton(text="Назад в меню")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выбери программу тренировок",
    )


def get_playlists_keyboard():
    buttons = []
    for name in playlist.keys():
        buttons.append([KeyboardButton(text=name)])

    buttons.append([KeyboardButton(text="Назад в меню")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выбери плейлист",
    )


back_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_main")]
    ]
)


@dp.message(lambda message: message.text == "Программы тренировок")
async def show_programs_menu(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "Для доступа к функциям бота необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        return

    keyboard = get_programs_keyboard()
    await message.answer("Выбери программу тренировок:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "Плейлисты для зала")
async def show_playlists_menu(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "⚠️ Для доступа к функциям бота необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        return

    keyboard = get_playlists_keyboard()
    await message.answer("Выбери плейлист:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "О боте")
async def about_bot(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "⚠️ Для доступа к боту необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        return

    about_text = (
        "О боте:\n"
        "Этот бот создан для помощи в тренировках\n"
        "Здесь ты найдешь:\n\n"
        "1. Программы тренировок\n"
        "2. Плейлисты для зала\n\n"
        "Используй меню для навигации по боту\n\n"
        "Для возврата в главное меню используй команду: /start"
    )
    await message.answer(about_text)


@dp.message(lambda message: message.text in programs.keys())
async def send_program_message(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "⚠️ Для доступа к программам необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        return

    program_text = programs[message.text]
    await message.answer(program_text, reply_markup=get_programs_keyboard())


@dp.message(lambda message: message.text in playlist.keys())
async def send_playlist_message(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "⚠️ Для доступа к плейлистам необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        return

    playlist_link = playlist[message.text]
    await message.answer(playlist_link, reply_markup=get_playlists_keyboard())


@dp.message(lambda message: message.text == "Назад в меню")
async def back_to_main_menu(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "⚠️ Для доступа к боту необходимо подписаться на канал:",
            reply_markup=get_subscription_keyboard(),
        )
        return

    await message.answer("Возврат в главное меню:", reply_markup=main_menu)


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
