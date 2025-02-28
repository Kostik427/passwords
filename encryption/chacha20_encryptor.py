from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os
import struct
from .base_encryptor import BaseEncryptor

class ChaCha20Encryptor(BaseEncryptor):
    def __init__(self):
        super().__init__()
        self.salt = None
        self.key = None
        self.cipher = None

    @property
    def algorithm_name(self) -> str:
        return "ChaCha20"

    def generate_key(self, password: str) -> None:
        self.salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        self.key = kdf.derive(password.encode())
        self.cipher = ChaCha20Poly1305(self.key)

    def load_key(self, password: str, salt: bytes) -> None:
        self.salt = salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        self.key = kdf.derive(password.encode())
        self.cipher = ChaCha20Poly1305(self.key)

    def encrypt_data(self, data: str) -> bytes:
        if not self.cipher:
            raise ValueError("Ключ не был инициализирован")
        
        nonce = os.urandom(12)  # ChaCha20 требует 12-байтовый nonce
        data_bytes = data.encode()
        
        # Шифруем данные
        encrypted_data = self.cipher.encrypt(nonce, data_bytes, None)
        return nonce + encrypted_data  # Добавляем nonce к зашифрованным данным

    def decrypt_data(self, encrypted_data: bytes) -> str:
        if not self.cipher:
            raise ValueError("Ключ не был инициализирован")
        
        nonce = encrypted_data[:12]  # Извлекаем nonce
        ciphertext = encrypted_data[12:]  # Извлекаем зашифрованные данные
        
        # Расшифровываем данные
        decrypted_data = self.cipher.decrypt(nonce, ciphertext, None)
        return decrypted_data.decode() 