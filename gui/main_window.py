from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QComboBox, QPushButton, 
    QTextEdit, QListWidget, QMessageBox, QInputDialog,
    QTabWidget, QFileDialog, QListWidgetItem
)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from encryption.encryptor_factory import EncryptorFactory
from database.db_manager import DatabaseManager
from .settings_window import SettingsWindow
import os

class DropArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        
        # Создаем метку с инструкцией
        self.label = QLabel("Перетащите файлы сюда или нажмите для выбора")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # Список выбранных файлов
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        # Кнопка для выбора файлов
        self.select_btn = QPushButton("Выбрать файлы")
        self.select_btn.clicked.connect(self.select_files)
        layout.addWidget(self.select_btn)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            self.file_list.addItem(url.toLocalFile())
            
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы")
        for file in files:
            self.file_list.addItem(file)
            
    def get_files(self):
        return [self.file_list.item(i).text() for i in range(self.file_list.count())]
        
    def clear(self):
        self.file_list.clear()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("passwords")
        self.setMinimumSize(800, 600)
        
        self.db_manager = DatabaseManager()
        self.current_encryptor = None
        
        self.setup_ui()
        self.load_encrypted_data_list()
        
    def setup_ui(self):
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем главный горизонтальный layout
        main_layout = QHBoxLayout(central_widget)
        
        # Создаем sidebar
        sidebar = QWidget()
        sidebar.setMaximumWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Список зашифрованных данных
        self.data_list = QListWidget()
        self.data_list.itemClicked.connect(self.on_data_selected)
        
        sidebar_layout.addWidget(QLabel("Сохраненные данные:"))
        sidebar_layout.addWidget(self.data_list)
        
        # Кнопка настроек
        settings_btn = QPushButton("⚙️ Расширенные настройки")
        settings_btn.clicked.connect(self.show_settings)
        sidebar_layout.addWidget(settings_btn)
        
        # Основная часть с вкладками
        main_content = QWidget()
        content_layout = QVBoxLayout(main_content)
        
        # Создаем вкладки
        self.tab_widget = QTabWidget()
        self.setup_text_tab()
        self.setup_files_tab()
        content_layout.addWidget(self.tab_widget)
        
        # Добавляем sidebar и основной контент в главный layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(main_content)
        
    def setup_text_tab(self):
        text_tab = QWidget()
        layout = QVBoxLayout(text_tab)
        
        # Выбор алгоритма
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Алгоритм:"))
        self.text_algo_combo = QComboBox()
        self.text_algo_combo.addItems(EncryptorFactory.get_available_algorithms())
        algo_layout.addWidget(self.text_algo_combo)
        layout.addLayout(algo_layout)
        
        # Название данных
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название:"))
        self.text_name_input = QLineEdit()
        name_layout.addWidget(self.text_name_input)
        layout.addLayout(name_layout)
        
        # Пароль
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Пароль:"))
        self.text_password_input = QLineEdit()
        self.text_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(self.text_password_input)
        layout.addLayout(pass_layout)
        
        # Текстовое поле для данных
        layout.addWidget(QLabel("Данные:"))
        self.text_data_input = QTextEdit()
        layout.addWidget(self.text_data_input)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.text_encrypt_btn = QPushButton("Зашифровать")
        self.text_encrypt_btn.clicked.connect(self.encrypt_text)
        self.text_decrypt_btn = QPushButton("Расшифровать")
        self.text_decrypt_btn.clicked.connect(self.decrypt_text)
        self.text_decrypt_btn.setEnabled(False)
        button_layout.addWidget(self.text_encrypt_btn)
        button_layout.addWidget(self.text_decrypt_btn)
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(text_tab, "Текст")
        
    def setup_files_tab(self):
        files_tab = QWidget()
        layout = QVBoxLayout(files_tab)
        
        # Выбор алгоритма
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Алгоритм:"))
        self.files_algo_combo = QComboBox()
        self.files_algo_combo.addItems(EncryptorFactory.get_available_algorithms())
        algo_layout.addWidget(self.files_algo_combo)
        layout.addLayout(algo_layout)
        
        # Пароль
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Пароль:"))
        self.files_password_input = QLineEdit()
        self.files_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(self.files_password_input)
        layout.addLayout(pass_layout)
        
        # Область для drag-and-drop
        self.drop_area = DropArea()
        layout.addWidget(self.drop_area)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.files_encrypt_btn = QPushButton("Зашифровать")
        self.files_encrypt_btn.clicked.connect(self.encrypt_files)
        self.files_decrypt_btn = QPushButton("Расшифровать")
        self.files_decrypt_btn.clicked.connect(self.decrypt_files)
        button_layout.addWidget(self.files_encrypt_btn)
        button_layout.addWidget(self.files_decrypt_btn)
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(files_tab, "Файлы")
        
    def encrypt_text(self):
        """Шифрует и сохраняет текстовые данные"""
        name = self.text_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название для данных")
            return
            
        password = self.text_password_input.text()
        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            return
            
        data = self.text_data_input.toPlainText()
        if not data:
            QMessageBox.warning(self, "Ошибка", "Введите данные для шифрования")
            return
            
        algorithm = self.text_algo_combo.currentText()
        self.current_encryptor = EncryptorFactory.create_encryptor(algorithm)
        self.current_encryptor.generate_key(password)
        
        try:
            # Шифруем данные
            encrypted_data = self.current_encryptor.encrypt_data(data)
            
            # Сохраняем в базу данных
            self.db_manager.save_encrypted_data(
                name=name,
                encrypted_data=encrypted_data,
                salt=self.current_encryptor.salt,
                algorithm=algorithm
            )
            
            self.load_encrypted_data_list()
            self.text_data_input.clear()
            self.text_password_input.clear()
            QMessageBox.information(self, "Успех", "Данные успешно зашифрованы")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось зашифровать данные: {str(e)}")
            
    def decrypt_text(self):
        """Расшифровывает выбранные текстовые данные"""
        current_item = self.data_list.currentItem()
        if not current_item:
            return
            
        data_id = current_item.data(Qt.ItemDataRole.UserRole)
        data_type = current_item.data(Qt.ItemDataRole.UserRole + 1)
        
        if data_type != 'text':
            QMessageBox.warning(self, "Ошибка", "Выбранный элемент не является текстом")
            return
            
        password, ok = QInputDialog.getText(
            self, "Расшифровка", 
            "Введите пароль:", QLineEdit.EchoMode.Password
        )
        if not ok or not password:
            return
            
        algorithm = self.text_algo_combo.currentText()
        self.current_encryptor = EncryptorFactory.create_encryptor(algorithm)
        
        try:
            encrypted_data, salt, _ = self.db_manager.get_encrypted_data_by_id(data_id, 'text')
            self.current_encryptor.load_key(password, salt)
            decrypted_data = self.current_encryptor.decrypt_data(encrypted_data)
            self.text_data_input.setText(decrypted_data)
            self.tab_widget.setCurrentIndex(0)  # Переключаемся на вкладку с текстом
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось расшифровать данные: {str(e)}")
            
    def encrypt_files(self):
        """Шифрует выбранные файлы"""
        files = self.drop_area.get_files()
        if not files:
            QMessageBox.warning(self, "Ошибка", "Выберите файлы для шифрования")
            return
            
        password = self.files_password_input.text()
        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            return
            
        algorithm = self.files_algo_combo.currentText()
        self.current_encryptor = EncryptorFactory.create_encryptor(algorithm, file_mode=True)
        self.current_encryptor.generate_key(password)
        
        try:
            for file_path in files:
                is_folder = os.path.isdir(file_path)
                if is_folder:
                    encrypted_path = self.current_encryptor.encrypt_folder(file_path)
                else:
                    encrypted_path = self.current_encryptor.encrypt_file(file_path)
                    
                # Сохраняем информацию в базу данных
                self.db_manager.save_encrypted_file(
                    original_path=file_path,
                    encrypted_path=encrypted_path,
                    salt=self.current_encryptor.salt,
                    algorithm=algorithm,
                    is_folder=is_folder
                )
            
            self.drop_area.clear()
            self.files_password_input.clear()
            self.load_encrypted_data_list()
            QMessageBox.information(self, "Успех", "Файлы успешно зашифрованы")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось зашифровать файлы: {str(e)}")
            
    def decrypt_files(self):
        """Расшифровывает выбранные файлы"""
        current_item = self.data_list.currentItem()
        if not current_item:
            return
            
        data_id = current_item.data(Qt.ItemDataRole.UserRole)
        data_type = current_item.data(Qt.ItemDataRole.UserRole + 1)
        
        if data_type != 'file':
            QMessageBox.warning(self, "Ошибка", "Выбранный элемент не является файлом")
            return
            
        password, ok = QInputDialog.getText(
            self, "Расшифровка", 
            "Введите пароль:", QLineEdit.EchoMode.Password
        )
        if not ok or not password:
            return
            
        try:
            # Получаем информацию о файле
            original_path, encrypted_path, salt, algorithm, is_folder = self.db_manager.get_file_info(data_id)
            
            # Запрашиваем путь для сохранения
            if is_folder:
                save_path = QFileDialog.getExistingDirectory(
                    self, 
                    "Выберите папку для сохранения расшифрованной директории"
                )
            else:
                default_name = os.path.basename(original_path)
                save_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Сохранить расшифрованный файл",
                    default_name,
                    "Все файлы (*.*)"
                )
                
            if not save_path:  # Пользователь отменил выбор
                return
                
            # Создаем шифровальщик и загружаем ключ
            self.current_encryptor = EncryptorFactory.create_encryptor(algorithm, file_mode=True)
            self.current_encryptor.load_key(password, salt)
            
            # Расшифровываем файл или папку
            if is_folder:
                self.current_encryptor.decrypt_folder(encrypted_path, save_path)
            else:
                self.current_encryptor.decrypt_file(encrypted_path, save_path)
                
            QMessageBox.information(self, "Успех", "Файл успешно расшифрован")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось расшифровать файл: {str(e)}")
            
    def on_data_selected(self, item):
        """Обработчик выбора данных из списка"""
        data_type = item.data(Qt.ItemDataRole.UserRole + 1)
        
        if data_type == 'text':
            self.text_decrypt_btn.setEnabled(True)
            self.text_name_input.setText(item.text().split(" (")[0])
            algorithm = item.text().split("(")[1].rstrip(")")
            index = self.text_algo_combo.findText(algorithm)
            if index >= 0:
                self.text_algo_combo.setCurrentIndex(index)
            self.tab_widget.setCurrentIndex(0)  # Переключаемся на вкладку с текстом
        else:
            self.files_decrypt_btn.setEnabled(True)
            algorithm = item.text().split("(")[1].rstrip(")")
            index = self.files_algo_combo.findText(algorithm)
            if index >= 0:
                self.files_algo_combo.setCurrentIndex(index)
            self.tab_widget.setCurrentIndex(1)  # Переключаемся на вкладку с файлами
            
    def show_settings(self):
        """Открывает окно настроек"""
        settings_dialog = SettingsWindow(self)
        settings_dialog.exec()

    def load_encrypted_data_list(self):
        """Загружает список зашифрованных данных в sidebar"""
        self.data_list.clear()
        try:
            for data_id, name, algorithm, data_type in self.db_manager.get_all_encrypted_data():
                if data_type == 'text':
                    item_text = f"📝 {name} ({algorithm})"
                else:
                    # Для файлов показываем только имя файла
                    item_text = f"📄 {os.path.basename(name)} ({algorithm})"
                    
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, data_id)
                item.setData(Qt.ItemDataRole.UserRole + 1, data_type)
                self.data_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список данных: {str(e)}")
    
    def encrypt_data(self):
        pass
    
    def decrypt_data(self):
        pass
    
    def encrypt_data(self):
        pass
    
    def decrypt_data(self):
        pass 