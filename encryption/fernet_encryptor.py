from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from .base_encryptor import BaseEncryptor

class FernetEncryptor(BaseEncryptor):
    def __init__(self):
        super().__init__()
        self.salt = None
        self.key = None
        self.fernet = None

    @property
    def algorithm_name(self) -> str:
        return "Fernet"

    def generate_key(self, password: str) -> None:
        self.salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.key = key
        self.fernet = Fernet(key)

    def load_key(self, password: str, salt: bytes) -> None:
        self.salt = salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.key = key
        self.fernet = Fernet(key)

    def encrypt_data(self, data: str) -> bytes:
        if not self.fernet:
            raise ValueError("Ключ не был инициализирован")
        return self.fernet.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        if not self.fernet:
            raise ValueError("Ключ не был инициализирован")
        return self.fernet.decrypt(encrypted_data).decode() 