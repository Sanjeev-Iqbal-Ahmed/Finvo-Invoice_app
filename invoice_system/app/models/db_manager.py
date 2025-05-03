import sqlite3
import os
from pathlib import Path

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
        
        if existing:
            print(f"Warning: Invoice number {invoice_data['invoice_no']} already exists. Updating existing invoice.")
            invoice_id = existing[0]
            
            # Update existing invoice
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
                    grand_total = ?
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
                invoice_id
            ))
            
            # Delete existing items for this invoice
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        else:
            # Insert new invoice
            cursor.execute("""
                INSERT INTO invoices (
                    customer_name, customer_address, gstin, state, state_code,
                    invoice_no, date, challan, transporter, consignment, grand_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                invoice_data['grand_total']
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

def get_invoice(invoice_id):
    """
    Retrieve an invoice and its items from the database
    
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



