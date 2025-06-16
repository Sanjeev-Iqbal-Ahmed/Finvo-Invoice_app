from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QButtonGroup, QRadioButton,
    QTableWidget, QTableWidgetItem, QPushButton, QScrollArea, QDialog, QDateEdit, QFileDialog,
    QFrame, QGridLayout, QHeaderView, QSizePolicy, QComboBox, QMessageBox, QDialogButtonBox
)
from PySide6.QtGui import QBrush, QColor, QIcon
from ..models.db_manager import get_all_challans, delete_challan
from .challan_preview import ChallanPreview_Window
from .create_challan import CreateChallan
import csv

class Manage_Challan(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Challans")
        self.resize(1200, 800)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        self.setup_header()
        
        # Search and filter section
        self.setup_search_filter()
        
        # Challans table
        self.setup_challans_table()
        
        # Buttons section
        self.setup_action_buttons()
        
        # Load challans
        self.load_challans()

        self.setStyleSheet("""
            QWidget { 
                background-color: #A6AEBF; 
                color: #333333; font-weight:bold;
            }
            QTableWidget { 
                background-color: white;
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
                background-color: white;
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
        title_label = QLabel("Manage Challans")
        title_label.setObjectName("pageTitle")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Challan statistics
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Total Challans
        total_challans_layout = QVBoxLayout()
        total_challans_label = QLabel("Total Challans")
        self.total_challans_value = QLabel("0")
        self.total_challans_value.setStyleSheet("font-size: 18px; font-weight: bold;")
        total_challans_layout.addWidget(total_challans_label)
        total_challans_layout.addWidget(self.total_challans_value)
        stats_layout.addLayout(total_challans_layout)
        
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
        self.search_input.setPlaceholderText("Search by challan #, customer name...")
        self.search_input.textChanged.connect(self.apply_filters)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        filter_layout.addLayout(search_layout)
        filter_layout.addStretch()
        
        # Date filter
        date_layout = QHBoxLayout()
        date_label = QLabel("Date Range:")
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setStyleSheet("background-color:white;")
        
        date_to_label = QLabel("to")
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setStyleSheet("background-color:white;")
        
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
    
    def setup_challans_table(self):
        """Set up the challans table"""
        # Create table widget
        self.challans_table = QTableWidget()
        self.challans_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.challans_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.challans_table.setAlternatingRowColors(True)
        self.challans_table.setColumnCount(7)
        
        # Set headers
        headers = ["Challan #", "Date", "Customer Name", "Items", "Grand Total", "Actions", "ID"]
        self.challans_table.setHorizontalHeaderLabels(headers)
        
        # Hide the ID column which we'll use internally
        self.challans_table.setColumnHidden(6, True)
        
        # Set column widths
        self.challans_table.setColumnWidth(0, 200)  # Challan #
        self.challans_table.setColumnWidth(1, 120)  # Date
        self.challans_table.setColumnWidth(2, 300)  # Customer Name
        self.challans_table.setColumnWidth(3, 80)   # Items
        self.challans_table.setColumnWidth(4, 120)  # Grand Total
        self.challans_table.setColumnWidth(5, 200)  # Actions
        
        # Set table to take all available space
        self.main_layout.addWidget(self.challans_table)
    
    def setup_action_buttons(self):
        """Set up action buttons at the bottom"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Export button
        self.export_button = QPushButton("Export to CSV")
        self.export_button.setStyleSheet("background-color:#44aa44;color:white;font-weight:bold")
        self.export_button.clicked.connect(self.export_to_csv)
        buttons_layout.addWidget(self.export_button) 
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet("background-color:#44aa44;color:white;font-weight:bold")
        self.refresh_button.clicked.connect(self.load_challans)
        buttons_layout.addWidget(self.refresh_button)
        
        self.main_layout.addLayout(buttons_layout)
    
    def load_challans(self):
        """Load challans from database"""
        try:
            # Clear existing table
            self.challans_table.setRowCount(0)
            self.challans_table.setStyleSheet("QTableWidget { font-weight:600; }")

            # Get all challans from database
            challans_data = get_all_challans()
            
            # Check if challans_data is None or empty
            if not challans_data:
                self.total_challans_value.setText("0")
                return
            
            # Track counts for statistics
            total_count = 0
            
            for challan_data in challans_data:
                # Convert to dictionary if it's not already
                if hasattr(challan_data, 'keys'):
                    # It's already a dict-like object
                    challan = dict(challan_data) if not isinstance(challan_data, dict) else challan_data
                else:
                    # Handle the case where it might be a tuple or other format
                    print(f"Unexpected challan data format: {type(challan_data)}")
                    continue
                
                # Apply filters if needed
                if not self.should_display_challan(challan):
                    continue
                
                # Count for statistics
                total_count += 1
                
                # Add row to table
                row_position = self.challans_table.rowCount()
                self.challans_table.insertRow(row_position)
                
                # Set challan data with safe getting
                self.challans_table.setItem(row_position, 0, QTableWidgetItem(str(challan.get('challan_no', ''))))
                self.challans_table.setItem(row_position, 1, QTableWidgetItem(str(challan.get('date', ''))))
                self.challans_table.setItem(row_position, 2, QTableWidgetItem(str(challan.get('customer_name', ''))))
                
                # Calculate number of items - this might need adjustment based on your data structure
                items_count = 0
                if 'items' in challan and challan['items']:
                    if isinstance(challan['items'], list) and len(challan['items']) > 0:
                        # Extract the actual count from the first (and only) item in the mock structure
                        items_count = challan['items'][0].get('count', 0)
                    else:
                        items_count = 0

                self.challans_table.setItem(row_position, 3, QTableWidgetItem(str(items_count)))
                
                # Format grand total with currency
                grand_total_value = challan.get('grand_total', 0)
                try:
                    grand_total = f"₹{float(grand_total_value):.2f}"
                except (ValueError, TypeError):
                    grand_total = "₹0.00"
                self.challans_table.setItem(row_position, 4, QTableWidgetItem(grand_total))
                
                # Add action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 2, 4, 2)
                
                # View button
                view_btn = QPushButton("View")
                view_btn.setStyleSheet("font-weight:bold;background-color:#555599;color:white")
                view_btn.setToolTip("View Challan")
                challan_id = challan.get('id')
                view_btn.clicked.connect(lambda checked, id=challan_id: self.view_challan(id))
                actions_layout.addWidget(view_btn)
                
                # Delete button
                delete_btn = QPushButton("Delete")
                delete_btn.setStyleSheet("font-weight:bold;background-color:#cc4444;color:white")
                delete_btn.setToolTip("Delete Challan")
                delete_btn.clicked.connect(lambda checked, id=challan_id: self.delete_challan(id))
                actions_layout.addWidget(delete_btn)
                
                self.challans_table.setCellWidget(row_position, 5, actions_widget)
                
                # Store challan ID (hidden)
                self.challans_table.setItem(row_position, 6, QTableWidgetItem(str(challan.get('id', ''))))
            
            # Update statistics
            self.total_challans_value.setText(str(total_count))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load challans: {str(e)}")
            print(f"Detailed error: {e}")  # For debugging
            print(f"Error type: {type(e)}")  # Additional debugging
    
    def should_display_challan(self, challan):
        """Check if the challan matches current filters"""
        # Search filter
        search_text = self.search_input.text().lower()
        if search_text:
            challan_matches = False
            # Check various fields for match
            for field in ['challan_no', 'customer_name', 'customer_address', 'gstin']:
                if field in challan and search_text in str(challan[field]).lower():
                    challan_matches = True
                    break
            if not challan_matches:
                return False
        
        # Date filter
        if 'date' in challan and challan['date']:
            try:
                # Try different date formats
                challan_date = None
                date_str = str(challan['date'])
                
                # Try DD-MM-YYYY format
                if '-' in date_str:
                    challan_date = QDate.fromString(date_str, "dd-MM-yyyy")
                    if not challan_date.isValid():
                        challan_date = QDate.fromString(date_str, "yyyy-MM-dd")
                # Try DD/MM/YYYY format
                elif '/' in date_str:
                    challan_date = QDate.fromString(date_str, "dd/MM/yyyy")
                    if not challan_date.isValid():
                        challan_date = QDate.fromString(date_str, "MM/dd/yyyy")
                
                if challan_date and challan_date.isValid():
                    if not (self.date_from.date() <= challan_date <= self.date_to.date()):
                        return False
            except Exception as e:
                print(f"Date parsing error for {challan.get('date')}: {e}")
                # If date parsing fails, don't filter by date
                pass
        
        return True
    
    def apply_filters(self):
        """Apply filters to the challans table"""
        self.load_challans()
    
    def view_challan(self, challan_id):
        """Open the challan preview window"""
        try:
            preview_window = ChallanPreview_Window(challan_id, self)
            preview_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open challan preview: {str(e)}")
    
    def delete_challan(self, challan_id):
        """Delete a challan after confirmation"""
        reply = QMessageBox.question(self, 
                                    "Confirm Deletion", 
                                    "Are you sure you want to delete this challan? This action cannot be undone.",
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                success = delete_challan(challan_id)
                
                if success:
                    QMessageBox.information(self, "Success", "Challan deleted successfully.")
                    self.load_challans()  # Refresh the table
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete challan.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting challan: {str(e)}")
    
    def export_to_csv(self):
        """Export the current challan list to CSV"""
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
                headers = ["Challan #", "Date", "Customer Name", "Items", "Grand Total"]
                writer.writerow(headers)
                
                # Write data rows
                for row in range(self.challans_table.rowCount()):
                    row_data = []
                    for col in range(5):  # Only export visible columns, excluding Actions and ID
                        item = self.challans_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Data exported successfully to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
    
    def create_new_challan(self):
        """Open the Create Challan window"""
        try:
            create_window = CreateChallan(self)
            create_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open create challan window: {str(e)}")