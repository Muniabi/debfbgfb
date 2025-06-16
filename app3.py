import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QTableWidget, QTableWidgetItem, QPushButton, 
                            QMessageBox, QInputDialog, QLineEdit, QLabel, 
                            QComboBox, QFormLayout, QDialog, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QIcon, QFont
import psycopg2

class DatabaseManager:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname="obraz_plus",
            user="postgres",
            password="toor",
            host="localhost"
        )
        self.cursor = self.connection.cursor()

    def get_materials(self):
        self.cursor.execute("SELECT * FROM Materials")
        return self.cursor.fetchall()

    def add_material(self, name, type_id, price, quantity, min_quantity, package_quantity, unit):
        self.cursor.execute(
            "INSERT INTO Materials (material_name, material_type_id, unit_price, quantity_in_stock, min_quantity, package_quantity, unit_of_measure) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, type_id, price, quantity, min_quantity, package_quantity, unit)
        )
        self.connection.commit()

    def update_material(self, material_id, name, type_id, price, quantity, min_quantity, package_quantity, unit):
        self.cursor.execute(
            "UPDATE Materials SET material_name = %s, material_type_id = %s, unit_price = %s, quantity_in_stock = %s, min_quantity = %s, package_quantity = %s, unit_of_measure = %s WHERE material_id = %s",
            (name, type_id, price, quantity, min_quantity, package_quantity, unit, material_id)
        )
        self.connection.commit()

    def delete_material(self, material_id):
        self.cursor.execute("DELETE FROM Materials WHERE material_id = %s", (material_id,))
        self.connection.commit()

    def get_material_types(self):
        self.cursor.execute("SELECT * FROM MaterialTypes")
        return self.cursor.fetchall()

    def get_products_by_material(self, material_id):
        self.cursor.execute(
            "SELECT p.product_name, mp.required_quantity FROM MaterialProducts mp JOIN Products p ON mp.product_id = p.product_id WHERE mp.material_id = %s",
            (material_id,)
        )
        return self.cursor.fetchall()

class MaterialDialog(QDialog):
    def __init__(self, material=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить/Редактировать материал" if not material else "Редактировать материал")
        self.setWindowIcon(QIcon('icon.png'))
        self.material = material
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #405C73;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                border: 1px solid #BFD6F6;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: #405C73;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #506C8B;
            }
        """)

        self.name_input = QLineEdit()
        layout.addRow("Наименование:", self.name_input)

        self.type_combo = QComboBox()
        types = self.db.get_material_types()
        for type_id, type_name, _ in types:
            self.type_combo.addItem(type_name, type_id)
        layout.addRow("Тип материала:", self.type_combo)

        self.price_input = QLineEdit()
        self.price_input.setValidator(QDoubleValidator())
        layout.addRow("Цена единицы:", self.price_input)

        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator())
        layout.addRow("Количество на складе:", self.quantity_input)

        self.min_quantity_input = QLineEdit()
        self.min_quantity_input.setValidator(QIntValidator())
        layout.addRow("Минимальное количество:", self.min_quantity_input)

        self.package_quantity_input = QLineEdit()
        self.package_quantity_input.setValidator(QDoubleValidator())
        layout.addRow("Количество в упаковке:", self.package_quantity_input)

        self.unit_input = QLineEdit()
        layout.addRow("Единица измерения:", self.unit_input)

        if self.material:
            self.name_input.setText(self.material[1])
            self.type_combo.setCurrentIndex(self.type_combo.findData(self.material[2]))
            self.price_input.setText(str(self.material[3]))
            self.quantity_input.setText(str(self.material[4]))
            self.min_quantity_input.setText(str(self.material[5]))
            self.package_quantity_input.setText(str(self.material[6]))
            self.unit_input.setText(self.material[7])

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_material)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def save_material(self):
        name = self.name_input.text()
        type_id = self.type_combo.currentData()
        price = float(self.price_input.text())
        quantity = int(self.quantity_input.text())
        min_quantity = int(self.min_quantity_input.text())
        package_quantity = float(self.package_quantity_input.text())
        unit = self.unit_input.text()

        if not name or not type_id or not price or not quantity or not min_quantity or not package_quantity or not unit:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        if self.material:
            self.db.update_material(self.material[0], name, type_id, price, quantity, min_quantity, package_quantity, unit)
        else:
            self.db.add_material(name, type_id, price, quantity, min_quantity, package_quantity, unit)

        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление материалами")
        self.setWindowIcon(QIcon('Образ плюс.ico'))
        self.db = DatabaseManager()
        self.init_ui()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QTableWidget {
                background-color: #FFFFFF;
                gridline-color: #BFD6F6;
                border: 1px solid #BFD6F6;
                selection-background-color: #405C73;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #405C73;
                color: white;
                padding: 4px;
                border: none;
            }
            QPushButton {
                background-color: #405C73;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #506C8B;
            }
        """)

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Наименование", "Тип", "Цена", "Количество", "Мин. количество", "Ед. измерения"])
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Добавить материал")
        self.add_button.clicked.connect(self.add_material)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Редактировать материал")
        self.edit_button.clicked.connect(self.edit_material)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить материал")
        self.delete_button.clicked.connect(self.delete_material)
        button_layout.addWidget(self.delete_button)

        self.products_button = QPushButton("Показать продукцию")
        self.products_button.clicked.connect(self.show_products)
        button_layout.addWidget(self.products_button)

        layout.addLayout(button_layout)
        self.central_widget.setLayout(layout)
        self.load_materials()

    def load_materials(self):
        materials = self.db.get_materials()
        self.table.setRowCount(len(materials))
        for row, material in enumerate(materials):
            for col, value in enumerate(material):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()

    def add_material(self):
        dialog = MaterialDialog()
        if dialog.exec_():
            self.load_materials()

    def edit_material(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите материал для редактирования!")
            return

        material_id = int(self.table.item(selected[0].row(), 0).text())
        materials = self.db.get_materials()
        material = next((m for m in materials if m[0] == material_id), None)

        if material:
            dialog = MaterialDialog(material)
            if dialog.exec_():
                self.load_materials()

    def delete_material(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите материал для удаления!")
            return

        material_id = int(self.table.item(selected[0].row(), 0).text())
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот материал?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_material(material_id)
            self.load_materials()

    def show_products(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите материал для просмотра продукции!")
            return

        material_id = int(self.table.item(selected[0].row(), 0).text())
        products = self.db.get_products_by_material(material_id)

        dialog = QDialog(self)
        dialog.setWindowTitle("Продукция, использующая материал")
        dialog.setWindowIcon(QIcon('icon.png'))
        dialog.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #405C73;
            }
        """)
        layout = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Продукция", "Необходимое количество"])
        table.setRowCount(len(products))
        table.verticalHeader().setVisible(False)

        for row, (product_name, quantity) in enumerate(products):
            table.setItem(row, 0, QTableWidgetItem(product_name))
            table.setItem(row, 1, QTableWidgetItem(str(quantity)))

        table.resizeColumnsToContents()
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Установка шрифта для всего приложения
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())