import PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QSize, QFile, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtWidgets import QGraphicsBlurEffect, QGraphicsDropShadowEffect, QGraphicsColorizeEffect, QGraphicsOpacityEffect
from PySide6.QtGui import QColor
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QPushButton, QScrollArea, QLabel
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QGridLayout


class AdvancedEffects:
    """Класс для продвинутых визуальных эффектов"""
    
    def __init__(self, widget):
        self.widget = widget
        self.blur_effect = QGraphicsBlurEffect()
        self.tint_effect = QGraphicsColorizeEffect()
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.opacity_effect = QGraphicsOpacityEffect()
        
        # Настройка эффектов
        self.setup_effects()
    
    def setup_effects(self):
        """Настройка базовых параметров эффектов"""
        # Эффект размытия
        self.blur_effect.setBlurRadius(0)
        
        # Эффект тонирования
        self.tint_effect.setColor(QColor(100, 150, 200, 30))
        self.tint_effect.setStrength(0.0)
        
        # Эффект тени
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setOffset(0, 5)
        self.shadow_effect.setColor(QColor(0, 0, 0, 50))
        
        # Эффект прозрачности
        self.opacity_effect.setOpacity(1.0)
    
    def apply_tinted_glass(self, blur_radius=15, tint_color=QColor(100, 150, 200, 30), tint_strength=0.8):
        """Применяет эффект тонированного стекла"""
        self.blur_effect.setBlurRadius(blur_radius)
        self.tint_effect.setColor(tint_color)
        self.tint_effect.setStrength(tint_strength)
        
        # Комбинируем эффекты
        self.widget.setGraphicsEffect(self.blur_effect)
    
    def animate_glass_effect(self, duration=500, blur_radius=20, tint_color=QColor(100, 150, 200, 80)):
        """Анимирует эффект тонированного стекла"""
        # Анимация размытия
        blur_animation = QPropertyAnimation(self.blur_effect, b"blurRadius")
        blur_animation.setDuration(duration)
        blur_animation.setStartValue(0)
        blur_animation.setEndValue(blur_radius)
        blur_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Анимация тонирования
        tint_animation = QPropertyAnimation(self.tint_effect, b"strength")
        tint_animation.setDuration(duration)
        tint_animation.setStartValue(0.0)
        tint_animation.setEndValue(0.9)
        tint_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Анимация прозрачности (меньше прозрачности для более сильного эффекта)
        opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        opacity_animation.setDuration(duration)
        opacity_animation.setStartValue(1.0)
        opacity_animation.setEndValue(0.95)
        opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        return [blur_animation, tint_animation, opacity_animation]
    
    def remove_glass_effect(self, duration=300):
        """Убирает эффект тонированного стекла"""
        # Анимация размытия обратно
        blur_animation = QPropertyAnimation(self.blur_effect, b"blurRadius")
        blur_animation.setDuration(duration)
        blur_animation.setStartValue(self.blur_effect.blurRadius())
        blur_animation.setEndValue(0)
        blur_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Анимация тонирования обратно
        tint_animation = QPropertyAnimation(self.tint_effect, b"strength")
        tint_animation.setDuration(duration)
        tint_animation.setStartValue(self.tint_effect.strength())
        tint_animation.setEndValue(0.0)
        tint_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Анимация прозрачности обратно
        opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        opacity_animation.setDuration(duration)
        opacity_animation.setStartValue(self.opacity_effect.opacity())
        opacity_animation.setEndValue(1.0)
        opacity_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        return [blur_animation, tint_animation, opacity_animation]
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
        self.auth_btn = self.win.findChild(QtWidgets.QPushButton, "auth_btn")
        
        # Проверяем, является ли пользователь гостем
        user_name = self.user_info.get("name", "Гость")
        
        if user_name == "Гость":
            # Для гостя: показываем кнопку авторизации, скрываем имя
            if self.username_label:
                self.username_label.setVisible(False)
            if self.auth_btn:
                self.auth_btn.setVisible(True)
                self.auth_btn.raise_()
                self.auth_btn.clicked.connect(self.show_login)
        else:
            # Для авторизованного пользователя: показываем имя, скрываем кнопку
            if self.username_label:
                self.username_label.setText(user_name)
                self.username_label.setVisible(True)
            if self.auth_btn:
                self.auth_btn.setVisible(False)

        self.trash_btn = self.win.findChild(QtWidgets.QPushButton, "trash_btn")
        self.trash_btn.clicked.connect(self.change_to_trash)

        # Инициализация поиска
        self.search_edit = self.win.findChild(QtWidgets.QLineEdit, "search")
        if self.search_edit:
            self.search_edit.textChanged.connect(self.on_search_changed)

        # Инициализация сворачивания панели
        self.collapse_btn = self.win.findChild(QtWidgets.QPushButton, "collapse_btn")
        if self.collapse_btn:
            self.collapse_btn.clicked.connect(self.toggle_sidebar)
            # Кнопка сворачивания остается с оригинальным стилем
        
        # Состояние панели (развернута/свернута)
        self.sidebar_expanded = True
        self.sidebar_width_expanded = 250
        self.sidebar_width_collapsed = 50
        
        # Инициализация панели категорий (дизайн в UI файле)
        self.sidebar_panel = self.win.findChild(QtWidgets.QLabel, "label_33")
        
        # Инициализация верхней панели (дизайн в UI файле)
        self.top_panel = self.win.findChild(QtWidgets.QLabel, "label_2")
        
        # Анимация для панели
        self.sidebar_animation = QPropertyAnimation(self.win.findChild(QtWidgets.QLabel, "label_33"), b"geometry")
        self.sidebar_animation.setDuration(500)
        self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # Анимация для кнопки сворачивания
        self.button_animation = QPropertyAnimation(self.collapse_btn, b"geometry")
        self.button_animation.setDuration(500)
        self.button_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # Анимации для элементов панели
        self.element_animations = []
        self.element_animations_duration = 400

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
        self.admin_btn = self.win.findChild(QPushButton, "admin_btn")
        
        # Стили кнопок управляются через UI файл  

        self.exit_btn.clicked.connect(self.exit)
        
        # Проверяем роль пользователя для отображения кнопки администратора
        user_role = self.user_info.get("role", None)
        if self.admin_btn:
            if user_role == 'admin':
                self.admin_btn.setVisible(True)
                self.admin_btn.clicked.connect(self.show_admin_panel)
            else:
                self.admin_btn.setVisible(False)

        # обработчики
        self.pencils_btn.clicked.connect(lambda: (
            
            self.set_current_filter("MacBook Pro"),
            self.load_products(name_filter="MacBook Pro")
        ))
        self.pens_btn.clicked.connect(lambda: (
            self.set_current_filter("MacBook Air"),
            self.load_products(name_filter="MacBook Air")
        ))
        self.sharpener_btn.clicked.connect(lambda: (
            self.set_current_filter("iPhone 17"),
            self.load_products(name_filter="iPhone 17")
        ))
        self.paint_btn.clicked.connect(lambda: (
            self.set_current_filter("iPhone 16"),
            self.load_products(name_filter="iPhone 16")
        ))
        self.all_btn.clicked.connect(lambda: (
            self.set_current_filter(None),
            self.load_products()            
        ))

        self.scroll_area = self.win.findChild(QScrollArea, 'product_table')
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # виджет-контейнер для карточек (сетка 4 в ширину)
        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(16)
        # Вычисляем симметричные отступы для центрирования
        # Считаем, что панель свёрнута и не занимает место (или минимально)
        sidebar_width_collapsed = 50  # Ширина свёрнутой панели
        card_width = 216
        card_spacing = 16
        cards_per_row = 4
        total_cards_width = (card_width * cards_per_row) + (card_spacing * (cards_per_row - 1))
        available_width = 1280 - sidebar_width_collapsed
        horizontal_margin = (available_width - total_cards_width) // 2
        
        self.scroll_layout.setContentsMargins(sidebar_width_collapsed + horizontal_margin, 16, horizontal_margin, 16)
        self.current_row = 0
        self.current_col = 0
        self.max_cols = 4  # 4 колонки

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
        
        # Убедиться, что все элементы боковой панели видны
        self.ensure_sidebar_visible()
        
        # Организация слоев (z-index)
        self.organize_layers()
        




    def ensure_sidebar_visible(self):
        """Убедиться, что все элементы боковой панели видны"""
        # Контейнеры с кнопками
        vertical_layout_widget = self.win.findChild(QtWidgets.QWidget, "verticalLayoutWidget")
        vertical_layout_widget_2 = self.win.findChild(QtWidgets.QWidget, "verticalLayoutWidget_2")
        app_title = self.win.findChild(QtWidgets.QLabel, "app_title")
        
        if vertical_layout_widget:
            vertical_layout_widget.setVisible(True)
            vertical_layout_widget.show()
        if vertical_layout_widget_2:
            vertical_layout_widget_2.setVisible(True)
            vertical_layout_widget_2.show()
        if app_title:
            app_title.setVisible(True)
            app_title.show()
        
        # Все кнопки на панели
        buttons = [
            self.pencils_btn,
            self.pens_btn,
            self.sharpener_btn,
            self.paint_btn,
            self.all_btn,
            self.exit_btn,
            self.sort_abc,
            self.sort_cba
        ]
        
        for button in buttons:
            if button:
                button.setVisible(True)
                button.show()

    def organize_layers(self):
        """Организация слоев элементов в правильном порядке"""
        # 1. Карточки товаров (самый нижний слой)
        if hasattr(self, 'scroll_content'):
            self.scroll_content.lower()
        
        # 2. Выдвигающаяся панель (средний слой)
        if hasattr(self, 'sidebar_panel'):
            self.sidebar_panel.raise_()
        
        # 3. Контейнеры с кнопками на панели
        vertical_layout_widget = self.win.findChild(QtWidgets.QWidget, "verticalLayoutWidget")
        vertical_layout_widget_2 = self.win.findChild(QtWidgets.QWidget, "verticalLayoutWidget_2")
        app_title = self.win.findChild(QtWidgets.QLabel, "app_title")
        
        if vertical_layout_widget:
            vertical_layout_widget.raise_()
            vertical_layout_widget.show()
        if vertical_layout_widget_2:
            vertical_layout_widget_2.raise_()
            vertical_layout_widget_2.show()
        if app_title:
            app_title.raise_()
            app_title.show()
        
        # 4. Кнопки на панели (самый верхний слой)
        buttons_to_raise = [
            self.collapse_btn,
            self.pencils_btn,
            self.pens_btn, 
            self.sharpener_btn,
            self.paint_btn,
            self.all_btn,
            self.exit_btn,
            self.sort_abc,
            self.sort_cba
        ]
        
        # Добавляем admin_btn только если пользователь - администратор
        user_role = self.user_info.get("role", None)
        if user_role == 'admin' and self.admin_btn:
            buttons_to_raise.append(self.admin_btn)
        
        for button in buttons_to_raise:
            if button:
                button.raise_()
                button.show()
        
        # Явно скрываем admin_btn для не-администраторов
        user_role = self.user_info.get("role", None)
        if self.admin_btn:
            if user_role != 'admin':
                self.admin_btn.setVisible(False)
                self.admin_btn.hide()
        
        # 5. Другие элементы интерфейса (верхний слой)
        ui_elements_to_raise = [
            self.search_edit,
            self.trash_btn
        ]
        
        for element in ui_elements_to_raise:
            if element:
                element.raise_()
        
        # 6. Кнопка авторизации (если пользователь - гость)
        if self.auth_btn and self.auth_btn.isVisible():
            self.auth_btn.raise_()

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
        # Сбрасываем позицию для сетки
        self.current_row = 0
        self.current_col = 0

    def create_product_card(self, product_id, name, price, description, image_path=None):
       
        # Основной блок продукта
        product_block = QtWidgets.QFrame()
        product_block.setObjectName("product_card")  # Устанавливаем objectName для стилизации
        product_block.setFixedSize(216, 320)

        # Основной макет карточки (вертикальный для сетки)
        card_layout = QVBoxLayout(product_block)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(10)

        # Блок с изображением (с отступом внутри карточки)
        image_frame = QtWidgets.QFrame()
        image_frame.setObjectName("product_image")
        image_frame.setFixedSize(200, 150)
        
        image_label = QtWidgets.QLabel(image_frame)
        
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
        else:
            pixmap = QPixmap(r'.\src\img\331d7bf29f945f874edb70410d4ed345.jpg')
            
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setGeometry(0, 0, 200, 150)
        image_label.setScaledContents(True)

        # Блок с информацией
        info_frame = QtWidgets.QFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(10)

        title = QtWidgets.QLabel(name)
        title.setObjectName("product_title")

        info_layout.addWidget(title)

        # Блок с кнопкой и ценой
        button_price_frame = QtWidgets.QFrame()
        button_price_layout = QVBoxLayout(button_price_frame)
        button_price_layout.setContentsMargins(0, 0, 0, 0)
        button_price_layout.setSpacing(8)
        button_price_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

        # Кнопка "Купить"
        buy_btn = QtWidgets.QPushButton("Купить")
        buy_btn.setObjectName("buy_button")
        buy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        buy_btn.setFixedHeight(42)
        buy_btn.clicked.connect(lambda _, pid=product_id: self.add_to_cart(pid))

        # Цена
        price_value = f"{price:.2f}" if price is not None else "0.00"
        price_label = QtWidgets.QLabel(f"{price_value} руб.")
        price_label.setObjectName("product_price")
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Добавляем кнопку и цену
        button_price_layout.addWidget(buy_btn)
        button_price_layout.addWidget(price_label)

        # Добавляем все блоки в основной макет (вертикально для сетки)
        card_layout.addWidget(image_frame)
        card_layout.addWidget(info_frame)
        card_layout.addWidget(button_price_frame)

        # Добавляем карточку в сетку
        self.scroll_layout.addWidget(product_block, self.current_row, self.current_col)
        
        # Убеждаемся, что карточка находится в нижнем слое
        product_block.lower()
        
        # Обновляем позицию для следующей карточки
        self.current_col += 1
        if self.current_col >= self.max_cols:  # 4 карточки в ряд
            self.current_col = 0
            self.current_row += 1

    def refresh_products(self):
        self.load_products()

    def on_search_changed(self):
        """Обработка изменений в поле поиска"""
        search_text = self.search_edit.text().strip()
        if search_text:
            self.load_products(name_filter=search_text)
        else:
            self.load_products(name_filter=self.current_filter)

    def toggle_sidebar(self):
        """Переключение состояния панели категорий"""
        if not self.collapse_btn:
            print("Кнопка сворачивания не найдена!")
            return  # Если кнопка не найдена, не выполняем анимацию
            
        print(f"Переключение панели. Текущее состояние: {self.sidebar_expanded}")
        if self.sidebar_expanded:
            self.collapse_sidebar()
        else:
            self.expand_sidebar()

    def collapse_sidebar(self):
        """Сворачивание панели"""
        print("Начинаем сворачивание панели")
        self.sidebar_expanded = False
        
        # Сначала скрыть элементы панели
        self.hide_sidebar_elements()
        
        # Изменить иконку кнопки
        self.collapse_btn.setText("▶")
        
        # Анимация панели с задержкой
        QTimer.singleShot(200, self.start_collapse_animation)
    
    def start_collapse_animation(self):
        """Запуск анимации сворачивания панели"""
        print("Запускаем анимацию сворачивания")
        # Анимация панели
        self.sidebar_animation.setStartValue(self.win.findChild(QtWidgets.QLabel, "label_33").geometry())
        self.sidebar_animation.setEndValue(QtCore.QRect(0, 50, self.sidebar_width_collapsed, 671))
        self.sidebar_animation.start()
        
        # Анимация кнопки (переместить влево, чтобы остаться видимой)
        self.button_animation.setStartValue(self.collapse_btn.geometry())
        self.button_animation.setEndValue(QtCore.QRect(25, 315, 20, 40))  # x=25 для свернутой панели, y=315 по центру
        self.button_animation.start()
        
        # Убеждаемся, что кнопка остается на верхнем слое
        self.collapse_btn.raise_()
        
        # Анимация области товаров
        self.animate_content_area(True)

    def expand_sidebar(self):
        """Разворачивание панели"""
        print("Начинаем разворачивание панели")
        self.sidebar_expanded = True
        
        # Анимация панели
        self.sidebar_animation.setStartValue(self.win.findChild(QtWidgets.QLabel, "label_33").geometry())
        self.sidebar_animation.setEndValue(QtCore.QRect(0, 50, self.sidebar_width_expanded, 671))
        self.sidebar_animation.start()
        
        # Анимация кнопки (переместить вправо, на правый край развернутой панели)
        self.button_animation.setStartValue(self.collapse_btn.geometry())
        self.button_animation.setEndValue(QtCore.QRect(220, 315, 20, 40))  # x=220 для развернутой панели, y=315 по центру
        self.button_animation.start()
        
        # Убеждаемся, что кнопка остается на верхнем слое
        self.collapse_btn.raise_()
        
        # Изменить иконку кнопки
        self.collapse_btn.setText("◀")
        
        # Анимация области товаров
        self.animate_content_area(False)
        
        # Показать элементы панели с задержкой
        QTimer.singleShot(300, self.show_sidebar_elements)

    def hide_sidebar_elements(self):
        """Плавно скрыть элементы панели"""
        elements_to_hide = [
            self.win.findChild(QtWidgets.QLabel, "app_title"),
            self.win.findChild(QtWidgets.QWidget, "verticalLayoutWidget"),
            self.win.findChild(QtWidgets.QWidget, "verticalLayoutWidget_2"),
            self.win.findChild(QtWidgets.QPushButton, "exit_btn")
        ]
        
        # Очистить предыдущие анимации
        for anim in self.element_animations:
            anim.stop()
        self.element_animations.clear()
        
        # Анимация сжатия и исчезновения элементов (одновременно)
        for element in elements_to_hide:
            if element:
                self.animate_element_hide(element)

    def animate_element_hide(self, element):
        """Анимация скрытия отдельного элемента"""
        if element:
            # Анимация сжатия по ширине
            anim = QPropertyAnimation(element, b"geometry")
            
            # Ускорить только элементы категорий
            if "verticalLayoutWidget" in element.objectName():
                anim.setDuration(200)  # Быстрее для категорий
            else:
                anim.setDuration(self.element_animations_duration)  # Обычная скорость для остальных
                
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            
            # Текущая геометрия
            current_geom = element.geometry()
            
            # Элемент "уезжает" влево за границу панели
            anim.setStartValue(current_geom)
            anim.setEndValue(QtCore.QRect(-current_geom.width(), current_geom.y(), current_geom.width(), current_geom.height()))
            
            # Скрыть элемент после анимации
            anim.finished.connect(lambda: element.hide())
            
            anim.start()
            self.element_animations.append(anim)

    def show_sidebar_elements(self):
        """Плавно показать элементы панели"""
        elements_to_show = [
            self.win.findChild(QtWidgets.QLabel, "app_title"),
            self.win.findChild(QtWidgets.QWidget, "verticalLayoutWidget"),
            self.win.findChild(QtWidgets.QWidget, "verticalLayoutWidget_2"),
            self.win.findChild(QtWidgets.QPushButton, "exit_btn")
        ]
        
        # Очистить предыдущие анимации
        for anim in self.element_animations:
            anim.stop()
        self.element_animations.clear()
        
        # Сначала показать элементы за левой границей панели
        for element in elements_to_show:
            if element:
                current_geom = element.geometry()
                # Элементы начинают за левой границей панели
                element.setGeometry(QtCore.QRect(-current_geom.width(), current_geom.y(), current_geom.width(), current_geom.height()))
                element.show()
        
        # Анимация расширения элементов (одновременно)
        for element in elements_to_show:
            if element:
                self.animate_element_show(element)

    def animate_element_show(self, element):
        """Анимация показа отдельного элемента"""
        if element:
            # Анимация "въезда" элемента
            anim = QPropertyAnimation(element, b"geometry")
            
            # Ускорить только элементы категорий
            if "verticalLayoutWidget" in element.objectName():
                anim.setDuration(200)  # Быстрее для категорий
            else:
                anim.setDuration(self.element_animations_duration)  # Обычная скорость для остальных
                
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            
            # Текущая геометрия (за левой границей)
            current_geom = element.geometry()
            
            # Получить оригинальную позицию и размеры
            if "app_title" in element.objectName():
                original_x = 10
                original_width = 230
            elif "verticalLayoutWidget" in element.objectName():
                original_x = 30
                original_width = 190
            elif "verticalLayoutWidget_2" in element.objectName():
                original_x = 30
                original_width = 190
            elif "exit_btn" in element.objectName():
                original_x = 65
                original_width = 121
            else:
                original_x = 10
                original_width = 190
                
            # Ограничить ширину размером панели
            max_width = self.sidebar_width_expanded - 20  # отступ от краев
            original_width = min(original_width, max_width)
            
            # Элемент "въезжает" в свою позицию
            anim.setStartValue(current_geom)
            anim.setEndValue(QtCore.QRect(original_x, current_geom.y(), original_width, current_geom.height()))
            
            anim.start()
            self.element_animations.append(anim)

    def animate_content_area(self, collapsed):
        """Анимация области товаров - карточки остаются на месте без размытия"""
        # Карточки товаров остаются на своих местах без размытия
        # Панель категорий просто перекрывает их при разворачивании
        pass
    
    # def apply_blur_effect(self, should_blur):
    #     """Применяет эффект размытия к карточкам товаров, которые находятся за панелью"""
    #     # Функция отключена - размытие карточек убрано по запросу пользователя
    #     pass

    def show_login(self):
        """Открыть окно авторизации"""
        from login import Login
        self.login_win = Login()
        self.login_win.show()
        self.win.close()

    def show_admin_panel(self):
        """Открыть панель администратора"""
        from choose_mode import Choose_mode
        self.admin_win = Choose_mode()
        self.admin_win.show()
        self.win.close()

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




