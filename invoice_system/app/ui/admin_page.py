from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout,
    QHBoxLayout, QFrame, QTabWidget, QTextEdit, QComboBox, QGridLayout,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QFont

class AdminPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #F4F4F4;
                color: #18230F;
                font-family: 'Segoe UI', Arial;
            }
            QLabel {
                color: #18230F;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #1F7D53;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #1F7D53;
            }
            QPushButton {
                background-color: #1F7D53;
                color: white;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #26A36D;
            }
            QPushButton:pressed {
                background-color: #1A6D48;
            }
            QTabWidget::pane {
                border: 1px solid #1F7D53;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1F7D53;
                color: white;
            }
            QFrame#headerFrame {
                background-color: #1F7D53;
                border-radius: 8px;
                margin-bottom: 15px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        welcome_label = QLabel("Admin Dashboard")
        welcome_label.setStyleSheet("color: white; background: transparent; font-size: 22px; font-weight: bold;")
        
        date_label = QLabel("Today's Date")
        date_label.setStyleSheet("color: black; background: transparent; font-size: 14px;")
        
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(date_label)
        
        main_layout.addWidget(header_frame)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create container widget for scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Profile Form
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 8px; padding: 15px;")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Title
        profile_title = QLabel("Admin Profile Information")
        profile_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1F7D53;")
        scroll_layout.addWidget(profile_title)
        
        # Input Fields with better styling
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QTextEdit()
        self.company_name = QLineEdit()
        self.address_input.setMaximumHeight(80)

        self.logo_button = QPushButton("Upload Logo")
        self.logo_button.setMinimumHeight(40)
        self.logo_button.setStyleSheet("background-color:#4C585B;color:white")

        # Set placeholders
        self.name_input.setPlaceholderText("Enter admin name")
        self.email_input.setPlaceholderText("Enter email address")
        self.phone_input.setPlaceholderText("Enter phone number")
        self.address_input.setPlaceholderText("Enter address")
        self.company_name.setPlaceholderText("Enter company name")
        
        # Add to form layout with better labels
        form_layout.addRow(QLabel("<b>Admin Name:</b>"), self.name_input)
        form_layout.addRow(QLabel("<b>Email Address:</b>"), self.email_input)
        form_layout.addRow(QLabel("<b>Phone Number:</b>"), self.phone_input)
        form_layout.addRow(QLabel("<b>Address:</b>"), self.address_input)
        form_layout.addRow(QLabel("<b>Company's Name:</b>"), self.company_name)
        form_layout.addRow(QLabel("<b>Company's Logo:</b>"), self.logo_button)
        
        """logo_layout = QHBoxLayout()
        logo_layout.addWidget(QLabel("<b>Company's Logo:</b>"))
        logo_layout.addWidget(logo_button)
        logo_layout.addStretch()
        form_layout.addRow(" ", logo_layout)"""

        scroll_layout.addWidget(form_frame)
        
        # Buttons with better layout
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Changes")
        save_button.setMinimumHeight(40)
        save_button.clicked.connect(self.save_admin_info)
        
        
        buttons_layout.addWidget(save_button)
        
        scroll_layout.addLayout(buttons_layout)
        scroll_layout.addStretch()
        
        # Set the scroll content and add to main layout
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def save_admin_info(self):
        admin_name = self.name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        address = self.address_input.toPlainText()
        role = self.role_input.currentText()
        company = self.company_name.text()

        # Print or store values (you can later integrate this with a database)
        print(f"Admin Name: {admin_name}")
        print(f"Email: {email}")
        print(f"Phone: {phone}")
        print(f"Address: {address}")
        print(f"Role: {role}")
        print(f"Company: {company}")

   