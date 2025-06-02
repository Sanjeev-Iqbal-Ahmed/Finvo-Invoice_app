from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QDialog, QFormLayout,
    QSpinBox, QDoubleSpinBox, QTextEdit, QDialogButtonBox,
    QGroupBox, QCheckBox
)
from PySide6.QtGui import QFont, QColor, QPalette
from ..models.db_manager import (
    get_all_inventory_items, delete_inventory_item, 
    update_inventory_item, search_inventory_items,
    get_low_stock_items, initialize_database
)

class EditItemDialog(QDialog):
    """Dialog for editing inventory items."""
    
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.original_data = item_data.copy()  # Keep original data for comparison
        self.setWindowTitle("Edit Inventory Item")
        self.setModal(True)
        self.setMinimumSize(500, 600)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add styling for dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                background-color: transparent;
                font-weight: bold;
                color: #333;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border: 2px solid #555599;
            }
            QLineEdit:read-only {
                background-color: #f0f0f0;
                color: #666;
            }
            QPushButton {
                background-color: #555599;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #444488;
            }
            QPushButton:pressed {
                background-color: #333377;
            }
            QDialogButtonBox QPushButton {
                background-color: #555599;
                color: white;
                padding: 8px 18px;
                border-radius: 4px;
                font-size: 12px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #444488;
            }
            QDialogButtonBox QPushButton:pressed {
                background-color: #333377;
            }
        """)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Product Name
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Enter product name")
        form_layout.addRow("Product Name:", self.product_name)
        
        # Product Code (readonly)
        self.product_code = QLineEdit()
        self.product_code.setReadOnly(True)
        self.product_code.setToolTip("Product code cannot be changed")
        form_layout.addRow(QLabel("Product Code:"), self.product_code)
        
        # Category
        self.category = QComboBox()
        self.category.addItems(["Electronics", "Clothing", "Food", "Stationery", "Home Appliances", "Other"])
        self.category.setEditable(True)  # Allow custom categories
        form_layout.addRow(QLabel("Category:"), self.category)
        
        # Unit
        self.unit = QLineEdit()
        self.unit.setPlaceholderText("e.g., pcs, kg, ltr")
        form_layout.addRow(QLabel("Unit:"), self.unit)
        
        # Quantity
        self.quantity = QSpinBox()
        self.quantity.setRange(0, 100000)
        self.quantity.setSuffix(" units")
        form_layout.addRow(QLabel("Stock:"), self.quantity)
        
        # Purchase Price
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 1000000)
        self.purchase_price.setPrefix("₹ ")
        self.purchase_price.setDecimals(2)
        form_layout.addRow(QLabel("Purchase Price:"), self.purchase_price)
        
        # Selling Price
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setRange(0, 1000000)
        self.selling_price.setPrefix("₹ ")
        self.selling_price.setDecimals(2)
        form_layout.addRow(QLabel("Selling Price:"), self.selling_price)
        
        # GST
        self.gst = QComboBox()
        self.gst.addItems(["None", "5%", "12%", "18%", "28%"])
        form_layout.addRow(QLabel("GST %:"), self.gst)
        
        # Description
        self.description = QTextEdit()
        self.description.setMaximumHeight(100)
        self.description.setPlaceholderText("Optional description...")
        form_layout.addRow(QLabel("Description:"), self.description)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Save).setText("Save Changes")
        button_box.accepted.connect(self.save_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def load_data(self):
        """Load existing data into form fields."""
        self.product_name.setText(self.item_data.get('product_name', ''))
        self.product_code.setText(self.item_data.get('product_code', ''))
        
        # Set category
        category = self.item_data.get('category', 'Other')
        index = self.category.findText(category)
        if index >= 0:
            self.category.setCurrentIndex(index)
        else:
            # Add custom category if not in list
            self.category.addItem(category)
            self.category.setCurrentText(category)
            
        self.unit.setText(self.item_data.get('unit', ''))
        self.quantity.setValue(self.item_data.get('quantity_in_stock', 0))
        self.purchase_price.setValue(self.item_data.get('purchase_price', 0.0))
        self.selling_price.setValue(self.item_data.get('selling_price', 0.0))
        
        # Set GST
        gst = self.item_data.get('gst_percentage', 'None')
        gst_index = self.gst.findText(gst)
        if gst_index >= 0:
            self.gst.setCurrentIndex(gst_index)
            
        self.description.setPlainText(self.item_data.get('description', ''))
        
        # Calculate initial profit margin
        """self.calculate_profit_margin()"""
        
    def has_changes(self):
        """Check if any data has been modified."""
        current_data = {
            'product_name': self.product_name.text().strip(),
            'category': self.category.currentText(),
            'unit': self.unit.text().strip(),
            'quantity_in_stock': self.quantity.value(),
            'purchase_price': self.purchase_price.value(),
            'selling_price': self.selling_price.value(),
            'gst_percentage': self.gst.currentText(),
            'description': self.description.toPlainText().strip()
        }
        
        print(f"Current data: {current_data}")  # Debug line
        print(f"Original data: {self.original_data}")  # Debug line
        
        for key, value in current_data.items():
            original_value = self.original_data.get(key, '')
            if str(value) != str(original_value):
                print(f"Change detected in {key}: '{original_value}' -> '{value}'")  # Debug line
                return True
        return False
        
    def save_changes(self):
        """Save changes to database with enhanced validation and debugging."""
        try:
            # Validate required fields
            if not self.product_name.text().strip():
                QMessageBox.warning(self, "Validation Error", "Product name is required!")
                self.product_name.setFocus()
                return
                
            if not self.unit.text().strip():
                QMessageBox.warning(self, "Validation Error", "Unit is required!")
                self.unit.setFocus()
                return
            
            # Validate prices
            if self.purchase_price.value() < 0:
                QMessageBox.warning(self, "Validation Error", "Purchase price cannot be negative!")
                self.purchase_price.setFocus()
                return
                
            if self.selling_price.value() < 0:
                QMessageBox.warning(self, "Validation Error", "Selling price cannot be negative!")
                self.selling_price.setFocus()
                return
            
            # Check if there are actually changes to save
            if not self.has_changes():
                QMessageBox.information(self, "No Changes", "No changes were made to save.")
                self.reject()
                return
            
            # Confirm if selling price is lower than purchase price
            if self.selling_price.value() < self.purchase_price.value():
                reply = QMessageBox.question(
                    self, "Price Warning",
                    "Selling price is lower than purchase price. This will result in a loss. Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # Debug: Print the data being sent
            print(f"Updating item with ID: {self.item_data['id']}")
            print(f"Product name: {self.product_name.text().strip()}")
            print(f"Category: {self.category.currentText()}")
            print(f"Unit: {self.unit.text().strip()}")
            print(f"Quantity: {self.quantity.value()}")
            print(f"Purchase price: {self.purchase_price.value()}")
            print(f"Selling price: {self.selling_price.value()}")
            print(f"GST: {self.gst.currentText()}")
            print(f"Description: {self.description.toPlainText().strip()}")
            
            # Update item with explicit parameter names
            success = update_inventory_item(
                item_id=self.item_data['id'],
                product_name=self.product_name.text().strip(),
                category=self.category.currentText(),
                unit=self.unit.text().strip(),
                quantity_in_stock=self.quantity.value(),  # Make sure this matches the database field name
                purchase_price=self.purchase_price.value(),
                selling_price=self.selling_price.value(),
                gst_percentage=self.gst.currentText(),
                description=self.description.toPlainText().strip()
            )
            
            print(f"Update result: {success}")  # Debug line
            
            if success:
                QMessageBox.information(self, "Success", "Item updated successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update item! Please check your input and try again.\n\nCheck the console for detailed error messages.")
                
        except Exception as e:
            print(f"Exception in save_changes: {e}")  # Debug line
            QMessageBox.critical(self, "Error", f"An error occurred while saving: {str(e)}")
            
    def reject(self):
        """Override reject to check for unsaved changes."""
        if self.has_changes():
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to close without saving?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        super().reject()

class InventoryViewPage(QWidget):
    """Main inventory view page with table display and management features."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_items = []
        self.filtered_items = []  # Store filtered results separately
        initialize_database()  # Ensure database is initialized
        self.setup_ui()
        self.load_inventory_data()
        self.setWindowTitle("Inventory Management")
        
        # Auto-refresh timer (optional)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_inventory_data)
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                background-color: #A6AEBF;
                color: #333333;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
                border-radius: 3px;
                font-weight: normal;
            }
            QComboBox QAbstractItemView {
                background-color: white;  /* Dropdown list background */
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #555599;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                color: black;
            }
            #refreshButton {
                background-color: #555599;
                color: white;
            }
            #refreshButton:hover {
                background-color: #6666aa;
            }
            #deleteButton {
                background-color: #cc4444;
                color: white;
            }
            #deleteButton:hover {
                background-color: #dd5555;
            }
            #exportButton {
                background-color: #44aa44;
                color: white;
            }
            #exportButton:hover {
                background-color: #55bb55;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-weight: normal;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #555599;
                color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #cccccc;
                font-weight: bold;
                color: #333333;
            }
            QGroupBox {
                font-weight: bold;
                color: #333333;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Inventory Management")
        header_label.setObjectName("pageHeader")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header_label.setFont(font)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.load_inventory_data)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        """header_layout.addWidget(self.clear_filters_button)"""
        header_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(header_layout)
        
        # Search and Filter Section
        search_group = QGroupBox("Search & Filter")
        search_layout = QHBoxLayout()
        
        # Search box
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, code, category, or description...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setClearButtonEnabled(True)  # Add clear button
        search_layout.addWidget(self.search_input)
        
        # Category filter
        search_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "Electronics", "Clothing", "Food", "Stationery", "Home Appliances", "Other"])
        self.category_filter.currentTextChanged.connect(self.apply_filters)
        search_layout.addWidget(self.category_filter)
        
        # Low stock checkbox
        self.low_stock_checkbox = QCheckBox("Show Low Stock Only")
        self.low_stock_checkbox.stateChanged.connect(self.apply_filters)
        search_layout.addWidget(self.low_stock_checkbox)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # Statistics Section
        stats_group = QGroupBox("Inventory Statistics")
        stats_layout = QHBoxLayout()
        
        self.total_items_label = QLabel("Total Items: 0")
        self.total_value_label = QLabel("Total Value: ₹0.00")
        self.low_stock_label = QLabel("Low Stock Items: 0")
        self.filtered_count_label = QLabel("Showing: 0 items")
        
        stats_layout.addWidget(self.total_items_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.total_value_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.low_stock_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.filtered_count_label)
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # Table
        self.table = QTableWidget()
        self.setup_table()
        main_layout.addWidget(self.table)
        
        # Action Buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.setObjectName("refreshButton")
        self.edit_button.clicked.connect(self.edit_selected_item)
        self.edit_button.setEnabled(False)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected_item)
        self.delete_button.setEnabled(False)
        
        self.export_button = QPushButton("Export Data")
        self.export_button.setObjectName("exportButton")
        self.export_button.clicked.connect(self.export_data)
        
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.export_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Connect table selection change
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def setup_table(self):
        """Setup the inventory table."""
        columns = [
            "ID", "Product Name", "Product Code", "Category", "Unit", 
            "Stock", "Purchase Price", "Selling Price", "GST %", "Total Value"
        ]
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Product Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Product Code
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Category
        
        # Hide ID column
        self.table.setColumnHidden(0, True)
        
        # Set table properties
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSortingEnabled(True)
        
    def load_inventory_data(self):
        """Load inventory data from database."""
        try:
            self.current_items = get_all_inventory_items()
            print(f"Loaded {len(self.current_items)} items")  # Debug line
            if self.current_items:
                print(f"Sample item keys: {list(self.current_items[0].keys())}")  # Debug line
            self.apply_filters()  # Apply current filters to new data
            self.update_statistics()
            
        except Exception as e:
            print(f"Detailed error: {e}")  # Debug line
            QMessageBox.critical(self, "Error", f"Failed to load inventory data: {str(e)}")
            
    def populate_table(self, items):
        """Populate table with inventory items."""
        self.table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # Calculate total value
            total_value = item['quantity_in_stock'] * item['selling_price']
            
            # Populate columns
            self.table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(item['product_name'] or ''))
            self.table.setItem(row, 2, QTableWidgetItem(item['product_code'] or ''))
            self.table.setItem(row, 3, QTableWidgetItem(item['category'] or ''))
            self.table.setItem(row, 4, QTableWidgetItem(item['unit'] or ''))
            
            # Stock quantity with color coding
            stock_item = QTableWidgetItem(str(item['quantity_in_stock']))
            if item['quantity_in_stock'] <= 10:  # Low stock threshold
                stock_item.setBackground(QColor("#ffeeee"))
                stock_item.setForeground(QColor("#cc0000"))
            self.table.setItem(row, 5, stock_item)
            
            self.table.setItem(row, 6, QTableWidgetItem(f"₹{item['purchase_price']:.2f}"))
            self.table.setItem(row, 7, QTableWidgetItem(f"₹{item['selling_price']:.2f}"))
            self.table.setItem(row, 8, QTableWidgetItem(item['gst_percentage'] or 'None'))
            self.table.setItem(row, 9, QTableWidgetItem(f"₹{total_value:.2f}"))
            
        # Update filtered count
        self.filtered_count_label.setText(f"Showing: {len(items)} items")
            
    def update_statistics(self):
        """Update inventory statistics."""
        if not self.current_items:
            self.total_items_label.setText("Total Items: 0")
            self.total_value_label.setText("Total Value: ₹0.00")
            self.low_stock_label.setText("Low Stock Items: 0")
            return
            
        total_items = len(self.current_items)
        total_value = sum(item['quantity_in_stock'] * item['selling_price'] for item in self.current_items)
        low_stock_count = sum(1 for item in self.current_items if item['quantity_in_stock'] <= 10)
        
        self.total_items_label.setText(f"Total Items: {total_items}")
        self.total_value_label.setText(f"Total Value: ₹{total_value:,.2f}")
        self.low_stock_label.setText(f"Low Stock Items: {low_stock_count}")
        
    def on_search_changed(self):
        """Handle search input changes with improved debouncing."""
        # Clear existing timer if any
        if hasattr(self, 'search_timer'):
            self.search_timer.stop()
            self.search_timer.deleteLater()
        
        # Create new timer with shorter delay for better responsiveness
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.search_timer.start(300)  # Reduced from 500ms to 300ms
        
    def perform_search(self):
        """Perform enhanced search with multiple criteria."""
        search_term = self.search_input.text().strip().lower()
        
        if search_term:
            # Enhanced local search - search in multiple fields
            filtered_items = []
            for item in self.current_items:
                # Search in multiple fields
                searchable_text = ' '.join([
                    str(item.get('product_name', '')).lower(),
                    str(item.get('product_code', '')).lower(),
                    str(item.get('category', '')).lower(),
                    str(item.get('description', '')).lower(),
                    str(item.get('unit', '')).lower()
                ])
                
                # Support multiple search terms (AND logic)
                search_terms = search_term.split()
                if all(term in searchable_text for term in search_terms):
                    filtered_items.append(item)
            
            self.filtered_items = filtered_items
        else:
            # No search term, apply other filters
            self.filtered_items = self.current_items.copy()
        
        # Apply additional filters
        self.apply_additional_filters()
            
    def apply_filters(self):
        """Apply category and low stock filters."""
        # Start with current items or search results
        if self.search_input.text().strip():
            self.perform_search()
            return
        else:
            self.filtered_items = self.current_items.copy()
            
        self.apply_additional_filters()
        
    def apply_additional_filters(self):
        """Apply category and low stock filters to current filtered items."""
        items_to_filter = self.filtered_items.copy()
        
        # Category filter
        selected_category = self.category_filter.currentText()
        if selected_category != "All Categories":
            items_to_filter = [item for item in items_to_filter if item['category'] == selected_category]
            
        # Low stock filter
        if self.low_stock_checkbox.isChecked():
            items_to_filter = [item for item in items_to_filter if item['quantity_in_stock'] <= 10]
            
        self.populate_table(items_to_filter)
        
    def on_selection_changed(self):
        """Handle table selection changes."""
        has_selection = bool(self.table.currentRow() >= 0)
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
    def get_selected_item(self):
        """Get the currently selected item data."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
            
        try:
            item_id = int(self.table.item(current_row, 0).text())
            return next((item for item in self.current_items if item['id'] == item_id), None)
        except (ValueError, AttributeError):
            return None
        
    def edit_selected_item(self):
        """Edit the selected inventory item with enhanced error handling."""
        selected_item = self.get_selected_item()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select an item to edit.")
            return
            
        try:
            dialog = EditItemDialog(selected_item, self)
            if dialog.exec() == QDialog.Accepted:
                self.load_inventory_data()  # Refresh data
                QMessageBox.information(self, "Success", "Changes saved and data refreshed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit dialog: {str(e)}")
            
    def delete_selected_item(self):
        """Delete the selected inventory item."""
        selected_item = self.get_selected_item()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select an item to delete.")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete '{selected_item['product_name']}'?\n\n"
            f"Product Code: {selected_item.get('product_code', 'N/A')}\n"
            f"Current Stock: {selected_item.get('quantity_in_stock', 0)}\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = delete_inventory_item(selected_item['id'])
                if success:
                    QMessageBox.information(self, "Success", "Item deleted successfully!")
                    self.load_inventory_data()  # Refresh data
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete item!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
                
    def export_data(self):
        """Export inventory data to CSV with enhanced functionality."""
        try:
            import csv
            from PySide6.QtWidgets import QFileDialog
            import datetime
            
            # Get current displayed items (respects filters)
            current_row_count = self.table.rowCount()
            items_to_export = []
            
            for row in range(current_row_count):
                item_id = int(self.table.item(row, 0).text())
                item = next((item for item in self.current_items if item['id'] == item_id), None)
                if item:
                    items_to_export.append(item)
            
            if not items_to_export:
                QMessageBox.warning(self, "No Data", "No items to export!")
                return
            
            # Generate default filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"inventory_export_{timestamp}.csv"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Inventory Data", default_filename, "CSV Files (*.csv)"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['product_name', 'product_code', 'category', 'unit', 
                                'quantity_in_stock', 'purchase_price', 'selling_price', 
                                'gst_percentage', 'description', 'total_value']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for item in items_to_export:
                        # Calculate total value for export
                        total_value = item['quantity_in_stock'] * item['selling_price']
                        export_item = {field: item.get(field, '') for field in fieldnames[:-1]}
                        export_item['total_value'] = f"{total_value:.2f}"
                        writer.writerow(export_item)
                        
                QMessageBox.information(
                    self, "Export Success", 
                    f"Successfully exported {len(items_to_export)} items to:\n{file_path}"
                )
                
        except ImportError:
            QMessageBox.warning(self, "Export Error", "CSV module not available!")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")