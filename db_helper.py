import sqlite3
import os
import pandas as pd

# Local DB File
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'database.sqlite')
EXCEL_FILE = os.path.join(BASE_DIR, 'login_data.xlsx')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database with required tables."""
    if not os.path.exists(DB_FILE):
        print("Initializing SQLite Database...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create Market Prices Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT NOT NULL,
            price REAL NOT NULL,
            atlanta_retail REAL,
            chicago_retail REAL,
            la_retail REAL,
            new_york_retail REAL,
            average_spread TEXT,
            market TEXT NOT NULL,
            trend TEXT,
            phone TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Disease Data Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disease_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease TEXT NOT NULL,
            treatment TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Create Soil Test History Table (App Data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soil_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_phone TEXT,
            n_val REAL,
            p_val REAL,
            k_val REAL,
            ph_val REAL,
            recommendation TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Seed Data if empty
    cursor.execute('SELECT count(*) FROM market_prices')
    if cursor.fetchone()[0] == 0:
        market_data = [
            ("Tomato", 2500, "Local Mandi", "up"),
            ("Potato", 1200, "City Market", "down"),
            ("Onion", 1800, "Wholesale", "up")
        ]
        cursor.executemany('INSERT INTO market_prices (crop, price, market, trend) VALUES (?, ?, ?, ?)', market_data)

    cursor.execute('SELECT count(*) FROM disease_data')
    if cursor.fetchone()[0] == 0:
        disease_data = [
            ("Leaf Blight", "Use Fungicide X", "Fungal infection affecting leaves."),
            ("Rust", "Remove infected leaves", "Reddish-brown pustules on leaves."),
            ("Healthy", "Keep monitoring", "Plant is in good condition.")
        ]
        cursor.executemany('INSERT INTO disease_data (disease, treatment, description) VALUES (?, ?, ?)', disease_data)

    conn.commit()
    conn.close()
    print("Database initialization complete.")

def get_market_prices(limit=None):
    conn = get_db_connection()
    if limit:
        prices = conn.execute('SELECT * FROM market_prices ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    else:
        prices = conn.execute('SELECT * FROM market_prices ORDER BY id DESC').fetchall()
    conn.close()
    return [dict(ix) for ix in prices]

def add_market_item(crop, price, market, phone=None):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO market_prices (crop, price, market, trend, phone) VALUES (?, ?, ?, ?, ?)', 
                     (crop, price, market, 'new', phone))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding market item: {e}")
        return False

def register_user(phone, password, name):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (phone, password, name) VALUES (?, ?, ?)', 
                     (phone, password, name))
        conn.commit()
        conn.close()

        # --- NEW: Store in Excel ---
        data = {'Name': [name], 'Phone': [phone], 'Password': [password]}
        df_new = pd.DataFrame(data)
        
        if os.path.exists(EXCEL_FILE):
            df_old = pd.read_excel(EXCEL_FILE)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_final = df_new
            
        df_final.to_excel(EXCEL_FILE, index=False)
        # ---------------------------

        return True
    except sqlite3.IntegrityError:
        return False # User already exists
    except Exception as e:
        print(f"Error registering user: {e}")
        return False

def verify_user(phone, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE phone = ? AND password = ?', (phone, password)).fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def get_disease_info(disease_name):
    conn = get_db_connection()
    info = conn.execute('SELECT * FROM disease_data WHERE disease = ?', (disease_name,)).fetchone()
    conn.close()
    if info:
        return dict(info)
    return None

def save_soil_test(user_phone, n, p, k, ph, recommendation):
    """Saves soil test results / app data."""
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO soil_tests (user_phone, n_val, p_val, k_val, ph_val, recommendation)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_phone, n, p, k, ph, recommendation))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving soil test: {e}")
        return False

