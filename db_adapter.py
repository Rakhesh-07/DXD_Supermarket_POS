import sqlite3
import hashlib
import os

try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False

# Perform MySQL availability check once on module load
MYSQL_AVAILABLE = False
if HAS_MYSQL:
    try:
        # Check connection with a tight 1-second timeout to avoid lag
        con = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='root',
            connect_timeout=1
        )
        con.close()
        MYSQL_AVAILABLE = True
    except Exception:
        MYSQL_AVAILABLE = False

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def get_connection():
    """
    Attempts to connect to MySQL database 'project'.
    If MySQL connection fails or is not installed, falls back to a local SQLite database 'project.db'.
    Returns (connection, cursor, is_sqlite_bool)
    """
    # 1. Try MySQL only if it was verified as available on startup
    if MYSQL_AVAILABLE:
        try:
            con = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='root'
            )
            # Create DB if it doesn't exist
            mycursor = con.cursor()
            mycursor.execute("CREATE DATABASE IF NOT EXISTS project")
            con.database = 'project'
            return con, mycursor, False
        except Exception:
            pass
            
    # 2. SQLite Fallback
    db_path = "project.db"
    con = sqlite3.connect(db_path)
    mycursor = con.cursor()
    return con, mycursor, True

def execute_query(query, params=None, commit=False, fetch="all"):
    """
    Executes a query safely, handles connections, and returns results.
    query: SQL query string (uses ? for SQLite and %s for MySQL)
    params: tuple of parameters
    commit: True to commit changes (insert/update/delete)
    fetch: 'all' to fetchall, 'one' to fetchone, 'none' to not fetch
    """
    con, cursor, is_sqlite = get_connection()
    
    # If using MySQL, replace ? placeholders with %s
    if not is_sqlite and params:
        query = query.replace("?", "%s")
        
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if commit:
            con.commit()
            
        if fetch == "all":
            result = cursor.fetchall()
        elif fetch == "one":
            result = cursor.fetchone()
        else:
            result = None
            
        return result
    except Exception as e:
        print(f"Database Query Error: {e} \nQuery: {query}")
        raise e
    finally:
        cursor.close()
        con.close()

def init_tables():
    """
    Initializes database tables and default employee seed accounts.
    """
    con, mycursor, is_sqlite = get_connection()
    
    if is_sqlite:
        # Create SQLite tables
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS EMPLOYEES (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """)
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS STOCK (
            item_code INTEGER PRIMARY KEY,
            item_name TEXT UNIQUE NOT NULL,
            price INTEGER NOT NULL,
            available_stock INTEGER NOT NULL
        )
        """)
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS MEMBERSHIP (
            mem_id INTEGER PRIMARY KEY,
            mem_name TEXT NOT NULL,
            phone_number INTEGER UNIQUE NOT NULL,
            exp_date TEXT NOT NULL,
            address TEXT NOT NULL
        )
        """)
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS BILLS (
            bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cashier_username TEXT,
            customer_phone TEXT,
            customer_name TEXT,
            bill_date TEXT,
            total_amount INTEGER,
            discount_amount INTEGER,
            final_amount INTEGER,
            amount_paid INTEGER,
            amount_returned INTEGER
        )
        """)
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS BILL_ITEMS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER,
            item_code INTEGER,
            item_name TEXT,
            quantity INTEGER,
            price_at_sale INTEGER
        )
        """)
    else:
        # Create MySQL tables
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS EMPLOYEES (
            username VARCHAR(255) PRIMARY KEY,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL
        )
        """)
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS STOCK (
            item_code INT PRIMARY KEY,
            item_name VARCHAR(255) UNIQUE NOT NULL,
            price INT NOT NULL,
            available_stock INT NOT NULL
        )
        """)
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS MEMBERSHIP (
            mem_id INT PRIMARY KEY,
            mem_name VARCHAR(255) NOT NULL,
            phone_number BIGINT UNIQUE NOT NULL,
            exp_date DATE NOT NULL,
            address VARCHAR(255) NOT NULL
        )
        """)
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS BILLS (
            bill_id INT AUTO_INCREMENT PRIMARY KEY,
            cashier_username VARCHAR(255),
            customer_phone VARCHAR(50),
            customer_name VARCHAR(255),
            bill_date DATE,
            total_amount INT,
            discount_amount INT,
            final_amount INT,
            amount_paid INT,
            amount_returned INT
        )
        """)
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS BILL_ITEMS (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bill_id INT,
            item_code INT,
            item_name VARCHAR(255),
            quantity INT,
            price_at_sale INT
        )
        """)
    
    con.commit()
    
    # 3. Seed Default Employees if empty
    mycursor.execute("SELECT COUNT(*) FROM EMPLOYEES")
    if mycursor.fetchone()[0] == 0:
        default_employees = [
            ("rocky2003", hash_password("vrv07"), "SAKTHIVEL", "Cashier"),
            ("rohith_2k3", hash_password("tartaglia"), "ROHITH", "Cashier"),
            ("aniruths003", hash_password("anir100"), "ANIRUTH", "Cashier"),
            ("giffyy", hash_password("jose123"), "GIFTON", "Cashier"),
            ("dxd", hash_password("ryomen"), "ADMIN", "Manager")
        ]
        placeholder = "?" if is_sqlite else "%s"
        mycursor.executemany(f"INSERT INTO EMPLOYEES VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})", default_employees)
        con.commit()
        
    # 4. Seed Stock if empty
    mycursor.execute("SELECT COUNT(*) FROM STOCK")
    if mycursor.fetchone()[0] == 0:
        sample_items = [
            (101, "APPLE", 120, 50),
            (102, "BANANA", 60, 50),
            (103, "MILK", 40, 50),
            (104, "BREAD", 30, 50),
            (105, "EGG", 6, 100),
            (106, "CHOCOLATE", 80, 50),
        ]
        placeholder = "?" if is_sqlite else "%s"
        mycursor.executemany(f"INSERT INTO STOCK VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})", sample_items)
        con.commit()

    con.close()

# Auto-initialize tables when module is imported to ensure database is always ready
try:
    init_tables()
except Exception as e:
    print(f"Warning: Database tables could not be initialized: {e}")
