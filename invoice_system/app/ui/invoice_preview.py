from PySide6.QtWidgets import (QWidget, QLineEdit, QPushButton, QDialog, QVBoxLayout,
                            QLabel, QRadioButton, QButtonGroup, QDialogButtonBox, QTableWidget,
                            QMessageBox, QMainWindow, QTextEdit, QScrollArea, QFrame, QTableWidgetItem,
                            QHBoxLayout, QGridLayout, QHeaderView, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QPoint, QRect, QMarginsF, QSize
from PySide6.QtGui import QFont, QPainter, QPixmap, QPdfWriter, QPageLayout, QPageSize, QRegion, QColor
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
import os
import sqlite3
from ..models.db_manager import calculate_and_insert_invoice_taxes

class InvoicePreviewWindow(QMainWindow):
    def __init__(self, invoice_id, parent=None):
        super().__init__(parent)
        self.invoice_id = invoice_id
        #self.conn = sqlite3.connect('invoice_app.db')

        self.setWindowTitle("Invoice Preview")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        # Set main window styles
        self.setStyleSheet("""
            QMainWindow { 
                background-color: white; 
            }
            QLabel {
                color: #000000;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                background-color: transparent;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #000000;
                gridline-color: #000000;
                selection-background-color: #f5f5f5;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QHeaderView::section {
                background-color: white;
                border: 1px solid #000000;
                padding: 8px 12px;
                font-weight: 600;
                color: #000000;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QPushButton {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 14px;
                font-weight: 500;
                padding: 12px 24px;
                border-radius: 6px;
                border: none;
                min-width: 120px;
            }
            QPushButton#downloadButton {
                background-color: #007bff;
                color: white;
            }
            QPushButton#downloadButton:hover {
                background-color: #0056b3;
            }
            QPushButton#closeButton {
                background-color: #6c757d;
                color: white;
            }
            QPushButton#closeButton:hover {
                background-color: #545b62;
            }
            QFrame#separatorLine {
                background-color: #000000;
                border: none;
                max-height: 1px;
                min-height: 1px;
            }
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        # Initialize UI
        self.init_ui()
        
        # Load invoice data
        self.load_invoice_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create scroll area for invoice content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create invoice content widget
        self.invoice_content = QWidget()
        self.invoice_content.setStyleSheet("background-color: white;")
        self.content_layout = QVBoxLayout(self.invoice_content)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(25)
        
        # Set content to scroll area
        self.scroll_area.setWidget(self.invoice_content)
        main_layout.addWidget(self.scroll_area)
        
        # Bottom buttons
        self.create_bottom_buttons(main_layout)
    
    def create_bottom_buttons(self, parent_layout):
        """Create bottom action buttons"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Add stretch to push buttons to the right
        button_layout.addStretch()
        
        # Download PDF button
        self.download_button = QPushButton("Download Invoice")
        self.download_button.setObjectName("downloadButton")
        self.download_button.clicked.connect(self.download_invoice)
        button_layout.addWidget(self.download_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        parent_layout.addLayout(button_layout)
    
    def load_invoice_data(self):
        """Load invoice data from database and display it"""
        try:
            conn = sqlite3.connect('invoice_app.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Fetch invoice details
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (self.invoice_id,))
            invoice = cursor.fetchone()

            if not invoice:
                error_label = QLabel("Invoice not found!")
                error_label.setStyleSheet("color: #dc3545; font-weight: bold;")
                self.content_layout.addWidget(error_label)
                return

            # Fetch invoice items
            cursor.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (self.invoice_id,))
            items = cursor.fetchall()

            # Fetch company info
            cursor.execute("SELECT * FROM company_info WHERE id = 1")
            company = cursor.fetchone()

            conn.close()

            # Ensure tax data exists and is up to date
            self.ensure_tax_data_exists(self.invoice_id)
            
            # Fetch updated tax data after ensuring it exists
            conn = sqlite3.connect('invoice_app.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoice_taxes WHERE invoice_id = ?", (self.invoice_id,))
            taxes = cursor.fetchall()
            conn.close()

            # Display UI with tax data
            self.create_invoice_ui(invoice, items, company, taxes)

        except Exception as e:
            error_label = QLabel(f"Error loading invoice: {str(e)}")
            error_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.content_layout.addWidget(error_label)

    def create_invoice_ui(self, invoice, items, company, taxes):
        """Create the complete invoice UI"""
        # Clear existing content
        self.clear_layout(self.content_layout)
        
        # === TITLE ===
        self.create_title()
        
        # === HEADER SECTION (Company Info + Logo) ===
        self.create_header_section(company)
        
        # === SEPARATOR ===
        self.content_layout.addWidget(self.create_separator())
        
        # === DETAILS SECTION (Customer + Invoice Details) ===
        self.create_details_section(invoice)
        
        # === ITEMS TABLE ===
        self.create_items_table(items)

        # === TAX BREAKDOWN ===
        # Call the tax breakdown method with the correct invoice_id
        self.create_tax_breakdown_section(self.invoice_id)
        
        # === GRAND TOTAL ===
        self.create_grand_total_section(invoice['grand_total'])
        
        # === FOOTER NOTES ===
        self.create_footer_notes()

    
    def create_title(self):
        """Create centered title"""
        title_layout = QHBoxLayout()
        title_label = QLabel("INVOICE")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #000000; margin: 10px 0 20px 0; letter-spacing: 2px;")
        title_layout.addWidget(title_label)
        self.content_layout.addLayout(title_layout)
    
    def create_header_section(self, company):
        """Create header with company info and logo"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(40)
        
        # Company Information (Left)
        company_widget = QWidget()
        company_layout = QVBoxLayout(company_widget)
        company_layout.setContentsMargins(0, 0, 0, 0)
        company_layout.setSpacing(8)
        
        # Company name
        company_name = QLabel(company["name"] if company else "Company Name Not Available")
        company_name.setFont(QFont("Segoe UI", 18, QFont.Bold))
        company_name.setStyleSheet("color: #000000; margin-bottom: 5px;")
        company_layout.addWidget(company_name)
        
        # Company address
        company_address = QLabel(company["address"] if company else "Address Not Available")
        company_address.setFont(QFont("Segoe UI", 12))
        company_address.setStyleSheet("color: #000000; line-height: 1.4;")
        company_address.setWordWrap(True)
        company_layout.addWidget(company_address)
        
        # Company contact
        company_contact = QLabel(f"Contact: {company['contact']}" if company else "Contact Not Available")
        company_contact.setFont(QFont("Segoe UI", 12))
        company_contact.setStyleSheet("color: #000000;")
        company_layout.addWidget(company_contact)
        
        company_layout.addStretch()
        header_layout.addWidget(company_widget, 3)
        
        # Logo Section (Right)
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_label = QLabel()
        if company and company["logo_path"]:
            try:
                pixmap = QPixmap(company["logo_path"])
                if not pixmap.isNull():
                    logo_label.setPixmap(pixmap.scaledToWidth(150, Qt.SmoothTransformation))
            except Exception as e:
                print(f"Failed to load logo: {e}")
        
        # Placeholder if no logo
        if logo_label.pixmap() is None or logo_label.pixmap().isNull():
            logo_label.setText("COMPANY\nLOGO")
            logo_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
            logo_label.setStyleSheet("""
                color: #666666; 
                border: 2px solid #000000; 
                padding: 30px; 
                text-align: center;
                background-color: #f8f9fa;
            """)
            logo_label.setFixedSize(150, 100)
        
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        
        header_layout.addWidget(logo_widget, 1)
        self.content_layout.addLayout(header_layout)
    
    def create_details_section(self, invoice):
        """Create customer and invoice details section with three boxes"""
        details_layout = QHBoxLayout()
        details_layout.setSpacing(20)
        
        # Bill To Section (Left)
        bill_to_section = self.create_bill_to_section(invoice)
        details_layout.addWidget(bill_to_section, 1)
        
        # Ship To Section (Middle)
        ship_to_section = self.create_ship_to_section(invoice)
        details_layout.addWidget(ship_to_section, 1)
        
        # Invoice Details Section (Right)
        invoice_section = self.create_invoice_details_section(invoice)
        details_layout.addWidget(invoice_section, 1)
        
        self.content_layout.addLayout(details_layout)
    
    def create_bill_to_section(self, invoice):
        """Create Bill To section"""
        bill_widget = QWidget()
        bill_widget.setStyleSheet("border: 1px solid #000000; padding: 15px; background-color: white;")
        bill_layout = QVBoxLayout(bill_widget)
        bill_layout.setSpacing(15)
        
        # Bill To Section
        bill_title = QLabel("BILL TO:")
        bill_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        bill_title.setStyleSheet("color: #000000; border: none; padding: 0; margin-bottom: 5px;")
        bill_layout.addWidget(bill_title)
        
        bill_details = [
            invoice['customer_name'] if invoice['customer_name'] else 'N/A',
            invoice['customer_address'] if invoice['customer_address'] else 'N/A',
            f"GSTIN: {invoice['gstin']}" if invoice['gstin'] else 'GSTIN: N/A',
            f"State: {invoice['state']}" if invoice['state'] else 'State: N/A',
            f"State Code: {invoice['state_code']}" if invoice['state_code'] else 'State Code: N/A'
        ]
        
        for detail in bill_details:
            if detail and 'N/A' not in detail:
                detail_label = QLabel(str(detail))
                detail_label.setFont(QFont("Segoe UI", 11))
                detail_label.setStyleSheet("color: #000000; border: none; padding: 0; margin-bottom: 3px;")
                detail_label.setWordWrap(True)
                bill_layout.addWidget(detail_label)
        
        bill_layout.addStretch()
        return bill_widget

    def create_ship_to_section(self, invoice):
        """Create Ship To section"""
        ship_widget = QWidget()
        ship_widget.setStyleSheet("border: 1px solid #000000; padding: 15px; background-color: white;")
        ship_layout = QVBoxLayout(ship_widget)
        ship_layout.setSpacing(15)
        
        # Ship To Section
        ship_title = QLabel("SHIP TO:")
        ship_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        ship_title.setStyleSheet("color: #000000; border: none; padding: 0; margin-bottom: 5px;")
        ship_layout.addWidget(ship_title)
        
        ship_details = [
            invoice['customer_name'] if invoice['customer_name'] else 'N/A',
            invoice['customer_address'] if invoice['customer_address'] else 'N/A',
            f"GSTIN: {invoice['gstin']}" if invoice['gstin'] else 'GSTIN: N/A',
            f"State: {invoice['state']}" if invoice['state'] else 'State: N/A',
            f"State Code: {invoice['state_code']}" if invoice['state_code'] else 'State Code: N/A'
        ]
        
        for detail in ship_details:
            if detail and 'N/A' not in detail:
                detail_label = QLabel(str(detail))
                detail_label.setFont(QFont("Segoe UI", 11))
                detail_label.setStyleSheet("color: #000000; border: none; padding: 0; margin-bottom: 3px;")
                detail_label.setWordWrap(True)
                ship_layout.addWidget(detail_label)
        
        ship_layout.addStretch()
        return ship_widget

    def create_invoice_details_section(self, invoice):
        """Create invoice details section"""
        invoice_widget = QWidget()
        invoice_widget.setStyleSheet("border: 1px solid #000000; padding: 15px; background-color: white;")
        invoice_layout = QVBoxLayout(invoice_widget)
        invoice_layout.setSpacing(8)
        
        # Title
        title = QLabel("INVOICE DETAILS")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #000000; border: none; padding: 0; margin-bottom: 10px;")
        invoice_layout.addWidget(title)
        
        # Invoice details
        details = [
            ("Invoice No:", invoice['invoice_no']),
            ("Invoice Date:", invoice['date']),
            ("Payment Status:", invoice['payment_status'])
        ]
        
        for label_text, value in details:
            if value and value != 'N/A':
                detail_layout = QVBoxLayout()
                detail_layout.setSpacing(2)
                
                label = QLabel(label_text)
                label.setFont(QFont("Segoe UI", 10, QFont.Bold))
                label.setStyleSheet("color: #000000; border: none; padding: 0;")
                
                value_label = QLabel(str(value))
                value_label.setFont(QFont("Segoe UI", 11))
                value_label.setStyleSheet("color: #000000; border: none; padding: 0; margin-bottom: 8px;")
                
                detail_layout.addWidget(label)
                detail_layout.addWidget(value_label)
                invoice_layout.addLayout(detail_layout)
        
        invoice_layout.addStretch()
        return invoice_widget
    
    def create_items_table(self, items):
        """Create items table"""
        # Table title
        table_title = QLabel("INVOICE ITEMS")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        table_title.setAlignment(Qt.AlignCenter)
        table_title.setStyleSheet("color: #000000; margin: 25px 0 15px 0;")
        self.content_layout.addWidget(table_title)
        
        # Create table
        table = QTableWidget()
        table.setColumnCount(8)
        headers = ["Sl No.", "Description", "HSN/SAC", "Quantity", "Type", "Rate", "GST%", "Total"]
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(items))
        table.setStyleSheet("""
            QTableWidget {
                font: 11pt "Segoe UI";
                gridline-color: black;
                border: 1px solid black;
            }
            QTableWidget::item {
                background-color: #f8f9fa;
                padding: 8px;
                border-right: 1px solid #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                font-weight: bold;
                border: 1px solid black;
                padding: 10px;
            }
        """)
        
        # Populate table
        for row, item in enumerate(items):
            # Serial number
            sl_item = QTableWidgetItem(str(row + 1))
            sl_item.setTextAlignment(Qt.AlignCenter)
            sl_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 0, sl_item)
            
            # Description
            desc_item = QTableWidgetItem(item["description"] or "")
            desc_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 1, desc_item)
            
            # HSN/SAC
            hsn_item = QTableWidgetItem(item["hsn"] or "")
            hsn_item.setTextAlignment(Qt.AlignCenter)
            hsn_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 2, hsn_item)
            
            # Quantity
            qty_item = QTableWidgetItem(str(item["quantity"]) if item["quantity"] else "0")
            qty_item.setTextAlignment(Qt.AlignRight)
            qty_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 3, qty_item)
            
            # Type
            type_item = QTableWidgetItem(item["type"] or "")
            type_item.setTextAlignment(Qt.AlignCenter)
            type_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 4, type_item)
            
            # Rate
            rate_item = QTableWidgetItem(f"₹{item['rate']:.2f}" if item["rate"] else "₹0.00")
            rate_item.setTextAlignment(Qt.AlignRight)
            rate_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 5, rate_item)
            
            # GST%
            gst_item = QTableWidgetItem(f"{item['gst_percent']}%" if item["gst_percent"] else "0%")
            gst_item.setTextAlignment(Qt.AlignCenter)
            gst_item.setFont(QFont("Segoe UI", 11))
            table.setItem(row, 6, gst_item)
            
            # Total
            total_item = QTableWidgetItem(f"₹{item['total']:.2f}" if item["total"] else "₹0.00")
            total_item.setTextAlignment(Qt.AlignRight)
            total_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            table.setItem(row, 7, total_item)
        
        # Configure table
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.verticalHeader().setVisible(False)
        
        # Set column widths
        table.setColumnWidth(0, 60)   # Sl No
        table.setColumnWidth(2, 80)   # HSN
        table.setColumnWidth(3, 80)   # Quantity  
        table.setColumnWidth(4, 60)   # Type
        table.setColumnWidth(5, 100)  # Rate
        table.setColumnWidth(6, 70)   # GST%
        table.setColumnWidth(7, 120)  # Total
        
        # Description column stretches
        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Set table height
        row_height = 35
        header_height = 40
        table_height = (len(items) * row_height) + header_height + 10
        table.setFixedHeight(min(table_height, 400))
        
        self.content_layout.addWidget(table)
    
    def create_grand_total_section(self, grand_total):
        """Create grand total section"""
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        
        # Grand total box
        total_widget = QWidget()
        total_widget.setStyleSheet("""
            QWidget {
                border: 2px solid #000000;
                background-color: white;
                padding: 20px;
            }
        """)
        
        total_inner_layout = QHBoxLayout(total_widget)
        total_inner_layout.setSpacing(20)
        
        total_label = QLabel("GRAND TOTAL:")
        total_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        total_label.setStyleSheet("color: #000000; border: none; background: transparent;")
        
        total_amount = QLabel(f"₹{grand_total:.2f}")
        total_amount.setFont(QFont("Segoe UI", 18, QFont.Bold))
        total_amount.setStyleSheet("color: #000000; border: none; background: transparent;")
        
        total_inner_layout.addWidget(total_label)
        total_inner_layout.addWidget(total_amount)
        
        total_layout.addWidget(total_widget)
        self.content_layout.addLayout(total_layout)
    
    def create_footer_notes(self):
        """Create footer notes section"""
        self.content_layout.addSpacing(30)
        
        notes_widget = QWidget()
        notes_widget.setStyleSheet("""
            QWidget {
                border: 1px solid #000000;
                background-color: white;
                padding: 20px;
            }
        """)
        
        notes_layout = QVBoxLayout(notes_widget)
        notes_layout.setSpacing(10)
        
        notes_title = QLabel("NOTES:")
        notes_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        notes_title.setStyleSheet("color: #000000; border: none; background: transparent;")
        
        notes_text = QLabel("Thank you for your business!")
        notes_text.setFont(QFont("Segoe UI", 11))
        notes_text.setStyleSheet("color: #000000; border: none; background: transparent; line-height: 1.5;")
        notes_text.setWordWrap(True)
        
        notes_layout.addWidget(notes_title)
        notes_layout.addWidget(notes_text)
        
        self.content_layout.addWidget(notes_widget)

   # Add this method to your InvoicePreviewWindow class

    def get_tax_breakdown_from_db(self, invoice_id):
        """Get tax breakdown from invoice_taxes table"""
        try:
            conn = sqlite3.connect('invoice_app.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if not invoice_id:
                return []
            
            # Get all tax records for this invoice, ordered by GST rate
            cursor.execute("""
                SELECT gst_percent, sgst_amount, cgst_amount, igst_amount, tax_total
                FROM invoice_taxes 
                WHERE invoice_id = ?
                ORDER BY gst_percent
            """, (invoice_id,))
            
            tax_records = cursor.fetchall()
            
            # Convert to list of dictionaries
            return [dict(record) for record in tax_records]
            
        except Exception as e:
            print(f"Error fetching tax breakdown: {e}")
            return []
        finally:
            if conn:
                conn.close()


    def create_tax_breakdown_section(self, invoice_id=None):
        """Create tax breakdown section using database data"""
        tax_title = QLabel("TAX BREAKDOWN")
        tax_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        tax_title.setAlignment(Qt.AlignCenter)
        tax_title.setStyleSheet("color: #000000; margin: 25px 0 15px 0;")
        self.content_layout.addWidget(tax_title)
        
        # Get tax breakdown from database
        tax_breakdown = self.get_tax_breakdown_from_db(invoice_id) if invoice_id else []
        
        if not tax_breakdown:
            # Show message if no tax data available
            no_tax_label = QLabel("No tax data available for this invoice.")
            no_tax_label.setAlignment(Qt.AlignCenter)
            no_tax_label.setStyleSheet("color: #666; font-style: italic; margin: 20px;")
            self.content_layout.addWidget(no_tax_label)
            return
        
        # Create tax table
        tax_table = QTableWidget()
        tax_table.setColumnCount(6)  # Added one more column for Taxable Amount
        tax_headers = ["GST Rate", "Total Amount", "SGST Amount", "CGST Amount", "IGST Amount", "Total Tax"]
        tax_table.setHorizontalHeaderLabels(tax_headers)
        
        tax_table.setRowCount(len(tax_breakdown) + 1)  # +1 for total row
        tax_table.setStyleSheet("""
            QTableWidget {
                font: 11pt "Segoe UI";
                gridline-color: black;
                border: 1px solid black;
            }
            QTableWidget::item {
                background-color: #f8f9fa;
                padding: 8px;
                border-right: 1px solid #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                font-weight: bold;
                border: 1px solid black;
                padding: 10px;
            }
        """)
        
        # Variables to track totals
        total_taxable = 0.0
        total_sgst = 0.0
        total_cgst = 0.0
        total_igst = 0.0
        grand_tax_total = 0.0
        
        # Get taxable amounts for each GST rate
        try:
            conn = sqlite3.connect('invoice_app.db')
            cursor = conn.cursor()
            
            # Populate tax table
            for row, tax in enumerate(tax_breakdown):
                gst_percent = tax['gst_percent']
                
                # Get taxable amount for this GST rate
                cursor.execute("""
                    SELECT SUM(total) as taxable_amount
                    FROM invoice_items 
                    WHERE invoice_id = ? AND gst_percent = ?
                """, (invoice_id, gst_percent))
                
                result = cursor.fetchone()
                taxable_amount = result[0] if result[0] else 0.0
                
                # GST Rate
                rate_item = QTableWidgetItem(f"{gst_percent}%")
                rate_item.setTextAlignment(Qt.AlignCenter)
                tax_table.setItem(row, 0, rate_item)
                
                # Taxable Amount
                taxable_item = QTableWidgetItem(f"₹{taxable_amount:.2f}")
                taxable_item.setTextAlignment(Qt.AlignRight)
                tax_table.setItem(row, 1, taxable_item)
                total_taxable += taxable_amount
                
                # SGST Amount
                sgst_amount = tax['sgst_amount']
                sgst_item = QTableWidgetItem(f"₹{sgst_amount:.2f}")
                sgst_item.setTextAlignment(Qt.AlignRight)
                tax_table.setItem(row, 2, sgst_item)
                total_sgst += sgst_amount
                
                # CGST Amount
                cgst_amount = tax['cgst_amount']
                cgst_item = QTableWidgetItem(f"₹{cgst_amount:.2f}")
                cgst_item.setTextAlignment(Qt.AlignRight)
                tax_table.setItem(row, 3, cgst_item)
                total_cgst += cgst_amount
                
                # IGST Amount
                igst_amount = tax['igst_amount']
                igst_item = QTableWidgetItem(f"₹{igst_amount:.2f}")
                igst_item.setTextAlignment(Qt.AlignRight)
                tax_table.setItem(row, 4, igst_item)
                total_igst += igst_amount
                
                # Total Tax
                tax_total = tax['tax_total']
                total_item = QTableWidgetItem(f"₹{tax_total:.2f}")
                total_item.setTextAlignment(Qt.AlignRight)
                tax_table.setItem(row, 5, total_item)
                grand_tax_total += tax_total
            
            conn.close()
            
        except Exception as e:
            print(f"Error getting taxable amounts: {e}")
            if conn:
                conn.close()
        
        # Add total row
        if tax_breakdown:
            total_row = len(tax_breakdown)
            
            # Total label
            total_label_item = QTableWidgetItem("TOTAL")
            total_label_item.setTextAlignment(Qt.AlignCenter)
            total_label_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            total_label_item.setBackground(QColor("#e8f4fd"))
            tax_table.setItem(total_row, 0, total_label_item)
            
            # Total amounts
            totals_data = [
                (1, f"₹{total_taxable:.2f}"),
                (2, f"₹{total_sgst:.2f}"),
                (3, f"₹{total_cgst:.2f}"),
                (4, f"₹{total_igst:.2f}"),
                (5, f"₹{grand_tax_total:.2f}")
            ]
            
            for col, text in totals_data:
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignRight)
                item.setFont(QFont("Segoe UI", 11, QFont.Bold))
                item.setBackground(QColor("#e8f4fd"))
                tax_table.setItem(total_row, col, item)
        
        # Configure table
        tax_table.setEditTriggers(QTableWidget.NoEditTriggers)
        tax_table.setSelectionMode(QTableWidget.NoSelection)
        tax_table.verticalHeader().setVisible(False)
        
        # Set column widths
        tax_table.setColumnWidth(0, 80)   # GST Rate
        tax_table.setColumnWidth(1, 120)  # Taxable Amount
        tax_table.setColumnWidth(2, 110)  # SGST Amount
        tax_table.setColumnWidth(3, 110)  # CGST Amount
        tax_table.setColumnWidth(4, 110)  # IGST Amount
        tax_table.setColumnWidth(5, 120)  # Total Tax
        
        # Set table height based on content
        row_height = 35
        header_height = 45
        table_height = ((len(tax_breakdown) + 1) * row_height) + header_height + 10
        tax_table.setFixedHeight(min(table_height, 400))
        
        # Make table width fit content
        total_width = sum([80, 120, 110, 110, 110, 120]) + 20  # column widths + padding
        tax_table.setFixedWidth(total_width)
        
        self.content_layout.addWidget(tax_table)


    # Additional helper function to ensure tax data exists when viewing invoice
    def ensure_tax_data_exists(self, invoice_id):
        """Ensure tax data exists in invoice_taxes table for the given invoice"""
        try:
            conn = sqlite3.connect('invoice_app.db')
            cursor = conn.cursor()
            
            # Check if tax data already exists
            cursor.execute("SELECT COUNT(*) FROM invoice_taxes WHERE invoice_id = ?", (invoice_id,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Tax data doesn't exist, calculate and insert it
                print(f"Tax data missing for invoice {invoice_id}, calculating...")
                conn.close()
                calculate_and_insert_invoice_taxes(invoice_id)
            else:
                conn.close()
                
        except Exception as e:
            print(f"Error checking tax data: {e}")
            if conn:
                conn.close()
    
    def create_separator(self):
        """Create a separator line"""
        line = QFrame()
        line.setObjectName("separatorLine")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        return line

    def download_invoice(self):
        """Download invoice as PDF"""
        folder_path = r"C:\Users\91863\OneDrive\Desktop\Practice\Invoices_pdf"
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_name = f"Invoice_{self.invoice_id}.pdf"
        file_path = os.path.join(folder_path, file_name)

        try:
            # PDF writer setup
            pdf_writer = QPdfWriter(file_path)
            pdf_writer.setPageSize(QPageSize(QPageSize.A4))
            pdf_writer.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Millimeter)

            # Create painter
            painter = QPainter(pdf_writer)
            if not painter.isActive():
                raise RuntimeError("Painter could not start on PDF writer")

            # Scale widget to fit width of PDF page
            self.invoice_content.adjustSize()
            widget_width = self.invoice_content.width()
            pdf_width = pdf_writer.width()
            scale = pdf_width / widget_width
            painter.scale(scale, scale)

            # Render the invoice content
            self.invoice_content.render(
                painter,
                QPoint(0, 0),
                QRegion(self.invoice_content.rect()),
                QWidget.RenderFlags(QWidget.DrawChildren)
            )

            painter.end()
            
            # Success message
            msg = QMessageBox(self)
            msg.setWindowTitle("Success")
            msg.setText("Invoice saved successfully!")
            msg.setDetailedText(f"File saved at:\n{file_path}")
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #212529;
                }
            """)
            msg.exec()

        except Exception as e:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Error")
            error_msg.setText("Failed to generate PDF")
            error_msg.setDetailedText(str(e))
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #212529;
                }
            """)
            error_msg.exec()
    
    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()