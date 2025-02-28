"""from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from twofish import Twofish
import os
import struct
from .base_encryptor import BaseEncryptor

class TwofishEncryptor(BaseEncryptor):
    def __init__(self):
        self.salt = None
        self.key = None
        self.cipher = None

    @property
    def algorithm_name(self) -> str:
        return "Twofish"

    def generate_key(self, password: str) -> None:
        self.salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        self.key = kdf.derive(password.encode())
        self.cipher = Twofish(self.key)

    def load_key(self, password: str, salt: bytes) -> None:
        self.salt = salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        self.key = kdf.derive(password.encode())
        self.cipher = Twofish(self.key)

    def encrypt_data(self, data: str) -> bytes:
        if not self.cipher:
            raise ValueError("Ключ не был инициализирован")
        
        # Добавляем padding до размера блока (16 байт)
        data_bytes = data.encode()
        padding_length = 16 - (len(data_bytes) % 16)
        padded_data = data_bytes + bytes([padding_length] * padding_length)
        
        # Шифруем данные блоками
        encrypted_data = b''
        for i in range(0, len(padded_data), 16):
            block = padded_data[i:i+16]
            encrypted_block = self.cipher.encrypt(block)
            encrypted_data += encrypted_block
        
        return encrypted_data

    def decrypt_data(self, encrypted_data: bytes) -> str:
        if not self.cipher:
            raise ValueError("Ключ не был инициализирован")
        
        # Расшифровываем данные блоками
        decrypted_data = b''
        for i in range(0, len(encrypted_data), 16):
            block = encrypted_data[i:i+16]
            decrypted_block = self.cipher.decrypt(block)
            decrypted_data += decrypted_block
        
        # Удаляем padding
        padding_length = decrypted_data[-1]
        unpadded_data = decrypted_data[:-padding_length]
        
        return unpadded_data.decode()

    def save_encrypted_data(self, data: str, filename: str) -> None:
        encrypted_data = self.encrypt_data(data)
        with open(filename, 'wb') as f:
            f.write(self.salt)
            f.write(struct.pack('<Q', len(encrypted_data)))
            f.write(encrypted_data)

    def load_encrypted_data(self, filename: str, password: str) -> str:
        with open(filename, 'rb') as f:
            salt = f.read(16)
            size = struct.unpack('<Q', f.read(8))[0]
            encrypted_data = f.read(size)
        
        self.load_key(password, salt)
        return self.decrypt_data(encrypted_data) """