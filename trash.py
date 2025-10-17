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

from session import session

class TrashWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)  # Важно передать parent в родительский класс
        self.parent_window = parent 
        
    

        # Загрузка UI
        loader = QUiLoader()                          
        ui_file = ('./ui/trash.ui')    
        self.win = loader.load(ui_file)

        if not self.connect():
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка",
                "Не удалось подключиться к базе данных"
            )
            return
        
        
        # Настройка ScrollArea
        self.scroll_area = self.win.findChild(QScrollArea, "product_area")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        
        # Кнопка оформления заказа
        self.buy_btn = self.win.findChild(QPushButton, "buy_btn")
        self.buy_btn.clicked.connect(self.process_order)

        self.back_btn = self.win.findChild(QPushButton, "back_btn")
        self.back_btn.clicked.connect(self.return_to_products)
        
        # Метка для суммы
        self.sum_label = self.win.findChild(QLabel, "sum_pay")
        

        
        # Загрузка товаров в корзину
        self.load_cart_items()
        self.update_total_sum()

    def return_to_products(self):
          # Проверяем наличие родительского окна
        self.parent().show()  # Показываем родительское окно
        self.win.close()

    def clear_cart_ui(self):
        """Очистка UI корзины"""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

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

    def load_cart_items(self):
        """Загрузка товаров из корзины"""
        try:
            # 1. Очистка предыдущих данных
            self.clear_cart_ui()
            self.cart_items = {}  # Используем словарь для хранения товаров
            
            # 2. Проверка соединения
            if not hasattr(self, 'cursor') or not self.cursor:
                print("Ошибка: Курсор не инициализирован")
                return

            # 3. Получаем товары из корзины пользователя
            query = """
            SELECT 
                p.id, 
                p.name, 
                p.price, 
                c.quantity, 
                COALESCE(p.image_path, './src/img/fon_reg_aut.jpg') as image_path
            FROM cart c
            JOIN product p ON c.product_id = p.id
            WHERE c.user_id = ?
            """
            self.cursor.execute(query, (session.id,))
            items = self.cursor.fetchall()
            
            print(f"Загружено товаров из БД: {len(items)}")  # Отладочный вывод
            
            if not items:
                label = QLabel("Корзина пуста")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("font: 14pt 'Segoe UI'; color: #888;")
                self.scroll_layout.addWidget(label)
                return

            # 4. Добавляем товары в интерфейс
            for item in items:
                product_id, name, price, quantity, image_path = item
                print(f"Добавляем товар: {name} (ID: {product_id})")  # Отладочный вывод
                
                cart_item = {
                    'id': product_id,
                    'name': name,
                    'price': float(price),
                    'quantity': quantity,
                    'image': image_path
                }
                self.cart_items[product_id] = cart_item
                self.add_cart_item(cart_item)

            # 5. Обновляем общую сумму
            self.update_total_sum()

        except pyodbc.Error as e:
            error_msg = f"Ошибка БД при загрузке корзины: {str(e)}"
            print(error_msg)
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка базы данных",
                error_msg
            )
        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            print(error_msg)
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка",
                error_msg
            )
    def add_cart_item(self, item):
        # Основной фрейм
        item_frame = QFrame()
        item_frame.setStyleSheet("""
            background-color: #31363F;
            border-radius: 10px;
            border: none;
        """)
        item_frame.setFixedHeight(120)

        # Горизонтальный layout
        layout = QHBoxLayout(item_frame)
        layout.setContentsMargins(15, 15, 15, 15)

        # Изображение товара
        image_label = QLabel()
        pixmap = QPixmap(item["image"]).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio) if item.get("image") else QPixmap()
        image_label.setPixmap(pixmap)
        image_label.setFixedSize(80, 80)

        # Информация о товаре
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_widget.setStyleSheet("""
        border: none;
        """)
        
        name_label = QLabel(item["name"])
        name_label.setStyleSheet("font: bold 12pt 'Segoe UI'; border: none; color: white;")
        
        # Блок с количеством и ценой
        quantity_widget = QWidget()
        quantity_layout = QHBoxLayout(quantity_widget)
        quantity_layout.setContentsMargins(0, 0, 0, 0)
        quantity_widget.setStyleSheet("""
        border: none;
        """)
        
        # Кнопка уменьшения
        minus_btn = QPushButton("-")
        minus_btn.setFixedSize(25, 25)
        minus_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # Поле количества
        quantity_spin = QSpinBox()
        quantity_spin.setValue(item["quantity"])
        quantity_spin.setRange(1, 99)
        quantity_spin.setFixedWidth(50)
        quantity_spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        quantity_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 2px;
                color: white;
            }
        """)
        
        # Кнопка увеличения
        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(25, 25)
        plus_btn.setStyleSheet(minus_btn.styleSheet())
        
        # Цена и общая сумма
        price_layout = QHBoxLayout()
        price_label = QLabel(f"Цена: {item['price']:.2f} руб.")
        price_label.setStyleSheet("font: 10pt 'Segoe UI'; color: white; border: none;")
        
        total_label = QLabel(f"Сумма: {item['price'] * item['quantity']:.2f} руб.")
        total_label.setStyleSheet("font: 10pt 'Segoe UI'; color: white; font-weight: bold; border: none;")
        
        # Добавляем элементы в layout
        quantity_layout.addWidget(minus_btn)
        quantity_layout.addWidget(quantity_spin)
        quantity_layout.addWidget(plus_btn)
        quantity_layout.addSpacing(20)
        quantity_layout.addWidget(price_label)
        quantity_layout.addWidget(total_label)
        quantity_layout.addStretch()
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(quantity_widget)

        # Кнопка удаления
        delete_btn = QPushButton("Удалить")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff3333;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                border:none;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        delete_btn.setFixedSize(80, 30)

        # Добавляем элементы в основной layout
        layout.addWidget(image_label)
        layout.addWidget(info_widget, stretch=1)
        layout.addWidget(delete_btn)

        # Подключаем сигналы
        minus_btn.clicked.connect(lambda: self.change_quantity(item["id"], -1, total_label))
        plus_btn.clicked.connect(lambda: self.change_quantity(item["id"], 1, total_label))
        quantity_spin.valueChanged.connect(lambda v: self.set_quantity(item["id"], v, total_label))
        delete_btn.clicked.connect(lambda: self.remove_item(item["id"]))

        # Сохраняем ссылки на нужные виджеты
        item["widgets"] = {
            "spin": quantity_spin,
            "total_label": total_label
        }

        # Добавляем карточку в ScrollArea
        self.scroll_layout.addWidget(item_frame)

    def change_quantity(self, item_id, delta, total_label):
        try:
            # Проверяем наличие товара в корзине
            if item_id not in self.cart_items:
                print(f"Товар с ID {item_id} не найден в корзине")
                return

            item = self.cart_items[item_id]
            new_quantity = item["quantity"] + delta

            if 1 <= new_quantity <= 99:
                update_query = """
                UPDATE cart 
                SET quantity = ? 
                WHERE user_id = ? AND product_id = ?
                """
                self.cursor.execute(update_query, (new_quantity, session.id, item_id))
                self.conn.commit()
                
                item["quantity"] = new_quantity
                if "widgets" in item:
                    item["widgets"]["spin"].setValue(new_quantity)
                    if total_label:  
                        total_label.setText(f"Сумма: {item['price'] * new_quantity:.2f} руб.")
                
                self.update_total_sum()
                
        except pyodbc.Error as e:
            print(f"Ошибка БД при изменении количества: {e}")
            if self.conn:
                self.conn.rollback()
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")

    def set_quantity(self, item_id, value, total_label):
        if item_id in self.cart_items:
            item = self.cart_items[item_id]
            item["quantity"] = value
            self.update_item_total(item)
            self.update_total_sum()

    def update_item_total(self, item):
        total = item["price"] * item["quantity"]
        item["widgets"]["total_label"].setText(f"Сумма: {total:.2f} руб.")


        

    def remove_item(self, item_id):
        try:
            if item_id in self.cart_items:
                # Удаляем из БД
                delete_query = "DELETE FROM cart WHERE user_id = ? AND product_id = ?"
                self.cursor.execute(delete_query, (session.id, item_id))
                self.conn.commit()
                
                # Удаляем из локальных данных
                del self.cart_items[item_id]
                self.load_cart_items()
                
        except pyodbc.Error as e:
            print(f"Ошибка БД при удалении товара: {e}")
            if self.conn:
                self.conn.rollback()

    def update_total_sum(self):
        try:
            total = sum(
                item["price"] * item["quantity"] 
                for item in self.cart_items.values()
            )
            self.sum_label.setText(
                f'<html><head/><body><p><span style=" font-size:18pt; color:white;">{total:.2f}</span></p></body></html>'
            )
        except Exception as e:
            print(f"Ошибка расчета общей суммы: {e}")

    def process_order(self):
        try:
            if not self.cart_items or not isinstance(self.cart_items, dict):
                QtWidgets.QMessageBox.warning(
                    self.win,
                    "Ошибка",
                    "Невозможно оформить пустой заказ"
                )
                return

            for item_id, item in self.cart_items.items():
                self.cursor.execute(
                    "SELECT count FROM product WITH (UPDLOCK) WHERE id = ?", 
                    (item_id,)
                )
                available = self.cursor.fetchone()
                
                if not available:
                    raise Exception(f"Товар с ID {item_id} не найден")
                if available[0] < item['quantity']:
                    raise Exception(
                        f"Недостаточно товара '{item['name']}'. Доступно: {available[0]}, требуется: {item['quantity']}"
                    )

            for item_id, item in self.cart_items.items():
                update_query = """
                UPDATE product 
                SET count = count - ? 
                WHERE id = ?
                """
                self.cursor.execute(update_query, (item['quantity'], item_id))

            clear_query = "DELETE FROM cart WHERE user_id = ?"
            self.cursor.execute(clear_query, (session.id,))

            self.conn.commit()

            self.cart_items = {}
            self.load_cart_items()
            self.update_total_sum()

            QtWidgets.QMessageBox.information(
                self.win,
                "Успех",
                "Заказ успешно оформлен!"
            )

        except pyodbc.Error as e:
            self.conn.rollback()
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка БД",
                f"Не удалось оформить заказ:\n{str(e)}"
            )
        except Exception as e:
            self.conn.rollback()
            QtWidgets.QMessageBox.critical(
                self.win,
                "Ошибка",
                str(e) 
            )
    def show(self):
        self.win.show()

def main():
    loader = QUiLoader()
    app = QApplication(sys.argv)
    window = TrashWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()