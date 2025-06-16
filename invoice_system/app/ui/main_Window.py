from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QStackedWidget, QSpacerItem, QSizePolicy,QPushButton
)
from .sideBar import Sidebar
from .invoice_view import InvoiceView
from .challan_view import ChallanView
from .inventory import InventoryView
from .customers_view import CustomerView
from .admin_page import AdminPage
from .styles import load_stylesheet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice System")
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(load_stylesheet())
        
        # Main layout widget
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainBackground")
        self.setCentralWidget(self.main_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create header
        self.create_header()
        
        # Content area
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.main_layout.addLayout(self.content_layout)
        
        # Create sidebar
        self.sidebar = Sidebar()
        self.content_layout.addWidget(self.sidebar)
        
        # Create stacked widget for main content
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("contentWidget")
        self.content_layout.addWidget(self.stacked_widget)
        
        # Initialize pages
        self.invoice_page = InvoiceView()
        self.challan_page = ChallanView()
        self.inventory_page = InventoryView()
        self.customers_page = CustomerView()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.invoice_page)
        self.stacked_widget.addWidget(self.challan_page)
        self.stacked_widget.addWidget(self.inventory_page)
        self.stacked_widget.addWidget(self.customers_page)
        
        # Connect signals
        self.sidebar.invoice_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.invoice_page))
        self.sidebar.challan_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.challan_page))
        self.sidebar.inventory_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.inventory_page))
        self.sidebar.customers_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.customers_page))
        
    def create_header(self):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # App title
        app_title = QLabel("Invoice System")
        app_title.setObjectName("appTitle")
        header_layout.addStretch()
        header_layout.addWidget(app_title)
        
        # Spacer
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Admin button
        admin_button = QPushButton("Admin")
        admin_button.setObjectName("adminButton")
        header_layout.addWidget(admin_button)

        admin_button.clicked.connect(self.open_admin_page)
        
        self.main_layout.addLayout(header_layout)

    def open_admin_page(self):
        self.admin_window=AdminPage()
        self.admin_window.show()
        self.showMaximized()