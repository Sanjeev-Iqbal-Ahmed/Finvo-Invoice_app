from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QStackedWidget, 
    QGridLayout, QFrame, QSizePolicy
)
from ..models.db_manager import get_invoice_summary

class InvoiceView(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Stacked widget for invoice sub-pages
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Create sub-pages
        self.invoice_widget = InvoiceWidget()  # New Default Page

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.invoice_widget)  # Index 0

        # Set Invoice page as default
        self.stacked_widget.setCurrentWidget(self.invoice_widget)

        # Set up auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(3000)  # Refresh every 5 seconds (adjust as needed)

        self.refresh_dashboard()  # Load data on startup

    def show_invoice(self):
        self.stacked_widget.setCurrentWidget(self.invoice_widget)

    def refresh_dashboard(self):
        """Refresh dashboard data from database"""
        try:
            data = get_invoice_summary()
            self.invoice_widget.update_values(data)
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")

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
        """Brief highlight effect when value changes"""
        original_style = self.value_label.styleSheet()
        self.value_label.setStyleSheet(original_style + "color: #4CAF50;")  # Green highlight
        
        # Reset color after brief moment
        QTimer.singleShot(500, lambda: self.value_label.setStyleSheet(original_style))

class InvoiceWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Main Layout (Moves Boxes to the Top)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Added margin for better spacing
        main_layout.setSpacing(20)  # Space between sections

        # Create Hover Boxes
        self.total_invoice_box = HoverBox("TOTAL INVOICES", "0")
        self.due_amount_box = HoverBox("DUE AMOUNT", "Rs. 0")
        self.pending_bills_box = HoverBox("PENDING BILLS", "0")
        self.paid_bills_box = HoverBox("PAID BILLS", "0")

        # Set size policy to make them expand nicely
        for box in [self.total_invoice_box, self.due_amount_box, self.pending_bills_box, self.paid_bills_box]:
            box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a Container Widget
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(15)

        # Adding hover boxes
        grid_layout.addWidget(self.total_invoice_box, 0, 0)
        grid_layout.addWidget(self.due_amount_box, 0, 1)
        grid_layout.addWidget(self.pending_bills_box, 1, 0)
        grid_layout.addWidget(self.paid_bills_box, 1, 1)

        # Add container widget to main layout
        main_layout.addWidget(grid_container, 0, Qt.AlignTop)

        # Now, adding stretch to push everything to the top
        main_layout.addStretch()

    def update_values(self, data):
        """Updates values dynamically from database"""
        if data:
            self.total_invoice_box.set_value(data.get("total_invoices", "0"))
            self.due_amount_box.set_value(f"Rs. {data.get('due_amount', '0')}")
            self.pending_bills_box.set_value(data.get("pending_bills", "0"))
            self.paid_bills_box.set_value(data.get("paid_bills", "0"))