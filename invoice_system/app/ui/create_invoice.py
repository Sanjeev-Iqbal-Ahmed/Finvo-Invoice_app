from PySide6.QtCore import Qt,QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,QButtonGroup,QRadioButton,
    QTableWidget, QTableWidgetItem, QPushButton, QScrollArea,QDialog,
    QFrame, QGridLayout, QHeaderView, QSizePolicy, QComboBox,QMessageBox,QDialogButtonBox
)
import datetime
import time 
from PySide6.QtGui import QFont, QKeyEvent
from .invoice_preview import InvoicePreviewWindow
from ..models.db_manager import create_tables, save_invoice

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

class CreateInvoice(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Invoice")
        
        self.current_invoice_id = None
        
        # Need to add a QLabel or similar widget to display the grand total
        self.grand_total = QLineEdit()
        self.grand_total.setReadOnly(True)
        self.grand_total.setText("0.00")
        
        create_tables()
        
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
                background-color: #FAF1E6;
                gridline-color: #cccccc;
            }
            QLineEdit {
                background-color: #F8FAFC;
                border: 1px solid #cccccc;
                padding: 5px;
                border-radius: 3px; 
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
            #saveAndPrintButton {
                background-color: #449944;
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
            #termsTitle {
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
        title_label = QLabel("CREATE INVOICE")
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
        customer_layout.addWidget(QLabel("Invoice No :"), 0, 2)
        self.invoice_no = QLineEdit()
        self.invoice_no.setText(self.generate_invoice_no())
        self.invoice_no.setReadOnly(True)   # Make it non-editable
        customer_layout.addWidget(self.invoice_no, 0, 3)
        
        customer_layout.addWidget(QLabel("Date :"), 1, 2)
        self.invoice_date = QLineEdit()
        self.invoice_date.setText(QDate.currentDate().toString("dd-MM-yyyy"))
        self.invoice_date.setReadOnly(True)
        customer_layout.addWidget(self.invoice_date, 1, 3)
        
        # Challan section
        customer_layout.addWidget(QLabel("Challan No :"), 2, 2)
        challan_layout = QHBoxLayout()
        self.challan_combo = QComboBox()
        self.challan_combo.addItems(["NO", "YES"])
        self.challan_combo.currentTextChanged.connect(self.toggle_challan_field)
        challan_layout.addWidget(self.challan_combo)
        
        self.challan_no = QLineEdit()
        self.challan_no.setPlaceholderText("Challan no. if yes")
        self.challan_no.setEnabled(False)
        challan_layout.addWidget(self.challan_no)
        customer_layout.addLayout(challan_layout, 2, 3)
        
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
        
        # Consignment section
        customer_layout.addWidget(QLabel("Consignment No :"), 5, 2)
        consign_layout = QHBoxLayout()
        self.consignment_combo = QComboBox()
        self.consignment_combo.addItems(["NO", "YES"])
        self.consignment_combo.currentTextChanged.connect(self.toggle_consignment_field)
        consign_layout.addWidget(self.consignment_combo)
        
        self.consignment_no = QLineEdit()
        self.consignment_no.setPlaceholderText("Consignment no. if yes")
        self.consignment_no.setEnabled(False)
        consign_layout.addWidget(self.consignment_no)
        customer_layout.addLayout(consign_layout, 5, 3)
        
        main_layout.addWidget(customer_frame)
        
        
        # (Items Table) section - made larger with scroll
        terms_title = QLabel("TERMS OF SALE")
        terms_title.setObjectName("termsTitle")
        terms_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(terms_title)
        
        # Create a scroll area for the Terms of Sale table
        self.terms_scroll = QScrollArea()
        self.terms_scroll.setWidgetResizable(True)
        self.terms_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.terms_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.terms_scroll.setMinimumHeight(300)  # Make it larger
        
       # Table Widget for items
        self.current_rows = 8
        self.items_table = CustomTableWidget(self.current_rows, 7)
        self.items_table.cellChanged.connect(self.calculate_totals)
        self.items_table.setHorizontalHeaderLabels(["Description", "HSN/SAC", "Quantity", "Type", "Rate", "GST %", "Total"])

        # Set column stretch
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.Interactive)

        # Populate row numbers
        self.update_row_numbers()
        
        self.terms_scroll.setWidget(self.items_table)
        main_layout.addWidget(self.terms_scroll)
        
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

        self.grand_total = QLineEdit(" ")
        self.grand_total.setStyleSheet("font-weight: bold;")
        self.grand_total.setFixedWidth(100)
        add_and_total_layout.addWidget(self.grand_total)

        main_layout.addLayout(add_and_total_layout)

         # GST rates section
        gst_frame = QFrame()
        gst_layout = QGridLayout(gst_frame)
        
        # Right side - GST rates
        gst_rates = ["1.25%", "1.5%", "2.5%", "3%", "6%", "9%", "14%"]
        for i, rate in enumerate(gst_rates):
            gst_layout.addWidget(QLabel(rate), 0, i+2)
        
        # Create GST fields
        self.gst_fields = {}
        gst_types = ["SGST", "CGST", "IGST", "Taxation"]
        for i, gst_type in enumerate(gst_types):
            gst_layout.addWidget(QLabel(gst_type), i+1, 1)
            row_fields = []
            for j in range(7):
                field = QLineEdit()
                gst_layout.addWidget(field, i+1, j+2)
                row_fields.append(field)
            self.gst_fields[gst_type] = row_fields
        
        main_layout.addWidget(gst_frame)
        
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
        self.save_button.clicked.connect(self.save_invoice_to_db)
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

    def generate_invoice_no(self):
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        unique_id = str(int(time.time() * 1000))[-5:]  # Last 5 digits of milliseconds
        return f"INV-{date_str}-{unique_id}"

    def calculate_totals(self): 
        self.items_table.blockSignals(True)
        grand_total = 0.0

        # Clear GST fields first
        for gst_type in self.gst_fields:
            for field in self.gst_fields[gst_type]:
                field.setText("")

        # Create GST accumulators
        gst_accumulator = {
            "SGST": [0.0] * 7,
            "CGST": [0.0] * 7,
            "IGST": [0.0] * 7,
            "Taxation": [0.0] * 7,
        }

        # Rate reference
        gst_rates = ["1.25%", "1.5%", "2.5%", "3%", "6%", "9%", "14%"]
        gst_rate_values = [float(rate.strip('%')) for rate in gst_rates]

        for row in range(self.items_table.rowCount()):
            quantity_item = self.items_table.item(row, 2)
            rate_item = self.items_table.item(row, 4)
            gst_item = self.items_table.item(row, 5)

            if quantity_item and rate_item and quantity_item.text().strip() and rate_item.text().strip():
                try:
                    quantity = float(quantity_item.text())
                    rate = float(rate_item.text())
                    total = quantity * rate

                    total_item = QTableWidgetItem(f"{total:.2f}")
                    total_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled|Qt.ItemIsEditable)
                    self.items_table.setItem(row, 6, total_item)

                    grand_total += total

                    # GST calculation
                    if gst_item and gst_item.text().strip():
                        gst_value = float(gst_item.text())
                        if gst_value in gst_rate_values:
                            index = gst_rate_values.index(gst_value)

                            sgst = (gst_value / 2) * total / 100
                            cgst = (gst_value / 2) * total / 100
                            igst = 0.0  # Assuming IGST is 0
                            tax_total = sgst + cgst + igst

                            gst_accumulator["SGST"][index] += sgst
                            gst_accumulator["CGST"][index] += cgst
                            gst_accumulator["IGST"][index] += igst
                            gst_accumulator["Taxation"][index] += tax_total

                except ValueError:
                    pass
            else:
                # Clear total column if inputs are empty
                self.items_table.setItem(row, 6, QTableWidgetItem(""))

        # Update GST fields
        for gst_type in self.gst_fields:
            for i in range(7):
                amount = gst_accumulator[gst_type][i]
                if gst_type == "IGST":
                    self.gst_fields[gst_type][i].setText("0.00")  # Always show 0.00
                else:
                    self.gst_fields[gst_type][i].setText(f"{amount:.2f}" if amount > 0 else "")
        self.grand_total.setText(f"{grand_total:.2f}")
        self.items_table.blockSignals(False)

    
    def toggle_challan_field(self, text):
        self.challan_no.setEnabled(text == "YES")
        if text == "NO":
            self.challan_no.clear()
    
    def toggle_transporter_field(self, text):
        self.transporter_no.setEnabled(text == "YES")
        if text == "NO":
            self.transporter_no.clear()
    
    def toggle_consignment_field(self, text):
        self.consignment_no.setEnabled(text == "YES")
        if text == "NO":
            self.consignment_no.clear()
    
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
        self.invoice_no.clear()
        self.invoice_date.clear()
        
        # Reset combo boxes
        self.challan_combo.setCurrentIndex(0)
        self.transporter_combo.setCurrentIndex(0)
        self.consignment_combo.setCurrentIndex(0)
        
        # Clear dependent fields
        self.challan_no.clear()
        self.transporter_no.clear()
        self.consignment_no.clear()
        
        # Clear table
        for row in range(self.items_table.rowCount()):
            for col in range(self.items_table.columnCount()):
                self.items_table.setItem(row, col, QTableWidgetItem(""))
        
        # Clear GST fields
        self.grand_total.clear()
        for gst_type, fields in self.gst_fields.items():
            for field in fields:
                field.clear()

    def get_cell_text(self, row, col):
        """Safely get text from a table cell"""
        item = self.items_table.item(row, col)
        return item.text() if item else ""

    def save_invoice_to_db(self):
        
        """Open payment status dialog before saving the invoice"""
        payment_status = self.get_payment_status()
        
        if not payment_status:
            # User canceled the payment status dialog
            return
        
        print(f"Selected payment status: {payment_status}")  # Debug print
        
        try:
            # Validate required fields
            if not self.invoice_no.text():
                QMessageBox.warning(self, "Missing Field", "Invoice number is required.")
                return
    
            # Try to parse grand total as float if provided
            grand_total = 0.0
            if self.grand_total.text():
                try:
                    grand_total = float(self.grand_total.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Grand total must be a valid number.")
                    return

            # Create invoice data dictionary with payment_status included
            invoice_data = {
                "customer_name": self.customer_name.text(),
                "customer_address": self.customer_address.text(),
                "gstin": self.customer_gstin.text(),
                "state": self.customer_state.text(),
                "state_code": self.state_code.text(),
                "invoice_no": self.invoice_no.text(),
                "date": self.invoice_date.text(),
                "challan": self.challan_no.text() if self.challan_combo.currentText() == "YES" else "",
                "transporter": self.transporter_no.text() if self.transporter_combo.currentText() == "YES" else "",
                "consignment": self.consignment_no.text() if self.consignment_combo.currentText() == "YES" else "",
                "grand_total": grand_total,
                "payment_status": payment_status  # This is the key line!
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
                    gst = float(self.get_cell_text(row, 5)) if self.get_cell_text(row, 5) else 0.0
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", f"Row {row + 1}: GST must be a number.")
                    return

                try:
                    total = float(self.get_cell_text(row, 6)) if self.get_cell_text(row, 6) else 0.0
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", f"Row {row + 1}: Total must be a number.")
                    return

                item_data = {
                    "description": description,
                    "hsn": self.get_cell_text(row, 1),
                    "quantity": quantity,
                    "type": self.get_cell_text(row, 3),
                    "rate": rate,
                    "gst": gst,
                    "total": total,
                }
                items.append(item_data)

            if not items:
                QMessageBox.warning(self, "Empty Invoice", "At least one item is required.")
                return

            # Save to database and get the invoice_id
            invoice_id = save_invoice(invoice_data, items)
        
            if invoice_id:
                self.current_invoice_id = invoice_id
                QMessageBox.information(self, "Success", f"Invoice saved successfully with payment status: {payment_status}")
                self.show_invoice_preview()

                # If you need to call save_and_print_invoice, do it here AFTER saving to the database
                if hasattr(self, 'save_and_print_invoice'):
                    self.save_and_print_invoice(payment_status)
            else:
                QMessageBox.critical(self, "Error", "Failed to save invoice to database.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the invoice:\n{str(e)}")

    def get_payment_status(self):
        """Show dialog asking for payment status"""
        # Create a custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Payment Status")
        dialog.setFixedWidth(300)
        dialog.setFixedHeight(150)
        
        # Create dialog layout
        layout = QVBoxLayout()
        
        # Add question label
        label = QLabel("Do you want the bill to be listed as:")
        layout.addWidget(label)
        
        # Create button group for radio buttons
        button_group = QButtonGroup(dialog)
        
        # Create radio buttons
        paid_radio = QRadioButton("Paid")
        pending_radio = QRadioButton("Pending")
        pending_radio.setChecked(True)  # Default to pending
        
        # Add radio buttons to button group
        button_group.addButton(paid_radio, 1)
        button_group.addButton(pending_radio, 2)
        
        # Add radio buttons to layout
        layout.addWidget(paid_radio)
        layout.addWidget(pending_radio)
        
        # Add spacer
        layout.addSpacing(10)
        
        # Create button box for OK/Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Set dialog layout
        dialog.setLayout(layout)
        
        # Execute dialog and get result
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Return "Paid" or "Pending" based on selection
            return "Paid" if paid_radio.isChecked() else "Pending"
        else:
            # User canceled
            return None

    def show_invoice_preview(self):
        """Open the invoice preview window"""
        if self.current_invoice_id:
            preview_window = InvoicePreviewWindow(self.current_invoice_id, self)
            preview_window.show()       
    
