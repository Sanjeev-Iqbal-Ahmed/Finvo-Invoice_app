from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTextEdit, QFormLayout, QSpinBox,
    QDoubleSpinBox, QStackedWidget, QFrame
)
from PySide6.QtGui import QFont

class AddItemPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.setStyleSheet("""
            QWidget { 
                 background-color: #A6AEBF;
                color: #333333; font-weight:bold;
            }
            QLineEdit {
                background-color: #F8FAFC;
                border: 1px solid #cccccc;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            #pageHeader{
                font-weight:bold;
                font-size:16px;
            }
            #formContainer{
                background-color:#A6AEBF;
                font-weight:bold;
                color:black;font-size:12px;
            }
            QTextEdit, QSpinBox, QDoubleSpinBox,QComboBox {
                background-color: #F8FAFC;
               border: 1px solid #cccccc;
                padding: 5px;
                border-radius: 3px;
            }
            #clearButton {
                background-color: #666666;
                color: white;
            }
            #clearButton:hover {
                 background-color: #7a7a7a;
            }
            #clearButton:pressed {
                background-color: #4d4d4d;
            }
            #saveButton {
                background-color: #555599;
                color: white;
            }
            #saveButton:hover {
                background-color: #6666aa;
            }
            #saveButton:pressed {
                background-color: #333366;
            }""")


       # Header
        header_label = QLabel("Add New Inventory Item")
        header_label.setObjectName("pageHeader")
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Form container
        form_container = QFrame()
        form_container.setObjectName("formContainer")
        form_container.setFrameShape(QFrame.StyledPanel)
        form_container.setFrameShadow(QFrame.Raised)
        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Product Name
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Enter product name")
        form_layout.addRow("Product Name:", self.product_name)
        
        # Product Code 
        self.product_code = QLineEdit()
        self.product_code.setPlaceholderText("Enter product code ")
        form_layout.addRow("Product Code ", self.product_code)
        
        # Category
        self.category = QComboBox()
        self.category.addItems(["Default","Electronics", "Clothing", "Food", "Stationery", "Home Appliances", "Other"])
        form_layout.addRow("Category:", self.category)
        
        # Unit
        self.unit = QLineEdit()
        self.unit.setPlaceholderText("pcs/kg/box")
        form_layout.addRow("Unit:", self.unit)
        
        # Quantity in Stock
        self.quantity = QSpinBox()
        self.quantity.setRange(0, 100000)
        form_layout.addRow("Quantity in Stock:", self.quantity)
        
        # Purchase Price
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 1000000)
        self.purchase_price.setPrefix("₹ ")
        self.purchase_price.setDecimals(2)
        form_layout.addRow("Purchase Price (₹):", self.purchase_price)
        
        # Selling Price
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setRange(0, 1000000)
        self.selling_price.setPrefix("₹ ")
        self.selling_price.setDecimals(2)
        form_layout.addRow("Selling Price (₹):", self.selling_price)
        
        # GST %
        self.gst = QComboBox()
        self.gst.addItems(["None", "5%", "12%", "18%", "28%"])
        form_layout.addRow("GST % (optional):", self.gst)
        
        # Description
        self.description = QTextEdit()
        self.description.setPlaceholderText("Enter product description")
        self.description.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description)
        
        main_layout.addWidget(form_container)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        
        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("saveButton")
        self.save_button.setMinimumWidth(120)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setMinimumWidth(120)
        
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        # Connect signals
        self.clear_button.clicked.connect(self.clear_form)
        self.save_button.clicked.connect(self.save_item)
        
    def clear_form(self):
        self.product_name.clear()
        self.product_code.clear()
        self.category.setCurrentIndex(0)
        self.unit.clear()
        self.quantity.setValue(0)
        self.purchase_price.setValue(0)
        self.selling_price.setValue(0)
        self.gst.setCurrentIndex(0)
        self.description.clear()
        
    def save_item(self):
        # TODO: Implement save logic
        # This would typically involve validation and database operations
        pass

class InventoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create stacked widget for inventory pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create inventory main page
        self.inventory_main_page = QWidget()
        self.setup_inventory_main_page()
        self.stacked_widget.addWidget(self.inventory_main_page)
        
        # Create add item page
        self.add_item_page = AddItemPage()
        self.add_item_page.back_button.clicked.connect(self.show_inventory_main)
        self.stacked_widget.addWidget(self.add_item_page)
        
        # Set default page
        self.stacked_widget.setCurrentWidget(self.inventory_main_page)
        
    def setup_inventory_main_page(self):
        layout = QVBoxLayout(self.inventory_main_page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with title and add button
        header_layout = QHBoxLayout()
        header_label = QLabel("Inventory Management")
        header_label.setObjectName("pageHeader")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        header_label.setFont(font)
        
        self.add_item_button = QPushButton("Add New Item")
        self.add_item_button.setObjectName("primaryButton")
        self.add_item_button.clicked.connect(self.show_add_item)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_item_button)
        
        layout.addLayout(header_layout)
        
        # Placeholder for inventory list
        inventory_placeholder = QLabel("Inventory items will be displayed here")
        inventory_placeholder.setAlignment(Qt.AlignCenter)
        inventory_placeholder.setObjectName("placeholderText")
        layout.addWidget(inventory_placeholder)
        layout.addStretch()
    
    def show_add_item(self):
        self.stacked_widget.setCurrentWidget(self.add_item_page)
    
    def show_inventory_main(self):
        self.stacked_widget.setCurrentWidget(self.inventory_main_page)
