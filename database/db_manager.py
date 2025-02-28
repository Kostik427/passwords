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
            
            # Таблица для хранения зашифрованных текстовых данных
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS encrypted_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    data BLOB NOT NULL,
                    salt BLOB NOT NULL,
                    algorithm TEXT NOT NULL,
                    type TEXT DEFAULT 'text',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица для хранения информации о зашифрованных файлах
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS encrypted_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_path TEXT NOT NULL,
                    encrypted_path TEXT NOT NULL,
                    salt BLOB NOT NULL,
                    algorithm TEXT NOT NULL,
                    is_folder BOOLEAN NOT NULL,
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
        """Сохраняет зашифрованные текстовые данные в базу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO encrypted_data (name, data, salt, algorithm, type) VALUES (?, ?, ?, ?, ?)',
                (name, encrypted_data, salt, algorithm, 'text')
            )
            conn.commit()

    def save_encrypted_file(self, original_path: str, encrypted_path: str, salt: bytes, algorithm: str, is_folder: bool) -> None:
        """Сохраняет информацию о зашифрованном файле в базу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO encrypted_files (original_path, encrypted_path, salt, algorithm, is_folder) VALUES (?, ?, ?, ?, ?)',
                (original_path, encrypted_path, salt, algorithm, is_folder)
            )
            conn.commit()

    def get_all_encrypted_data(self) -> List[Tuple[int, str, str, str]]:
        """Возвращает список всех зашифрованных данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Получаем текстовые данные
            cursor.execute('SELECT id, name, algorithm, type FROM encrypted_data ORDER BY created_at DESC')
            text_data = cursor.fetchall()
            
            # Получаем файлы
            cursor.execute('SELECT id, original_path, algorithm, "file" as type FROM encrypted_files ORDER BY created_at DESC')
            file_data = cursor.fetchall()
            
            # Объединяем результаты
            return text_data + file_data

    def get_encrypted_data_by_id(self, data_id: int, data_type: str = 'text') -> Tuple[bytes, bytes, str]:
        """Возвращает зашифрованные данные по ID и типу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if data_type == 'text':
                cursor.execute('SELECT data, salt, algorithm FROM encrypted_data WHERE id = ?', (data_id,))
            else:
                cursor.execute('SELECT encrypted_path, salt, algorithm FROM encrypted_files WHERE id = ?', (data_id,))
            result = cursor.fetchone()
            if result:
                return result
            raise ValueError(f"Данные с ID {data_id} не найдены")

    def get_file_info(self, file_id: int) -> Tuple[str, str, bytes, str, bool]:
        """Возвращает информацию о зашифрованном файле"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT original_path, encrypted_path, salt, algorithm, is_folder FROM encrypted_files WHERE id = ?',
                (file_id,)
            )
            result = cursor.fetchone()
            if result:
                return result
            raise ValueError(f"Файл с ID {file_id} не найден")

    def delete_encrypted_data(self, data_id: int, data_type: str = 'text') -> None:
        """Удаляет зашифрованные данные по ID и типу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if data_type == 'text':
                cursor.execute('DELETE FROM encrypted_data WHERE id = ?', (data_id,))
            else:
                # Получаем путь к зашифрованному файлу перед удалением
                cursor.execute('SELECT encrypted_path FROM encrypted_files WHERE id = ?', (data_id,))
                result = cursor.fetchone()
                if result and os.path.exists(result[0]):
                    os.remove(result[0])
                cursor.execute('DELETE FROM encrypted_files WHERE id = ?', (data_id,))
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