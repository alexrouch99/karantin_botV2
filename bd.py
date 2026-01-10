# test_tlg/db/database.py

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "quarantine.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """
    Инициализация БД:
    - если файла нет → создаётся новая БД
    - если файл есть → используется существующая
    """
    is_new_db = not DB_PATH.exists()

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS found_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            name TEXT,
            image_path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            time DATETIME,
            old_name TEXT,
            new_name TEXT,
            image_path TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT UNIQUE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS upgrades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            old_name TEXT,
            new_name TEXT,
            result TEXT
        )
        """)

        conn.commit()

    if is_new_db:
        print("🆕 Создана новая база данных:", DB_PATH)
    else:
        print("📂 Используется существующая база данных:", DB_PATH)
