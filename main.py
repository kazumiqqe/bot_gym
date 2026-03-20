from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
import asyncio
import os
from database import init_db, add_workout, get_exercise_history, get_user_exercises
from dotenv import load_dotenv

from data.programs import programs
from data.playlist import playlist

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not API_TOKEN:
    print("ОШИБКА: Не найден BOT_TOKEN в .env файле!")
    exit(1)

if not CHANNEL_ID:
    print("ВНИМАНИЕ: Не найден CHANNEL_ID в .env файле!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class AddWorkout(StatesGroup):
    waiting_for_exercise = State()
    waiting_for_sets = State()
    waiting_for_reps = State()
    waiting_for_weight = State()


def get_main_menu_keyboard():
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
            [
                InlineKeyboardButton(
                    text="📊 Прогресс тренировок", callback_data="progress"
                )
            ],
            [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")],
        ]
    )
    return keyboard


async def check_subscription(user_id: int) -> bool:
    if not CHANNEL_ID:
        return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return True


def get_subscription_keyboard():
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
    await message.answer(
        "Добро пожаловать в бота для тренировок!\nВыбери нужный раздел в меню ниже:",
        reply_markup=get_main_menu_keyboard(),
    )


@dp.callback_query(lambda c: c.data == "check_sub")
async def check_subscription_callback(callback: types.CallbackQuery):
    is_subscribed = await check_subscription(callback.from_user.id)
    if is_subscribed:
        await callback.message.edit_text(
            "Отлично! Ты подписан.\n\nДобро пожаловать!",
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer("Подписка подтверждена!")
    else:
        await callback.answer("Ты еще не подписан на канал!", show_alert=True)


def get_programs_keyboard():
    buttons = []
    for index, name in enumerate(programs.keys()):
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"prog_{index}")])
    buttons.append(
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_playlist_keyboard():
    buttons = []
    for index, name in enumerate(playlist.keys()):
        buttons.append(
            [InlineKeyboardButton(text=name, callback_data=f"playlist_{index}")]
        )
    buttons.append(
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📋 Главное меню:", reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "programs")
async def show_programs_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "💪 Выбери программу тренировок:", reply_markup=get_programs_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "playlists")
async def show_playlist_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎵 Выбери плейлист:", reply_markup=get_playlist_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "about")
async def about_bot(callback: types.CallbackQuery):
    about_text = "ℹ️ О боте:\n\nЭтот бот создан для помощи в тренировках.\n\n💪 Программы тренировок\n🎵 Плейлисты для зала\n📊 Прогресс тренировок"
    await callback.message.edit_text(
        about_text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Назад в меню", callback_data="back_to_main"
                    )
                ]
            ]
        ),
    )
    await callback.answer()


@dp.callback_query(F.data == "progress")
async def show_progress_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Записать тренировку", callback_data="add_workout"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📈 История упражнений", callback_data="show_history"
                )
            ],
            [InlineKeyboardButton(text="🤖 Совет ИИ", callback_data="ai_advice")],
            [
                InlineKeyboardButton(
                    text="🔙 Назад в меню", callback_data="back_to_main"
                )
            ],
        ]
    )
    await callback.message.edit_text(
        "📊 *Прогресс тренировок*\n\nВыбери действие 👇",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    await callback.answer()


@dp.callback_query(F.data == "add_workout")
async def add_workout_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💪 *Запись тренировки*\n\nНапиши название упражнения:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="progress")]
            ]
        ),
    )
    await state.set_state(AddWorkout.waiting_for_exercise)
    await callback.answer()


@dp.message(AddWorkout.waiting_for_exercise)
async def get_exercise(message: types.Message, state: FSMContext):
    await state.update_data(exercise=message.text)
    await message.delete()
    await message.answer(
        f"✅ Упражнение: *{message.text}*\n\nСколько подходов сделал?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="progress")]
            ]
        ),
    )
    await state.set_state(AddWorkout.waiting_for_sets)


@dp.message(AddWorkout.waiting_for_sets)
async def get_sets(message: types.Message, state: FSMContext):
    await state.update_data(sets=message.text)
    await message.delete()
    await message.answer(
        "Сколько повторений? (например: 8 или 6-8)",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="progress")]
            ]
        ),
    )
    await state.set_state(AddWorkout.waiting_for_reps)


