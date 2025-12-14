"""SQLite data layer for the Diabetes Lifestyle Tracker.

This module centralizes all database access to keep the Streamlit
application focused on presentation logic.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "tracker.db"


def _ensure_db_path() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Return a connection with Row factory enabled for dict-like access."""
    _ensure_db_path()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not already exist."""
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sleep_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date TEXT NOT NULL UNIQUE,
                wake_time TEXT,
                sleep_time TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS meal_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date TEXT NOT NULL,
                meal_name TEXT NOT NULL,
                meal_time TEXT NOT NULL,
                carbs_grams INTEGER
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workout_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date TEXT NOT NULL,
                workout_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS comment_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date TEXT NOT NULL,
                comment_text TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT
            )
            """
        )
        conn.commit()
        _ensure_meal_carbs_column(conn)


def _ensure_meal_carbs_column(conn: sqlite3.Connection) -> None:
    """Add carbs_grams column to meal_logs if the DB was created pre-update."""
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(meal_logs)").fetchall()
    }
    if "carbs_grams" not in columns:
        conn.execute("ALTER TABLE meal_logs ADD COLUMN carbs_grams INTEGER")
        conn.commit()


def _rows_to_dicts(rows: Iterable[sqlite3.Row]) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows]


# Sleep operations ---------------------------------------------------------

def get_sleep_log(log_date: str) -> Optional[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT * FROM sleep_logs WHERE log_date = ?",
            (log_date,),
        ).fetchone()
    return dict(row) if row else None


def upsert_sleep_log(log_date: str, wake_time: str, sleep_time: str) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            INSERT INTO sleep_logs (log_date, wake_time, sleep_time)
            VALUES (?, ?, ?)
            ON CONFLICT(log_date)
            DO UPDATE SET wake_time = excluded.wake_time,
                          sleep_time = excluded.sleep_time
            """,
            (log_date, wake_time, sleep_time),
        )
        conn.commit()


def delete_sleep_log(log_date: str) -> None:
    with closing(get_connection()) as conn:
        conn.execute("DELETE FROM sleep_logs WHERE log_date = ?", (log_date,))
        conn.commit()


# Meal operations ----------------------------------------------------------

def add_meal(log_date: str, meal_name: str, meal_time: str, carbs_grams: Optional[int]) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            "INSERT INTO meal_logs (log_date, meal_name, meal_time, carbs_grams) VALUES (?, ?, ?, ?)",
            (log_date, meal_name, meal_time, carbs_grams),
        )
        conn.commit()


def update_meal(meal_id: int, meal_name: str, meal_time: str, carbs_grams: Optional[int]) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            "UPDATE meal_logs SET meal_name = ?, meal_time = ?, carbs_grams = ? WHERE id = ?",
            (meal_name, meal_time, carbs_grams, meal_id),
        )
        conn.commit()


def delete_meal(meal_id: int) -> None:
    with closing(get_connection()) as conn:
        conn.execute("DELETE FROM meal_logs WHERE id = ?", (meal_id,))
        conn.commit()


def get_meals_for_date(log_date: str) -> List[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM meal_logs WHERE log_date = ? ORDER BY meal_time",
            (log_date,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_meals_between(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT * FROM meal_logs
            WHERE log_date BETWEEN ? AND ?
            ORDER BY log_date DESC, meal_time DESC
            """,
            (start_date, end_date),
        ).fetchall()
    return _rows_to_dicts(rows)


# Workout operations -------------------------------------------------------

def add_workout(log_date: str, workout_name: str, start_time: str, duration_minutes: int) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            INSERT INTO workout_logs (log_date, workout_name, start_time, duration_minutes)
            VALUES (?, ?, ?, ?)
            """,
            (log_date, workout_name, start_time, duration_minutes),
        )
        conn.commit()


def update_workout(workout_id: int, workout_name: str, start_time: str, duration_minutes: int) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            UPDATE workout_logs
            SET workout_name = ?, start_time = ?, duration_minutes = ?
            WHERE id = ?
            """,
            (workout_name, start_time, duration_minutes, workout_id),
        )
        conn.commit()


def delete_workout(workout_id: int) -> None:
    with closing(get_connection()) as conn:
        conn.execute("DELETE FROM workout_logs WHERE id = ?", (workout_id,))
        conn.commit()


