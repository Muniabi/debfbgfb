import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QTableWidget, QTableWidgetItem, QPushButton, 
                            QMessageBox, QInputDialog, QLineEdit, QLabel, 
                            QComboBox, QFormLayout, QDialog, QTabWidget, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QIcon, QColor, QPalette
from PyQt5.QtGui import QFont
import psycopg2

class StyledMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.primary_bg = "#FFFFFF"  
        self.secondary_bg = "#BFD6F6"  
        self.accent_color = "#405C73" 
        self.text_color = "#333333"  
        
        self.setWindowTitle("Система управления производством")
        self.setWindowIcon(QIcon('Образ плюс.ico'))
        self.resize(1000, 700)
        
        
        self.setup_styles()
        
    def setup_styles(self):
        # Глобальные стили 
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.primary_bg};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.accent_color};
                background: {self.secondary_bg};
                border-radius: 4px;
                margin: 2px;
            }}
            QTabBar::tab {{
                background: {self.secondary_bg};
                color: {self.text_color};
                padding: 8px;
                border: 1px solid {self.accent_color};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: {self.primary_bg};
                color: {self.accent_color};
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {self.accent_color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #506C8B;
            }}
            QTableWidget {{
                background-color: {self.primary_bg};
                gridline-color: {self.secondary_bg};
                border: 1px solid {self.secondary_bg};
                selection-background-color: {self.accent_color};
                selection-color: white;
            }}
            QHeaderView::section {{
                background-color: {self.accent_color};
                color: white;
                padding: 4px;
                border: none;
            }}
            QLineEdit, QComboBox {{
                border: 1px solid {self.accent_color};
                border-radius: 3px;
                padding: 4px;
            }}
            QLabel {{
                color: {self.text_color};
            }}
        """)

class DatabaseManager:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname="obraz_plus_v2",
            user="postgres",
            password="toor",
            host="localhost"
        )
        self.cursor = self.connection.cursor()

    # Методы для работы с материалами
    def get_materials(self):
        self.cursor.execute("""
            SELECT m.material_id, m.material_name, mt.type_name, m.unit_price, 
                   m.quantity_in_stock, m.min_quantity, m.unit_of_measure
            FROM Materials m
            JOIN MaterialTypes mt ON m.material_type_id = mt.material_type_id
        """)
        return self.cursor.fetchall()

    def add_material(self, name, type_id, price, quantity, min_quantity, package_quantity, unit):
        self.cursor.execute(
            "INSERT INTO Materials (material_name, material_type_id, unit_price, quantity_in_stock, min_quantity, package_quantity, unit_of_measure) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, type_id, price, quantity, min_quantity, package_quantity, unit)
        )
        self.connection.commit()

    def update_material(self, material_id, name, type_id, price, quantity, min_quantity, package_quantity, unit):
        self.cursor.execute(
            "UPDATE Materials SET material_name=%s, material_type_id=%s, unit_price=%s, quantity_in_stock=%s, min_quantity=%s, package_quantity=%s, unit_of_measure=%s WHERE material_id=%s",
            (name, type_id, price, quantity, min_quantity, package_quantity, unit, material_id)
        )
        self.connection.commit()

    def delete_material(self, material_id):
        self.cursor.execute("DELETE FROM Materials WHERE material_id = %s", (material_id,))
        self.connection.commit()

    # Методы для работы с продукцией
    def get_products(self):
        self.cursor.execute("""
            SELECT p.product_id, p.product_name, pt.type_name, p.min_partner_price
            FROM Products p
            JOIN ProductTypes pt ON p.product_type_id = pt.product_type_id
        """)
        return self.cursor.fetchall()

    # Методы для работы с партнерами
    def get_partners(self):
        self.cursor.execute("SELECT partner_id, company_name, phone, email FROM Partners")
        return self.cursor.fetchall()

    def get_material_types(self):
        self.cursor.execute("SELECT material_type_id, type_name FROM MaterialTypes")
        return self.cursor.fetchall()

    def get_product_types(self):
        self.cursor.execute("SELECT product_type_id, type_name FROM ProductTypes")
        return self.cursor.fetchall()

    def get_products_by_material(self, material_id):
        self.cursor.execute("""
            SELECT p.product_name, mp.required_quantity 
            FROM MaterialProducts mp 
            JOIN Products p ON mp.product_id = p.product_id 
            WHERE mp.material_id = %s
        """, (material_id,))
        return self.cursor.fetchall()

class MaterialDialog(QDialog):
    def __init__(self, material=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить материал" if not material else "Редактировать материал")
        self.material = material
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # Поле наименования
        self.name_input = QLineEdit()
        layout.addRow("Наименование:", self.name_input)

        # Выбор типа материала
        self.type_combo = QComboBox()
        types = self.db.get_material_types()
        for type_id, type_name in types:
            self.type_combo.addItem(type_name, type_id)
        layout.addRow("Тип материала:", self.type_combo)

        # Поля с валидацией чисел
        self.price_input = QLineEdit()
        self.price_input.setValidator(QDoubleValidator(0, 999999, 2))
        layout.addRow("Цена единицы:", self.price_input)

        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator(0, 999999))
        layout.addRow("Количество на складе:", self.quantity_input)

        self.min_quantity_input = QLineEdit()
        self.min_quantity_input.setValidator(QIntValidator(0, 999999))
        layout.addRow("Минимальное количество:", self.min_quantity_input)

        self.package_input = QLineEdit()
        self.package_input.setValidator(QDoubleValidator(0, 999999, 2))
        layout.addRow("Количество в упаковке:", self.package_input)

        self.unit_input = QLineEdit()
        layout.addRow("Единица измерения:", self.unit_input)

        # Заполнение полей при редактировании
        if self.material:
            self.name_input.setText(self.material[1])
            self.type_combo.setCurrentIndex(self.type_combo.findData(self.material[2]))
            self.price_input.setText(str(self.material[3]))
            self.quantity_input.setText(str(self.material[4]))
            self.min_quantity_input.setText(str(self.material[5]))
            self.package_input.setText(str(self.material[6]))
            self.unit_input.setText(self.material[7])

        # Кнопка сохранения
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_material)
        layout.addRow(self.save_btn)

        self.setLayout(layout)

    def save_material(self):
        try:
            name = self.name_input.text()
            type_id = self.type_combo.currentData()
            price = float(self.price_input.text())
            quantity = int(self.quantity_input.text())
            min_quantity = int(self.min_quantity_input.text())
            package_quantity = float(self.package_input.text())
            unit = self.unit_input.text()

            if not name or not unit:
                raise ValueError("Не все обязательные поля заполнены")

            if self.material:
                self.db.update_material(
                    self.material[0], name, type_id, price, 
                    quantity, min_quantity, package_quantity, unit
                )
            else:
                self.db.add_material(
                    name, type_id, price, quantity, 
                    min_quantity, package_quantity, unit
                )
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить материал: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления производством")
        self.db = DatabaseManager()
        self.init_ui()
        self.resize(800, 600)

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Заголовок
        header = QLabel("Система управления производством 'Образ Плюс'")
        header.setStyleSheet(f"""
            QLabel {{
                color: {self.accent_color};
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::tab-bar {
                alignment: center;
            }
        """)
        
        # Вкладка материалов
        self.materials_tab = QWidget()
        self.init_materials_tab()
        self.tabs.addTab(self.materials_tab, "📦 Материалы")
        
        # Вкладка продукции
        self.products_tab = QWidget()
        self.init_products_tab()
        self.tabs.addTab(self.products_tab, "🛋️ Продукция")
        
        # Вкладка партнеров
        self.partners_tab = QWidget()
        self.init_partners_tab()
        self.tabs.addTab(self.partners_tab, "🤝 Партнеры")
        
        layout.addWidget(self.tabs)
        self.central_widget.setLayout(layout)
        
    def init_materials_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Таблица материалов
        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(7)
        self.materials_table.setHorizontalHeaderLabels(
            ["ID", "Наименование", "Тип", "Цена", "Количество", "Мин. количество", "Ед. измерения"]
        )
        self.materials_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.materials_table.verticalHeader().setVisible(False)
        layout.addWidget(self.materials_table)
        
        # Панель кнопок с иконками
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.clicked.connect(self.add_material)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.clicked.connect(self.edit_material)
        btn_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("❌ Удалить")
        self.delete_btn.clicked.connect(self.delete_material)
        btn_layout.addWidget(self.delete_btn)
        
        self.products_btn = QPushButton("🔍 Используется в")
        self.products_btn.clicked.connect(self.show_material_products)
        btn_layout.addWidget(self.products_btn)
        
        layout.addLayout(btn_layout)
        self.materials_tab.setLayout(layout)
        
        # Загрузка данных
        self.load_materials()
    
    def load_materials(self):
        materials = self.db.get_materials()
        self.materials_table.setRowCount(len(materials))
        for row, material in enumerate(materials):
            for col, value in enumerate(material):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.materials_table.setItem(row, col, item)
        self.materials_table.resizeColumnsToContents()
    
    def add_material(self):
        dialog = MaterialDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_materials()
    
    def edit_material(self):
        selected = self.materials_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите материал для редактирования")
            return
        
        material_id = int(self.materials_table.item(selected[0].row(), 0).text())
        materials = self.db.get_materials()
        material = next((m for m in materials if m[0] == material_id), None)
        
        if material:
            dialog = MaterialDialog(material)
            if dialog.exec_() == QDialog.Accepted:
                self.load_materials()
    
    def delete_material(self):
        selected = self.materials_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите материал для удаления")
            return
        
        material_id = int(self.materials_table.item(selected[0].row(), 0).text())
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить этот материал?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.delete_material(material_id)
            self.load_materials()
    
    def show_material_products(self):
        selected = self.materials_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите материал")
            return
        
        material_id = int(self.materials_table.item(selected[0].row(), 0).text())
        material_name = self.materials_table.item(selected[0].row(), 1).text()
        products = self.db.get_products_by_material(material_id)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Продукция, использующая {material_name}")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Продукция", "Количество"])
        table.setRowCount(len(products))
        
        for row, (product, quantity) in enumerate(products):
            table.setItem(row, 0, QTableWidgetItem(product))
            table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        
        table.resizeColumnsToContents()
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def init_products_tab(self):
        layout = QVBoxLayout()
        label = QLabel("Раздел продукции в разработке")
        layout.addWidget(label)
        self.products_tab.setLayout(layout)
    
    def init_partners_tab(self):
        layout = QVBoxLayout()
        label = QLabel("Раздел партнеров в разработке")
        layout.addWidget(label)
        self.partners_tab.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())