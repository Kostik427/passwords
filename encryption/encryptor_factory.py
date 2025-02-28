from typing import Dict, Type
from .base_encryptor import BaseEncryptor
from .fernet_encryptor import FernetEncryptor
from .chacha20_encryptor import ChaCha20Encryptor
from .triple_des_encryptor import TripleDESEncryptor

class EncryptorFactory:
    _encryptors: Dict[str, Type[BaseEncryptor]] = {
        "Fernet": FernetEncryptor,
        "ChaCha20": ChaCha20Encryptor,
        "Triple DES": TripleDESEncryptor
    }

    @classmethod
    def get_available_algorithms(cls) -> list[str]:
        """Возвращает список доступных алгоритмов шифрования"""
        return list(cls._encryptors.keys())

    @classmethod
    def create_encryptor(cls, algorithm_name: str) -> BaseEncryptor:
        """Создает экземпляр шифровальщика по имени алгоритма"""
        if algorithm_name not in cls._encryptors:
            raise ValueError(f"Неизвестный алгоритм шифрования: {algorithm_name}")
        return cls._encryptors[algorithm_name]() 