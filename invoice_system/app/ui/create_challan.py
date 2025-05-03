from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QPushButton, QScrollArea,
    QFrame, QGridLayout, QHeaderView, QSizePolicy, QComboBox,
    QTextEdit,QMessageBox
)
from PySide6.QtGui import QFont, QKeyEvent

class CreateChallan(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Challan")
        self.resize(1200, 800)
        
        
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
            #noteTextEdit {
                background-color: #F8FAFC;
                border: 1px solid #ffcccc;
                border-radius: 3px;
                padding: 5px;
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
        
        # Left side - Customer details
        customer_layout.addWidget(QLabel("M/S :"), 0, 0)
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Enter the Customer Name")
        customer_layout.addWidget(self.customer_name, 0, 1)
        
        customer_layout.addWidget(QLabel("Address :"), 1, 0)
        self.customer_address = QLineEdit()
        self.customer_address.setPlaceholderText("Enter the Customer Address")
        customer_layout.addWidget(self.customer_address, 1, 1)
        
        customer_layout.addWidget(QLabel("GSTIN :"), 2, 0)
        self.customer_gstin = QLineEdit()
        self.customer_gstin.setPlaceholderText("Customer GSTIN/ URP")
        customer_layout.addWidget(self.customer_gstin, 2, 1)
        
        customer_layout.addWidget(QLabel("State :"), 3, 0)
        self.customer_state = QLineEdit()
        self.customer_state.setPlaceholderText("Customer State")
        customer_layout.addWidget(self.customer_state, 3, 1)
        
        customer_layout.addWidget(QLabel("Code :"), 3, 2)
        self.state_code = QLineEdit()
        self.state_code.setPlaceholderText("Eg 18 for Assam")
        customer_layout.addWidget(self.state_code, 3, 3)
        
        # Right side - Challan details
        customer_layout.addWidget(QLabel("Challan No :"), 0, 2)
        self.challan_no = QLineEdit()
        customer_layout.addWidget(self.challan_no, 0, 3)
        
        customer_layout.addWidget(QLabel("Date :"), 1, 2)
        self.challan_date = QLineEdit()
        customer_layout.addWidget(self.challan_date, 1, 3)
        
        # Note section
        customer_layout.addWidget(QLabel("Note :"), 2, 2)
        note_layout = QHBoxLayout()
        self.note_combo = QComboBox()
        self.note_combo.addItems(["YES", "NO"])
        self.note_combo.currentTextChanged.connect(self.toggle_note_field)
        note_layout.addWidget(self.note_combo)
        
        self.note_text = QTextEdit()
        self.note_text.setObjectName("noteTextEdit")
        self.note_text.setMaximumHeight(70)
        note_layout.addWidget(self.note_text)
        customer_layout.addLayout(note_layout, 2, 3)
        
        main_layout.addWidget(customer_frame)
        
        # Terms of Sale section - made larger with scroll
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
        self.current_rows = 11
        self.items_table = QTableWidget(self.current_rows, 7)
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
        
        # Add button
        add_button_layout = QHBoxLayout()
        add_button = QPushButton("Add +")
        add_button.setObjectName("addButton")
        add_button.clicked.connect(self.add_row)
        add_button_layout.addWidget(add_button)
        add_button_layout.addStretch()
        main_layout.addLayout(add_button_layout)
        
        # GST rates section
        gst_frame = QFrame()
        gst_layout = QGridLayout(gst_frame)
        
        # Left side - Grand Total
        gst_layout.addWidget(QLabel("GRAND TOTAL"), 0, 0)
        self.grand_total = QLineEdit()
        gst_layout.addWidget(self.grand_total, 0, 1)
        
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
        
        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_challan_to_db)
        button_layout.addWidget(self.save_button)
        
        save_print_button = QPushButton("Save & Print")
        save_print_button.setObjectName("saveAndPrintButton")
        save_print_button.clicked.connect(self.save_and_print)
        button_layout.addWidget(save_print_button)
        
        main_layout.addLayout(button_layout)
        
        # Set the main container to the scroll area
        main_scroll.setWidget(main_container)
        
        # Main layout for this widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_scroll)
        
        # Maximize window when opened
        self.showMaximized()
    
    def toggle_note_field(self, text):
        self.note_text.setEnabled(text == "YES")
        if text == "NO":
            self.note_text.clear()
    
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
        self.challan_no.clear()
        self.challan_date.clear()
        
        # Reset note combo and clear note text
        self.note_combo.setCurrentIndex(0)
        self.note_text.clear()
        
        # Clear table
        for row in range(self.items_table.rowCount()):
            for col in range(self.items_table.columnCount()):
                self.items_table.setItem(row, col, QTableWidgetItem(""))
        
        # Clear GST fields
        self.grand_total.clear()
        for gst_type, fields in self.gst_fields.items():
            for field in fields:
                field.clear()
    
    def save_challan_to_db(self):
        # Implement database saving logic here
        QMessageBox.information(self, "Save", "Challan saved successfully")
    
    def save_and_print(self):
        # Save the challan to database
        self.save_challan_to_db()
        # Implement print logic here
        QMessageBox.information(self, "Print", "Challan saved and sent to printer")