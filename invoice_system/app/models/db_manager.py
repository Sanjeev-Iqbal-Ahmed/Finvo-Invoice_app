import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

def connect():
    """
    Establish a connection to the SQLite database.
    Ensures the directory exists before creating the database file.
    """
    # Get the directory of the database file
    db_dir = Path.cwd()
    db_path = db_dir / "invoice_app.db"
    
    # Create the directory if it doesn't exist
    os.makedirs(db_dir, exist_ok=True)
    
    # Connect to the database
    return sqlite3.connect(str(db_path))

def create_tables():
    """Create the necessary tables if they don't exist"""
    conn = connect()
    cursor = conn.cursor()
    
    # Create invoices table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        customer_address TEXT,
        gstin TEXT,
        state TEXT,
        state_code TEXT,
        invoice_no TEXT UNIQUE,
        date TEXT,
        challan TEXT,
        transporter TEXT,
        consignment TEXT,
        grand_total REAL
    )
    """)
     # Check if 'payment_status' column exists, add if not
    cursor.execute("PRAGMA table_info(invoices)")
    columns = [col[1] for col in cursor.fetchall()]
    if "payment_status" not in columns:
        cursor.execute("ALTER TABLE invoices ADD COLUMN payment_status TEXT DEFAULT 'Pending'")
    
    
    # Create invoice_items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        description TEXT,
        hsn TEXT,
        quantity INTEGER,
        type TEXT,
        rate REAL,
        gst_percent REAL,
        total REAL,
        FOREIGN KEY(invoice_id) REFERENCES invoices(id)
    )
    """)

    #Create Admin or Company_info table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS company_info (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        name TEXT,
        gstin TEXT,
        contact TEXT,
        address TEXT,
        logo_path TEXT,
        bank_name TEXT,
        account_number TEXT,
        bank_ifsc TEXT,
        bank_branch TEXT
    )
    """)

    # Drop the existing inventory_items table (if it exists)
    """cursor.execute("DROP TABLE IF EXISTS inventory_items")"""

    # Create a new inventory_items table without created_at and updated_at
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_code TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL DEFAULT 'Other',
            unit TEXT NOT NULL,
            quantity_in_stock INTEGER NOT NULL DEFAULT 0,
            purchase_price REAL NOT NULL DEFAULT 0.0,
            selling_price REAL NOT NULL DEFAULT 0.0,
            gst_percentage TEXT DEFAULT 'None',
            description TEXT
        )
    """)

    # Create challans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_address TEXT,
            gstin TEXT,
            state TEXT,
            state_code TEXT,
            challan_no TEXT UNIQUE NOT NULL,
            date TEXT NOT NULL,
            vehicle TEXT,
            transporter TEXT,
            lr TEXT,
            grand_total REAL DEFAULT 0.0
        )
    ''')
    
    # Create challan_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challan_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challan_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            hsn TEXT,
            quantity INTEGER DEFAULT 0,
            type TEXT,
            rate REAL DEFAULT 0.0,
            total REAL DEFAULT 0.0,
            FOREIGN KEY (challan_id) REFERENCES challans (id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_challan_no ON challans (challan_no)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_challan_items_challan_id ON challan_items (challan_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_challans_date ON challans (date)')
    
    conn.commit()
    conn.close()

def save_invoice(invoice_data, items):
    """
    Save invoice data and its line items to the database.
    
    Args:
        invoice_data (dict): Dictionary containing invoice header information
        items (list): List of dictionaries containing line item details
    
    Returns:
        int: ID of the saved invoice, or None if an error occurred
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Check if invoice number already exists
        cursor.execute("SELECT id FROM invoices WHERE invoice_no = ?", (invoice_data['invoice_no'],))
        existing = cursor.fetchone()
        
        # Make sure payment_status is included, default to 'Pending' if not provided
        payment_status = invoice_data.get('payment_status', 'Pending')
        print(f"Processing invoice with payment status: {payment_status}")
        
        if existing:
            print(f"Warning: Invoice number {invoice_data['invoice_no']} already exists. Updating existing invoice.")
            invoice_id = existing[0]
            
            # Update existing invoice - now including payment_status
            cursor.execute("""
                UPDATE invoices SET
                    customer_name = ?,
                    customer_address = ?,
                    gstin = ?,
                    state = ?,
                    state_code = ?,
                    date = ?,
                    challan = ?,
                    transporter = ?,
                    consignment = ?,
                    grand_total = ?,
                    payment_status = ?
                WHERE id = ?
            """, (
                invoice_data['customer_name'],
                invoice_data['customer_address'],
                invoice_data['gstin'],
                invoice_data['state'],
                invoice_data['state_code'],
                invoice_data['date'],
                invoice_data['challan'],
                invoice_data['transporter'],
                invoice_data['consignment'],
                invoice_data['grand_total'],
                payment_status,
                invoice_id
            ))
            
            # Delete existing items for this invoice
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        else:
            # Insert new invoice - now including payment_status
            cursor.execute("""
                INSERT INTO invoices (
                    customer_name, customer_address, gstin, state, state_code,
                    invoice_no, date, challan, transporter, consignment, grand_total,
                    payment_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_data['customer_name'],
                invoice_data['customer_address'],
                invoice_data['gstin'],
                invoice_data['state'],
                invoice_data['state_code'],
                invoice_data['invoice_no'],
                invoice_data['date'],
                invoice_data['challan'],
                invoice_data['transporter'],
                invoice_data['consignment'],
                invoice_data['grand_total'],
                payment_status
            ))
            
            invoice_id = cursor.lastrowid  # Get the auto-generated invoice ID
        
        # Insert line items
        for item in items:
            cursor.execute("""
                INSERT INTO invoice_items (
                    invoice_id, description, hsn, quantity, type, rate, gst_percent, total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id,
                item['description'],
                item['hsn'],
                item['quantity'],
                item['type'],
                item['rate'],
                item['gst'],
                item['total']
            ))
        
        # Verify payment status was saved correctly
        cursor.execute("SELECT payment_status FROM invoices WHERE id = ?", (invoice_id,))
        saved_status = cursor.fetchone()[0]
        print(f"Verified: Invoice {invoice_id} saved with payment status: {saved_status}")
        
        conn.commit()
        conn.close()
        return invoice_id
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return None
    except Exception as e:
        print(f"Error saving invoice: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return None

# Add this function to your db_manager.py file

def get_all_invoices():
    """
    Retrieve all invoices from the database with their basic information
    
    Returns:
        list: List of invoice dictionaries, or empty list if none found
    """
    try:
        conn = connect()
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        # Get all invoices with basic information
        cursor.execute("""
            SELECT 
                id,
                invoice_no,
                date,
                customer_name,
                customer_address,
                gstin,
                state,
                state_code,
                challan,
                transporter,
                consignment,
                grand_total,
                payment_status
            FROM invoices 
            ORDER BY id DESC
        """)
        
        invoices_rows = cursor.fetchall()
        invoices = []
        
        for invoice_row in invoices_rows:
            invoice_data = dict(invoice_row)
            
            # Get item count for this invoice
            cursor.execute("SELECT COUNT(*) as item_count FROM invoice_items WHERE invoice_id = ?", (invoice_data['id'],))
            item_count_row = cursor.fetchone()
            invoice_data['items'] = [{'count': item_count_row['item_count']}]  # Mock items structure for compatibility
            
            invoices.append(invoice_data)
        
        conn.close()
        return invoices
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.close()
        return []
    except Exception as e:
        print(f"Error retrieving invoices: {e}")
        if conn:
            conn.close()
        return []

def get_invoice(invoice_id):
    """
    Retrieve a specific invoice and its items from the database
    
    Args:
        invoice_id (int): ID of the invoice to retrieve
        
    Returns:
        tuple: (invoice_data, items) or (None, None) if not found
    """
    try:
        conn = connect()
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        # Get invoice data
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        invoice_row = cursor.fetchone()
        
        if not invoice_row:
            return None, None
            
        invoice_data = dict(invoice_row)
        
        # Get items
        cursor.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        items_rows = cursor.fetchall()
        items = [dict(row) for row in items_rows]
        
        conn.close()
        return invoice_data, items
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.close()
        return None, None

def delete_invoice(invoice_id):
    """
    Delete an invoice and its items from the database
    Args:
        invoice_id (int): ID of the invoice to delete   
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Delete items first (foreign key constraint)
        cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        
        # Delete invoice
        cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        
        # Check if any rows were affected
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return success
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"Error deleting invoice: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def update_payment_status(invoice_id, new_status):
    """
    Update the payment status of an invoice
    
    Args:
        invoice_id (int): ID of the invoice to update
        new_status (str): New payment status ('Paid' or 'Pending')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Update payment status
        cursor.execute("""
            UPDATE invoices 
            SET payment_status = ? 
            WHERE id = ?
        """, (new_status, invoice_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        print(f"Updated invoice {invoice_id} payment status to: {new_status}")
        return success
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"Error updating payment status: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    
def save_company_info(data):
    """
    Save or update the company information in a single-row table.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT,
            gstin TEXT,
            contact TEXT,
            address TEXT,
            logo_path TEXT,
            bank_name TEXT,
            account_number TEXT,
            bank_ifsc TEXT,
            bank_branch TEXT
        )
        """)

        # Check if row exists
        cursor.execute("SELECT id FROM company_info WHERE id = 1")
        exists = cursor.fetchone()

        if exists:
            # Update existing
            cursor.execute("""
                UPDATE company_info SET
                    name = ?, gstin = ?, contact = ?, address = ?, logo_path = ?,
                    bank_name = ?, account_number = ?, bank_ifsc = ?, bank_branch = ?
                WHERE id = 1
            """, (
                data['name'], data['gstin'], data['contact'], data['address'],
                data['logo_path'], data['bank_name'], data['account_number'],
                data['bank_ifsc'], data['bank_branch']
            ))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO company_info (
                    id, name, gstin, contact, address, logo_path,
                    bank_name, account_number, bank_ifsc, bank_branch
                ) VALUES (
                    1, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                data['name'], data['gstin'], data['contact'], data['address'],
                data['logo_path'], data['bank_name'], data['account_number'],
                data['bank_ifsc'], data['bank_branch']
            ))

        conn.commit()
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def load_company_info():
    """
    Load the company information from the database.
    Returns a dictionary or None if not found.
    """
    try:
        conn = connect()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM company_info WHERE id = 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_invoice_summary():
    """
    Get summary data for the invoice dashboard.

    Returns:
        dict: Contains total invoices, paid bills, pending bills, and due amount.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Total invoices
        cursor.execute("SELECT COUNT(*) FROM invoices")
        total_invoices = cursor.fetchone()[0]
        
        # Paid bills
        cursor.execute("SELECT COUNT(*) FROM invoices WHERE payment_status = 'Paid'")
        paid_bills = cursor.fetchone()[0]
        
        # Pending bills
        cursor.execute("SELECT COUNT(*) FROM invoices WHERE payment_status = 'Pending'")
        pending_bills = cursor.fetchone()[0]
        
        # Due amount (sum of grand_total for pending invoices)
        cursor.execute("SELECT COALESCE(SUM(grand_total), 0) FROM invoices WHERE payment_status = 'Pending'")
        due_amount = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_invoices": total_invoices,
            "paid_bills": paid_bills,
            "pending_bills": pending_bills,
            "due_amount": due_amount
        }
        
    except sqlite3.Error as e:
        print(f"Database error in get_invoice_summary: {e}")
        if conn:
            conn.close()
        return {
            "total_invoices": 0,
            "paid_bills": 0,
            "pending_bills": 0,
            "due_amount": 0.0
        }

     #  INVENTORY SECTION

def add_inventory_item(product_name: str, product_code: str, category: str, 
                      unit: str, quantity: int, purchase_price: float, 
                      selling_price: float, gst_percentage: str = 'None', 
                      description: str = '') -> bool:
    """
    Add a new inventory item to the database.
    
    Args:
        product_name: Name of the product
        product_code: Unique code for the product
        category: Product category
        unit: Unit of measurement (pcs/kg/box etc.)
        quantity: Quantity in stock
        purchase_price: Purchase price of the item
        selling_price: Selling price of the item
        gst_percentage: GST percentage (optional)
        description: Product description (optional)
    
    Returns:
        bool: True if item was added successfully, False otherwise
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Check if product code already exists
        cursor.execute("SELECT id FROM inventory_items WHERE product_code = ?", (product_code,))
        if cursor.fetchone():
            print(f"Error: Product code '{product_code}' already exists!")
            conn.close()
            return False
        
        # Insert new item
        cursor.execute("""
            INSERT INTO inventory_items 
            (product_name, product_code, category, unit, quantity_in_stock, 
             purchase_price, selling_price, gst_percentage, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (product_name, product_code, category, unit, quantity, 
              purchase_price, selling_price, gst_percentage, description))
        
        conn.commit()
        conn.close()
        print(f"Successfully added item: {product_name}")
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error adding item: {e}")
        return False

def update_inventory_item(item_id: int, **kwargs) -> bool:
    """
    Update an existing inventory item. 
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        allowed_fields = ['product_name', 'product_code', 'category', 'unit', 
                         'quantity_in_stock', 'purchase_price', 'selling_price', 
                         'gst_percentage', 'description']
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                values.append(value)
        
        if not update_fields:
            print("No valid fields to update")
            conn.close()
            return False
        
        # Add updated_at timestamp
        """update_fields.append("updated_at = CURRENT_TIMESTAMP")"""
        
        query = f"UPDATE inventory_items SET {', '.join(update_fields)} WHERE id = ?"
        values.append(item_id)
        
        print(f"Executing query: {query}")  # Debug line
        print(f"With values: {values}")     # Debug line
        
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            print(f"No item found with ID: {item_id}")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        print(f"Successfully updated item ID: {item_id}")
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error updating item: {e}")
        return False

def delete_inventory_item(item_id: int) -> bool:
    """
    Delete an inventory item by ID.
    
    Args:
        item_id: ID of the item to delete
    
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM inventory_items WHERE id = ?", (item_id,))
        
        if cursor.rowcount == 0:
            print(f"No item found with ID: {item_id}")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        print(f"Successfully deleted item ID: {item_id}")
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error deleting item: {e}")
        return False

def get_all_inventory_items():
    """Get all inventory items from database with better error handling."""
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, product_name, product_code, category, unit, 
                   quantity_in_stock, purchase_price, selling_price, 
                   gst_percentage, description
            FROM inventory_items 
            ORDER BY id DESC
        """)
        
        columns = [description[0] for description in cursor.description]
        items = []
        for row in cursor.fetchall():
            item_dict = dict(zip(columns, row))
            # Ensure all values are properly handled
            for key, value in item_dict.items():
                if value is None:
                    if key in ['purchase_price', 'selling_price']:
                        item_dict[key] = 0.0
                    elif key in ['quantity_in_stock']:
                        item_dict[key] = 0
                    else:
                        item_dict[key] = ''
            items.append(item_dict)
        
        conn.close()
        return items
        
    except Exception as e:
        print(f"Error fetching inventory items: {e}")
        return []
    
def get_inventory_item_by_code(product_code: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific inventory item by product code.
    
    Args:
        product_code: Product code to search for
    
    Returns:
        Dictionary containing item data or None if not found
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, product_name, product_code, category, unit, 
                   quantity_in_stock, purchase_price, selling_price, 
                   gst_percentage, description, created_at, updated_at
            FROM inventory_items 
            WHERE product_code = ?
        """, (product_code,))
        
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            item = dict(zip(columns, row))
            conn.close()
            return item
        
        conn.close()
        return None
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error retrieving item: {e}")
        return None

def search_inventory_items(search_term: str) -> List[Dict[str, Any]]:
    """
    Search inventory items by name, code, or category.
    
    Args:
        search_term: Term to search for
    
    Returns:
        List of dictionaries containing matching items
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        search_pattern = f"%{search_term}%"
        cursor.execute("""
            SELECT id, product_name, product_code, category, unit, 
                   quantity_in_stock, purchase_price, selling_price, 
                   gst_percentage, description
            FROM inventory_items 
            WHERE product_name LIKE ? OR product_code LIKE ? OR category LIKE ?
            ORDER BY product_name
        """, (search_pattern, search_pattern, search_pattern))
        
        columns = [description[0] for description in cursor.description]
        items = []
        
        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            items.append(item)
        
        conn.close()
        return items
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Error searching items: {e}")
        return []

def update_stock_quantity(product_code: str, quantity_change: int) -> bool:
    """
    Update stock quantity for a product (for sales/purchases).
    
    Args:
        product_code: Product code to update
        quantity_change: Change in quantity (positive for additions, negative for sales)
    
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Get current quantity
        cursor.execute("SELECT quantity_in_stock FROM inventory_items WHERE product_code = ?", 
                      (product_code,))
        result = cursor.fetchone()
        
        if not result:
            print(f"Product code '{product_code}' not found")
            conn.close()
            return False
        
        current_quantity = result[0]
        new_quantity = current_quantity + quantity_change
        
        if new_quantity < 0:
            print(f"Insufficient stock. Current: {current_quantity}, Requested: {abs(quantity_change)}")
            conn.close()
            return False
        
        # Update quantity
        cursor.execute("""
            UPDATE inventory_items 
            SET quantity_in_stock = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE product_code = ?
        """, (new_quantity, product_code))
        
        conn.commit()
        conn.close()
        print(f"Stock updated for {product_code}: {current_quantity} -> {new_quantity}")
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error updating stock: {e}")
        return False

def get_low_stock_items(threshold: int = 10) -> List[Dict[str, Any]]:
    """
    Get items with stock below the specified threshold.
    
    Args:
        threshold: Stock threshold (default: 10)
    
    Returns:
        List of dictionaries containing low stock items
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, product_name, product_code, category, unit, 
                   quantity_in_stock, purchase_price, selling_price, 
                   gst_percentage, description
            FROM inventory_items 
            WHERE quantity_in_stock <= ?
            ORDER BY quantity_in_stock ASC
        """, (threshold,))
        
        columns = [description[0] for description in cursor.description]
        items = []
        
        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            items.append(item)
        
        conn.close()
        return items
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Error retrieving low stock items: {e}")
        return []

# Initialize database on import
def initialize_database():
    """Initialize the database by creating necessary tables."""
    try:
        create_tables()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Call initialization when module is imported
if __name__ == "__main__":
    initialize_database()

    # CHALLAN SECTION

def save_challan(challan_data: Dict, items: List[Dict]) -> Optional[int]:
    """
    Save challan and its items to database
    
    Args:
        challan_data: Dictionary containing challan information
        items: List of dictionaries containing item information
    
    Returns:
        challan_id if successful, None if failed
    """
    conn = connect()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Insert challan data
        cursor.execute('''
            INSERT INTO challans (
                customer_name, customer_address, gstin, state, state_code,
                challan_no, date, vehicle, transporter, lr, grand_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            challan_data.get('customer_name', ''),
            challan_data.get('customer_address', ''),
            challan_data.get('gstin', ''),
            challan_data.get('state', ''),
            challan_data.get('state_code', ''),
            challan_data.get('challan_no', ''),
            challan_data.get('date', ''),
            challan_data.get('vehicle', ''),
            challan_data.get('transporter', ''),
            challan_data.get('lr', ''),
            challan_data.get('grand_total', 0.0)
        ))
        
        challan_id = cursor.lastrowid
        
        # Insert items
        for item in items:
            cursor.execute('''
                INSERT INTO challan_items (
                    challan_id, description, hsn, quantity, type, rate, total
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                challan_id,
                item.get('description', ''),
                item.get('hsn', ''),
                item.get('quantity', 0),
                item.get('type', ''),
                item.get('rate', 0.0),
                item.get('total', 0.0)
            ))
        
        conn.commit()
        print(f"Challan saved successfully with ID: {challan_id}")
        return challan_id
        
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        conn.rollback()
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_challan_by_id(challan_id):
    """
    Retrieve challan and its items by ID
    Args:
        challan_id: The ID of the challan to retrieve
    Returns:
        Tuple of (challan_data, items_list) if found, None if not found
    """
    conn = connect()
    if not conn:
        return None
    
    try:
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        # Get challan data
        cursor.execute('SELECT * FROM challans WHERE id = ?', (challan_id,))
        challan_row = cursor.fetchone()
        
        if not challan_row:
            return None
        
        # Convert row to dictionary - now this will work!
        challan_data = dict(challan_row)
        
        # Get items
        cursor.execute('SELECT * FROM challan_items WHERE challan_id = ?', (challan_id,))
        items_rows = cursor.fetchall()
        
        items = [dict(row) for row in items_rows]
        
        return challan_data, items
        
    except sqlite3.Error as e:
        print(f"Error retrieving challan: {e}")
        return None
    finally:
        conn.close()

def get_all_challans():
    """
    Retrieve all challans from the database with their basic information
    
    Returns:
        list: List of challan dictionaries, or empty list if none found
    """
    try:
        conn = connect()
        conn.row_factory = sqlite3.Row  # ✅ Add this line - same as in get_all_invoices()
        cursor = conn.cursor()
        
        # Get all challans with basic information
        cursor.execute("""
            SELECT 
                id,
                customer_name,
                customer_address,
                gstin,
                state,
                state_code,
                challan_no,
                date,
                vehicle,
                transporter,
                lr,
                grand_total
            FROM challans 
            ORDER BY id DESC
        """)
        
        challans_rows = cursor.fetchall()
        challans = []
        
        for challan_row in challans_rows:
            challan_data = dict(challan_row) 
            
            # Get item count for this challan
            cursor.execute("SELECT COUNT(*) as item_count FROM challan_items WHERE challan_id = ?", (challan_data['id'],))
            item_count_row = cursor.fetchone()
            challan_data['items'] = [{'count': item_count_row['item_count']}]  
            challans.append(challan_data)
        
        conn.close()
        return challans
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.close()
        return []
    except Exception as e:
        print(f"Error retrieving challans: {e}")
        if 'conn' in locals():
            conn.close()
        return []

def delete_challan(challan_id: int) -> bool:
    """
    Delete a challan and its items
    
    Args:
        challan_id: ID of the challan to delete
    
    Returns:
        True if successful, False otherwise
    """
    conn = connect()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Delete challan (items will be deleted automatically due to CASCADE)
        cursor.execute('DELETE FROM challans WHERE id = ?', (challan_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Challan {challan_id} deleted successfully")
            return True
        else:
            print(f"Challan {challan_id} not found")
            return False
            
    except sqlite3.Error as e:
        print(f"Error deleting challan: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def search_challans(search_term: str) -> List[Dict]:
    """
    Search challans by customer name, challan number, or GSTIN
    
    Args:
        search_term: Term to search for
    
    Returns:
        List of matching challan dictionaries
    """
    conn = connect()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        search_pattern = f"%{search_term}%"
        
        cursor.execute('''
            SELECT * FROM challans 
            WHERE customer_name LIKE ? 
            OR challan_no LIKE ? 
            OR gstin LIKE ?
            ORDER BY date DESC
        ''', (search_pattern, search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    except sqlite3.Error as e:
        print(f"Error searching challans: {e}")
        return []
    finally:
        conn.close()

def update_challan(challan_id: int, challan_data: Dict, items: List[Dict]) -> bool:
    """
    Update an existing challan and its items
    
    Args:
        challan_id: ID of the challan to update
        challan_data: Updated challan data
        items: Updated items list
    
    Returns:
        True if successful, False otherwise
    """
    conn = connect()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Update challan data
        cursor.execute('''
            UPDATE challans SET
                customer_name = ?, customer_address = ?, gstin = ?, state = ?, 
                state_code = ?, challan_no = ?, date = ?, vehicle = ?, 
                transporter = ?, lr = ?, grand_total = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            challan_data.get('customer_name', ''),
            challan_data.get('customer_address', ''),
            challan_data.get('gstin', ''),
            challan_data.get('state', ''),
            challan_data.get('state_code', ''),
            challan_data.get('challan_no', ''),
            challan_data.get('date', ''),
            challan_data.get('vehicle', ''),
            challan_data.get('transporter', ''),
            challan_data.get('lr', ''),
            challan_data.get('grand_total', 0.0),
            challan_id
        ))
        
        # Delete existing items
        cursor.execute('DELETE FROM challan_items WHERE challan_id = ?', (challan_id,))
        
        # Insert updated items
        for item in items:
            cursor.execute('''
                INSERT INTO challan_items (
                    challan_id, description, hsn, quantity, type, rate, total
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                challan_id,
                item.get('description', ''),
                item.get('hsn', ''),
                item.get('quantity', 0),
                item.get('type', ''),
                item.get('rate', 0.0),
                item.get('total', 0.0)
            ))
        
        conn.commit()
        print(f"Challan {challan_id} updated successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"Error updating challan: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Initialize database when module is imported
create_tables()

if __name__ == "__main__":
    print("Database initialization completed")
