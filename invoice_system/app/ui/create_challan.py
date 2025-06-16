from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QPushButton, QScrollArea,
    QFrame, QGridLayout, QHeaderView, QSizePolicy, QComboBox, QMessageBox
)
import datetime
import time 
from PySide6.QtGui import QFont, QKeyEvent
from .challan_preview import ChallanPreview_Window
from ..models.db_manager import create_tables, save_challan

class CustomTableWidget(QTableWidget):
    def __init__(self, rows, cols, parent=None):
        super().__init__(rows, cols, parent)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            current = self.currentIndex()
            row, col = current.row(), current.column()

            # Move to the next column
            if col < self.columnCount() - 1:
                next_col = col + 1
                while next_col < self.columnCount() and self.isColumnHidden(next_col):
                    next_col += 1  # Skip hidden columns if any
                if next_col < self.columnCount():
                    self.setCurrentCell(row, next_col)
                else:
                    self.setCurrentCell(row + 1, 0)
            else:
                # Move to the first column of the next row
                next_row = row + 1
                if next_row < self.rowCount():
                    self.setCurrentCell(next_row, 0)
        else:
            # Default handler for other keys
            super().keyPressEvent(event)

class CreateChallan(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Challan")
        
        self.current_challan_id = None
        
        # Need to add a QLabel or similar widget to display the grand total
        self.grand_total = QLineEdit()
        self.grand_total.setReadOnly(True)
        self.grand_total.setText("0.00")
        
        create_tables
        
        # Create a main scroll area for the entire window
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main container widget inside scroll area
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Set background color
        self.setStyleSheet("""
            QWidget { 
                background-color: #A6AEBF; 
                color: #333333; font-weight:bold;
            }
            QTableWidget { 
                background-color: white;
                gridline-color: #cccccc;
                font-weight:600;
            }
            QLineEdit {
                background-color: #F8FAFC;
                border: 1px solid #cccccc;
                padding: 5px;
                border-radius: 3px; 
                font-weight:600;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QMessageBox{
                background-color:white;
            }
            QLabel {
                background: transparent;
                color: black;
                font-weight: bold;
            }
            #addButton {
                background-color: #444444;
                color: white;
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
            }
            QHeaderView::section {
                background-color: #dddddd;
                padding: 5px;
                font-weight: bold;
                border: none;
                border-right: 1px solid #cccccc;
                border-bottom: 1px solid #cccccc;
            }
            #itemsTitle {
                font-weight: bold;
                font-size: 14px;
                color: #333333;
            }
            #titleLabel {
                font-weight: bold;
                font-size: 16px;
                color: #333333;
                background-color: #dddddd;
                padding: 10px;
                border-radius: 5px; 
            }
        """)
        
        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("CREATE CHALLAN")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        # Customer Info Section
        customer_frame = QFrame()
        customer_frame.setFrameShape(QFrame.StyledPanel)
        customer_layout = QGridLayout(customer_frame)
        
        # Left side
        customer_layout.addWidget(QLabel("M/S :"), 0, 0)
        self.customer_name = QLineEdit()
        customer_layout.addWidget(self.customer_name, 0, 1)
        
        customer_layout.addWidget(QLabel("Address :"), 1, 0)
        self.customer_address = QLineEdit()
        customer_layout.addWidget(self.customer_address, 1, 1)
        
        customer_layout.addWidget(QLabel("GSTIN :"), 2, 0)
        self.customer_gstin = QLineEdit()
        customer_layout.addWidget(self.customer_gstin, 2, 1)
        
        customer_layout.addWidget(QLabel("State :"), 3, 0)
        self.customer_state = QLineEdit()
        customer_layout.addWidget(self.customer_state, 3, 1)
        
        customer_layout.addWidget(QLabel("Code :"), 3, 2)
        self.state_code = QLineEdit()
        customer_layout.addWidget(self.state_code, 3, 3)
        
        # Right side
        customer_layout.addWidget(QLabel("Challan No :"), 0, 2)
        self.challan_no = QLineEdit()
        self.challan_no.setText(self.generate_challan_no())
        self.challan_no.setReadOnly(True)   # Make it non-editable
        customer_layout.addWidget(self.challan_no, 0, 3)
        
        customer_layout.addWidget(QLabel("Date :"), 1, 2)
        self.challan_date = QLineEdit()
        self.challan_date.setText(QDate.currentDate().toString("dd-MM-yyyy"))
        self.challan_date.setReadOnly(True)
        customer_layout.addWidget(self.challan_date, 1, 3)
        
        # Vehicle section
        customer_layout.addWidget(QLabel("Vehicle No :"), 2, 2)
        vehicle_layout = QHBoxLayout()
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.addItems(["NO", "YES"])
        self.vehicle_combo.currentTextChanged.connect(self.toggle_vehicle_field)
        vehicle_layout.addWidget(self.vehicle_combo)
        
        self.vehicle_no = QLineEdit()
        self.vehicle_no.setPlaceholderText("Vehicle no. if yes")
        self.vehicle_no.setEnabled(False)
        vehicle_layout.addWidget(self.vehicle_no)
        customer_layout.addLayout(vehicle_layout, 2, 3)
        
        # Transporter section
        customer_layout.addWidget(QLabel("Transporter No :"), 4, 2)
        transporter_layout = QHBoxLayout()
        self.transporter_combo = QComboBox()
        self.transporter_combo.addItems(["NO", "YES"])
        self.transporter_combo.currentTextChanged.connect(self.toggle_transporter_field)
        transporter_layout.addWidget(self.transporter_combo)
        
        self.transporter_no = QLineEdit()
        self.transporter_no.setPlaceholderText("Transporter no. if yes")
        self.transporter_no.setEnabled(False)
        transporter_layout.addWidget(self.transporter_no)
        customer_layout.addLayout(transporter_layout, 4, 3)
        
        # LR section
        customer_layout.addWidget(QLabel("LR No :"), 5, 2)
        lr_layout = QHBoxLayout()
        self.lr_combo = QComboBox()
        self.lr_combo.addItems(["NO", "YES"])
        self.lr_combo.currentTextChanged.connect(self.toggle_lr_field)
        lr_layout.addWidget(self.lr_combo)
        
        self.lr_no = QLineEdit()
        self.lr_no.setPlaceholderText("LR no. if yes")
        self.lr_no.setEnabled(False)
        lr_layout.addWidget(self.lr_no)
        customer_layout.addLayout(lr_layout, 5, 3)
        
        main_layout.addWidget(customer_frame)
        
        # Items Table section - made larger with scroll
        items_title = QLabel("ITEMS")
        items_title.setObjectName("itemsTitle")
        items_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(items_title)
        
        # Create a scroll area for the Items table
        self.items_scroll = QScrollArea()
        self.items_scroll.setWidgetResizable(True)
        self.items_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.items_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.items_scroll.setMinimumHeight(300)  # Make it larger
        
        # Table Widget for items (removed GST % column)
        self.current_rows = 8
        self.items_table = CustomTableWidget(self.current_rows, 6)
        self.items_table.cellChanged.connect(self.calculate_totals)
        self.items_table.setHorizontalHeaderLabels(["Description", "HSN/SAC", "Quantity", "Type", "Rate", "Total"])

        # Set column stretch
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.Interactive)

        # Populate row numbers
        self.update_row_numbers()
        
        self.items_scroll.setWidget(self.items_table)
        main_layout.addWidget(self.items_scroll)
        
        # Add button + Grand Total in the same row
        add_and_total_layout = QHBoxLayout()

        # Add Button
        add_button = QPushButton("Add +")
        add_button.setObjectName("addButton")
        add_button.clicked.connect(self.add_row)
        add_and_total_layout.addWidget(add_button)

        # Spacer between button and total
        add_and_total_layout.addStretch()

        # Grand Total Label
        grand_total_label = QLabel("GRAND TOTAL:")
        grand_total_label.setStyleSheet("font-weight: bold;")
        add_and_total_layout.addWidget(grand_total_label)

        self.grand_total = QLineEdit("0.00")
        self.grand_total.setStyleSheet("font-weight: bold;")
        self.grand_total.setFixedWidth(100)
        self.grand_total.setReadOnly(True)
        add_and_total_layout.addWidget(self.grand_total)

        main_layout.addLayout(add_and_total_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        clear_button = QPushButton("Clear")
        clear_button.setObjectName("clearButton")
        clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)
        
        self.save_button = QPushButton("Save && Print")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_challan_to_db)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        # Set the main container to the scroll area
        main_scroll.setWidget(main_container)
        
        # Main layout for this widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_scroll)
        
        # Maximize window when opened
        self.showMaximized()

    def generate_challan_no(self):
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        unique_id = str(int(time.time() * 1000))[-5:]  # Last 5 digits of milliseconds
        return f"CH-{date_str}-{unique_id}"

    def calculate_totals(self): 
        self.items_table.blockSignals(True)
        grand_total = 0.0

        for row in range(self.items_table.rowCount()):
            quantity_item = self.items_table.item(row, 2)
            rate_item = self.items_table.item(row, 4)

            if quantity_item and rate_item and quantity_item.text().strip() and rate_item.text().strip():
                try:
                    quantity = float(quantity_item.text())
                    rate = float(rate_item.text())
                    total = quantity * rate

                    total_item = QTableWidgetItem(f"{total:.2f}")
                    total_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                    self.items_table.setItem(row, 5, total_item)

                    grand_total += total

                except ValueError:
                    pass
            else:
                # Clear total column if inputs are empty
                self.items_table.setItem(row, 5, QTableWidgetItem(""))

        self.grand_total.setText(f"{grand_total:.2f}")
        self.items_table.blockSignals(False)

    def toggle_vehicle_field(self, text):
        self.vehicle_no.setEnabled(text == "YES")
        if text == "NO":
            self.vehicle_no.clear()
    
    def toggle_transporter_field(self, text):
        self.transporter_no.setEnabled(text == "YES")
        if text == "NO":
            self.transporter_no.clear()
    
    def toggle_lr_field(self, text):
        self.lr_no.setEnabled(text == "YES")
        if text == "NO":
            self.lr_no.clear()
    
    def add_row(self):
        # Add a new row to the table
        self.current_rows += 1
        self.items_table.setRowCount(self.current_rows)
        # Update row numbers
        self.update_row_numbers()
    
    def update_row_numbers(self):
        # Update row numbers in the vertical header
        for i in range(self.current_rows):
            self.items_table.setVerticalHeaderItem(i, QTableWidgetItem(str(i+1)))
    
    def clear_form(self):
        # Clear all form fields
        self.customer_name.clear()
        self.customer_address.clear()
        self.customer_gstin.clear()
        self.customer_state.clear()
        self.state_code.clear()
        self.challan_no.setText(self.generate_challan_no())
        self.challan_date.setText(QDate.currentDate().toString("dd-MM-yyyy"))
        
        # Reset combo boxes
        self.vehicle_combo.setCurrentIndex(0)
        self.transporter_combo.setCurrentIndex(0)
        self.lr_combo.setCurrentIndex(0)
        
        # Clear dependent fields
        self.vehicle_no.clear()
        self.transporter_no.clear()
        self.lr_no.clear()
        
        # Clear table
        for row in range(self.items_table.rowCount()):
            for col in range(self.items_table.columnCount()):
                self.items_table.setItem(row, col, QTableWidgetItem(""))
        
        # Clear grand total
        self.grand_total.setText("0.00")

    def get_cell_text(self, row, col):
        """Safely get text from a table cell"""
        item = self.items_table.item(row, col)
        return item.text() if item else ""

    def save_challan_to_db(self):
        try:
            # Validate required fields
            if not self.challan_no.text():
                QMessageBox.warning(self, "Missing Field", "Challan number is required.")
                return
    
            # Try to parse grand total as float if provided
            grand_total = 0.0
            if self.grand_total.text():
                try:
                    grand_total = float(self.grand_total.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Grand total must be a valid number.")
                    return

            # Create challan data dictionary
            challan_data = {
                "customer_name": self.customer_name.text(),
                "customer_address": self.customer_address.text(),
                "gstin": self.customer_gstin.text(),
                "state": self.customer_state.text(),
                "state_code": self.state_code.text(),
                "challan_no": self.challan_no.text(),
                "date": self.challan_date.text(),
                "vehicle": self.vehicle_no.text() if self.vehicle_combo.currentText() == "YES" else "",
                "transporter": self.transporter_no.text() if self.transporter_combo.currentText() == "YES" else "",
                "lr": self.lr_no.text() if self.lr_combo.currentText() == "YES" else "",
                "grand_total": grand_total
            }

            items = []
            for row in range(self.items_table.rowCount()):
                description = self.get_cell_text(row, 0)
                if not description:
                    continue

                try:
                    quantity = int(self.get_cell_text(row, 2)) if self.get_cell_text(row, 2) else 0
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", f"Row {row + 1}: Quantity must be a number.")
                    return

                try:
                    rate = float(self.get_cell_text(row, 4)) if self.get_cell_text(row, 4) else 0.0
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", f"Row {row + 1}: Rate must be a number.")
                    return

                try:
                    total = float(self.get_cell_text(row, 5)) if self.get_cell_text(row, 5) else 0.0
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", f"Row {row + 1}: Total must be a number.")
                    return

                item_data = {
                    "description": description,
                    "hsn": self.get_cell_text(row, 1),
                    "quantity": quantity,
                    "type": self.get_cell_text(row, 3),
                    "rate": rate,
                    "total": total,
                }
                items.append(item_data)

            if not items:
                QMessageBox.warning(self, "Empty Challan", "At least one item is required.")
                return

            # Save to database and get the challan_id
            challan_id = save_challan(challan_data, items)
        
            if challan_id:
                self.current_challan_id = challan_id
                QMessageBox.information(self, "Success", "Challan saved successfully!")
                self.show_challan_preview()
            else:
                QMessageBox.critical(self, "Error", "Failed to save challan to database.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the challan:\n{str(e)}")

    def show_challan_preview(self):
        """Open the challan preview window"""
        if self.current_challan_id:
            preview_window = ChallanPreview_Window(self.current_challan_id, self)
            preview_window.show()