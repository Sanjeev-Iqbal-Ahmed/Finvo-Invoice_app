from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QStackedWidget, 
    QGridLayout, QFrame, QSizePolicy, QPushButton
)
from .inventory_view import InventoryViewPage
from .add_items import AddItems_Page

class HoverBox(QFrame):
    def __init__(self, title, value="", parent=None):
        super().__init__(parent)
        self.setObjectName("hoverBox")
        self.setMouseTracking(True)

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(250, 120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setStyleSheet("""
            #hoverBox {
                background-color: #2D3250;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        self.value_label = QLabel(value)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("font-size: 16px; color: white; margin-top: 10px;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

        self.animation = QPropertyAnimation(self, b"minimumSize")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

        self.normal_size = QSize(250, 120)
        self.hover_size = QSize(280, 140)

    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.size())
        self.animation.setEndValue(self.hover_size)
        self.animation.start()

        self.setStyleSheet("""
            #hoverBox {
                background-color: #DDDDDD;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2D3250;")
        self.value_label.setStyleSheet("font-size: 16px; margin-top: 10px; color: #2D3250;")

        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.size())
        self.animation.setEndValue(self.normal_size)
        self.animation.start()

        self.setStyleSheet("""
            #hoverBox {
                background-color: #2D3250;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        self.value_label.setStyleSheet("font-size: 16px; margin-top: 10px; color: white;")

        super().leaveEvent(event)

    def set_value(self, value):
        self.value_label.setText(value)


class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMouseTracking(True)

        self.normal_size = QSize(180, 80)
        self.hover_size = QSize(200, 90)

        self.setMinimumSize(self.normal_size)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setStyleSheet("""
            QPushButton {
                background-color: #2D3250;
                color: white;
                border-radius: 10px;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #DDDDDD;
                color:#2D3250;
            }
            QPushButton:pressed {
                background-color: #2D3250;
                color:#a8a8a8
            }
        """)

        self.animation = QPropertyAnimation(self, b"minimumSize")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.size())
        self.animation.setEndValue(self.hover_size)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.size())
        self.animation.setEndValue(self.normal_size)
        self.animation.start()
        super().leaveEvent(event)



class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
    
        # Stacked widget for inventory sub-pages
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Create sub-pages
        self.inventory_widget = InventoryWidget()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.inventory_widget)  # Index 0

        # Set Inventory page as default
        self.stacked_widget.setCurrentWidget(self.inventory_widget)

    def show_inventory(self):
        self.stacked_widget.setCurrentWidget(self.inventory_widget)


class InventoryWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Create Hover Box and Buttons
        self.most_sold_box = HoverBox("MOST SOLD:", "Product Name")
        self.add_inventory_button = StyledButton("ADD INVENTORY")
        self.view_button = StyledButton("VIEW")

        # Connect button signals (implement these functions as needed)
        self.add_inventory_button.clicked.connect(self.add_inventory)
        self.view_button.clicked.connect(self.view_inventory)

        # Create a Container Widget for grid layout
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(15)

        # Adding widgets to match the image layout
        # Most Sold box on the left
        grid_layout.addWidget(self.most_sold_box, 0, 0, 2, 1)
        
        # Add Inventory button on top right
        grid_layout.addWidget(self.add_inventory_button, 0, 1)
        
        # View button on bottom right
        grid_layout.addWidget(self.view_button, 1, 1)

        # Add container widget to main layout
        main_layout.addWidget(grid_container, 0, Qt.AlignTop)

        # Add stretch to push everything to the top
        main_layout.addStretch()

    def add_inventory(self):
        self.add_inventory_window=AddItems_Page()
        self.add_inventory_window.show()
        self.add_inventory_window.showMaximized()
        
    def view_inventory(self):
        self.inventory_view_window=InventoryViewPage()
        self.inventory_view_window.show()
        self.inventory_view_window.showMaximized()
        
    def update_most_sold(self, product_name):
        """Updates the most sold product display"""
        self.most_sold_box.set_value(product_name)