def get_workouts_for_date(log_date: str) -> List[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM workout_logs WHERE log_date = ? ORDER BY start_time",
            (log_date,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_workouts_between(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT * FROM workout_logs
            WHERE log_date BETWEEN ? AND ?
            ORDER BY log_date DESC, start_time DESC
            """,
            (start_date, end_date),
        ).fetchall()
    return _rows_to_dicts(rows)


# Comment operations -------------------------------------------------------

def add_comment(log_date: str, comment_text: str, start_time: Optional[str], end_time: Optional[str]) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            INSERT INTO comment_logs (log_date, comment_text, start_time, end_time)
            VALUES (?, ?, ?, ?)
            """,
            (log_date, comment_text, start_time, end_time),
        )
        conn.commit()


def update_comment(comment_id: int, comment_text: str, start_time: Optional[str], end_time: Optional[str]) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            UPDATE comment_logs
            SET comment_text = ?, start_time = ?, end_time = ?
            WHERE id = ?
            """,
            (comment_text, start_time, end_time, comment_id),
        )
        conn.commit()


def delete_comment(comment_id: int) -> None:
    with closing(get_connection()) as conn:
        conn.execute("DELETE FROM comment_logs WHERE id = ?", (comment_id,))
        conn.commit()


def get_comments_for_date(log_date: str) -> List[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM comment_logs WHERE log_date = ? ORDER BY start_time",
            (log_date,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_comments_between(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT * FROM comment_logs
            WHERE log_date BETWEEN ? AND ?
            ORDER BY log_date DESC, start_time DESC
            """,
            (start_date, end_date),
        ).fetchall()
    return _rows_to_dicts(rows)


# Historical queries -------------------------------------------------------

def get_days_with_data(start_date: str, end_date: str) -> List[str]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT log_date FROM (
                SELECT log_date FROM sleep_logs
                UNION ALL
                SELECT log_date FROM meal_logs
                UNION ALL
                SELECT log_date FROM workout_logs
            )
            WHERE log_date BETWEEN ? AND ?
            ORDER BY log_date DESC
            """,
            (start_date, end_date),
        ).fetchall()
    return [row[0] for row in rows]


def get_daily_snapshot(log_date: str) -> Dict[str, Any]:
    return {
        "sleep": get_sleep_log(log_date),
        "meals": get_meals_for_date(log_date),
        "workouts": get_workouts_for_date(log_date),
    }


def get_history(category: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Return records filtered by category name and date range."""
    normalized = (category or "all").lower()
    with closing(get_connection()) as conn:
        if normalized == "sleep":
            rows = conn.execute(
                """
                SELECT * FROM sleep_logs
                WHERE log_date BETWEEN ? AND ?
                ORDER BY log_date DESC
                """,
                (start_date, end_date),
            ).fetchall()
        elif normalized == "meals":
            rows = conn.execute(
                """
                SELECT * FROM meal_logs
                WHERE log_date BETWEEN ? AND ?
                ORDER BY log_date DESC, meal_time DESC
                """,
                (start_date, end_date),
            ).fetchall()
        elif normalized == "workouts":
            rows = conn.execute(
                """
                SELECT * FROM workout_logs
                WHERE log_date BETWEEN ? AND ?
                ORDER BY log_date DESC, start_time DESC
                """,
                (start_date, end_date),
            ).fetchall()
        elif normalized == "comments":
            rows = conn.execute(
                """
                SELECT * FROM comment_logs
                WHERE log_date BETWEEN ? AND ?
                ORDER BY log_date DESC, start_time DESC
                """,
                (start_date, end_date),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT 'sleep' AS category, id, log_date, wake_time, sleep_time, NULL AS meal_name,
                       NULL AS meal_time, NULL AS carbs_grams, NULL AS workout_name, NULL AS start_time, NULL AS duration_minutes,
                       NULL AS comment_text, NULL AS end_time
                FROM sleep_logs
                WHERE log_date BETWEEN ? AND ?
                UNION ALL
                SELECT 'meals' AS category, id, log_date, NULL, NULL, meal_name, meal_time, carbs_grams, NULL, NULL, NULL,
                       NULL, NULL
                FROM meal_logs
                WHERE log_date BETWEEN ? AND ?
                UNION ALL
                SELECT 'workouts' AS category, id, log_date, NULL, NULL, NULL, NULL, NULL, workout_name, start_time, duration_minutes,
                       NULL, NULL
                FROM workout_logs
                WHERE log_date BETWEEN ? AND ?
                UNION ALL
                SELECT 'comments' AS category, id, log_date, NULL, NULL, NULL, NULL, NULL, NULL, start_time, NULL,
                       comment_text, end_time
                FROM comment_logs
                WHERE log_date BETWEEN ? AND ?
                ORDER BY log_date DESC
                """,
                (start_date, end_date, start_date, end_date, start_date, end_date, start_date, end_date),
            ).fetchall()
    return _rows_to_dicts(rows)
