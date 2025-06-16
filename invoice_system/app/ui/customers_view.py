from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QStackedWidget, 
    QGridLayout, QFrame, QSizePolicy, QPushButton
)
from .add_customer import Add_Customer
from .edit_customer import Edit_Customer

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
        self.value_label.setStyleSheet("font-size: 20px; font-weight: bold;color: white; margin-top: 10px;")

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
        self.value_label.setStyleSheet("font-size: 20px; font-weight: bold;margin-top: 10px; color: #2D3250;")

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
        self.value_label.setStyleSheet("font-size: 20px;font-weight: bold; margin-top: 10px; color: white;")

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


class CustomerView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
    
        # Stacked widget for customer sub-pages
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Create sub-pages
        self.customer_widget = CustomerWidget()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.customer_widget)  # Index 0

        # Set Customer page as default
        self.stacked_widget.setCurrentWidget(self.customer_widget)

    def show_customers(self):
        self.stacked_widget.setCurrentWidget(self.customer_widget)


class CustomerWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Create Hover Box and Buttons
        self.total_customers_box = HoverBox("TOTAL CUSTOMERS:", "5")
        self.add_customer_button = StyledButton("ADD")
        self.edit_customer_button = StyledButton("EDIT")

        # Connect button signals (implement these functions as needed)
        self.add_customer_button.clicked.connect(self.add_customer)
        self.edit_customer_button.clicked.connect(self.edit_customer)

        # Create a Container Widget for grid layout
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(15)

        # Adding widgets to match the layout
        # Total Customers box on the left
        grid_layout.addWidget(self.total_customers_box, 0, 0, 2, 1)
        
        # Add Customer button on top right
        grid_layout.addWidget(self.add_customer_button, 0, 1)
        
        # Edit Customer button on bottom right
        grid_layout.addWidget(self.edit_customer_button, 1, 1)

        # Add container widget to main layout
        main_layout.addWidget(grid_container, 0, Qt.AlignTop)

        # Add stretch to push everything to the top
        main_layout.addStretch()

    def add_customer(self):
        self.addCustomer_window=Add_Customer()
        self.addCustomer_window.show()
        self.addCustomer_window.setMinimumSize(700,450)
        
        
    def edit_customer(self):
        self.editCustomer_window=Edit_Customer()
        self.editCustomer_window.show()
        self.editCustomer_window.showMaximized()
        
    def update_total_customers(self, count):
        """Updates the total customers display"""
        self.total_customers_box.set_value(str(count))