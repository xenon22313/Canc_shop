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



class Registration(QMainWindow):

    
    def __init__(self):
        super().__init__()

        #connect ui
        loader = QUiLoader()                          
        ui_file = ('./ui/registration.ui')    
        self.win = loader.load(ui_file)

        self.win.setMinimumSize(1280, 720)
        self.win.setMaximumSize(1280, 720)



        base_dir = os.path.dirname(os.path.abspath(__file__))
        bg_image = os.path.join(base_dir, "src", "img", "69452687601.jpg")
        frame_image = os.path.join(base_dir, "src", "img", "69452687602.jpg")
        
        self.fon1 = self.win.findChild(QLabel, 'label_fon1') 
        self.fon2 = self.win.findChild(QLabel, 'label_fon2') 

        self.connect()

        self.btn = self.win.findChild(QtWidgets.QPushButton, "registration")
        self.btn.clicked.connect(self.registration)
        self.login = self.win.findChild(QtWidgets.QPushButton, "sing_in")
        self.login.clicked.connect(self.change_to_login)
        

        self.name_edit = self.win.findChild(QtWidgets.QPlainTextEdit, 'name_edit')
        self.email_edit = self.win.findChild(QtWidgets.QPlainTextEdit, 'email_edit')
        self.password_edit1 = self.win.findChild(QtWidgets.QPlainTextEdit, 'password_edit1')
        self.password_edit2 = self.win.findChild(QtWidgets.QPlainTextEdit, 'password_edit2')

        #подсказки

        self.name_edit.setPlaceholderText("enter your name")
        self.email_edit.setPlaceholderText("enter your email")
        self.password_edit1.setPlaceholderText("enter your password")
        self.password_edit2.setPlaceholderText("enter your password")

        self.name_edit.mousePressEvent = lambda event: self.clear_on_click(self.name_edit, event)
        self.email_edit.mousePressEvent = lambda event: self.clear_on_click(self.email_edit, event)
        self.password_edit1.mousePressEvent = lambda event: self.clear_on_click(self.password_edit1, event)
        self.password_edit2.mousePressEvent = lambda event: self.clear_on_click(self.password_edit2, event)


    #подсказки
    def clear_on_click(self, field, event):
        
        if field.toPlainText() in ["enter your name", "enter your email", "enter your password"]:
            field.clear()

        QtWidgets.QPlainTextEdit.mousePressEvent(field, event)

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

        

    def registration(self):
        name = self.name_edit.toPlainText().strip()
        email = self.email_edit.toPlainText().strip()
        password = self.password_edit1.toPlainText().strip()
        password2 = self.password_edit2.toPlainText().strip()

        if not all([name, email, password, password2]):
            QtWidgets.QMessageBox.warning(
                self.win,
                "Ошибка",
                "Все поля должны быть заполнены"
            )
            return

        
        if '@' not in email or '.' not in email:
            QtWidgets.QMessageBox.warning(self.win, "Ошибка", "Некорректный email")
            return

        # Проверка на запрещенные символы
        for field in [email, password, password2, name]:
            if any(char in field for char in ['"', "'", "`"]):
                QtWidgets.QMessageBox.warning(
                    self.win, 
                    "Ошибка", 
                    "Недопустимые символы в полях ввода"
                )
                return

        # Проверка совпадения паролей
        if password != password2:
            QtWidgets.QMessageBox.warning(
                self.win,
                "Ошибка",
                "Пароли не совпадают"
            )
            return

        try:
            # Проверка существования пользователя
            check_query = "SELECT id FROM users WHERE email = ?"
            self.cursor.execute(check_query, (email,))
            if self.cursor.fetchone():
                QtWidgets.QMessageBox.warning(
                    self.win,
                    "Ошибка",
                    "Пользователь с таким email уже существует"
                )
                return

        except pyodbc.Error as e:
            self.conn.rollback()
            print(f"Ошибка регистрации: {e}")
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка",
                f"Не удалось зарегистрировать пользователя: {str(e)}"
            )

            # Хеширование пароля
        password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Параметризованный запрос
        query = """
        INSERT INTO users (name, email, password) 
        OUTPUT INSERTED.id
        VALUES (?, ?, ?)
        """
            
            # Выполнение запроса
        self.cursor.execute(query, (name, email, password_hash))
        user_id = self.cursor.fetchone()[0]
        self.conn.commit()
            
        print(f"Пользователь {user_id} успешно зарегистрирован")
        QtWidgets.QMessageBox.information(
            self.win,
            "Успех",
            "Регистрация прошла успешно"
        )
        self.change_to_login()
            

            
        
    def change_to_login(self):
        from login import Login
        print("go")
        self.login_win = Login()
        self.login_win.show()
        self.win.close()
        



    def show(self):
        self.win.show()

def main():

    loader = QUiLoader()
    app = QApplication(sys.argv)
    page = Registration()
    page.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()