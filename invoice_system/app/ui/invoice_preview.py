from PySide6.QtWidgets import (QWidget, QLineEdit, QPushButton, QDialog, QVBoxLayout,
                            QLabel, QRadioButton, QButtonGroup, QDialogButtonBox,QTableWidget,
                            QMessageBox, QMainWindow, QTextEdit, QScrollArea, QFrame,QTableWidgetItem,
                            QHBoxLayout,QGridLayout,QHeaderView)
from PySide6.QtCore import Qt,QPoint,QRect,QMarginsF
from PySide6.QtGui import QFont, QPainter,QPixmap,QPdfWriter, QPageLayout, QPageSize,QRegion 
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
import os
import sqlite3

class InvoicePreviewWindow(QMainWindow):
    def __init__(self, invoice_id, parent=None):
        super().__init__(parent)
        self.invoice_id = invoice_id
        self.setWindowTitle("Invoice Preview")
        self.setStyleSheet("background-color:white")
        self.resize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create a scroll area for the invoice content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Create invoice content widget
        self.invoice_content = QWidget()
        self.content_layout = QVBoxLayout(self.invoice_content)
        
        # Load invoice data
        self.load_invoice_data()
        
        # Set the content widget to the scroll area
        scroll_area.setWidget(self.invoice_content)
        main_layout.addWidget(scroll_area)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        
        # Download/Print button
        self.download_button = QPushButton("Download Invoice")
        self.download_button.clicked.connect(self.download_invoice)
        button_layout.addWidget(self.download_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        # Add buttons to main layout
        main_layout.addLayout(button_layout)
    
    def load_invoice_data(self):
        """Load invoice data from database and display it"""
        try:
            conn = sqlite3.connect('invoice_app.db')
            conn.row_factory = sqlite3.Row  # Access columns by name
            cursor = conn.cursor()

            # Fetch invoice details
            cursor.execute("""
                SELECT * FROM invoices
                WHERE id = ?
            """, (self.invoice_id,))
            invoice = cursor.fetchone()

            if not invoice:
                self.content_layout.addWidget(QLabel("Invoice not found!"))
                return

            # Fetch invoice items
            cursor.execute("""
                SELECT * FROM invoice_items
                WHERE invoice_id = ?
            """, (self.invoice_id,))
            items = cursor.fetchall()

            # Fetch company info (assuming only one row with id = 1)
            cursor.execute("SELECT * FROM company_info WHERE id = 1")
            company = cursor.fetchone()
            print("Company Info:", dict(company) if company else "None")

            conn.close()

            # Display UI
            self.create_invoice_ui(invoice, items, company)

        except Exception as e:
            self.content_layout.addWidget(QLabel(f"Error loading invoice: {str(e)}"))



    def create_invoice_ui(self, invoice, items, company):
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # === INVOICE TITLE (centered at top) ===
        invoice_title = QLabel("INVOICE")
        invoice_title.setFont(QFont("Arial", 18, QFont.Bold))
        invoice_title.setAlignment(Qt.AlignLeft)
        self.content_layout.addWidget(invoice_title)

        # === Company Info and Logo Side by Side ===
        info_logo_layout = QHBoxLayout()

        # --- Company Info (Left Side) ---
        company_info_layout = QVBoxLayout()
        if company:
            name_label = QLabel(company["name"])
            name_label.setFont(QFont("Arial", 14, QFont.Bold))
            address_label = QLabel(company["address"])
            contact_label = QLabel(f"Contact: {company['contact']}")

            company_info_layout.addWidget(name_label)
            company_info_layout.addWidget(address_label)
            company_info_layout.addWidget(contact_label)
        else:
            company_info_layout.addWidget(QLabel("Company Info Not Found"))

        info_logo_layout.addLayout(company_info_layout, 3)  # More space for info

        # --- Logo (Right Side) ---
        logo_layout = QVBoxLayout()
        if company and company["logo_path"]:
            try:
                logo_label = QLabel()
                pixmap = QPixmap(company["logo_path"])
                logo_label.setPixmap(pixmap.scaledToWidth(100, Qt.SmoothTransformation))
                logo_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
                logo_layout.addWidget(logo_label)
            except Exception as e:
                print(f"Failed to load logo: {e}")

        info_logo_layout.addLayout(logo_layout, 1)  # Less space for logo

        # Add to main content layout
        self.content_layout.addLayout(info_logo_layout)

        # --- Separator ---
        self.content_layout.addWidget(self._separator_line())
        self.content_layout.addSpacing(10)

        # --- Customer Info Section ---
        customer_layout = QHBoxLayout()
        
        # Bill To
        bill_to_section = QVBoxLayout()
        bill_to_title = QLabel("BILL TO:")
        bill_to_title.setFont(QFont("Arial", 11, QFont.Bold))
        bill_to_section.addWidget(bill_to_title)
        bill_to_section.addWidget(QLabel(invoice['customer_name']))
        bill_to_section.addWidget(QLabel(invoice['customer_address']))
        bill_to_section.addWidget(QLabel(f"GSTIN: {invoice['gstin']}"))
        bill_to_section.addWidget(QLabel(f"State: {invoice['state']}"))
        bill_to_section.addWidget(QLabel(f"State Code: {invoice['state_code']}"))
        customer_layout.addLayout(bill_to_section)
        
        # Ship To
        ship_to_section = QVBoxLayout()
        ship_to_title = QLabel("SHIP TO:")
        ship_to_title.setFont(QFont("Arial", 11, QFont.Bold))
        ship_to_section.addWidget(ship_to_title)
        ship_to_section.addWidget(QLabel(invoice['customer_name']))
        ship_to_section.addWidget(QLabel(invoice['customer_address']))
        ship_to_section.addWidget(QLabel(f"GSTIN: {invoice['gstin']}"))
        ship_to_section.addWidget(QLabel(f"State: {invoice['state']}"))
        ship_to_section.addWidget(QLabel(f"State Code: {invoice['state_code']}"))
        customer_layout.addLayout(ship_to_section)
        
        # Invoice Details
        invoice_details_section = QVBoxLayout()
        invoice_details_title = QLabel("INVOICE DETAILS")
        invoice_details_title.setFont(QFont("Arial", 11, QFont.Bold))
        invoice_details_section.addWidget(invoice_details_title)
        invoice_details_section.addWidget(QLabel(f"Invoice No.: {invoice['invoice_no']}"))
        invoice_details_section.addWidget(QLabel(f"Invoice Date: {invoice['date']}"))
        invoice_details_section.addWidget(QLabel(f"Payment Status: {invoice['payment_status']}"))
        customer_layout.addLayout(invoice_details_section)
        
        self.content_layout.addLayout(customer_layout)
        self.content_layout.addSpacing(15)

        # --- Items Table ---
        items_label = QLabel("Invoice Items")
        items_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.content_layout.addWidget(items_label)

        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels(["Sl No.", "Description", "HSN/SAC", "Quantity", "Type", "Rate", "GST%", "Total"])
        table.setRowCount(len(items))

        for row, item in enumerate(items):
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))  # Auto increment
            table.setItem(row, 1, QTableWidgetItem(item["description"]))
            table.setItem(row, 2, QTableWidgetItem(item["hsn"]))
            table.setItem(row, 3, QTableWidgetItem(str(item["quantity"])))
            table.setItem(row, 4, QTableWidgetItem(item["type"]))
            table.setItem(row, 5, QTableWidgetItem(f"{item['rate']:.2f}"))
            table.setItem(row, 6, QTableWidgetItem(f"{item['gst_percent']}%"))
            table.setItem(row, 7, QTableWidgetItem(f"{item['total']:.2f}"))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)

        self.content_layout.addWidget(table)

        # --- Separator ---
        self.content_layout.addWidget(self._separator_line())

        # --- Totals ---
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        total_label = QLabel(f"Grand Total: ₹{invoice['grand_total']:.2f}")
        total_label.setFont(QFont("Arial", 12, QFont.Bold))
        totals_layout.addWidget(total_label)
        self.content_layout.addLayout(totals_layout)

        # --- Notes ---
        if hasattr(self, 'show_notes') and self.show_notes:
            self.content_layout.addSpacing(20)
            notes_title = QLabel("Notes:")
            notes_title.setFont(QFont("Arial", 10, QFont.Bold))
            self.content_layout.addWidget(notes_title)
            self.content_layout.addWidget(QLabel("Thank you for your business!"))

    # Helper method
    def _separator_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line


    # Helper method
    def _separator_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def download_invoice(self):
        folder_path = r"C:\Users\91863\OneDrive\Desktop\Practice\Invoices_pdf"
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_name = f"Invoice_{self.invoice_id}.pdf"
        file_path = os.path.join(folder_path, file_name)

        try:
            # PDF writer setup
            pdf_writer = QPdfWriter(file_path)
            pdf_writer.setPageSize(QPageSize(QPageSize.A4))
            pdf_writer.setPageMargins(QMarginsF(10, 10, 10, 10), QPageLayout.Millimeter)

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

            # ✅ Correct render call
            self.invoice_content.render(
                painter,
                QPoint(0, 0),
                QRegion(self.invoice_content.rect()),
                QWidget.RenderFlags(QWidget.DrawChildren)
            )

            painter.end()
            QMessageBox.information(self, "Success", f"Invoice saved to:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF:\n{str(e)}")

