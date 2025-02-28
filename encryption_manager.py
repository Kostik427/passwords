from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from encryption_settings import EncryptionSettings

class EncryptionManager:
    def __init__(self):
        self.salt = None
        self.key = None
        self.fernet = None
        self.settings = EncryptionSettings()

    def generate_key(self, password: str) -> None:
        """Генерирует ключ на основе пароля"""
        settings = self.settings.get_settings()
        self.salt = os.urandom(settings['salt_size'])
        kdf = PBKDF2HMAC(
            algorithm=self.settings.get_hash_algorithm(),
            length=settings['key_length'],
            salt=self.salt,
            iterations=settings['iterations'],
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.key = key
        self.fernet = Fernet(key)

    def load_key(self, password: str, salt: bytes) -> None:
        """Загружает существующий ключ"""
        settings = self.settings.get_settings()
        self.salt = salt
        kdf = PBKDF2HMAC(
            algorithm=self.settings.get_hash_algorithm(),
            length=settings['key_length'],
            salt=self.salt,
            iterations=settings['iterations'],
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.key = key
        self.fernet = Fernet(key)

    def encrypt_data(self, data: str) -> bytes:
        """Шифрует данные"""
        if not self.fernet:
            raise ValueError("Ключ не был инициализирован")
        return self.fernet.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Расшифровывает данные"""
        if not self.fernet:
            raise ValueError("Ключ не был инициализирован")
        return self.fernet.decrypt(encrypted_data).decode()

    def save_encrypted_data(self, data: str, filename: str) -> None:
        """Сохраняет зашифрованные данные в файл"""
        encrypted_data = self.encrypt_data(data)
        with open(filename, 'wb') as f:
            f.write(self.salt)  # Сначала записываем соль
            f.write(encrypted_data)  # Затем зашифрованные данные

    def load_encrypted_data(self, filename: str, password: str) -> str:
        """Загружает и расшифровывает данные из файла"""
        with open(filename, 'rb') as f:
            salt = f.read(16)  # Читаем соль
            encrypted_data = f.read()  # Читаем зашифрованные данные
        
        self.load_key(password, salt)
        return self.decrypt_data(encrypted_data) 