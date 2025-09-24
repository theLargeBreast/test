"""Database setup and models for the sales quoting application."""

import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional, Any

DATABASE_NAME = "sales_quotes.db"

def init_database():
    """Initialize the database with required tables."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(100),
                base_product BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Accessories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accessories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Product-Accessory compatibility rules
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_accessory_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                base_product_sku VARCHAR(50) NOT NULL,
                accessory_sku VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (base_product_sku) REFERENCES products(sku),
                FOREIGN KEY (accessory_sku) REFERENCES accessories(sku),
                UNIQUE(base_product_sku, accessory_sku)
            )
        """)
        
        # Quotes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_number VARCHAR(50) UNIQUE NOT NULL,
                customer_name VARCHAR(200),
                total_amount DECIMAL(10,2) DEFAULT 0.00,
                status VARCHAR(20) DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Quote items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quote_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                sku VARCHAR(50) NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                unit_price DECIMAL(10,2) NOT NULL,
                line_total DECIMAL(10,2) NOT NULL,
                item_type VARCHAR(20) NOT NULL DEFAULT 'product',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quote_id) REFERENCES quotes(id)
            )
        """)
        
        conn.commit()

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

class ProductDB:
    """Database operations for products."""
    
    @staticmethod
    def create_product(sku: str, name: str, price: float, description: str = "", 
                      category: str = "", base_product: bool = False) -> int:
        """Create a new product."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (sku, name, description, price, category, base_product)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sku, name, description, price, category, base_product))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_all_products() -> List[Dict[str, Any]]:
        """Get all products."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_product_by_sku(sku: str) -> Optional[Dict[str, Any]]:
        """Get product by SKU."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE sku = ?", (sku,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def update_product(sku: str, **kwargs) -> bool:
        """Update product by SKU."""
        if not kwargs:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [sku]
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE products SET {set_clause} WHERE sku = ?", values)
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete_product(sku: str) -> bool:
        """Delete product by SKU."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE sku = ?", (sku,))
            conn.commit()
            return cursor.rowcount > 0

class AccessoryDB:
    """Database operations for accessories."""
    
    @staticmethod
    def create_accessory(sku: str, name: str, price: float, description: str = "") -> int:
        """Create a new accessory."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accessories (sku, name, description, price)
                VALUES (?, ?, ?, ?)
            """, (sku, name, description, price))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_all_accessories() -> List[Dict[str, Any]]:
        """Get all accessories."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accessories ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_compatible_accessories(base_product_sku: str) -> List[Dict[str, Any]]:
        """Get accessories compatible with a base product."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.* FROM accessories a
                JOIN product_accessory_rules par ON a.sku = par.accessory_sku
                WHERE par.base_product_sku = ?
                ORDER BY a.name
            """, (base_product_sku,))
            return [dict(row) for row in cursor.fetchall()]

class CompatibilityDB:
    """Database operations for product-accessory compatibility rules."""
    
    @staticmethod
    def add_compatibility_rule(base_product_sku: str, accessory_sku: str) -> bool:
        """Add a compatibility rule."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO product_accessory_rules (base_product_sku, accessory_sku)
                    VALUES (?, ?)
                """, (base_product_sku, accessory_sku))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    @staticmethod
    def remove_compatibility_rule(base_product_sku: str, accessory_sku: str) -> bool:
        """Remove a compatibility rule."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM product_accessory_rules 
                WHERE base_product_sku = ? AND accessory_sku = ?
            """, (base_product_sku, accessory_sku))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def is_compatible(base_product_sku: str, accessory_sku: str) -> bool:
        """Check if accessory is compatible with base product."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM product_accessory_rules
                WHERE base_product_sku = ? AND accessory_sku = ?
            """, (base_product_sku, accessory_sku))
            return cursor.fetchone() is not None

class QuoteDB:
    """Database operations for quotes."""
    
    @staticmethod
    def create_quote(quote_number: str, customer_name: str = "") -> int:
        """Create a new quote."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quotes (quote_number, customer_name)
                VALUES (?, ?)
            """, (quote_number, customer_name))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def add_quote_item(quote_id: int, sku: str, quantity: int, unit_price: float, 
                      item_type: str = 'product') -> int:
        """Add item to quote."""
        line_total = quantity * unit_price
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quote_items (quote_id, sku, quantity, unit_price, line_total, item_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (quote_id, sku, quantity, unit_price, line_total, item_type))
            conn.commit()
            
            # Update quote total
            cursor.execute("""
                UPDATE quotes SET total_amount = (
                    SELECT SUM(line_total) FROM quote_items WHERE quote_id = ?
                ), updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (quote_id, quote_id))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_quote_with_items(quote_id: int) -> Optional[Dict[str, Any]]:
        """Get quote with all its items."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get quote
            cursor.execute("SELECT * FROM quotes WHERE id = ?", (quote_id,))
            quote_row = cursor.fetchone()
            if not quote_row:
                return None
            
            quote = dict(quote_row)
            
            # Get quote items
            cursor.execute("SELECT * FROM quote_items WHERE quote_id = ?", (quote_id,))
            quote['items'] = [dict(row) for row in cursor.fetchall()]
            
            return quote

if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
    print("Database initialized successfully!")