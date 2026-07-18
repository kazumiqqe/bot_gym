from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import os

from keyboards import *
from states import *
from services import check_subscription, generate_program
from database import init_db, add_workout, get_exercise_history, get_user_exercises
from bot import bot, dp

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

@dp.message(GenerateProgram.waiting_for_equipment)
async def process_equipment(message: types.Message, state: FSMContext):
    equipment = message.text
    await state.update_data(equipment=equipment)

    data = await state.get_data()
    await state.clear()
    await message.answer("⏳ ИИ анализирует твой зал и составляет программу... Подожди пару секунд.")
    await generate_program(message, data)

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
    about_text = "ℹ️ О боте:\n\nЭтот бот создан для помощи в тренировках.\n\n💪 Мои личные программы тренировок\n🎵 Плейлисты для зала\n🤖 Генератор программ тренировок\n📊 Прогресс тренировок"
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

@dp.callback_query(F.data == "generate_program")
async def generate_program_start(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🤖 *Генератор программ тренировок*\n\n"
        "Давай подберём идеальную программу под тебя.\n\n"
        "1️⃣ Какой у тебя уровень подготовки?",
        parse_mode="Markdown",
        reply_markup=get_experience_keyboard()
    )
    await state.set_state(GenerateProgram.waiting_for_experience)
    await callback.answer()

@dp.callback_query(F.data.startswith("exp_"))
async def process_experience(callback: types.CallbackQuery, state: FSMContext):
    exp_map = {
        "exp_beginner": "Новичок (< 6 мес)",
        "exp_intermediate": "Средний (6-12 мес)",
        "exp_advanced": "Продвинутый (> 1 года)"
    }

    experience = exp_map.get(callback.data, "Неизвестно")
    await state.update_data(experience=experience)
    await callback.message.edit_text(
        f"✅ Уровень: *{experience}*\n\n"
        f"2️⃣ Сколько дней в неделю ты готов тренироваться?",
        parse_mode="Markdown",
        reply_markup=get_days_keyboard()
    )
    await callback.answer()
    await state.set_state(GenerateProgram.waiting_for_days)

@dp.callback_query(F.data.startswith("days_"))
async def time_days(callback: types.CallbackQuery, state: FSMContext):
    days_map = {
        "days_2": "2 дня",
        "days_3": "3 дня",
        "days_4": "4 дня",
        "days_5": "5 дней",
        "days_6": "6 дней"
    }
    
    days = days_map.get(callback.data, "Неизвестно")
    await state.update_data(days=days)
    await callback.message.edit_text(
        f"✅ Дней в неделю: *{days}*\n\n"
        f"3️⃣ Какой тип тренировки предпочитаешь?",
        parse_mode="Markdown",
        reply_markup=get_split_keyboard()
    )
    await callback.answer()
    await state.set_state(GenerateProgram.waiting_for_split)

@dp.callback_query(F.data.startswith("split"))
async def type_split(callback: types.CallbackQuery, state: FSMContext):
    split_map = {
        "split_fullbody": "Фуллбади",
        "split_upper_lower": "Вверх/Низ",
        "split_split": "Сплит"
    }
    
    split = split_map.get(callback.data, "Неизвестно")
    await state.update_data(split=split)
    await callback.message.edit_text(
        f"✅ Тип: *{split}*\n\n"
        f"4️⃣ Какие мышцы отстают? (напиши текстом, например: грудь, плечи)",
        parse_mode="Markdown",
        reply_markup=get_weak_points_keyboard()
    )
    await callback.answer()
    await state.set_state(GenerateProgram.waiting_for_weak_points)

@dp.callback_query(F.data.startswith("weak_"))
async def weak_muscles(callback: types.CallbackQuery, state: FSMContext):
    weak_map = {
        "weak_arms": "Руки",
        "weak_shoulders": "Плечи",
        "weak_chest": "Грудь",
        "weak_back": "Спина",
        "weak_legs": "Ноги"
    }

    weak = weak_map.get(callback.data, "Неизвестно")
    await state.update_data(weak=weak)

    await callback.message.edit_text(
        f"✅ Отстающие мышцы: *{weak}*\n\n"
        f"5️⃣ Сколько подходов ты обычно делаешь на упражнение?",
        parse_mode="Markdown",
        reply_markup=get_intensity_keyboard()
    )
    await callback.answer()
    await state.set_state(GenerateProgram.waiting_for_intensity)

@dp.callback_query(F.data.startswith("intensity_"))
async def process_intensity(callback: types.CallbackQuery, state: FSMContext):
    intensity_map = {
        "intensity_2": "2 подхода",
        "intensity_3": "3 подхода",
        "intensity_4": "4 подхода",
    }
    
    intensity = intensity_map.get(callback.data, "Неизвестно")
    await state.update_data(intensity=intensity)
    
    await callback.message.edit_text(
        f"✅ Интенсивность: *{intensity}*\n\n"
        f"6️⃣ Какие тренажеры и снаряды есть в твоем зале? (напиши просто текстом, например: штанга, гантели, турник, брусья)",
        parse_mode="Markdown"
    )
    await callback.answer()
    await state.set_state(GenerateProgram.waiting_for_equipment)

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