@dp.message(AddWorkout.waiting_for_reps)
async def get_reps(message: types.Message, state: FSMContext):
    await state.update_data(reps=message.text)
    await message.delete()
    await message.answer(
        "Какой вес? (например: 70 или 70/60 если менялся)",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="progress")]
            ]
        ),
    )
    await state.set_state(AddWorkout.waiting_for_weight)


@dp.message(AddWorkout.waiting_for_weight)
async def get_weight(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await message.delete()

    add_workout(
        user_id=message.from_user.id,
        exercise=data["exercise"],
        sets=data["sets"],
        reps=data["reps"],
        weight=message.text,
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Ещё упражнение", callback_data="add_workout"
                )
            ],
            [InlineKeyboardButton(text="📊 Прогресс", callback_data="progress")],
        ]
    )

    await message.answer(
        f"✅ *Записано!*\n\n"
        f"💪 {data['exercise']}\n"
        f"📊 {data['sets']} подхода × {data['reps']} повт.\n"
        f"⚖️ {message.text} кг",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


@dp.callback_query(F.data == "show_history")
async def show_history(callback: types.CallbackQuery):
    exercises = get_user_exercises(callback.from_user.id)
    if not exercises:
        await callback.message.edit_text(
            "📭 У тебя пока нет записей тренировок.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="progress")]
                ]
            ),
        )
        await callback.answer()
        return

    buttons = []
    for exercise in exercises:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"💪 {exercise}", callback_data=f"hist_{exercise[:30]}"
                )
            ]
        )
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="progress")])

    await callback.message.edit_text(
        "📈 *История упражнений*\n\nВыбери упражнение:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("hist_"))
async def show_exercise_history(callback: types.CallbackQuery):
    exercise = callback.data[5:]
    history = get_exercise_history(callback.from_user.id, exercise)

    if not history:
        await callback.answer("Нет данных", show_alert=True)
        return

    text = f"📊 *{exercise}*\n\nПоследние записи:\n\n"
    for i, (sets, reps, weight, date) in enumerate(history, 1):
        text += f"{i}. {date}\n {sets} подх × {reps} повт - {weight} кг\n\n"

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="show_history")]
            ]
        ),
    )
    await callback.answer()


@dp.callback_query(F.data == "ai_advice")
async def ai_advice(callback: CallbackQuery):
    exercises = get_user_exercises(callback.from_user.id)
    if not exercises:
        await callback.message.edit_text(
            "📭 Нет данных для анализа. Сначала запиши несколько тренировок.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="progress")]
                ]
            ),
        )
        await callback.answer()
        return

    buttons = []
    for exercise in exercises:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"🤖 {exercise}", callback_data=f"advice_{exercise[:25]}"
                )
            ]
        )
        buttons.append(
            [InlineKeyboardButton(text="🔙 Назад", callback_data="progress")]
        )

        await callback.message.edit_text(
            "🤖 *Совет ИИ*\n\nПо какому упражнению получить совет?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        await callback.answer()


@dp.callback_query(F.data.startswith("advice_"))
async def get_ai_advice(callback: types.CallbackQuery):
    exercise = callback.data[7:]
    history = get_exercise_history(callback.from_user.id, exercise)

    if not history:
        await callback.answer("Нет данных", show_alert=True)
        return

    await callback.message.edit_text("⏳ Анализирую твой прогресс...")

    history_text = ""
    for i, (sets, reps, weight, date) in enumerate(history, 1):
        history_text += f"{date}: {sets} подх × {reps} повт, {weight} кг\n"

    prompt = (
        f"Ты фитнес тренер. Проанализируй прогресс в упражнении '{exercise}':\n\n"
        f"{history_text}\n"
        f"Дай конкретный совет — повысить вес или повторения на следующей тренировке и почему. "
        f"Ответь коротко, 3-4 предложения, на русском языке."
    )

    from groq import Groq

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    advice = response.choices[0].message.content

    await callback.message.edit_text(
        f"🤖 *Совет по {exercise}:*\n\n{advice}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="ai_advice")]
            ]
        ),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("prog_"))
async def send_program(callback: types.CallbackQuery):
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
    while True:
        await asyncio.sleep(600)
        print("Keep-alive: бот активен")


async def main():
    init_db()
    asyncio.create_task(keep_alive())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
