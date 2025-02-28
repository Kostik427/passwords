from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSpinBox, QComboBox, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from encryption_settings import EncryptionSettings

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = EncryptionSettings()
        self.current_settings = self.settings.get_settings()
        
        self.setWindowTitle("Расширенные настройки шифрования")
        self.setModal(True)
        
        # Создаем предупреждающую надпись
        warning_label = QLabel(
            "⚠️ ВНИМАНИЕ: Изменение этих настроек может повлиять на безопасность\n"
            "ваших данных. Меняйте их только если полностью понимаете последствия!"
        )
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Создаем элементы управления
        layout = QVBoxLayout()
        layout.addWidget(warning_label)
        layout.addSpacing(10)
        
        # Количество итераций
        iterations_layout = QHBoxLayout()
        iterations_label = QLabel("Количество итераций:")
        self.iterations_spin = QSpinBox()
        self.iterations_spin.setRange(100000, 1000000)
        self.iterations_spin.setSingleStep(10000)
        self.iterations_spin.setValue(self.current_settings['iterations'])
        iterations_layout.addWidget(iterations_label)
        iterations_layout.addWidget(self.iterations_spin)
        layout.addLayout(iterations_layout)
        
        # Длина ключа
        key_length_layout = QHBoxLayout()
        key_length_label = QLabel("Длина ключа (байт):")
        self.key_length_spin = QSpinBox()
        self.key_length_spin.setRange(16, 64)
        self.key_length_spin.setValue(self.current_settings['key_length'])
        key_length_layout.addWidget(key_length_label)
        key_length_layout.addWidget(self.key_length_spin)
        layout.addLayout(key_length_layout)
        
        # Алгоритм хеширования
        hash_layout = QHBoxLayout()
        hash_label = QLabel("Алгоритм хеширования:")
        self.hash_combo = QComboBox()
        self.hash_combo.addItems(['SHA256', 'SHA384', 'SHA512'])
        self.hash_combo.setCurrentText(self.current_settings['hash_algorithm'])
        hash_layout.addWidget(hash_label)
        hash_layout.addWidget(self.hash_combo)
        layout.addLayout(hash_layout)
        
        # Размер соли
        salt_layout = QHBoxLayout()
        salt_label = QLabel("Размер соли (байт):")
        self.salt_spin = QSpinBox()
        self.salt_spin.setRange(16, 64)
        self.salt_spin.setValue(self.current_settings['salt_size'])
        salt_layout.addWidget(salt_label)
        salt_layout.addWidget(self.salt_spin)
        layout.addLayout(salt_layout)
        
        # Информационная надпись
        info_label = QLabel(
            "\nПримечание:\n"
            "• Изменения влияют только на новые пароли\n"
            "• Увеличение значений замедляет работу программы\n"
            "• Уменьшение значений снижает безопасность"
        )
        info_label.setStyleSheet("color: gray;")
        layout.addWidget(info_label)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_settings(self):
        try:
            new_settings = {
                'iterations': self.iterations_spin.value(),
                'key_length': self.key_length_spin.value(),
                'hash_algorithm': self.hash_combo.currentText(),
                'salt_size': self.salt_spin.value()
            }
            
            self.settings.update_settings(new_settings)
            QMessageBox.information(self, "Успех", "Настройки успешно сохранены")
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e)) 