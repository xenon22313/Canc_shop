import PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QSize, QFile
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QPushButton, QScrollArea, QLabel
from PySide6.QtWidgets import *
import sys
import os
import pyodbc
import hashlib

from session import session






class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        

        #connect ui
        loader = QUiLoader()                          
        ui_file = ('./ui/login.ui')    
        self.win = loader.load(ui_file)

        self.win.setMinimumSize(1280, 720)
        self.win.setMaximumSize(1280, 720)

        self.connect()

        self.btn = self.win.findChild(QtWidgets.QPushButton, "sing_in")
        self.btn.clicked.connect(self.login)
        self.reg_btn = self.win.findChild(QtWidgets.QPushButton, "registration")
        self.reg_btn.clicked.connect(self.change_to_registration)
        self.guest_btn = self.win.findChild(QtWidgets.QPushButton, "guest_btn")
        if self.guest_btn:
            self.guest_btn.clicked.connect(self.login_as_guest)

        self.email_edit = self.win.findChild(QtWidgets.QLineEdit, 'email_edit')
        self.password_edit = self.win.findChild(QtWidgets.QLineEdit, 'password_edit')

        #подсказки
        self.email_edit.setPlaceholderText("Введите email")
        self.password_edit.setPlaceholderText("Введите пароль")





    #connect db
    def connect(self):
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
       

    def login(self):
##############################################################################################################
        try:
            email = self.email_edit.text().strip()
            password = self.password_edit.text().strip()

            if not all([email, password]):
                QtWidgets.QMessageBox.warning(
                    self.win,
                    "Ошибка",
                    "Все поля должны быть заполнены"
                )
                return

            if '@' not in email or '.' not in email:
                QtWidgets.QMessageBox.warning(self.win, "Ошибка", "Некорректный email")
                return

            # проверка на запрещенные символы
            for field in [email, password]:
                if any(char in field for char in ['"', "'", "`"]):
                    QtWidgets.QMessageBox.warning(
                        self.win, 
                        "Ошибка", 
                        "Недопустимые символы в полях ввода"
                    )
                    return
            
            # хеширование пароля
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # проверка пользователя в БД
            query = """
            SELECT id, name, password, role
            FROM users 
            WHERE email = ?
            """
            self.cursor.execute(query, (email,))
            user_data = self.cursor.fetchone()

            if not user_data:
                QtWidgets.QMessageBox.warning(
                    self.win,
                    "Ошибка",
                    "Пользователь с таким email не найден"
                )
                return False

            user_id, username, db_password_hash, role = user_data

            # проверка пароля
            if password_hash != db_password_hash:
                QtWidgets.QMessageBox.warning(
                    self.win,
                    "Ошибка",
                    "Неверный пароль"
                )
                return False

            # успешная авторизация
            from session import session
            session.id = user_id
            session.username = username
            session.email = email
            session.role = role
            
            QtWidgets.QMessageBox.information(
                self.win,
                "Успех",
                f"Добро пожаловать, {username}! Ваша роль: {role}"
            )

            print(user_id, username)
            if role == 'admin':
                self.change_to_product()
            else:
                self.change_to_product()
            
            return True
        

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка базы данных",
                f"Ошибка при авторизации: {str(e)}"
            )
            return False
        
    def show_admin_panel(self):
        from choose_mode import Choose_mode
        self.prod_win = Choose_mode()
        self.prod_win.show()
        self.win.close()

    def change_to_registration(self):
        from registration import Registration
        print("go")
        self.reg_win = Registration()
        self.reg_win.show()
        self.win.close()

    def login_as_guest(self):
        """Вход как гость - переход в окно Product без авторизации"""
        from product import Product
        
        # Создаем окно Product с данными гостя
        self.prod_win = Product(
            user_info={
                'name': 'Гость'
            }
        )
        self.prod_win.show()
        self.win.close()

    def change_to_product(self):
        
        from product import Product
        from session import session 
        
        # окно Product с передачей данных пользователя
        self.prod_win = Product(
            user_info={
                'id': session.id,
                'name': session.username,
                'email': session.email,
                'role': session.role
            }
        )
        self.prod_win.show()
        self.win.close()

    def show(self):
        self.win.show()
        

def main():

    loader = QUiLoader()
    app = QApplication(sys.argv)
    page = Login()
    page.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
    