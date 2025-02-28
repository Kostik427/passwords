from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QComboBox, QPushButton, 
    QTextEdit, QListWidget, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from encryption.encryptor_factory import EncryptorFactory
from database.db_manager import DatabaseManager
from .settings_window import SettingsWindow

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
        
        # Основная часть
        main_content = QWidget()
        content_layout = QVBoxLayout(main_content)
        
        # Выбор алгоритма
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Алгоритм:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(EncryptorFactory.get_available_algorithms())
        algo_layout.addWidget(self.algo_combo)
        content_layout.addLayout(algo_layout)
        
        # Название данных
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        content_layout.addLayout(name_layout)
        
        # Пароль
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(self.password_input)
        content_layout.addLayout(pass_layout)
        
        # Текстовое поле для данных
        content_layout.addWidget(QLabel("Данные:"))
        self.data_input = QTextEdit()
        content_layout.addWidget(self.data_input)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.encrypt_btn = QPushButton("Зашифровать")
        self.encrypt_btn.clicked.connect(self.encrypt_data)
        self.decrypt_btn = QPushButton("Расшифровать")
        self.decrypt_btn.clicked.connect(self.decrypt_data)
        self.decrypt_btn.setEnabled(False)
        button_layout.addWidget(self.encrypt_btn)
        button_layout.addWidget(self.decrypt_btn)
        content_layout.addLayout(button_layout)
        
        # Добавляем sidebar и основной контент в главный layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(main_content)
        
    def load_encrypted_data_list(self):
        """Загружает список зашифрованных данных в sidebar"""
        self.data_list.clear()
        try:
            for data_id, name, algorithm in self.db_manager.get_all_encrypted_data():
                item_text = f"{name} ({algorithm})"
                item = self.data_list.addItem(item_text)
                # Сохраняем ID в данных элемента
                self.data_list.item(self.data_list.count() - 1).setData(Qt.ItemDataRole.UserRole, data_id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список данных: {str(e)}")
    
    def on_data_selected(self, item):
        """Обработчик выбора данных из списка"""
        self.decrypt_btn.setEnabled(True)
        self.name_input.setText(item.text().split(" (")[0])
        algorithm = item.text().split("(")[1].rstrip(")")
        index = self.algo_combo.findText(algorithm)
        if index >= 0:
            self.algo_combo.setCurrentIndex(index)
    
    def encrypt_data(self):
        """Шифрует и сохраняет данные"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название для данных")
            return
            
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            return
            
        data = self.data_input.toPlainText()
        if not data:
            QMessageBox.warning(self, "Ошибка", "Введите данные для шифрования")
            return
            
        algorithm = self.algo_combo.currentText()
        self.current_encryptor = EncryptorFactory.create_encryptor(algorithm)
        self.current_encryptor.generate_key(password)
        
        try:
            self.current_encryptor.save_encrypted_data(data, name)
            self.load_encrypted_data_list()
            self.data_input.clear()
            self.password_input.clear()
            QMessageBox.information(self, "Успех", "Данные успешно зашифрованы")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось зашифровать данные: {str(e)}")
    
    def decrypt_data(self):
        """Расшифровывает выбранные данные"""
        current_item = self.data_list.currentItem()
        if not current_item:
            return
            
        data_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        password, ok = QInputDialog.getText(
            self, "Расшифровка", 
            "Введите пароль:", QLineEdit.EchoMode.Password
        )
        if not ok or not password:
            return
            
        algorithm = self.algo_combo.currentText()
        self.current_encryptor = EncryptorFactory.create_encryptor(algorithm)
        
        try:
            decrypted_data = self.current_encryptor.load_encrypted_data(data_id, password)
            self.data_input.setText(decrypted_data)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось расшифровать данные: {str(e)}")
    
    def show_settings(self):
        """Открывает окно настроек"""
        settings_dialog = SettingsWindow(self)
        settings_dialog.exec() 