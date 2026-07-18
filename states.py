from aiogram.fsm.state import State, StatesGroup

class AddWorkout(StatesGroup):
    waiting_for_exercise = State()
    waiting_for_sets = State()
    waiting_for_reps = State()
    waiting_for_weight = State()

class GenerateProgram(StatesGroup):
    waiting_for_experience = State()
    waiting_for_days = State()
    waiting_for_split = State()
    waiting_for_weak_points = State()
    waiting_for_intensity = State()
    waiting_for_equipment = State()