from cryptography.hazmat.primitives import hashes
import sqlite3
import json

class EncryptionSettings:
    DEFAULT_SETTINGS = {
        'iterations': 480000,
        'key_length': 32,
        'hash_algorithm': 'SHA256',
        'salt_size': 16
    }
    
    HASH_ALGORITHMS = {
        'SHA256': hashes.SHA256,
        'SHA384': hashes.SHA384,
        'SHA512': hashes.SHA512
    }
    
    def __init__(self, db_path='passwords.db'):
        self.db_path = db_path
        self._ensure_settings_table()
        
    def _ensure_settings_table(self):
        """Создает таблицу настроек, если она не существует"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encryption_settings
            (id INTEGER PRIMARY KEY,
             settings TEXT NOT NULL)
        ''')
        
        # Проверяем, есть ли уже настройки
        cursor.execute('SELECT COUNT(*) FROM encryption_settings')
        if cursor.fetchone()[0] == 0:
            # Если нет, добавляем настройки по умолчанию
            cursor.execute('INSERT INTO encryption_settings (settings) VALUES (?)',
                         (json.dumps(self.DEFAULT_SETTINGS),))
        conn.commit()
        conn.close()
    
    def get_settings(self):
        """Получает текущие настройки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT settings FROM encryption_settings ORDER BY id DESC LIMIT 1')
        settings = json.loads(cursor.fetchone()[0])
        conn.close()
        return settings
    
    def update_settings(self, new_settings):
        """Обновляет настройки с проверкой значений"""
        current = self.get_settings()
        
        # Проверка и валидация новых настроек
        if 'iterations' in new_settings:
            if not isinstance(new_settings['iterations'], int) or new_settings['iterations'] < 100000:
                raise ValueError("Количество итераций должно быть целым числом >= 100000")
        
        if 'key_length' in new_settings:
            if not isinstance(new_settings['key_length'], int) or new_settings['key_length'] < 16:
                raise ValueError("Длина ключа должна быть целым числом >= 16")
        
        if 'hash_algorithm' in new_settings:
            if new_settings['hash_algorithm'] not in self.HASH_ALGORITHMS:
                raise ValueError(f"Поддерживаемые алгоритмы хеширования: {', '.join(self.HASH_ALGORITHMS.keys())}")
        
        if 'salt_size' in new_settings:
            if not isinstance(new_settings['salt_size'], int) or new_settings['salt_size'] < 16:
                raise ValueError("Размер соли должен быть целым числом >= 16")
        
        # Обновляем только переданные настройки
        updated_settings = {**current, **new_settings}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO encryption_settings (settings) VALUES (?)',
                      (json.dumps(updated_settings),))
        conn.commit()
        conn.close()
        
    def get_hash_algorithm(self):
        """Возвращает текущий алгоритм хеширования"""
        settings = self.get_settings()
        return self.HASH_ALGORITHMS[settings['hash_algorithm']]() 