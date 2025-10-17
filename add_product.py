import PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QSize, QFile
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QPushButton, QScrollArea, QLabel
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
import sys
import os
import pyodbc
import hashlib



class Add_product(QMainWindow):

    
    def __init__(self):
        super().__init__()
        
        loader = QUiLoader()                          
        ui_file = ('./ui/add_product.ui')    
        self.win = loader.load(ui_file)
        
        self.win.setMinimumSize(600, 800)
        self.win.setMaximumSize(600, 800)
        
        self.name_Edit = self.win.findChild(QtWidgets.QPlainTextEdit, 'name_Edit')
        self.decryption_Edit = self.win.findChild(QtWidgets.QPlainTextEdit, 'decryption_Edit')
        self.price_Edit = self.win.findChild(QtWidgets.QPlainTextEdit, 'price_Edit')
        self.count_Edit = self.win.findChild(QtWidgets.QPlainTextEdit, 'count_Edit')
        self.choose_btn = self.win.findChild(QtWidgets.QPushButton, "choose_btn")
        self.add_btn = self.win.findChild(QtWidgets.QPushButton, "add_btn")
        self.back_btn = self.win.findChild(QtWidgets.QPushButton, "back_btn")
        self.photo = self.win.findChild(QLabel, "product_img")
        
        self.choose_btn.clicked.connect(self.choose_image)
        self.add_btn.clicked.connect(self.add_product)
        self.back_btn.clicked.connect(self.back)
        
        # Переменная для хранения пути к изображению
        self.current_image_path = None
        
        # Подключение к БД
        self.connect_db()
    
    def connect_db(self):
        try:
            server_name = r"DESKTOP-H38FHII\MSSQLSERVER05"
            self.conn = pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};"
                f"SERVER={server_name};"
                "DATABASE=kurs223;"
                "Trusted_Connection=yes;"
            )
            self.cursor = self.conn.cursor()
            return True
        except pyodbc.Error as e:
            print(f"Ошибка подключения к SQL Server: {e}")
            return False
    
    def choose_image(self):
        """Метод для выбора изображения товара"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.win,
            "Выберите изображение товара",
            "",
            "Изображения (*.png *.jpg *.jpeg);;All files (*.*)"
        )
        if file_path:
            self.current_image_path = file_path
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(
                self.photo.width(),
                self.photo.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.photo.setPixmap(pixmap)
    
    def add_product(self):
        """Метод для добавления товара в базу данных"""
        try:
            # Получаем данные из полей
            name = self.name_Edit.toPlainText().strip()
            description = self.decryption_Edit.toPlainText().strip()
            price = self.price_Edit.toPlainText().strip()
            count = self.count_Edit.toPlainText().strip()
            
            # Валидация данных
            if not all([name, price, count]):
                QtWidgets.QMessageBox.warning(
                    self.win,
                    "Ошибка",
                    "Заполните обязательные поля: Название, Цена и Количество"
                )
                return
            
            try:
                price = float(price)
                count = int(count)
            except ValueError:
                QtWidgets.QMessageBox.warning(
                    self.win,
                    "Ошибка",
                    "Цена должна быть числом (например 199.99), а количество - целым числом"
                )
                return
            
            # Проверяем подключение к БД
            if not hasattr(self, 'conn') or not self.conn:
                self.connect_db()
                if not hasattr(self, 'conn'):
                    return
            
            # SQL-запрос
            query = """
            INSERT INTO product (name, description, price, count, image_path)
            VALUES (?, ?, ?, ?, ?)
            """
            
            # Выполняем запрос
            self.cursor.execute(query, (name, description, price, count, self.current_image_path))
            self.conn.commit()
            
            QtWidgets.QMessageBox.information(
                self.win,
                "Успех",
                "Товар успешно добавлен в базу данных"
            )
            
            # Очищаем форму
            self.name_Edit.clear()
            self.decryption_Edit.clear()
            self.price_Edit.clear()
            self.count_Edit.clear()
            self.photo.clear()
            self.current_image_path = None

            self.back()
            
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка базы данных",
                f"Не удалось добавить товар:\n{str(e)}"
            )
    
    def back(self):
        from choose_mode import Choose_mode
        self.prod_win = Choose_mode()
        self.prod_win.show()
        self.win.close()

    def show(self):
        self.win.show()

def main():

    loader = QUiLoader()
    app = QApplication(sys.argv)
    page = Add_product()
    page.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()