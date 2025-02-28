from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import struct
from .base_encryptor import BaseEncryptor

class TripleDESEncryptor(BaseEncryptor):
    def __init__(self):
        super().__init__()
        self.salt = None
        self.key = None
        self.iv = None

    @property
    def algorithm_name(self) -> str:
        return "Triple DES"

    def generate_key(self, password: str) -> None:
        self.salt = os.urandom(16)
        self.iv = os.urandom(8)  # Triple DES требует 8-байтовый IV
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=24,  # Triple DES требует 24-байтовый ключ
            salt=self.salt,
            iterations=480000,
        )
        self.key = kdf.derive(password.encode())

    def load_key(self, password: str, salt: bytes) -> None:
        self.salt = salt
        self.iv = salt[:8]  # Используем первые 8 байт соли как IV
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=24,
            salt=self.salt,
            iterations=480000,
        )
        self.key = kdf.derive(password.encode())

    def encrypt_data(self, data: str) -> bytes:
        if not self.key:
            raise ValueError("Ключ не был инициализирован")

        # Создаем padder для данных
        padder = padding.PKCS7(64).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()

        # Создаем шифр
        cipher = Cipher(
            algorithms.TripleDES(self.key),
            modes.CBC(self.iv)
        )
        encryptor = cipher.encryptor()

        # Шифруем данные
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return encrypted_data

    def decrypt_data(self, encrypted_data: bytes) -> str:
        if not self.key:
            raise ValueError("Ключ не был инициализирован")

        # Создаем шифр
        cipher = Cipher(
            algorithms.TripleDES(self.key),
            modes.CBC(self.iv)
        )
        decryptor = cipher.decryptor()

        # Расшифровываем данные
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # Удаляем padding
        unpadder = padding.PKCS7(64).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data.decode() 