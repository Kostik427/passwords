from abc import ABC, abstractmethod
from database.db_manager import DatabaseManager

class BaseEncryptor(ABC):
    def __init__(self):
        self.db_manager = DatabaseManager()

    @abstractmethod
    def generate_key(self, password: str) -> None:
        """Генерирует ключ на основе пароля"""
        pass

    @abstractmethod
    def load_key(self, password: str, salt: bytes) -> None:
        """Загружает существующий ключ"""
        pass

    @abstractmethod
    def encrypt_data(self, data: str) -> bytes:
        """Шифрует данные"""
        pass

    @abstractmethod
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Расшифровывает данные"""
        pass

    def save_encrypted_data(self, data: str, name: str) -> None:
        """Сохраняет зашифрованные данные в базу данных"""
        encrypted_data = self.encrypt_data(data)
        self.db_manager.save_encrypted_data(name, encrypted_data, self.salt, self.algorithm_name)

    def load_encrypted_data(self, data_id: int, password: str) -> str:
        """Загружает и расшифровывает данные из базы данных"""
        encrypted_data, salt, algorithm = self.db_manager.get_encrypted_data_by_id(data_id)
        self.load_key(password, salt)
        return self.decrypt_data(encrypted_data)

    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """Возвращает название алгоритма"""
        pass 