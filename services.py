import os    
from data.programs import programs
from groq import Groq
from aiogram import types
from bot import CHANNEL_ID, bot

async def check_subscription(user_id: int) -> bool:
    if not CHANNEL_ID:
        return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return True

async def generate_program(message: types.Message, data: dict):
    experience = data.get('experience')
    days = data.get('days')
    split = data.get('split')
    weak = data.get('weak')
    intensity = data.get('intensity')
    equipment = data.get('equipment')

    prompt = f"""
    Ты профессиональный фитнес-тренер. Вот примеры моих авторских программ тренировок:

    === ПРИМЕР 1 ===
    {programs['программа тренировок вверх низ (сокращенные подходы)']}

    Изучи программу. Обрати внимание на:
    - Подбор упражнений
    - Количество подходов и повторений
    - Распределение нагрузки по мышцам

    Теперь составь НОВУЮ программу для пользователя с учётом его параметров:

    ПАРАМЕТРЫ:
    - Уровень подготовки: {experience}
    - Дней в неделю: {days}
    - Тип сплита: {split}
    - Отстающие мышцы: {weak}
    - Интенсивность (количество подходов): {intensity}
    - Доступное оборудование: {equipment}

    ТРЕБОВАНИЯ:
    1. Отстающие мышцы ставь в начало тренировки
    2. Учитывай только доступное оборудование
    3. Используй {intensity} на каждое упражнение (как указано в параметрах).
    4. Форматируй ответ СТРОГО по шаблону ниже:

    ШАБЛОН ОФОРМЛЕНИЯ:
    💪 Программа тренировок: {split}

    [День 1: Название группы мышц]
    1. [Упражнение] - {intensity} x [повторения]
    2. [Упражнение] - {intensity} x [повторения]

    [День 2: Название группы мышц]
    ...
    
    Отвечай ТОЛЬКО программой, без лишних вступлений и объяснений.
    """
    
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )
    
    program_text = response.choices[0].message.content
    
    await message.answer(program_text, parse_mode="Markdown")