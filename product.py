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
from login import Login
from session import session 

import datetime
import secrets




class Product(QMainWindow):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"name": "Гость"}  # По умолчанию "Гость"
        print(f"Текущий пользователь: {self.user_info.get('name', 'Гость')}")

        loader = QUiLoader()                          
        ui_file = './ui/product.ui'    
        self.win = loader.load(ui_file)
        
        self.win.setMinimumSize(1280, 720)
        self.win.setMaximumSize(1280, 720)
        
        self.username_label = self.win.findChild(QLabel, "username")
        if self.username_label != None:
            self.username_label.setText(self.user_info.get("name", "Гость"))

        self.trash_btn = self.win.findChild(QtWidgets.QPushButton, "trash_btn")
        self.trash_btn.clicked.connect(self.change_to_trash)

        self.current_filter = None

        self.sort_abc = self.win.findChild(QtWidgets.QPushButton, "sort_abc")
        self.sort_abc.clicked.connect(lambda: self.load_products(sort_order='ABC', name_filter=self.current_filter))
        self.sort_cba = self.win.findChild(QtWidgets.QPushButton, "sort_cba")
        self.sort_cba.clicked.connect(lambda: self.load_products(sort_order='CBA', name_filter=self.current_filter))

        self.pencils_btn = self.win.findChild(QPushButton, "pencil_btn")  
        self.pens_btn = self.win.findChild(QPushButton, "pen_btn")       
        self.sharpener_btn = self.win.findChild(QPushButton, "sharpener_btn")
        self.paint_btn = self.win.findChild(QPushButton, "paint_btn")  
        self.all_btn = self.win.findChild(QPushButton, "all_btn")  
        self.exit_btn = self.win.findChild(QPushButton, "exit_btn")  

        self.exit_btn.clicked.connect(self.exit)

        # обработчики
        self.pencils_btn.clicked.connect(lambda: (
            
            self.set_current_filter("карандаш"),
            self.load_products(name_filter="карандаш")
        ))
        self.pens_btn.clicked.connect(lambda: (
            self.set_current_filter("ручк"),
            self.load_products(name_filter="ручк")
        ))
        self.sharpener_btn.clicked.connect(lambda: (
            self.set_current_filter("точилк"),
            self.load_products(name_filter="точилк")
        ))
        self.paint_btn.clicked.connect(lambda: (
            self.set_current_filter("краск"),
            self.load_products(name_filter="краск")
        ))
        self.all_btn.clicked.connect(lambda: (
            self.set_current_filter(None),
            self.load_products()            
        ))

        self.scroll_area = self.win.findChild(QScrollArea, 'product_table')
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # виджет-контейнер для карточек
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)

        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        
        # Подключение к БД
        if not self.connect():
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка",
                "Не удалось подключиться к базе данных"
            )
            return
        
        # Загрузка товаров
        self.load_products()
        

    def set_current_filter(self, name_filter):
        self.current_filter = name_filter

    def change_to_trash(self):
        from trash import TrashWindow
        self.trash_win = TrashWindow(parent=self)
        self.trash_win.show()
        self.win.hide()

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
    def add_to_cart(self, product_id):
        try:
            # проверка авторизации через сессию
            if not hasattr(session, 'id') or not session.id:
                QtWidgets.QMessageBox.warning(
                    self.win,
                    "Ошибка",
                    "Для добавления в корзину необходимо авторизоваться"
                )
                return

            # есть ли товар в БД
            self.cursor.execute("SELECT id FROM product WHERE id = ?", (product_id,))
            if not self.cursor.fetchone():
                QtWidgets.QMessageBox.warning(
                    self.win,
                    "Ошибка",
                    "Товар не найден в базе данных"
                )
                return
            
            # есть ли уже товар в корзине
            self.cursor.execute(
                "SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", 
                (session.id, product_id)
            )
            existing_item = self.cursor.fetchone()
            
            if existing_item:
                # обновление количество, если товар уже в корзине
                query = """
                UPDATE cart 
                SET quantity = quantity + 1 
                WHERE user_id = ? AND product_id = ?
                """
            else:
                # новый товар в корзину
                query = """
                INSERT INTO cart (user_id, product_id, quantity) 
                VALUES (?, ?, 1)
                """

            self.cursor.execute(
            "SELECT count FROM product WHERE id = ?", 
            (product_id,)
            )
            available = self.cursor.fetchone()
            
            if not available or available[0] <= 0:
                QtWidgets.QMessageBox.warning(
                    self.win,
                    "Нет в наличии",
                    "Этот товар закончился"
                )
                return

            self.cursor.execute(query, (session.id, product_id))
            self.conn.commit()

            QtWidgets.QMessageBox.information(
                self.win,
                "Успех",
                "Товар добавлен в корзину"
            )

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка базы данных",
                f"Не удалось добавить товар в корзину:\n{str(e)}"
            )
            if self.conn:
                self.conn.rollback()

    def load_products(self, sort_order=None, name_filter=None):
        if not hasattr(self, 'cursor') or not self.cursor:
            return
            
        try:
            self.clear_product_cards()
            
            # Получение данных из таблицы product
            query = """
            SELECT id, name, price, description, image_path 
            FROM product
            """
            
            if name_filter:
                query += f" WHERE name LIKE '%{name_filter}%'"

            # Добавляем сортировку, если указана
            if sort_order == 'ABC':
                query += " ORDER BY price ASC"
            elif sort_order == 'CBA':
                query += " ORDER BY price DESC"
            else:
                query += " ORDER BY id"

            self.cursor.execute(query)
            products = self.cursor.fetchall()
            
            if not products:
                label = QtWidgets.QLabel("Товары не найдены")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("font: 14pt 'Segoe UI'; color: #888;")
                self.scroll_layout.addWidget(label)
                return
            
            # Создаем карточки для каждого товара
            for product in products:
                product_id, name, price, description, image_path = product
                self.create_product_card(product_id, name, price, description, image_path)
                
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка базы данных",
                f"Ошибка при загрузке товаров:\n{str(e)}"
            )

    def clear_product_cards(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def create_product_card(self, product_id, name, price, description, image_path=None):
       
        # Основной блок продукта
        product_block = QtWidgets.QFrame()
        product_block.setStyleSheet("""
            QFrame {
                background-color: #31363F;
                border-radius: 14px;
                border: 1px solid #222831;
                padding: 0px;
            }
            QFrame:hover {
                border: 1px solid #76ABAE;
                background-color: #31363F;
            }
        """)
        product_block.setFixedSize(1060, 220)

        # Основной макет карточки
        card_layout = QHBoxLayout(product_block)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(25)

        # Блок с изображением
        image_frame = QtWidgets.QFrame()
        image_frame.setFixedSize(160, 160)
        image_frame.setStyleSheet("""
            QFrame {
                border-radius: 10px;
                background: #222831;
                border: 1px;
            }
        """)
        
        image_label = QtWidgets.QLabel(image_frame)
        
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(
                150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        else:
            pixmap = QPixmap(r'.\src\img\331d7bf29f945f874edb70410d4ed345.jpg').scaled(
                150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setGeometry(5, 5, 150, 150)

        # Блок с информацией
        info_frame = QtWidgets.QFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 5, 0, 5)
        info_layout.setSpacing(12)
        info_frame.setStyleSheet("""
                
                border: none;
            
        """)

        title = QtWidgets.QLabel(name)
        title.setStyleSheet("""
            QLabel {
                font: bold 16px 'Segoe UI'; 
                color: #EEEEEE; 
                border: none;
                margin-bottom: 6px;
            }
        """)
        
        desc = QtWidgets.QLabel(description if description else "Нет описания")
        desc.setStyleSheet("""
            QLabel {
                font: 12px 'Segoe UI'; 
                color: #76ABAE; 
                border: none;
                border-color: white;
                margin-top: 4px;
                margin-bottom: 8px;
            }
        """)
        desc.setWordWrap(True)

        info_layout.addWidget(title)
        info_layout.addWidget(desc)
        info_layout.addStretch()

        # Блок с кнопкой и ценой
        button_price_frame = QtWidgets.QFrame()
        button_price_layout = QVBoxLayout(button_price_frame)
        button_price_layout.setContentsMargins(0, 0, 0, 0)
        button_price_layout.setSpacing(8)
        button_price_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_price_frame.setStyleSheet("""
                border: none;
        """)
        

        # Кнопка "Купить"
        buy_btn = QtWidgets.QPushButton("Купить")
        buy_btn.setStyleSheet("""
            QPushButton {
                background-color: #76ABAE;
                color: white;
                font: bold 12px 'Segoe UI';
                border-radius: 8px;
                padding: 10px 24px;
                min-width: 120px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5d8b8e;
            }
            QPushButton:pressed {
                background-color: #4a6d6f;
            }
        """)
        buy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        buy_btn.setFixedHeight(42)
        buy_btn.clicked.connect(lambda _, pid=product_id: self.add_to_cart(pid))

        # Цена
        price_value = f"{price:.2f}" if price is not None else "0.00"
        price_label = QtWidgets.QLabel(f"{price_value} руб.")
        price_label.setStyleSheet("""
            QLabel {
                font: bold 14px 'Segoe UI'; 
                color: #EEEEEE;
                margin-top: 0px;
            }
        """)
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Добавляем кнопку и цену
        button_price_layout.addWidget(buy_btn)
        button_price_layout.addWidget(price_label)
        button_price_layout.addStretch()

        # Добавляем все блоки в основной макет
        card_layout.addWidget(image_frame)
        card_layout.addWidget(info_frame, stretch=1)
        card_layout.addWidget(button_price_frame)

        self.scroll_layout.addWidget(product_block)

    def refresh_products(self):
        self.load_products()

    def exit(self):
        self.win.close()


    def show(self):
        self.win.show()

def main(user_info=None):

    loader = QUiLoader()
    app = QApplication(sys.argv)
    page = Product(user_info=user_info)
    page.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()




