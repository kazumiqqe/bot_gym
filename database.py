import sqlite3


def init_db():
    conn = sqlite3.connect("gym.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            exercise TEXT,
            sets INTEGER,
            reps TEXT,
            weight TEXT,
            date TEXT
        )
    """
    )

    conn.commit()
    conn.close()


def add_workout(user_id, exercise, sets, reps, weight, date):
    conn = sqlite3.connect("gym.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO workouts (user_id, exercise, sets, reps, weight, date) VALUES (?, ?, ?, ?, ?, ?)",
        (
            user_id,
            exercise,
            sets,
            reps,
            weight,
            date,
        ),
    )
    conn.commit()
    conn.close()


def get_exercise_history(user_id, exercise):
    conn = sqlite3.connect("gym.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sets, reps, weight, date FROM workouts WHERE user_id = ? AND exercise = ? ORDER BY date DESC LIMIT 5",
        (user_id, exercise),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_user_exercises(user_id):
    conn = sqlite3.connect("gym.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT exercise FROM workouts WHERE user_id = ?", (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]
