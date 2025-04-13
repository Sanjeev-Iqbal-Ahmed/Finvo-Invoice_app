from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QStackedWidget, 
    QGridLayout, QFrame, QSizePolicy
)

class ChallanView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
    
        # Stacked widget for challan sub-pages
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Create sub-pages
        self.challan_widget = ChallanWidget()  # New Default Page

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.challan_widget)  # Index 0

        # Set Challan page as default
        self.stacked_widget.setCurrentWidget(self.challan_widget)

    def show_challan(self):
        self.stacked_widget.setCurrentWidget(self.challan_widget)


class HoverBox(QFrame):
    def __init__(self, title, value="0", parent=None):
        super().__init__(parent)
        self.setObjectName("hoverBox")

        # Set up frame appearance
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(180, 120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Default Style
        self.setStyleSheet("""
            #hoverBox {
                background-color: #2D3250;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
        """)

        # Value label
        self.value_label = QLabel(value)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin-top: 10px;
        """)

        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

        # Animation for Hover Effect
        self.animation = QPropertyAnimation(self, b"minimumSize")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

        self.normal_size = QSize(250, 120)
        self.hover_size = QSize(300, 150)  # Enlarged Size

    def enterEvent(self, event):
        # Change color on hover
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
        self.title_label.setStyleSheet("color: #2D3250; font-size: 16px; font-weight: bold;")
        self.value_label.setStyleSheet("color: #2D3250; font-size: 24px; font-weight: bold; margin-top: 10px;")

        super().enterEvent(event)

    def leaveEvent(self, event):
        # Change back to original size and color
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
        self.title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-top: 10px;")

        super().leaveEvent(event)


class ChallanWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Main Layout (Moves Boxes to the Top)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Added margin for better spacing
        main_layout.setSpacing(20)  # Space between sections


        # Create Hover Boxes
        self.total_challan_box = HoverBox("TOTAL CHALLAN", "0")
        self.pending_challan_box = HoverBox("PENDING CHALLAN", "0")

        # Set size policy to make them expand nicely
        for box in [self.total_challan_box, self.pending_challan_box]:
            box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a Container Widget
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(15)

        # Adding hover boxes
        grid_layout.addWidget(self.total_challan_box, 0, 0)
        grid_layout.addWidget(self.pending_challan_box, 0, 1)
       

        # Add container widget to main layout
        main_layout.addWidget(grid_container, 0, Qt.AlignTop)

        # Now, adding stretch to push everything to the top
        main_layout.addStretch()

    def update_values(self, data):
        """Updates values dynamically from database"""
        self.total_challan_box.set_value(data.get("total_challan", "0"))
        self.pending_challan_box.set_value(f"{data.get('pending_challan', '0')} ")
        