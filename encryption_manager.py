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
        self.salt = os.urandom(settings["salt_size"])
        kdf = PBKDF2HMAC(
            algorithm=self.settings.get_hash_algorithm(),
            length=settings["key_length"],
            salt=self.salt,
            iterations=settings["iterations"],
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
            length=settings["key_length"],
            salt=self.salt,
            iterations=settings["iterations"],
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
        with open(filename, "wb") as f:
            f.write(self.salt)  # Сначала записываем соль
            f.write(encrypted_data)  # Затем зашифрованные данные

    def load_encrypted_data(self, filename: str, password: str) -> str:
        """Загружает и расшифровывает данные из файла"""
        with open(filename, "rb") as f:
            salt = f.read(16)  # Читаем соль
            encrypted_data = f.read()  # Читаем зашифрованные данные

        self.load_key(password, salt)
        return self.decrypt_data(encrypted_data)


class FileEncryptionManager(EncryptionManager):
    def __init__(self):
        super().__init__()
        self.chunk_size = 64 * 1024  # 64KB chunks for file processing

    def encrypt_file(self, input_path: str, output_path: str = None) -> str:
        """Шифрует файл и возвращает путь к зашифрованному файлу"""
        if not self.fernet:
            raise ValueError("Ключ не был инициализирован")

        if output_path is None:
            output_path = input_path + ".encrypted"

        with open(input_path, "rb") as in_file, open(output_path, "wb") as out_file:
            # Записываем соль в начало файла
            out_file.write(self.salt)

            # Читаем и шифруем файл по частям
            while True:
                chunk = in_file.read(self.chunk_size)
                if not chunk:
                    break
                encrypted_chunk = self.fernet.encrypt(chunk)
                out_file.write(len(encrypted_chunk).to_bytes(8, byteorder="big"))
                out_file.write(encrypted_chunk)

        return output_path

    def decrypt_file(self, input_path: str, output_path: str = None) -> str:
        """Расшифровывает файл и возвращает путь к расшифрованному файлу"""
        if not self.fernet:
            raise ValueError("Ключ не был инициализирован")

        if output_path is None:
            output_path = input_path.rsplit(".encrypted", 1)[0]
            if output_path == input_path:
                output_path = input_path + ".decrypted"

        with open(input_path, "rb") as in_file, open(output_path, "wb") as out_file:
            # Читаем соль
            salt = in_file.read(16)

            # Читаем и расшифровываем файл по частям
            while True:
                chunk_size_bytes = in_file.read(8)
                if not chunk_size_bytes:
                    break

                chunk_size = int.from_bytes(chunk_size_bytes, byteorder="big")
                encrypted_chunk = in_file.read(chunk_size)

                if not encrypted_chunk:
                    break

                decrypted_chunk = self.fernet.decrypt(encrypted_chunk)
                out_file.write(decrypted_chunk)

        return output_path

    def encrypt_folder(self, folder_path: str, output_path: str = None) -> str:
        """Шифрует папку, создавая зашифрованный архив"""
        import tempfile
        import shutil
        import os

        if not self.fernet:
            raise ValueError("Ключ не был инициализирован")

        if output_path is None:
            output_path = folder_path + ".encrypted"

        # Создаем временный архив
        temp_archive = tempfile.mktemp(".zip")
        shutil.make_archive(temp_archive[:-4], "zip", folder_path)

        # Шифруем архив
        encrypted_path = self.encrypt_file(temp_archive, output_path)

        # Удаляем временный архив
        os.remove(temp_archive)

        return encrypted_path

    def decrypt_folder(self, encrypted_path: str, output_folder: str = None) -> str:
        """Расшифровывает папку из зашифрованного архива"""
        import tempfile
        import zipfile
        import os

        if not self.fernet:
            raise ValueError("Ключ не был инициализирован")

        if output_folder is None:
            output_folder = encrypted_path.rsplit(".encrypted", 1)[0]

        # Создаем временный файл для расшифрованного архива
        temp_archive = tempfile.mktemp(".zip")

        # Расшифровываем архив
        self.decrypt_file(encrypted_path, temp_archive)

        # Создаем папку для распаковки, если её нет
        os.makedirs(output_folder, exist_ok=True)

        # Распаковываем архив
        with zipfile.ZipFile(temp_archive, "r") as zip_ref:
            zip_ref.extractall(output_folder)

        # Удаляем временный архив
        os.remove(temp_archive)

        return output_folder
