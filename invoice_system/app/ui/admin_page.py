import os
from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog,
    QScrollArea, QFrame, QGroupBox, QSizePolicy
)
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from ..models.db_manager import save_company_info,load_company_info


class AdminPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Company Administration")
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint|
                            Qt.WindowCloseButtonHint)
        self.setMinimumSize(700, 650)
        self.setStyleSheet("""
            QWidget { 
                background-color: #A6AEBF; 
                color: #333333; font-weight:bold;
            }
            QLineEdit,QTextEdit {
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
            #clearButton {
                background-color: #666666;
                color: white;
            }
            #clearButton:hover{
                background-color:#635e5e; color:white
            }
            #clearButton:pressed{
                background-color:#2e2e2e; color:white          
            }
            #cancelButton {
                background-color: #ff4444;
                color: white;
            }
            #cancelButton:hover {
                background-color: #f78888;
                color: white;
            }
            #cancelButton:pressed {
                background-color: #c71c1c;
                color: white;
            }
            #saveButton {
                background-color: #555599;
                color: white;
            }
            #saveButton:hover {
                background-color: #7070b8;
                color: white;
            }
             #saveButton:pressed {
                background-color: #474780;
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
        self.company_name.setPlaceholderText("")
        
        self.gstin = QLineEdit()
        self.gstin.setPlaceholderText("")
        
        self.contact = QLineEdit()
        self.contact.setPlaceholderText("")
        
        self.address = QTextEdit()
        self.address.setMaximumHeight(100)
        self.address.setPlaceholderText("")
        self.address.setStyleSheet("background-color:#F8FAFC")
        
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
        self.add_logo_btn.clicked.connect(self.add_logo)
        self.add_logo_btn.setStyleSheet("background-color:#666666;color:white")
        
        self.remove_logo_btn = QPushButton("Remove Logo")
        self.remove_logo_btn.clicked.connect(self.remove_logo)
        self.remove_logo_btn.setStyleSheet("background-color:#666666;color:white")

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
        self.bank_name.setPlaceholderText("")
        
        self.account_number = QLineEdit()
        self.account_number.setPlaceholderText("")
        
        self.bank_ifsc = QLineEdit()
        self.bank_ifsc.setPlaceholderText("")
        
        self.bank_branch = QLineEdit()
        self.bank_branch.setPlaceholderText("")
        
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
        self.clear_btn.setObjectName("clearButton")    #setObjectName is used to add the stylesheet
        
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

        #Load saved data from the database
        self.load_data()

        #loads circular logo
        self.load_logo()
        
    def add_logo(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
        self, "Select Logo", "", "Image Files (*.png *.jpg *.jpeg)"
        )

        if file_path:
            self.logo_path = file_path
            original_pixmap = QPixmap(file_path)

            # Scale image to desired size (e.g., 180x180)
            size = 180
            scaled_pixmap = original_pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

            # Create circular mask
            mask = QPixmap(size, size)
            mask.fill(Qt.transparent)

            painter = QPainter(mask)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, size, size)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.end()

            self.logo_frame.setPixmap(mask)
            self.logo_frame.setStyleSheet("background-color: transparent;")
    
    def remove_logo(self):
        self.logo_path = None
        self.logo_frame.clear()
        self.logo_frame.setStyleSheet("background-color: #f8f8f8; border-radius: 90px;")
    
    def load_logo(self):
        if hasattr(self, 'logo_path') and os.path.exists(self.logo_path):
            original_pixmap = QPixmap(self.logo_path)
            size = 180
            scaled_pixmap = original_pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

            # Create circular mask again
            mask = QPixmap(size, size)
            mask.fill(Qt.transparent)

            painter = QPainter(mask)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, size, size)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.end()

            self.logo_frame.setPixmap(mask)
            self.logo_frame.setStyleSheet("background-color: transparent;")
   
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
        # Gather data from form fields
        company_data = {
            'name': self.company_name.text().strip(),
            'gstin': self.gstin.text().strip(),
            'contact': self.contact.text().strip(),
            'address': self.address.toPlainText().strip(),
            'logo_path': self.logo_path,
            'bank_name': self.bank_name.text().strip(),
            'account_number': self.account_number.text().strip(),
            'bank_ifsc': self.bank_ifsc.text().strip(),
            'bank_branch': self.bank_branch.text().strip()
        }

        # Save using db_manager
        success = save_company_info(company_data)

        if success:
            print("Company data saved successfully.")
            self.accept()
        else:
            print("Failed to save company data.")

    def load_data(self):
        data = load_company_info()
        if data:
            self.company_name.setText(data.get('name', ''))
            self.gstin.setText(data.get('gstin', ''))
            self.contact.setText(data.get('contact', ''))
            self.address.setPlainText(data.get('address', ''))
            self.bank_name.setText(data.get('bank_name', ''))
            self.account_number.setText(data.get('account_number', ''))
            self.bank_ifsc.setText(data.get('bank_ifsc', ''))
            self.bank_branch.setText(data.get('bank_branch', ''))
        
            self.logo_path = data.get('logo_path')
            if self.logo_path and os.path.exists(self.logo_path):
                pixmap = QPixmap(self.logo_path).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_frame.setPixmap(pixmap)
                self.logo_frame.setStyleSheet("background-color: transparent; border-radius: 90px;")
            else:
                self.remove_logo()
