from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QButtonGroup, QRadioButton,
    QTableWidget, QTableWidgetItem, QPushButton, QScrollArea, QDialog, QDateEdit, QFileDialog,
    QFrame, QGridLayout, QHeaderView, QSizePolicy, QComboBox, QMessageBox, QDialogButtonBox
)
from PySide6.QtGui import QBrush, QColor, QIcon
from ..models.db_manager import get_all_invoices, get_invoice, delete_invoice,update_payment_status
from .invoice_preview import InvoicePreviewWindow
from .create_invoice import CreateInvoice
import csv

class ManageInvoice(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Invoices")
        self.resize(1200, 800)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        self.setup_header()
        
        # Search and filter section
        self.setup_search_filter()
        
        # Invoices table
        self.setup_invoices_table()
        
        # Buttons section
        self.setup_action_buttons()
        
        # Load invoices
        self.load_invoices()

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
                background-color: #F4E7E1;
                color: black;
            }
            QPushButton:hover {
                background-color: #7070b8;
                color: white;
            }
            QPushButton:pressed {
                background-color: #474780;
                color: white;
            }
            """)
        
    def setup_header(self):
        """Set up the header section with title and total info"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Manage Invoices")
        title_label.setObjectName("pageTitle")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Invoice statistics
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Total Invoices
        total_invoices_layout = QVBoxLayout()
        total_invoices_label = QLabel("Total Invoices")
        self.total_invoices_value = QLabel("0")
        self.total_invoices_value.setStyleSheet("font-size: 18px; font-weight: bold;")
        total_invoices_layout.addWidget(total_invoices_label)
        total_invoices_layout.addWidget(self.total_invoices_value)
        stats_layout.addLayout(total_invoices_layout)
        
        # Paid Invoices
        paid_invoices_layout = QVBoxLayout()
        paid_invoices_label = QLabel("Paid")
        self.paid_invoices_value = QLabel("0")
        self.paid_invoices_value.setStyleSheet("font-size: 18px; font-weight: bold; color:black;")
        paid_invoices_layout.addWidget(paid_invoices_label)
        paid_invoices_layout.addWidget(self.paid_invoices_value)
        stats_layout.addLayout(paid_invoices_layout)
        
        # Pending Invoices
        pending_invoices_layout = QVBoxLayout()
        pending_invoices_label = QLabel("Pending")
        self.pending_invoices_value = QLabel("0")
        self.pending_invoices_value.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        pending_invoices_layout.addWidget(pending_invoices_label)
        pending_invoices_layout.addWidget(self.pending_invoices_value)
        stats_layout.addLayout(pending_invoices_layout)
        
        header_layout.addLayout(stats_layout)
        
        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(20)
    
    def setup_search_filter(self):
        """Set up search and filter controls"""
        filter_layout = QHBoxLayout()
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by invoice #, customer name...")
        self.search_input.textChanged.connect(self.apply_filters)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        filter_layout.addLayout(search_layout)
        filter_layout.addStretch()
        
        # Payment status filter
        status_layout = QHBoxLayout()
        status_label = QLabel("Payment Status:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Paid", "Pending"])
        self.status_combo.currentTextChanged.connect(self.apply_filters)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_combo)
        
        filter_layout.addLayout(status_layout)
        
        # Date filter
        date_layout = QHBoxLayout()
        date_label = QLabel("Date Range:")
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        
        date_to_label = QLabel("to")
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        
        self.apply_date_filter = QPushButton("Apply")
        self.apply_date_filter.clicked.connect(self.apply_filters)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(date_to_label)
        date_layout.addWidget(self.date_to)
        date_layout.addWidget(self.apply_date_filter)
        
        filter_layout.addLayout(date_layout)
        
        self.main_layout.addLayout(filter_layout)
        self.main_layout.addSpacing(10)
    
    def setup_invoices_table(self):
        """Set up the invoices table"""
        # Create table widget
        self.invoices_table = QTableWidget()
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.invoices_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.setColumnCount(8)
        
        # Set headers
        headers = ["Invoice #", "Date", "Customer Name", "Items", "Grand Total", "Payment Status", "Actions", "ID"]
        self.invoices_table.setHorizontalHeaderLabels(headers)
        
        # Hide the ID column which we'll use internally
        self.invoices_table.setColumnHidden(7, True)
        
        # Set column widths
        self.invoices_table.setColumnWidth(0, 200)  # Invoice #
        self.invoices_table.setColumnWidth(1, 120)  # Date
        self.invoices_table.setColumnWidth(2, 250)  # Customer Name
        self.invoices_table.setColumnWidth(3, 80)   # Items
        self.invoices_table.setColumnWidth(4, 120)  # Grand Total
        self.invoices_table.setColumnWidth(5, 120)  # Payment Status
        self.invoices_table.setColumnWidth(6, 310)  # Actions
        
        # Set table to take all available space
        self.main_layout.addWidget(self.invoices_table)
    
    def setup_action_buttons(self):
        """Set up action buttons at the bottom"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Export button
        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        buttons_layout.addWidget(self.export_button) 
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_invoices)
        buttons_layout.addWidget(self.refresh_button)
        
        self.main_layout.addLayout(buttons_layout)
    
    def load_invoices(self):
        """Load invoices from database"""
        try:
            # Clear existing table
            self.invoices_table.setRowCount(0)
            
            # Get all invoices from database - FIXED: Using get_all_invoices() instead of get_invoice()
            invoices = get_all_invoices()
            
            # Track counts for statistics
            total_count = 0
            paid_count = 0
            pending_count = 0
            
            for invoice in invoices:
                # Apply filters if needed
                if not self.should_display_invoice(invoice):
                    continue
                
                # Count for statistics
                total_count += 1
                if invoice.get('payment_status') == 'Paid':
                    paid_count += 1
                else:  # Assuming 'Pending' is the default
                    pending_count += 1
                
                # Add row to table
                row_position = self.invoices_table.rowCount()
                self.invoices_table.insertRow(row_position)
                
                # Set invoice data
                self.invoices_table.setItem(row_position, 0, QTableWidgetItem(str(invoice.get('invoice_no', ''))))
                self.invoices_table.setItem(row_position, 1, QTableWidgetItem(str(invoice.get('date', ''))))
                self.invoices_table.setItem(row_position, 2, QTableWidgetItem(str(invoice.get('customer_name', ''))))
                
                # Calculate number of items - FIXED: Handle the mock items structure
                items_count = invoice.get('items', [{}])[0].get('count', 0) if invoice.get('items') else 0
                self.invoices_table.setItem(row_position, 3, QTableWidgetItem(str(items_count)))
                
                # Format grand total with currency
                grand_total = f"₹{float(invoice.get('grand_total', 0)):.2f}"
                self.invoices_table.setItem(row_position, 4, QTableWidgetItem(grand_total))
                
                # Payment status with colored indicator
                payment_status = invoice.get('payment_status', 'Pending')
                payment_status_item = QTableWidgetItem(payment_status)
                if payment_status == 'Paid':
                    payment_status_item.setForeground(QBrush(QColor("#0B5D02")))
                else:
                    payment_status_item.setForeground(QBrush(QColor("#CE6706")))
                self.invoices_table.setItem(row_position, 5, payment_status_item)
                
                # Add action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 2, 4, 2)
                
                # View button
                view_btn = QPushButton("View")
                view_btn.setToolTip("View Invoice")
                view_btn.clicked.connect(lambda checked, id=invoice['id']: self.view_invoice(id))
                actions_layout.addWidget(view_btn)
                
                # Payment Status Toggle button 
                current_status = invoice.get('payment_status', 'Pending')
                if current_status == 'Paid':
                    toggle_btn = QPushButton("Mark Pending")
                    toggle_btn.setStyleSheet("background-color: #CA7842; color: white;")
                    toggle_btn.setToolTip("Change status to Pending")
                    new_status = 'Pending'
                else:
                    toggle_btn = QPushButton("Mark Paid")
                    toggle_btn.setStyleSheet("background-color: #0D4715; color: white;")
                    toggle_btn.setToolTip("Change status to Paid")
                    new_status = 'Paid'
                
                toggle_btn.clicked.connect(lambda checked, id=invoice['id'], status=new_status: self.toggle_payment_status(id, status))
                actions_layout.addWidget(toggle_btn)
                
                # Delete button
                delete_btn = QPushButton("Delete")
                delete_btn.setToolTip("Delete Invoice")
                delete_btn.clicked.connect(lambda checked, id=invoice['id']: self.delete_invoice(id))
                actions_layout.addWidget(delete_btn)
                
                self.invoices_table.setCellWidget(row_position, 6, actions_widget)
                
                # Store invoice ID (hidden)
                self.invoices_table.setItem(row_position, 7, QTableWidgetItem(str(invoice['id'])))
            
            # Update statistics
            self.total_invoices_value.setText(str(total_count))
            self.paid_invoices_value.setText(str(paid_count))
            self.pending_invoices_value.setText(str(pending_count))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load invoices: {str(e)}")
            print(f"Detailed error: {e}")  # For debugging
    
    def should_display_invoice(self, invoice):
        """Check if the invoice matches current filters"""
        # Search filter
        search_text = self.search_input.text().lower()
        if search_text:
            invoice_matches = False
            # Check various fields for match
            for field in ['invoice_no', 'customer_name', 'customer_address', 'gstin']:
                if field in invoice and search_text in str(invoice[field]).lower():
                    invoice_matches = True
                    break
            if not invoice_matches:
                return False
        
        # Payment status filter
        status_filter = self.status_combo.currentText()
        if status_filter != "All" and invoice.get('payment_status') != status_filter:
            return False
        
        # Date filter
        if 'date' in invoice and invoice['date']:
            try:
                # Try different date formats
                invoice_date = None
                date_str = str(invoice['date'])
                
                # Try DD/MM/YYYY format
                if '/' in date_str:
                    invoice_date = QDate.fromString(date_str, "dd/MM/yyyy")
                    if not invoice_date.isValid():
                        invoice_date = QDate.fromString(date_str, "MM/dd/yyyy")
                # Try YYYY-MM-DD format
                elif '-' in date_str:
                    invoice_date = QDate.fromString(date_str, "yyyy-MM-dd")
                
                if invoice_date and invoice_date.isValid():
                    if not (self.date_from.date() <= invoice_date <= self.date_to.date()):
                        return False
            except Exception as e:
                print(f"Date parsing error for {invoice.get('date')}: {e}")
                # If date parsing fails, don't filter by date
                pass
        
        return True
    
    def apply_filters(self):
        """Apply filters to the invoices table"""
        self.load_invoices()
    
    def view_invoice(self, invoice_id):
        """Open the invoice preview window"""
        try:
            preview_window = InvoicePreviewWindow(invoice_id, self)
            preview_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open invoice preview: {str(e)}")
    
    def toggle_payment_status(self, invoice_id, new_status):
        """Toggle payment status between Paid and Pending"""
        try:
            # Show confirmation dialog
            current_status = "Pending" if new_status == "Paid" else "Paid"
            reply = QMessageBox.question(self, 
                                        "Confirm Status Change", 
                                        f"Change payment status from {current_status} to {new_status}?",
                                        QMessageBox.Yes | QMessageBox.No, 
                                        QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                success = update_payment_status(invoice_id, new_status)
                
                if success:
                    QMessageBox.information(self, "Success", f"Payment status updated to {new_status}")
                    self.load_invoices()  # Refresh the table to show updated status
                else:
                    QMessageBox.critical(self, "Error", "Failed to update payment status.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating payment status: {str(e)}")
    
    def delete_invoice(self, invoice_id):
        """Delete an invoice after confirmation"""
        reply = QMessageBox.question(self, 
                                    "Confirm Deletion", 
                                    "Are you sure you want to delete this invoice? This action cannot be undone.",
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                success = delete_invoice(invoice_id)
                
                if success:
                    QMessageBox.information(self, "Success", "Invoice deleted successfully.")
                    self.load_invoices()  # Refresh the table
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete invoice.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting invoice: {str(e)}")
    
    def export_to_csv(self):
        """Export the current invoice list to CSV"""
        try:
            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save CSV File", "", "CSV Files (*.csv)"
            )
            
            if not file_path:
                return  # User canceled
            
            # Add .csv extension if not provided
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                headers = ["Invoice #", "Date", "Customer Name", "Items", "Grand Total", "Payment Status"]
                writer.writerow(headers)
                
                # Write data rows
                for row in range(self.invoices_table.rowCount()):
                    row_data = []
                    for col in range(6):  # Only export visible columns, excluding Actions and ID
                        item = self.invoices_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Data exported successfully to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
    
    def create_new_invoice(self):
        """Open the Create Invoice window"""
        try:
            create_window = CreateInvoice(self)
            create_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open create invoice window: {str(e)}")