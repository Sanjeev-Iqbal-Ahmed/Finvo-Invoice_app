from PySide6.QtCore import Qt,QPropertyAnimation
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel, QFrame,
    QSpacerItem, QSizePolicy, QPushButton
)
from .create_invoice import CreateInvoice
from .admin_page import AdminPage
from .create_challan import CreateChallan
from .manage_invoice import ManageInvoice
from .add_items import AddItems_Page
from .manage_challan import Manage_Challan 

class SidebarButton(QToolButton):
    def __init__(self, text, has_icon=True, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon if has_icon else Qt.ToolButtonTextOnly)
        self.setMinimumHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setObjectName("sidebarButton")

class SubMenuButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(30)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setObjectName("subMenuButton")

class Sidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 20, 10, 20)
        self.layout.setSpacing(5)
        
        logo_label = QLabel("Finvo")
        logo_label.setObjectName("sidebarLogo")
        self.layout.addWidget(logo_label)
        self.layout.addSpacing(20)
        
        # Invoice Button and Submenu
        self.invoice_button = SidebarButton("INVOICE ▼")
        self.invoice_button.setCheckable(True)
        self.invoice_button.clicked.connect(self.toggle_invoice_menu)
        self.layout.addWidget(self.invoice_button)
        
        # Create animation container for invoice submenu
        self.invoice_animation_container = QWidget()
        self.invoice_animation_layout = QVBoxLayout(self.invoice_animation_container)
        self.invoice_animation_layout.setContentsMargins(0, 0, 0, 0)
        self.invoice_animation_layout.setSpacing(0)
        self.layout.addWidget(self.invoice_animation_container)
        
        # Create actual invoice menu
        self.invoice_menu = QWidget()
        self.invoice_menu_layout = QVBoxLayout(self.invoice_menu)
        self.invoice_menu_layout.setContentsMargins(15, 0, 0, 0)
        
        self.create_invoice_button = SubMenuButton("Create Invoice")
        self.create_invoice_button.clicked.connect(self.open_createInvoice_page)
        self.invoice_menu_layout.addWidget(self.create_invoice_button)
        
        self.manage_invoice_button = SubMenuButton("Manage Invoice")
        self.manage_invoice_button.clicked.connect(self.open_manageInvoice_page)
        self.invoice_menu_layout.addWidget(self.manage_invoice_button)
        
        self.invoice_animation_layout.addWidget(self.invoice_menu)
        
        # Create animation for invoice menu
        self.invoice_animation = QPropertyAnimation(self.invoice_animation_container, b"maximumHeight")
        self.invoice_animation.setDuration(200)  # 200ms duration
        self.invoice_animation.setStartValue(0)
        self.invoice_animation_container.setMaximumHeight(0)
        
        # Challan Button and Submenu
        self.challan_button = SidebarButton("CHALLAN ▼")
        self.challan_button.setCheckable(True)
        self.challan_button.clicked.connect(self.toggle_challan_menu)
        self.layout.addWidget(self.challan_button)
        
        # Create animation container for challan submenu
        self.challan_animation_container = QWidget()
        self.challan_animation_layout = QVBoxLayout(self.challan_animation_container)
        self.challan_animation_layout.setContentsMargins(0, 0, 0, 0)
        self.challan_animation_layout.setSpacing(0)
        self.layout.addWidget(self.challan_animation_container)
        
        # Create actual challan menu
        self.challan_menu = QWidget()
        self.challan_menu_layout = QVBoxLayout(self.challan_menu)
        self.challan_menu_layout.setContentsMargins(15, 0, 0, 0)
        
        self.create_challan_button = SubMenuButton("Create Challan")
        self.challan_menu_layout.addWidget(self.create_challan_button)
        self.create_challan_button.clicked.connect(self.open_challanPage)
        
        self.manage_challan_button = SubMenuButton("Manage Challan")
        self.challan_menu_layout.addWidget(self.manage_challan_button)
        self.manage_challan_button.clicked.connect(self.open_manageChallan_page)
        
        self.challan_animation_layout.addWidget(self.challan_menu)
        
        # Create animation for challan menu
        self.challan_animation = QPropertyAnimation(self.challan_animation_container, b"maximumHeight")
        self.challan_animation.setDuration(200)  # 200ms duration
        self.challan_animation.setStartValue(0)
        self.challan_animation_container.setMaximumHeight(0)
        
        # Inventory Button and Submenu
        self.inventory_button = SidebarButton("INVENTORY ")
        self.inventory_button.setCheckable(True)
        self.inventory_button.clicked.connect(self.toggle_inventory_menu)
        self.layout.addWidget(self.inventory_button)
        
        # Create animation container for inventory submenu
        self.inventory_animation_container = QWidget()
        self.inventory_animation_layout = QVBoxLayout(self.inventory_animation_container)
        self.inventory_animation_layout.setContentsMargins(0, 0, 0, 0)
        self.inventory_animation_layout.setSpacing(0)
        self.layout.addWidget(self.inventory_animation_container)
        
        # Create actual inventory menu
        self.inventory_menu = QWidget()
        self.inventory_menu_layout = QVBoxLayout(self.inventory_menu)
        self.inventory_menu_layout.setContentsMargins(15, 0, 0, 0)
        
        self.inventory_animation_layout.addWidget(self.inventory_menu)
        
        # Create animation for inventory menu
        self.inventory_animation = QPropertyAnimation(self.inventory_animation_container, b"maximumHeight")
        self.inventory_animation.setDuration(200)  # 200ms duration
        self.inventory_animation.setStartValue(0)
        self.inventory_animation_container.setMaximumHeight(0)
        
        # Other Sidebar Buttons
        self.customers_button = SidebarButton("CUSTOMERS")
        self.layout.addWidget(self.customers_button)
        
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.admin_sidebar_button = SidebarButton("Admin", False)
        self.admin_sidebar_button.setObjectName("adminSidebarButton")
        self.layout.addWidget(self.admin_sidebar_button)
        
        # Connect signals
        self.invoice_button.clicked.connect(self.activate_invoice)
        self.challan_button.clicked.connect(self.activate_challan)
        self.inventory_button.clicked.connect(self.activate_inventory)
        self.customers_button.clicked.connect(self.activate_customers)
        self.admin_sidebar_button.clicked.connect(self.open_admin)
    
    def toggle_invoice_menu(self):
        # Calculate the expanded height based on content
        content_height = self.invoice_menu.sizeHint().height()
        
        if self.invoice_animation_container.maximumHeight() == 0:
            # Show animation - expand
            self.invoice_animation.setEndValue(content_height)
            self.invoice_button.setText("INVOICE ▲")  # Change arrow direction
            
            # Hide other menus
            self.collapse_other_menus("invoice")
        else:
            # Hide animation - collapse
            self.invoice_animation.setEndValue(0)
            self.invoice_button.setText("INVOICE ▼")  # Change arrow direction
        
        self.invoice_animation.start()
        self.invoice_button.setChecked(self.invoice_animation_container.maximumHeight() != 0)
    
    def toggle_challan_menu(self):
        # Calculate the expanded height based on content
        content_height = self.challan_menu.sizeHint().height()
        
        if self.challan_animation_container.maximumHeight() == 0:
            # Show animation - expand
            self.challan_animation.setEndValue(content_height)
            self.challan_button.setText("CHALLAN ▲")  # Change arrow direction
            
            # Hide other menus
            self.collapse_other_menus("challan")
        else:
            # Hide animation - collapse
            self.challan_animation.setEndValue(0)
            self.challan_button.setText("CHALLAN ▼")  # Change arrow direction
        
        self.challan_animation.start()
        self.challan_button.setChecked(self.challan_animation_container.maximumHeight() != 0)
    
    def toggle_inventory_menu(self):
        # Calculate the expanded height based on content
        content_height = self.inventory_menu.sizeHint().height()
        
        if self.inventory_animation_container.maximumHeight() == 0:
            # Show animation - expand
            self.inventory_animation.setEndValue(content_height)
            self.inventory_button.setText("INVENTORY")  # Change arrow direction
            
            # Hide other menus
            self.collapse_other_menus("inventory")
        else:
            # Hide animation - collapse
            self.inventory_animation.setEndValue(0)
            self.inventory_button.setText("INVENTORY ▼")  # Change arrow direction
        
        self.inventory_animation.start()
        self.inventory_button.setChecked(self.inventory_animation_container.maximumHeight() != 0)
    
    def collapse_other_menus(self, current_menu):
        # Collapse invoice menu if not current
        if current_menu != "invoice":
            self.invoice_animation.setEndValue(0)
            self.invoice_animation.start()
            self.invoice_button.setText("INVOICE ▼")
            self.invoice_button.setChecked(False)
        
        # Collapse challan menu if not current
        if current_menu != "challan":
            self.challan_animation.setEndValue(0)
            self.challan_animation.start()
            self.challan_button.setText("CHALLAN ▼")
            self.challan_button.setChecked(False)
        
        # Collapse inventory menu if not current
        if current_menu != "inventory":
            self.inventory_animation.setEndValue(0)
            self.inventory_animation.start()
            self.inventory_button.setText("INVENTORY ")
            self.inventory_button.setChecked(False)
    
    def collapse_all_menus(self):
        self.collapse_other_menus("")  # Pass empty string to collapse all
        
    def activate_invoice(self):
        self.invoice_button.setChecked(True)
        self.challan_button.setChecked(False)
        self.inventory_button.setChecked(False)
        self.customers_button.setChecked(False)
        
    def activate_challan(self):
        self.invoice_button.setChecked(False)
        self.challan_button.setChecked(True)
        self.inventory_button.setChecked(False)
        self.customers_button.setChecked(False)
        
    def activate_inventory(self):
        self.invoice_button.setChecked(False)
        self.challan_button.setChecked(False)
        self.inventory_button.setChecked(True)
        self.customers_button.setChecked(False)

    def activate_customers(self):
        self.invoice_button.setChecked(False)
        self.challan_button.setChecked(False)
        self.inventory_button.setChecked(False)
        self.customers_button.setChecked(True)
        
        # Collapse all menus
        self.collapse_all_menus()

    def open_createInvoice_page(self):
        self.createInvoice_window=CreateInvoice(None)
        self.createInvoice_window.show()
        self.createInvoice_window.showMaximized()

    def open_admin(self):
        self.admin_window=AdminPage()
        self.admin_window.show()

    def open_challanPage(self):
        self.createChallan_window=CreateChallan()
        self.createChallan_window.show()
        self.createChallan_window.showMaximized()
        
    def open_manageInvoice_page(self):
        self.manageInvoice_window = ManageInvoice()
        self.manageInvoice_window.show()
        self.manageInvoice_window.showMaximized()

    def open_manageChallan_page(self):
        self.manageChallan_window=Manage_Challan()
        self.manageChallan_window.show()
        self.manageChallan_window.showMaximized()