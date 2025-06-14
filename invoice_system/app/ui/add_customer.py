from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTextEdit, QFormLayout, QSpinBox,
    QDoubleSpinBox, QStackedWidget, QFrame, QMessageBox
)
from PySide6.QtGui import QFont
from..models.db_manager import create_tables,save_customer,update_customer,get_all_customers,delete_customer

class Add_Customer(QWidget):
    # Signal to notify when customer is saved
    customer_saved = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setWindowTitle("Add Customer Page")
        
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
                font-weight:normal;
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
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
                border-radius: 3px;
                font-weight:normal;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: black;
                selection-color: white;
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
        header_label = QLabel("Add New Customer")
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
        
        # Customer Name
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Enter customer name")
        form_layout.addRow("Customer Name:", self.customer_name)
        
        # Address
        self.address = QTextEdit()
        self.address.setPlaceholderText("Enter customer address")
        self.address.setMaximumHeight(100)
        form_layout.addRow("Address:", self.address)
        
        # State
        self.state = QComboBox()
        indian_states = [
            "Select State", "Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
            "Chandigarh", "Chhattisgarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Goa", 
            "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", 
            "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", 
            "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", 
            "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ]
        self.state.addItems(indian_states)
        form_layout.addRow("State:", self.state)
        
        # State Code
        self.state_code = QLineEdit()
        self.state_code.setPlaceholderText("Enter state code (e.g., 18 for Assam)")
        form_layout.addRow("State Code:", self.state_code)
        
        # GSTIN
        self.gstin = QLineEdit()
        self.gstin.setPlaceholderText("Enter GSTIN (optional)")
        self.gstin.setMaxLength(15)  # GSTIN is 15 characters
        form_layout.addRow("GSTIN:", self.gstin)
        
        # Phone Number
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Enter phone number")
        self.phone.setMaxLength(15)
        form_layout.addRow("Phone Number:", self.phone)
        
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
        self.save_button.clicked.connect(self.save_customer)
        self.gstin.textChanged.connect(self.validate_gstin_format)
        
    def validate_gstin_format(self, text):
        """Validate GSTIN format as user types."""
        # GSTIN format: 2 digits (state code) + 10 characters (PAN) + 1 digit + 1 character + 1 digit
        if text and len(text) >= 2:
            # Auto-fill state code from GSTIN if valid
            try:
                gstin_state_code = text[:2]
                if gstin_state_code.isdigit():
                    self.state_code.setText(gstin_state_code)
            except:
                pass
    
    def validate_form(self):
        """Validate form data before saving."""
        errors = []
        
        # Check required fields
        if not self.customer_name.text().strip():
            errors.append("Customer Name is required")
            
        if not self.address.toPlainText().strip():
            errors.append("Address is required")
            
        if self.state.currentText() == "Select State":
            errors.append("Please select a state")
            
        if not self.state_code.text().strip():
            errors.append("State Code is required")
        elif not self.state_code.text().strip().isdigit():
            errors.append("State Code must be numeric")
            
        # Validate GSTIN format if provided
        gstin = self.gstin.text().strip()
        if gstin:
            if len(gstin) != 15:
                errors.append("GSTIN must be exactly 15 characters")
            elif not gstin[:2].isdigit():
                errors.append("GSTIN must start with 2 digit state code")
                
        return errors
    
    def save_customer(self):
        """Save customer data to database"""
        # Validate form
        errors = self.validate_form()
        if errors:
            error_message = "\n".join(errors)
            self.show_message("Validation Error", error_message, "error")
            return
        
        # Prepare customer data
        customer_data = {
            'customer_name': self.customer_name.text().strip(),
            'address': self.address.toPlainText().strip(),
            'state': self.state.currentText(),
            'state_code': self.state_code.text().strip(),
            'gstin': self.gstin.text().strip(),
            'phone': self.phone.text().strip()
        }
        
        # Save to database
        success, customer_id, message = save_customer(customer_data)
        
        if success:
            self.show_message("Success", message, "information")
            self.clear_form()
            self.customer_saved.emit()  # Emit signal to refresh customer list
        else:
            self.show_message("Error", message, "error")
    
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
        self.customer_name.clear()
        self.address.clear()
        self.state.setCurrentIndex(0)
        self.state_code.clear()
        self.gstin.clear()
        self.phone.clear()