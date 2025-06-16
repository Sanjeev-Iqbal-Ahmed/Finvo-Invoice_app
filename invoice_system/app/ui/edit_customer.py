from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QHeaderView,
    QComboBox, QPushButton, QTextEdit, QFormLayout, QSpinBox, QAbstractItemView,
    QDoubleSpinBox, QStackedWidget, QFrame, QMessageBox, QTableWidget, QTableWidgetItem,
    QDialog, QDialogButtonBox, QGroupBox, QCheckBox
)
from PySide6.QtGui import QFont, QColor
from ..models.db_manager import create_tables, update_customer, get_all_customers, get_customer_by_id, delete_customer


class EditCustomerDialog(QDialog):
    """Dialog for editing customer details."""
    
    def __init__(self, customer_data, parent=None):
        super().__init__(parent)
        self.customer_data = customer_data
        self.original_data = customer_data.copy()  # Keep original data for comparison
        self.setWindowTitle("Edit Customer Details")
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
            QLineEdit, QComboBox, QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight:600;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
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
        
        # Customer ID (readonly)
        self.customer_id = QLineEdit()
        self.customer_id.setReadOnly(True)
        self.customer_id.setToolTip("Customer ID cannot be changed")
        form_layout.addRow("Customer ID:", self.customer_id)
        
        # Customer Name
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Enter customer name")
        form_layout.addRow("Customer Name:", self.customer_name)
        
        # Address
        self.address = QTextEdit()
        self.address.setPlaceholderText("Enter customer address")
        self.address.setMaximumHeight(100)
        form_layout.addRow("Address:", self.address)
        
        # State
        self.state = QComboBox()
        indian_states = [
            "Select State", "Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
            "Chandigarh", "Chhattisgarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Goa", 
            "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", 
            "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", 
            "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", 
            "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ]
        self.state.addItems(indian_states)
        form_layout.addRow("State:", self.state)
        
        # State Code
        self.state_code = QLineEdit()
        self.state_code.setPlaceholderText("Enter state code (e.g., 18 for Assam)")
        form_layout.addRow("State Code:", self.state_code)
        
        # GSTIN
        self.gstin = QLineEdit()
        self.gstin.setPlaceholderText("Enter GSTIN (optional)")
        self.gstin.setMaxLength(15)
        form_layout.addRow("GSTIN:", self.gstin)
        
        # Phone
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Enter phone number")
        self.phone.setMaxLength(15)
        form_layout.addRow("Phone Number:", self.phone)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Save).setText("Save Changes")
        button_box.accepted.connect(self.save_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect GSTIN validation
        self.gstin.textChanged.connect(self.validate_gstin_format)
        
    def validate_gstin_format(self, text):
        """Validate GSTIN format as user types."""
        if text and len(text) >= 2:
            try:
                gstin_state_code = text[:2]
                if gstin_state_code.isdigit():
                    self.state_code.setText(gstin_state_code)
            except:
                pass
        
    def load_data(self):
        """Load existing data into form fields."""
        self.customer_id.setText(str(self.customer_data.get('id', '')))
        self.customer_name.setText(self.customer_data.get('customer_name', ''))
        self.address.setPlainText(self.customer_data.get('address', ''))
        
        # Set state in combobox
        state_text = self.customer_data.get('state', '')
        state_index = self.state.findText(state_text)
        if state_index >= 0:
            self.state.setCurrentIndex(state_index)
        
        self.state_code.setText(self.customer_data.get('state_code', ''))
        self.gstin.setText(self.customer_data.get('gstin', '') or '')
        self.phone.setText(self.customer_data.get('phone', '') or '')
        
    def has_changes(self):
        """Check if any data has been modified."""
        current_data = {
            'customer_name': self.customer_name.text().strip(),
            'address': self.address.toPlainText().strip(),
            'state': self.state.currentText(),
            'state_code': self.state_code.text().strip(),
            'gstin': self.gstin.text().strip(),
            'phone': self.phone.text().strip()
        }
        
        for key, value in current_data.items():
            original_value = self.original_data.get(key, '') or ''
            if str(value) != str(original_value):
                return True
        return False
        
    def validate_form(self):
        """Validate form data before updating."""
        errors = []
        
        if not self.customer_name.text().strip():
            errors.append("Customer Name is required")
            
        if not self.address.toPlainText().strip():
            errors.append("Address is required")
            
        if self.state.currentText() == "Select State":
            errors.append("Please select a state")
            
        if not self.state_code.text().strip():
            errors.append("State Code is required")
        elif not self.state_code.text().strip().isdigit():
            errors.append("State Code must be numeric")
            
        gstin = self.gstin.text().strip()
        if gstin:
            if len(gstin) != 15:
                errors.append("GSTIN must be exactly 15 characters")
            elif not gstin[:2].isdigit():
                errors.append("GSTIN must start with 2 digit state code")
                
        return errors
        
    def save_changes(self):
        """Save changes to database."""
        try:
            # Validate form
            errors = self.validate_form()
            if errors:
                error_message = "\n".join(errors)
                QMessageBox.warning(self, "Validation Error", error_message)
                return
            
            # Check if there are actually changes to save
            if not self.has_changes():
                QMessageBox.information(self, "No Changes", "No changes were made to save.")
                self.reject()
                return
            
            # Prepare customer data
            customer_data = {
                'customer_name': self.customer_name.text().strip(),
                'address': self.address.toPlainText().strip(),
                'state': self.state.currentText(),
                'state_code': self.state_code.text().strip(),
                'gstin': self.gstin.text().strip(),
                'phone': self.phone.text().strip()
            }
            
            # Update in database
            success, message = update_customer(self.customer_data['id'], customer_data)
            
            if success:
                QMessageBox.information(self, "Success", "Customer updated successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", f"Failed to update customer: {message}")
                
        except Exception as e:
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


class Edit_Customer(QWidget):
    # Signal to notify when customer is updated
    customer_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_customers = []
        self.filtered_customers = []  # Store filtered results separately
        self.setup_ui()
        self.setWindowTitle("Customer Management")
        self.load_customers()
        
        # Auto-refresh timer (optional)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_customers)
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Apply same styling as inventory page
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
                font-weight: 600;
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
            QTableWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-weight: 600;
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
        header_label = QLabel("Customer Management")
        header_label.setObjectName("pageHeader")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        header_label.setFont(font)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.load_customers)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(header_layout)
        
        # Search and Filter Section
        search_group = QGroupBox("Search & Filter")
        search_layout = QHBoxLayout()
        
        # Search box
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, address, state, GSTIN, or phone...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setClearButtonEnabled(True)  # Add clear button
        search_layout.addWidget(self.search_input)
        
        # State filter
        search_layout.addWidget(QLabel("State:"))
        self.state_filter = QComboBox()
        states = ["All States", "Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
                 "Chandigarh", "Chhattisgarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Goa", 
                 "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", 
                 "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", 
                 "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", 
                 "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
                 "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]
        self.state_filter.addItems(states)
        self.state_filter.currentTextChanged.connect(self.apply_filters)
        search_layout.addWidget(self.state_filter)
        
        # GSTIN filter checkbox
        self.gstin_checkbox = QCheckBox("Show Customers with GSTIN Only")
        self.gstin_checkbox.stateChanged.connect(self.apply_filters)
        search_layout.addWidget(self.gstin_checkbox)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # Statistics Section
        stats_group = QGroupBox("Customer Statistics")
        stats_layout = QHBoxLayout()
        
        self.total_customers_label = QLabel("Total Customers: 0")
        self.gstin_customers_label = QLabel("Customers with GSTIN: 0")
        self.filtered_count_label = QLabel("Showing: 0 customers")
        
        stats_layout.addWidget(self.total_customers_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.gstin_customers_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.filtered_count_label)
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # Customer List Table
        self.customer_table = QTableWidget()
        self.setup_table()
        main_layout.addWidget(self.customer_table)
        
        # Action Buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.setObjectName("refreshButton")
        self.edit_button.clicked.connect(self.edit_selected_customer)
        self.edit_button.setEnabled(False)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected_customer)
        self.delete_button.setEnabled(False)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Connect table selection change
        self.customer_table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def setup_table(self):
        """Setup the customer table."""
        columns = ["ID", "Customer Name", "Address", "State", "State Code", "GSTIN", "Phone"]
        
        self.customer_table.setColumnCount(len(columns))
        self.customer_table.setHorizontalHeaderLabels(columns)
        self.customer_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.customer_table.setAlternatingRowColors(True)
        
        # Set column widths
        header = self.customer_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.customer_table.setColumnWidth(0, 50)
        
        # Hide ID column
        self.customer_table.setColumnHidden(0, True)
        
        # Set table properties
        self.customer_table.setSelectionMode(QTableWidget.SingleSelection)
        self.customer_table.setSortingEnabled(True)
    
    def load_customers(self):
        """Load all customers from database."""
        try:
            customers = get_all_customers()
            # Convert to dictionary format for consistency
            self.current_customers = []
            for customer in customers:
                customer_dict = {
                    'id': customer[0],
                    'customer_name': customer[1],
                    'address': customer[2],
                    'state': customer[3],
                    'state_code': customer[4],
                    'gstin': customer[5],
                    'phone': customer[6]
                }
                self.current_customers.append(customer_dict)
            
            self.apply_filters()  # Apply current filters to new data
            self.update_statistics()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load customer data: {str(e)}")
            
    def populate_table(self, customers):
        """Populate table with customer data."""
        self.customer_table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            self.customer_table.setItem(row, 0, QTableWidgetItem(str(customer['id'])))
            self.customer_table.setItem(row, 1, QTableWidgetItem(customer['customer_name'] or ''))
            self.customer_table.setItem(row, 2, QTableWidgetItem(customer['address'] or ''))
            self.customer_table.setItem(row, 3, QTableWidgetItem(customer['state'] or ''))
            self.customer_table.setItem(row, 4, QTableWidgetItem(customer['state_code'] or ''))
            self.customer_table.setItem(row, 5, QTableWidgetItem(customer['gstin'] or ''))
            self.customer_table.setItem(row, 6, QTableWidgetItem(customer['phone'] or ''))
            
        # Update filtered count
        self.filtered_count_label.setText(f"Showing: {len(customers)} customers")
            
    def update_statistics(self):
        """Update customer statistics."""
        if not self.current_customers:
            self.total_customers_label.setText("Total Customers: 0")
            self.gstin_customers_label.setText("Customers with GSTIN: 0")
            return
            
        total_customers = len(self.current_customers)
        gstin_customers = sum(1 for customer in self.current_customers if customer.get('gstin'))
        
        self.total_customers_label.setText(f"Total Customers: {total_customers}")
        self.gstin_customers_label.setText(f"Customers with GSTIN: {gstin_customers}")
        
    def on_search_changed(self):
        """Handle search input changes with debouncing."""
        # Clear existing timer if any
        if hasattr(self, 'search_timer'):
            self.search_timer.stop()
            self.search_timer.deleteLater()
        
        # Create new timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.search_timer.start(300)
        
    def perform_search(self):
        """Perform search with multiple criteria."""
        search_term = self.search_input.text().strip().lower()
        
        if search_term:
            # Enhanced local search - search in multiple fields
            filtered_customers = []
            for customer in self.current_customers:
                # Search in multiple fields
                searchable_text = ' '.join([
                    str(customer.get('customer_name', '')).lower(),
                    str(customer.get('address', '')).lower(),
                    str(customer.get('state', '')).lower(),
                    str(customer.get('gstin', '')).lower(),
                    str(customer.get('phone', '')).lower(),
                    str(customer.get('state_code', '')).lower()
                ])
                
                # Support multiple search terms (AND logic)
                search_terms = search_term.split()
                if all(term in searchable_text for term in search_terms):
                    filtered_customers.append(customer)
            
            self.filtered_customers = filtered_customers
        else:
            # No search term, apply other filters
            self.filtered_customers = self.current_customers.copy()
        
        # Apply additional filters
        self.apply_additional_filters()
            
    def apply_filters(self):
        """Apply state and GSTIN filters."""
        # Start with current customers or search results
        if self.search_input.text().strip():
            self.perform_search()
            return
        else:
            self.filtered_customers = self.current_customers.copy()
            
        self.apply_additional_filters()
        
    def apply_additional_filters(self):
        """Apply state and GSTIN filters to current filtered customers."""
        customers_to_filter = self.filtered_customers.copy()
        
        # State filter
        selected_state = self.state_filter.currentText()
        if selected_state != "All States":
            customers_to_filter = [customer for customer in customers_to_filter if customer['state'] == selected_state]
            
        # GSTIN filter
        if self.gstin_checkbox.isChecked():
            customers_to_filter = [customer for customer in customers_to_filter if customer.get('gstin')]
            
        self.populate_table(customers_to_filter)
        
    def on_selection_changed(self):
        """Handle table selection changes."""
        has_selection = bool(self.customer_table.currentRow() >= 0)
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
    def get_selected_customer(self):
        """Get the currently selected customer data."""
        current_row = self.customer_table.currentRow()
        if current_row < 0:
            return None
            
        try:
            customer_id = int(self.customer_table.item(current_row, 0).text())
            return next((customer for customer in self.current_customers if customer['id'] == customer_id), None)
        except (ValueError, AttributeError):
            return None
        
    def edit_selected_customer(self):
        """Edit the selected customer."""
        selected_customer = self.get_selected_customer()
        if not selected_customer:
            QMessageBox.warning(self, "No Selection", "Please select a customer to edit.")
            return
            
        try:
            dialog = EditCustomerDialog(selected_customer, self)
            if dialog.exec() == QDialog.Accepted:
                self.load_customers()  # Refresh data
                self.customer_updated.emit()  # Emit signal
                QMessageBox.information(self, "Success", "Changes saved and data refreshed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit dialog: {str(e)}")
            
    def delete_selected_customer(self):
        """Delete the selected customer."""
        selected_customer = self.get_selected_customer()
        if not selected_customer:
            QMessageBox.warning(self, "No Selection", "Please select a customer to delete.")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete '{selected_customer['customer_name']}'?\n\n"
            f"State: {selected_customer.get('state', 'N/A')}\n"
            f"Phone: {selected_customer.get('phone', 'N/A')}\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success, message = delete_customer(selected_customer['id'])
                if success:
                    QMessageBox.information(self, "Success", "Customer deleted successfully!")
                    self.load_customers()  # Refresh data
                    self.customer_updated.emit()  # Emit signal
                else:
                    QMessageBox.critical(self, "Error", f"Failed to delete customer: {message}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
                