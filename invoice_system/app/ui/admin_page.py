from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog,
    QScrollArea, QFrame, QGroupBox, QSizePolicy
)
from PySide6.QtGui import QPixmap, QIcon
import os

class AdminPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Company Administration")
        self.resize(700, 600)
        self.setMinimumSize(650, 550)
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
            #clearButton {
                background-color: #666666;
                color: white;
            }
            #cancelButton {
                background-color: #ff4444;
                color: white;
            }
            #saveButton {
                background-color: #555599;
                color: white;
            }""")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        scroll_layout = QVBoxLayout(content_widget)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(15)
        
        # Company Details Section
        company_group = QGroupBox("COMPANY DETAILS")
        company_group.setObjectName("adminGroupBox")
        company_layout = QHBoxLayout(company_group)
        
        # Left side - Company Form
        company_form = QFormLayout()
        company_form.setSpacing(10)
        company_form.setVerticalSpacing(15)
        
        # Form fields
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Customer GSTIN/URP")
        
        self.gstin = QLineEdit()
        self.gstin.setPlaceholderText("Customer GSTIN/URP")
        
        self.contact = QLineEdit()
        self.contact.setPlaceholderText("Customer GSTIN/URP")
        
        self.address = QTextEdit()
        self.address.setMaximumHeight(100)
        self.address.setPlaceholderText("")
        
        # Add fields to form
        company_form.addRow("Company Name:", self.company_name)
        company_form.addRow("GSTIN:", self.gstin)
        company_form.addRow("Contact:", self.contact)
        company_form.addRow("Address:", self.address)
        
        # Right side - Logo management
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # Logo placeholder
        self.logo_frame = QLabel()
        self.logo_frame.setFixedSize(180, 180)
        self.logo_frame.setStyleSheet("background-color: #f8f8f8; border-radius: 90px;")
        self.logo_frame.setAlignment(Qt.AlignCenter)
        
        # Logo buttons
        self.add_logo_btn = QPushButton("Add/Change Logo")
        self.add_logo_btn.setObjectName("logoButton")
        self.add_logo_btn.clicked.connect(self.add_logo)
        
        self.remove_logo_btn = QPushButton("Remove Logo")
        self.remove_logo_btn.setObjectName("logoButton")
        self.remove_logo_btn.clicked.connect(self.remove_logo)
        
        logo_layout.addWidget(self.logo_frame)
        logo_layout.addSpacing(15)
        logo_layout.addWidget(self.add_logo_btn)
        logo_layout.addWidget(self.remove_logo_btn)
        
        # Add both layouts to company section
        company_form_widget = QWidget()
        company_form_widget.setLayout(company_form)
        company_form_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        logo_widget = QWidget()
        logo_widget.setLayout(logo_layout)
        
        company_layout.addWidget(company_form_widget, 65)
        company_layout.addWidget(logo_widget, 35)
        
        # Bank Details Section
        bank_group = QGroupBox("BANK DETAILS")
        bank_group.setObjectName("adminGroupBox")
        bank_layout = QFormLayout(bank_group)
        bank_layout.setSpacing(10)
        bank_layout.setVerticalSpacing(15)
        
        # Bank form fields
        self.bank_name = QLineEdit()
        self.bank_name.setPlaceholderText("Enter the Customer Name")
        
        self.account_number = QLineEdit()
        self.account_number.setPlaceholderText("Enter the Customer Name")
        
        self.bank_ifsc = QLineEdit()
        self.bank_ifsc.setPlaceholderText("Enter the Customer Name")
        
        self.bank_branch = QLineEdit()
        self.bank_branch.setPlaceholderText("Enter the Bank Branch Name")
        
        # Add fields to bank form
        bank_layout.addRow("Bank Name:", self.bank_name)
        bank_layout.addRow("Account Number:", self.account_number)
        bank_layout.addRow("Bank IFSC:", self.bank_ifsc)
        bank_layout.addRow("Bank Branch:", self.bank_branch)
        
        # Add sections to scroll layout
        scroll_layout.addWidget(company_group)
        scroll_layout.addWidget(bank_group)
        scroll_layout.addStretch()
        
        # Set the widget to the scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(20, 10, 20, 20)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_form)
        self.clear_btn.setObjectName("clearButton")
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setObjectName("cancelButton")
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_data)
        self.save_btn.setObjectName("saveButton")
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(buttons_layout)
        
        # Store the logo path
        self.logo_path = None
        
    def add_logo(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Logo", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.logo_path = file_path
            pixmap = QPixmap(file_path)
            
            # Create circular mask for the logo
            scaled_pixmap = pixmap.scaled(
                180, 180, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            self.logo_frame.setPixmap(scaled_pixmap)
            self.logo_frame.setStyleSheet("background-color: transparent; border-radius: 90px;")
    
    def remove_logo(self):
        self.logo_path = None
        self.logo_frame.clear()
        self.logo_frame.setStyleSheet("background-color: #f8f8f8; border-radius: 90px;")
    
    def clear_form(self):
        # Clear all form fields
        self.company_name.clear()
        self.gstin.clear()
        self.contact.clear()
        self.address.clear()
        self.bank_name.clear()
        self.account_number.clear()
        self.bank_ifsc.clear()
        self.bank_branch.clear()
        # Clear logo
        self.remove_logo()
    
    def save_data(self):
        # Implement saving functionality here
        # You might want to save to a config file or database
        # For now, we'll just print the values
        company_data = {
            'name': self.company_name.text(),
            'gstin': self.gstin.text(),
            'contact': self.contact.text(),
            'address': self.address.toPlainText(),
            'logo_path': self.logo_path,
            'bank_name': self.bank_name.text(),
            'account_number': self.account_number.text(),
            'bank_ifsc': self.bank_ifsc.text(),
            'bank_branch': self.bank_branch.text()
        }
        
        print("Saving company data:", company_data)
        # Here you would add your actual save logic
        
        # Close the dialog
        self.accept()