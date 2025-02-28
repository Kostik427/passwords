import sqlite3
from typing import List, Tuple
import os

class DatabaseManager:
    def __init__(self, db_path: str = "passwords.db"):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self) -> None:
        """Создает необходимые таблицы в базе данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица для хранения зашифрованных данных
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS encrypted_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    data BLOB NOT NULL,
                    salt BLOB NOT NULL,
                    algorithm TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица для пользовательских настроек
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            conn.commit()

    def save_encrypted_data(self, name: str, encrypted_data: bytes, salt: bytes, algorithm: str) -> None:
        """Сохраняет зашифрованные данные в базу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO encrypted_data (name, data, salt, algorithm) VALUES (?, ?, ?, ?)',
                (name, encrypted_data, salt, algorithm)
            )
            conn.commit()

    def get_all_encrypted_data(self) -> List[Tuple[int, str, str]]:
        """Возвращает список всех зашифрованных данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, algorithm FROM encrypted_data ORDER BY created_at DESC')
            return cursor.fetchall()

    def get_encrypted_data_by_id(self, data_id: int) -> Tuple[bytes, bytes, str]:
        """Возвращает зашифрованные данные по ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT data, salt, algorithm FROM encrypted_data WHERE id = ?', (data_id,))
            result = cursor.fetchone()
            if result:
                return result
            raise ValueError(f"Данные с ID {data_id} не найдены")

    def delete_encrypted_data(self, data_id: int) -> None:
        """Удаляет зашифрованные данные по ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM encrypted_data WHERE id = ?', (data_id,))
            conn.commit()

    def save_setting(self, key: str, value: str) -> None:
        """Сохраняет настройку"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                (key, value)
            )
            conn.commit()

    def get_setting(self, key: str, default: str = None) -> str:
        """Получает значение настройки"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else default 