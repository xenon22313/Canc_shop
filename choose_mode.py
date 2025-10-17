import PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QSize, QFile
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QPushButton, QScrollArea, QLabel, QTableWidgetItem
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
import sys
import os
import pyodbc
import hashlib



class Choose_mode(QMainWindow):

    
    def __init__(self):
        super().__init__()
        
        loader = QUiLoader()                          
        ui_file = ('./ui/choose_mode.ui')    
        self.win = loader.load(ui_file)
        
        self.win.setMinimumSize(750, 580)
        self.win.setMaximumSize(750, 580)


        self.products_table = self.win.findChild(QTableWidget, "product_table")
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SingleSelection)

        self.products_table.setWordWrap(True)  # Включаем перенос текста
        self.products_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.products_table.resizeRowsToContents()
        
        # Кнопки
        self.add_btn = self.win.findChild(QtWidgets.QPushButton, "add_btn")
        self.change_btn = self.win.findChild(QtWidgets.QPushButton, "change_btn")
        self.del_btn = self.win.findChild(QtWidgets.QPushButton, "del_btn")

        self.add_btn.clicked.connect(self.add_prod)
        self.change_btn.clicked.connect(self.change_prod)
        self.del_btn.clicked.connect(self.del_prod)


        #self.ui.findChild(QPushButton, "refreshBtn").clicked.connect(self.load_products)
        #self.ui.findChild(QPushButton, "selectBtn").clicked.connect(self.select_product)
        
        # Загрузка данных
        self.connect()
        self.load_products()


    def load_products(self):
        try:
            self.products_table.setRowCount(0)  # Очищаем таблицу
            
            query = "SELECT id, name, description ,price, count, image_path  FROM product"
            self.cursor.execute(query)
            products = self.cursor.fetchall()
            
            for row_num, product in enumerate(products):
                self.products_table.insertRow(row_num)
                
                for col_num, value in enumerate(product):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # Запрет редактирования
                    self.products_table.setItem(row_num, col_num, item)
                    
                    
            # Устанавливаем заголовки
            headers = ["ID", "Название","Описание", "Цена", "Количество", "Фото"]
            self.products_table.setHorizontalHeaderLabels(headers)
            self.products_table.setWordWrap(True)  # Включаем перенос текста
            self.products_table.setTextElideMode(Qt.TextElideMode.ElideNone)
            self.products_table.resizeRowsToContents()
            
            
            
            
        except pyodbc.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки товаров: {str(e)}")

    #выбор товара
    def select_product(self):
        selected = self.products_table.currentRow()
        if selected >= 0:
            product_id = self.products_table.item(selected, 0).text()
            self.show_product_details(product_id)
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите товар из списка")



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

    def add_prod(self):
        from add_product import Add_product
        self.prod_win = Add_product()
        self.prod_win.show()
        self.win.close()

    def change_prod(self):
        selected_row = self.products_table.currentRow()
        if selected_row >= 0:
            product_id = self.products_table.item(selected_row, 0).text()
            print(product_id)  # Получаем ID из первого столбца
            
            from editing import Editing
            self.prod_win = Editing(product_id=product_id)  # Передаем ID в конструктор
            self.prod_win.show()
            self.win.close()
        else:
            QMessageBox.warning(self.win, "Ошибка", "Выберите товар для редактирования")

    def del_prod(self):
        selected_row = self.products_table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(self.win, "Ошибка", "Выберите товар для удаления")
            return
        
        product_id = self.products_table.item(selected_row, 0).text()
        product_name = self.products_table.item(selected_row, 1).text()
        
        # Запрос подтверждения
        reply = QMessageBox.question(
            self.win,
            "Подтверждение удаления",
            f"Вы действительно хотите удалить товар:\n{product_name} (ID: {product_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Проверяем подключение к БД
                if not hasattr(self, 'conn') or not self.conn:
                    self.connect()
                    if not hasattr(self, 'conn'):
                        return
                
                # Удаляем товар из БД
                query = "DELETE FROM product WHERE id = ?"
                self.cursor.execute(query, (product_id,))
                self.conn.commit()
                
                # Обновляем таблицу
                self.load_products()
                
                QMessageBox.information(
                    self.win,
                    "Успех",
                    "Товар успешно удален"
                )
                
            except pyodbc.Error as e:
                QMessageBox.critical(
                    self.win,
                    "Ошибка базы данных",
                    f"Не удалось удалить товар:\n{str(e)}"
                )
                self.conn.rollback()

    def show(self):
        self.win.show()

def main():

    loader = QUiLoader()
    app = QApplication(sys.argv)
    page = Choose_mode()
    page.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()