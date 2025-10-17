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



class Editing(QMainWindow):

    
    def __init__(self, product_id=None):  # Добавляем параметр product_id
        super().__init__()
        self.product_id = product_id
        
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

        self.connect_db()

        if self.product_id is not None:
            self.load_product_data()
            self.add_btn.setText("Сохранить изменения")

        
        # Переменная для хранения пути к изображению
        self.current_image_path = None
        
        # Подключение к БД
    
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
    
    def load_product_data(self):
        """Загрузка данных товара для редактирования"""
        try:
            query = "SELECT name, description, price, count, image_path FROM product WHERE id = ?"
            self.cursor.execute(query, (self.product_id,))
            product = self.cursor.fetchone()
            
            if product:
                self.name_Edit.setPlainText(product[0])
                self.decryption_Edit.setPlainText(product[1])
                self.price_Edit.setPlainText(str(product[2]))
                self.count_Edit.setPlainText(str(product[3]))
                
                if product[4]:  # Если есть путь к изображению
                    self.current_image_path = product[4]
                    pixmap = QPixmap(product[4])
                    pixmap = pixmap.scaled(
                        self.photo.width(),
                        self.photo.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.photo.setPixmap(pixmap)
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка",
                f"Не удалось загрузить данные товара:\n{str(e)}"
            )


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
        """Метод для добавления/обновления товара"""
        try:
            # Получаем данные из полей (исправляем имена полей!)
            name = self.name_Edit.toPlainText().strip()
            description = self.decryption_Edit.toPlainText().strip()
            price = self.price_Edit.toPlainText().strip()
            count = self.count_Edit.toPlainText().strip()
            
            # ... валидация данных (оставляем как есть) ...
            query = """
                UPDATE product 
                SET name = ?, description = ?, price = ?, count = ?, image_path = ?
                WHERE id = ?
                """
            self.cursor.execute(query, (name, description, price, count, self.current_image_path, self.product_id))
            success_message = "Изменения успешно сохранены"
            
            self.conn.commit()
            
            QtWidgets.QMessageBox.information(
                self.win,
                "Успех",
                success_message
            )

            
            # Очищаем форму
            self.name_Edit.clear()
            self.decryption_Edit.clear()
            self.price_Edit.clear()
            self.count_Edit.clear()
            self.photo.clear()
            self.current_image_path = None
            self.product_id = None  # Сбрасываем ID после сохранения

            self.back()
            
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка базы данных",
                f"Не удалось сохранить изменения:\n{str(e)}"
            )



   #
    
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
    page = Editing()
    page.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()