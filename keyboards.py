from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from data.programs import programs
from data.playlist import playlist

def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💪 Мои программы тренировок", callback_data="programs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎵 Плейлисты для зала", callback_data="playlists"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Сгенерировать программу", callback_data="generate_program"
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

def get_experience_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Новичок (< 6 мес)", callback_data="exp_beginner")],
            [InlineKeyboardButton(text="🟡 Средний (6-12 мес)", callback_data="exp_intermediate")],
            [InlineKeyboardButton(text="🔴 Продвинутый (> 1 года)", callback_data="exp_advanced")],
            [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
        ]
    )
    return keyboard

def get_days_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="2 дня", callback_data="days_2"), InlineKeyboardButton(text="3 дня", callback_data="days_3")],
            [InlineKeyboardButton(text="4 дня", callback_data="days_4"), InlineKeyboardButton(text="5 дней", callback_data="days_5")],
            [InlineKeyboardButton(text="6 дней", callback_data="days_6")],
            [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
        ]
    )
    return keyboard

def get_split_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Full Body (всё тело)", callback_data="split_fullbody")],
            [InlineKeyboardButton(text="Верх / Низ", callback_data="split_upper_lower")],
            [InlineKeyboardButton(text="Сплит (по группам мышц)", callback_data="split_split")],
            [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
        ]
    )
    return keyboard

def get_weak_points_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Руки", callback_data="weak_arms"),
             InlineKeyboardButton(text="Плечи", callback_data="weak_shoulders")],
            [InlineKeyboardButton(text="Грудь", callback_data="weak_chest"),
             InlineKeyboardButton(text="Спина", callback_data="weak_back")],
            [InlineKeyboardButton(text="Ноги", callback_data="weak_legs")],
            [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]
        ]
    )
    return keyboard

def get_intensity_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="2 подхода (лёгкая)", callback_data="intensity_2")],
            [InlineKeyboardButton(text="3 подхода (средняя)", callback_data="intensity_3")],
            [InlineKeyboardButton(text="4 подхода (тяжёлая)", callback_data="intensity_4")],
            [InlineKeyboardButton(text=" Назад в меню", callback_data="back_to_main")]
        ]
    )
    return keyboard