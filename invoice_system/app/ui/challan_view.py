from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve,QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QStackedWidget, 
    QGridLayout, QFrame, QSizePolicy,QHBoxLayout,QPushButton
)
from .create_challan import CreateChallan
from .manage_challan import Manage_Challan 
from ..models.db_manager import get_all_challans

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

        # Set up auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(3000)  # Refresh every 3 seconds (adjust as needed)

        self.refresh_dashboard()  # Load data on startup

    def show_challan(self):
        self.stacked_widget.setCurrentWidget(self.challan_widget)

    def refresh_dashboard(self):
        """Refresh dashboard data from database"""
        try:
            challan_list = get_all_challans()  # This returns a list of challans
            # Create a data dictionary with the total count
            data = {
                "total_challan": len(challan_list),  # Count the number of challans
                "challans": challan_list  # Store the actual challan data if needed elsewhere
            }
            self.challan_widget.update_values(data)
        except Exception as e:
            print(f"Error refreshing challan dashboard: {e}")
            # Set default values in case of error
            data = {"total_challan": 0}
            self.challan_widget.update_values(data)

    def manual_refresh(self):
        """Force an immediate refresh (can be called from other parts of the app)"""
        self.refresh_dashboard()

    def set_refresh_interval(self, milliseconds):
        """Change the auto-refresh interval"""
        self.refresh_timer.setInterval(milliseconds)

    def start_auto_refresh(self):
        """Start auto-refresh if stopped"""
        if not self.refresh_timer.isActive():
            self.refresh_timer.start()

    def stop_auto_refresh(self):
        """Stop auto-refresh"""
        self.refresh_timer.stop()

    def showEvent(self, event):
        """Called when widget becomes visible - refresh data"""
        super().showEvent(event)
        self.refresh_dashboard()
        self.start_auto_refresh()

    def hideEvent(self, event):
        """Called when widget becomes hidden - can pause refresh to save resources"""
        super().hideEvent(event)
        # Optionally stop auto-refresh when not visible to save resources
        # self.stop_auto_refresh()

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

    def set_value(self, new_value):
        """Update the value with animation effect"""
        old_value = self.value_label.text()
        if old_value != str(new_value):
            # Optional: Add a brief highlight effect when value changes
            self.value_label.setText(str(new_value))
            self.highlight_change()

    def highlight_change(self):
        """Add a brief highlight effect when value changes"""
        # Store original stylesheet
        original_style = self.value_label.styleSheet()
        
        # Apply highlight effect
        self.value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
            margin-top: 10px;
        """)
        
        # Use QTimer to revert back to original style after 500ms
        QTimer.singleShot(500, lambda: self.value_label.setStyleSheet(original_style))

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
                outline: none;
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

class ChallanWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Create Hover Box and Buttons
        self.total_challan_box = HoverBox("TOTAL CHALLAN:", "0")
        self.create_challan_button = StyledButton("CREATE CHALLAN")
        self.manage_challan_button = StyledButton("MANAGE CHALLAN")

        # Connect button signals (implement these functions as needed)
        self.create_challan_button.clicked.connect(self.open_challanPage)
        self.manage_challan_button.clicked.connect(self.open_manageChallan_page)

        # Create a Container Widget for grid layout
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(15)

        # Adding widgets to match the image layout
        # Most Sold box on the left
        grid_layout.addWidget(self.total_challan_box, 0, 0, 2, 1)
        
        # Add Inventory button on top right
        grid_layout.addWidget(self.create_challan_button, 0, 1)
        
        # View button on bottom right
        grid_layout.addWidget(self.manage_challan_button, 1, 1)

        # Add container widget to main layout
        main_layout.addWidget(grid_container, 0, Qt.AlignTop)

        # Add stretch to push everything to the top
        main_layout.addStretch()

    def update_values(self, data):
        """Updates values dynamically from database"""
        if data:
            total_challan = data.get("total_challan", 0)
            self.total_challan_box.set_value(total_challan)
        
    def open_challanPage(self):
        self.createChallan_window = CreateChallan()
        self.createChallan_window.show()
        self.createChallan_window.showMaximized()
        
    def open_manageChallan_page(self):
        self.manageChallan_window = Manage_Challan()
        self.manageChallan_window.show()
        self.manageChallan_window.showMaximized()