# test_tlg/db/database.py

import sqlite3
from pathlib import Path
from datetime import datetime

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
            old_name TEXT UNIQUE,
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

def is_blacklisted(item_name: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM blacklist WHERE item = ?",
            (item_name,)
        )
        return cursor.fetchone() is not None


def add_to_blacklist(item_name: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO blacklist (item) VALUES (?)",
            (item_name,)
        )
        conn.commit()

def add_found_item(location, name, image_path):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO found_items (location, name, image_path)
        VALUES (?, ?, ?)
        """, (location, name, image_path))
        conn.commit()

def add_unique_item(location, old_name, new_name, image_path):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO items (location, time, old_name, new_name, image_path)
            VALUES (?, datetime('now'), ?, ?, ?)
            """, (location, old_name, new_name, image_path))
            conn.commit()
            return True  # успешно добавлен
        except sqlite3.IntegrityError:
            return False  # такой old_name уже есть


def add_item_change(location, old_name, new_name, image_path):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO items (location, time, old_name, new_name, image_path)
        VALUES (?, ?, ?, ?, ?)
        """, (
            location,
            datetime.now(),
            old_name,
            new_name,
            image_path
        ))
        conn.commit()

def add_upgrade(old_name, new_name, result):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO upgrades (old_name, new_name, result)
        VALUES (?, ?, ?)
        """, (old_name, new_name, result))
        conn.commit()
