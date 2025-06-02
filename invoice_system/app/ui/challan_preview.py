from PySide6.QtWidgets import (QWidget, QLineEdit, QPushButton, QDialog, QVBoxLayout,
                            QLabel, QRadioButton, QButtonGroup, QDialogButtonBox, QTableWidget,
                            QMessageBox, QMainWindow, QTextEdit, QScrollArea, QFrame, QTableWidgetItem,
                            QHBoxLayout, QGridLayout, QHeaderView, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QPoint, QRect, QMarginsF, QSize
from PySide6.QtGui import QFont, QPainter, QPixmap, QPdfWriter, QPageLayout, QPageSize, QRegion, QColor
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
import os
import sqlite3

class ChallanPreview_Window(QMainWindow):
    def __init__(self, challan_id, parent=None):
        super().__init__(parent)
        self.challan_id = challan_id
        self.setWindowTitle("Delivery Challan Preview")
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
        
        # Load challan data
        self.load_challan_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create scroll area for challan content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create challan content widget
        self.challan_content = QWidget()
        self.challan_content.setStyleSheet("background-color: white;")
        self.content_layout = QVBoxLayout(self.challan_content)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(25)
        
        # Set content to scroll area
        self.scroll_area.setWidget(self.challan_content)
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
        self.download_button = QPushButton("Download PDF")
        self.download_button.setObjectName("downloadButton")
        self.download_button.clicked.connect(self.download_challan)
        button_layout.addWidget(self.download_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        parent_layout.addLayout(button_layout)
    
    def load_challan_data(self):
        """Load challan data from database and display it"""
        try:
            conn = sqlite3.connect('invoice_app.db')
            conn.row_factory = sqlite3.Row  # Access columns by name
            cursor = conn.cursor()

            # Fetch challan details
            cursor.execute("""
                SELECT * FROM challans
                WHERE id = ?
            """, (self.challan_id,))
            challan = cursor.fetchone()

            if not challan:
                self.content_layout.addWidget(QLabel("Challan not found!"))
                return

            # Fetch challan items
            cursor.execute("""
                SELECT * FROM challan_items
                WHERE challan_id = ?
            """, (self.challan_id,))
            items = cursor.fetchall()

            # Fetch company info (assuming only one row with id = 1)
            cursor.execute("SELECT * FROM company_info WHERE id = 1")
            company = cursor.fetchone()

            conn.close()

            # Display UI
            self.create_challan_ui(challan, items, company)

        except Exception as e:
            error_label = QLabel(f"Error loading challan: {str(e)}")
            error_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.content_layout.addWidget(error_label)
    
    def create_challan_ui(self, challan, items, company):
        """Create the complete challan UI"""
        # Clear existing content
        self.clear_layout(self.content_layout)
        
        # === TITLE ===
        self.create_title()
        
        # === HEADER SECTION (Company Info + Logo) ===
        self.create_header_section(company)
        
        # === SEPARATOR ===
        self.content_layout.addWidget(self.create_separator())
        
        # === DETAILS SECTION (Customer + Challan Details) ===
        self.create_details_section(challan)
        
        # === ITEMS TABLE ===
        self.create_items_table(items)
        
        # === GRAND TOTAL ===
        self.create_grand_total_section(challan['grand_total'])
        
        # === FOOTER NOTES ===
        self.create_footer_notes()
    
    def create_title(self):
        """Create centered title"""
        title_layout = QHBoxLayout()
        title_label = QLabel("DELIVERY CHALLAN")
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
    
    def create_details_section(self, challan):
        """Create customer and challan details section"""
        details_layout = QHBoxLayout()
        details_layout.setSpacing(50)
        
        # Customer Details (Left)
        customer_section = self.create_customer_section(challan)
        details_layout.addWidget(customer_section, 1)
        
        # Challan Details (Right)
        challan_section = self.create_challan_details_section(challan)
        details_layout.addWidget(challan_section, 1)
        
        self.content_layout.addLayout(details_layout)
    
    def create_customer_section(self, challan):
        """Create customer/consignee section"""
        customer_widget = QWidget()
        customer_widget.setStyleSheet("border: 1px solid #000000; padding: 15px; background-color: white;")
        customer_layout = QVBoxLayout(customer_widget)
        customer_layout.setSpacing(8)
        
        # Title
        title = QLabel("CONSIGNEE DETAILS")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #000000; border: none; padding: 0; margin-bottom: 10px;")
        customer_layout.addWidget(title)
        
        # Customer details
        details = [
            ("Name:", challan['customer_name'] if challan['customer_name'] else 'N/A'),
            ("Address:", challan['customer_address'] if challan['customer_address'] else 'N/A'),
            ("GSTIN:", challan['gstin'] if challan['gstin'] else 'N/A'),
            ("State:", challan['state'] if challan['state'] else 'N/A'),
            ("State Code:", challan['state_code'] if challan['state_code'] else 'N/A')
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
                value_label.setWordWrap(True)
                
                detail_layout.addWidget(label)
                detail_layout.addWidget(value_label)
                customer_layout.addLayout(detail_layout)
        
        customer_layout.addStretch()
        return customer_widget
    
    def create_challan_details_section(self, challan):
        """Create challan details section"""
        challan_widget = QWidget()
        challan_widget.setStyleSheet("border: 1px solid #000000; padding: 15px; background-color: white;")
        challan_layout = QVBoxLayout(challan_widget)
        challan_layout.setSpacing(8)
        
        # Title
        title = QLabel("CHALLAN DETAILS")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #000000; border: none; padding: 0; margin-bottom: 10px;")
        challan_layout.addWidget(title)
        
        # Challan details
        details = [
            ("Challan No:", challan['challan_no']),
            ("Date:", challan['date']),
        ]
        
        # Add transport details if available
        if challan['vehicle'] and challan['vehicle'].strip():
            details.append(("Vehicle No:", challan['vehicle']))
        if challan['transporter'] and challan['transporter'].strip():
            details.append(("Transporter:", challan['transporter']))
        if challan['lr'] and challan['lr'].strip():
            details.append(("LR No:", challan['lr']))
        
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
                challan_layout.addLayout(detail_layout)
        
        challan_layout.addStretch()
        return challan_widget
    
    def create_items_table(self, items):
        """Create items table"""
        # Table title
        table_title = QLabel("ITEMS DELIVERED")
        table_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        table_title.setAlignment(Qt.AlignCenter)
        table_title.setStyleSheet("color: #000000; margin: 25px 0 15px 0;")
        self.content_layout.addWidget(table_title)
        
        # Create table
        table = QTableWidget()
        table.setColumnCount(7)
        headers = ["Sl No.", "Description", "HSN/SAC", "Quantity", "Type", "Rate", "Total"]
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(items))
        
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
            
            # Total
            total_item = QTableWidgetItem(f"₹{item['total']:.2f}" if item["total"] else "₹0.00")
            total_item.setTextAlignment(Qt.AlignRight)
            total_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            table.setItem(row, 6, total_item)
        
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
        table.setColumnWidth(6, 120)  # Total
        
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
        
        notes_title = QLabel("NOTE:")
        notes_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        notes_title.setStyleSheet("color: #000000; border: none; background: transparent;")
        
        notes_text = QLabel(
            "1. This is a computer-generated delivery challan and does not require a signature.\n"
            "2. All goods mentioned above are delivered in good condition.\n"
            "3. Any discrepancy should be reported within 24 hours of delivery.\n"
            "4. This challan is valid for transportation purposes only."
        )
        notes_text.setFont(QFont("Segoe UI", 11))
        notes_text.setStyleSheet("color: #000000; border: none; background: transparent; line-height: 1.5;")
        notes_text.setWordWrap(True)
        
        notes_layout.addWidget(notes_title)
        notes_layout.addWidget(notes_text)
        
        self.content_layout.addWidget(notes_widget)
    
    def create_separator(self):
        """Create a separator line"""
        line = QFrame()
        line.setObjectName("separatorLine")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        return line
    
    def download_challan(self):
        """Download challan as PDF"""
        folder_path = r"C:\Users\91863\OneDrive\Desktop\Practice\Challans_pdf"
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_name = f"Challan_{self.challan_id}.pdf"
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
            self.challan_content.adjustSize()
            widget_width = self.challan_content.width()
            pdf_width = pdf_writer.width()
            scale = pdf_width / widget_width
            painter.scale(scale, scale)

            # Render the challan content
            self.challan_content.render(
                painter,
                QPoint(0, 0),
                QRegion(self.challan_content.rect()),
                QWidget.RenderFlags(QWidget.DrawChildren)
            )

            painter.end()
            
            # Success message
            msg = QMessageBox(self)
            msg.setWindowTitle("Success")
            msg.setText("Challan saved successfully!")
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
