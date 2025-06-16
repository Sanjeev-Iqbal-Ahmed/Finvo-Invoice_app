from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTextEdit, QFormLayout, QSpinBox,
    QDoubleSpinBox, QStackedWidget, QFrame, QMessageBox
)
from PySide6.QtGui import QFont
from ..models.db_manager import add_inventory_item, initialize_database

class AddItems_Page(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize database on startup
        initialize_database()
        self.setup_ui()
        self.setWindowTitle("Add Items Page")
        
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
                border-radius: 3px;font-weight:600;
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
                font-weight:600;
            }
             QComboBox QAbstractItemView {
                background-color: white;
                font-weight:600;
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
        form_layout.addRow("Product Code:", self.product_code)
        
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
        
    def validate_form(self):
        """Validate form data before saving."""
        errors = []
        
        # Check required fields
        if not self.product_name.text().strip():
            errors.append("Product Name is required")
            
        if not self.product_code.text().strip():
            errors.append("Product Code is required")
            
        if not self.unit.text().strip():
            errors.append("Unit is required")
            
        # Check if selling price is not less than purchase price
        if self.selling_price.value() < self.purchase_price.value():
            errors.append("Selling price should not be less than purchase price")
            
        return errors
    
    def show_message(self, title, message, message_type="information"):
        """Show message box to user."""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if message_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif message_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
            
        msg_box.exec()
        
    def clear_form(self):
        """Clear all form fields."""
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
        """Save the inventory item to database."""
        # Validate form data
        errors = self.validate_form()
        if errors:
            error_message = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
            self.show_message("Validation Error", error_message, "warning")
            return
        
        # Get form data
        product_name = self.product_name.text().strip()
        product_code = self.product_code.text().strip()
        category = self.category.currentText()
        unit = self.unit.text().strip()
        quantity = self.quantity.value()
        purchase_price = self.purchase_price.value()
        selling_price = self.selling_price.value()
        gst_percentage = self.gst.currentText()
        description = self.description.toPlainText().strip()
        
        # Handle default category
        if category == "Default":
            category = "Other"
        
        # Save to database
        try:
            success = add_inventory_item(
                product_name=product_name,
                product_code=product_code,
                category=category,
                unit=unit,
                quantity=quantity,
                purchase_price=purchase_price,
                selling_price=selling_price,
                gst_percentage=gst_percentage,
                description=description
            )
            
            if success:
                self.show_message("Success", f"Item '{product_name}' has been added successfully!", "information")
                self.clear_form()  # Clear form after successful save
            else:
                self.show_message("Error", "Failed to save item. Product code might already exist.", "error")
                
        except Exception as e:
            self.show_message("Error", f"An error occurred while saving: {str(e)}", "error")