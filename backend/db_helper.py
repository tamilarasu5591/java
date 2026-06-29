import sqlite3
import os
import pandas as pd
import bcrypt

# Local DB File
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'database.sqlite')
EXCEL_FILE = os.path.join(BASE_DIR, 'login_data.xlsx')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode for concurrency
    conn.execute("PRAGMA synchronous=NORMAL;")
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
            email TEXT,
            password TEXT NOT NULL
        )
    ''')

    # Migration: Add email column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists


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
    cursor.execute('CREATE TABLE IF NOT EXISTS soil_tests (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, n_val REAL, p_val REAL, k_val REAL, ph_val REAL, recommendation TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    
    # --- NEW TABLES ---

    # User Activities Table (Logs actions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Yield Estimates Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS yield_estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            crop TEXT NOT NULL,
            acres REAL NOT NULL,
            estimated_yield TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Forum Posts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forum_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            author_name TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            likes INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Forum Comments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forum_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            phone TEXT NOT NULL,
            author_name TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES forum_posts(id)
        )
    ''')

    # Store Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS store_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image_url TEXT,
            rating REAL DEFAULT 4.0,
            in_stock INTEGER DEFAULT 1
        )
    ''')

    # Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Placed',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES store_products(id)
        )
    ''')

    # Machinery Listings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS machinery_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_phone TEXT NOT NULL,
            owner_name TEXT DEFAULT 'Owner',
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            rate_per_hour REAL NOT NULL,
            location TEXT,
            available INTEGER DEFAULT 1,
            description TEXT
        )
    ''')

    # Rental Bookings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rental_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            renter_phone TEXT NOT NULL,
            listing_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            hours INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (listing_id) REFERENCES machinery_listings(id)
        )
    ''')

    # Market Price Matrix Table (vegetable × market grid)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_price_matrix (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vegetable TEXT NOT NULL,
            market TEXT NOT NULL,
            price REAL NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_by TEXT,
            UNIQUE(vegetable COLLATE NOCASE, market COLLATE NOCASE)
        )
    ''')

    # Add indexes for production performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_commodity ON market_prices(crop)') 
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_arrival_date ON market_prices(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_soil_tests_phone ON soil_tests(phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_forum_posts_cat ON forum_posts(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_store_products_cat ON store_products(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activities_phone ON user_activities(phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_matrix_veg ON market_price_matrix(vegetable COLLATE NOCASE)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_matrix_mkt ON market_price_matrix(market COLLATE NOCASE)')
    
    # Seed Data if empty
    cursor.execute('SELECT count(*) FROM market_prices')
    if cursor.fetchone()[0] == 0:
        market_data = [
            ("Tomato", 25, "Local Mandi", "up"),
            ("Potato", 20, "City Market", "down"),
            ("Onion", 30, "Wholesale", "up"),
            ("Wheat", 25, "FCI Depot", "stable"),
            ("Rice (Paddy)", 20, "APMC Yard", "up"),
            ("Maize", 22, "Kisan Mandi", "stable"),
            ("Cotton", 70, "Textile Hub", "up"),
            ("Sugarcane", 3.5, "Sugar Mill", "stable"),
            ("Soybean", 46, "Oilseeds Market", "down"),
            ("Mustard", 55, "Local APMC", "up"),
            ("Groundnut", 60, "Wholesale Hub", "stable"),
            ("Bengal Gram", 60, "Dal Mandi", "up"),
            ("Green Gram (Moong)", 85, "City Market", "down"),
            ("Black Gram (Urad)", 75, "Local Mandi", "up"),
            ("Turmeric", 140, "Spices Market", "stable"),
            ("Chilli (Red)", 190, "Export Zone", "up"),
            ("Garlic", 150, "City Market", "up"),
            ("Ginger", 80, "Local Mandi", "down"),
            ("Cabbage", 15, "Vegetable Market", "stable"),
            ("Cauliflower", 20, "Wholesale", "up"),
            ("Brinjal", 30, "Local Mandi", "down"),
            ("Okra (Bhindi)", 40, "City Market", "up"),
            ("Apple", 110, "Fruit Market", "stable"),
            ("Banana", 40, "Local APMC", "stable"),
            ("Mango", 80, "Wholesale", "up")
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

    # Seed Store Products
    cursor.execute('SELECT count(*) FROM store_products')
    if cursor.fetchone()[0] == 0:
        products = [
            ("Hybrid Tomato Seeds (500g)", "Seeds", 320, "High-yield hybrid tomato seeds suitable for all seasons. Disease resistant variety.", "🍅", 4.5, 1),
            ("Basmati Rice Seeds (1kg)", "Seeds", 450, "Premium Pusa Basmati 1121. Long grain, aromatic variety.", "🌾", 4.7, 1),
            ("Organic Neem Cake (5kg)", "Fertilizer", 280, "100% organic neem cake fertilizer. Improves soil health and repels pests.", "🌿", 4.3, 1),
            ("DAP Fertilizer (50kg)", "Fertilizer", 1350, "Di-Ammonium Phosphate. Essential for root development and flowering.", "🧪", 4.6, 1),
            ("Urea (45kg bag)", "Fertilizer", 267, "Standard grade urea for nitrogen supplementation. Government subsidized.", "🧪", 4.2, 1),
            ("Bio-Pesticide Neem Oil (1L)", "Pesticide", 380, "Cold-pressed neem oil. Organic pest control for all crops.", "🛡️", 4.4, 1),
            ("Drip Irrigation Kit (1 acre)", "Equipment", 8500, "Complete micro-drip system with timer. Saves 60% water.", "💧", 4.8, 1),
            ("Hand Sprayer (16L)", "Equipment", 1200, "Battery-operated knapsack sprayer. 4-hour battery life.", "🔋", 4.1, 1),
            ("Vermicompost (25kg)", "Fertilizer", 450, "Premium earthworm compost. Rich in NPK and beneficial microbes.", "🪱", 4.5, 1),
            ("Maize Seeds (2kg)", "Seeds", 550, "High-yield hybrid maize. Matures in 90-100 days.", "🌽", 4.3, 1),
            ("Soil Testing Kit", "Equipment", 1800, "Complete NPK + pH testing kit with 50 test strips.", "🧪", 4.6, 1),
            ("Greenhouse Net (10m x 5m)", "Equipment", 2200, "UV-stabilized shade net. 50% shade factor.", "🏗️", 4.2, 1),
        ]
        cursor.executemany('INSERT INTO store_products (name, category, price, description, image_url, rating, in_stock) VALUES (?, ?, ?, ?, ?, ?, ?)', products)

    # Seed Machinery Listings
    cursor.execute('SELECT count(*) FROM machinery_listings')
    if cursor.fetchone()[0] == 0:
        machinery = [
            ("9876543210", "Ravi Kumar", "Mahindra 575 DI Tractor", "Tractor", 800, "Salem, Tamil Nadu", 1, "45 HP tractor with rotavator attachment. Well maintained."),
            ("9876543211", "Suresh Reddy", "John Deere 5310 Tractor", "Tractor", 1000, "Coimbatore, Tamil Nadu", 1, "55 HP tractor. Ideal for ploughing and hauling."),
            ("9876543212", "Anand Patil", "DJI Agras T30 Drone", "Drone", 2500, "Bangalore, Karnataka", 1, "Agricultural spray drone. Covers 16 acres/hour. Operator included."),
            ("9876543213", "Meena Devi", "Kubota DC-70 Harvester", "Harvester", 3000, "Madurai, Tamil Nadu", 1, "Combine harvester for rice and wheat. Fuel included."),
            ("9876543214", "Prakash Sharma", "Rotavator (6ft)", "Attachment", 500, "Chennai, Tamil Nadu", 1, "Heavy duty rotavator. Compatible with 35+ HP tractors."),
            ("9876543215", "Lakshmi Farm Services", "Seed Drill Machine", "Planter", 600, "Trichy, Tamil Nadu", 1, "9-row seed drill. Precise spacing and depth control."),
        ]
        cursor.executemany('INSERT INTO machinery_listings (owner_phone, owner_name, name, type, rate_per_hour, location, available, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', machinery)

    # Seed Market Price Matrix
    cursor.execute('SELECT count(*) FROM market_price_matrix')
    if cursor.fetchone()[0] == 0:
        default_markets = ["Azadpur", "Koyambedu", "Vashi", "Devaraja", "Oddanchatram", "Salem", "Erode"]
        matrix_seed = [
            ("Tomato",          [28, 25, 30, 22, 24, 23, 26]),
            ("Potato",          [18, 22, 20, 16, 21, 20, 19]),
            ("Onion",           [32, 35, 30, 28, 34, 33, 31]),
            ("Brinjal",         [24, 20, 26, 18, 21, 19, 22]),
            ("Carrot",          [35, 30, 38, 28, 32, 29, 31]),
            ("Cabbage",         [15, 12, 18, 10, 13, 11, 14]),
            ("Cauliflower",     [22, 20, 25, 18, 19, 21, 20]),
            ("Ginger",          [85, 80, 90, 75, 82, 78, 81]),
            ("Garlic",          [150, 140, 160, 130, 145, 138, 142]),
            ("Chilli",          [45, 50, 48, 40, 49, 47, 46]),
            ("Rice (Paddy)",    [22, 20, 24, 18, 21, 19, 20]),
            ("Wheat",           [28, 25, 30, 22, 26, 24, 27]),
            ("Maize",           [20, 18, 22, 16, 19, 17, 18]),
            ("Cotton",          [72, 68, 75, 65, 70, 69, 71]),
            ("Sugarcane",       [3.5, 3.2, 3.8, 3.0, 3.3, 3.1, 3.4]),
            ("Banana",          [35, 40, 38, 30, 39, 37, 36]),
            ("Mango",           [80, 75, 85, 70, 77, 74, 78]),
            ("Grapes",          [60, 55, 65, 50, 58, 54, 56]),
            ("Apple",           [120, 110, 130, 100, 115, 105, 112]),
            ("Turmeric",        [140, 135, 150, 125, 138, 130, 136]),
        ]
        for veg, prices in matrix_seed:
            for i, market in enumerate(default_markets):
                cursor.execute(
                    'INSERT OR IGNORE INTO market_price_matrix (vegetable, market, price) VALUES (?, ?, ?)',
                    (veg, market, prices[i])
                )

    # Cleanup: Remove any erroneous 'Beginning' market entries
    cursor.execute("DELETE FROM market_price_matrix WHERE LOWER(market) = 'beginning'")
    if cursor.rowcount > 0:
        print(f"Cleaned up {cursor.rowcount} erroneous 'Beginning' market entries.")

    conn.commit()
    conn.close()
    print("Database initialization complete.")


def get_market_prices(limit=None):
    import random
    conn = get_db_connection()
    if limit:
        prices = conn.execute('SELECT * FROM market_prices ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    else:
        prices = conn.execute('SELECT * FROM market_prices ORDER BY id DESC').fetchall()
    conn.close()
    
    result = []
    for row in prices:
        item = dict(row)
        base = float(item['price'])
        # Add slight realistic variations for the other markets so they aren't zero
        item['atlanta_retail'] = round(base * random.uniform(1.02, 1.08), 2)  # Delhi
        item['chicago_retail'] = round(base * random.uniform(1.05, 1.12), 2)  # Chennai
        item['la_retail'] = round(base * random.uniform(1.08, 1.15), 2)       # Mumbai
        item['new_york_retail'] = round(base * random.uniform(0.98, 1.05), 2) # Mysuru
        item['average_spread'] = str(round(((item['la_retail'] - base) / base) * 100, 1)) + "%"
        result.append(item)
        
    return result

def add_market_item(crop, price, market, phone=None):
    """Legacy function — also upserts into matrix for compatibility."""
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO market_prices (crop, price, market, trend, phone) VALUES (?, ?, ?, ?, ?)', 
                     (crop, price, market, 'new', phone))
        conn.commit()
        conn.close()
        # Also update the matrix
        upsert_market_price(crop, market, price, phone)
        return True
    except Exception as e:
        print(f"Error adding market item: {e}")
        return False


# =============================================
# MARKET PRICE MATRIX FUNCTIONS
# =============================================

def upsert_market_price(vegetable, market, price, phone=None):
    """Insert or update a single cell in the vegetable × market matrix.
    Uses case-insensitive matching. Returns a result dict."""
    try:
        vegetable = vegetable.strip()
        market = market.strip()
        price = round(float(price), 2)
        
        conn = get_db_connection()
        
        # Check what exists (case-insensitive)
        existing_veg = conn.execute(
            'SELECT vegetable FROM market_price_matrix WHERE vegetable = ? COLLATE NOCASE LIMIT 1',
            (vegetable,)
        ).fetchone()
        existing_mkt = conn.execute(
            'SELECT market FROM market_price_matrix WHERE market = ? COLLATE NOCASE LIMIT 1',
            (market,)
        ).fetchone()
        
        # Use the canonical casing if it already exists
        if existing_veg:
            vegetable = dict(existing_veg)['vegetable']
        if existing_mkt:
            market = dict(existing_mkt)['market']
        
        # Upsert: INSERT or UPDATE only the targeted cell
        conn.execute('''
            INSERT INTO market_price_matrix (vegetable, market, price, updated_by, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(vegetable, market) DO UPDATE SET
                price = excluded.price,
                updated_by = excluded.updated_by,
                updated_at = CURRENT_TIMESTAMP
        ''', (vegetable, market, price, phone))
        conn.commit()
        conn.close()
        
        action = 'updated'
        if not existing_veg and not existing_mkt:
            action = 'new_both'
        elif not existing_veg:
            action = 'new_vegetable'
        elif not existing_mkt:
            action = 'new_market'
        
        return {'success': True, 'action': action, 'vegetable': vegetable, 'market': market, 'price': price}
    except Exception as e:
        print(f"Error upserting market price: {e}")
        return {'success': False, 'error': str(e)}


def get_market_matrix():
    """Returns the full market price matrix as:
    { markets: [...], vegetables: [...], data: { 'Tomato': {'Market1': 20, ...}, ... } }"""
    conn = get_db_connection()
    
    # Get all unique markets (column headers), ordered alphabetically
    markets_rows = conn.execute(
        "SELECT DISTINCT market FROM market_price_matrix WHERE LOWER(market) NOT IN ('beginning', 'koyambedu') ORDER BY market"
    ).fetchall()
    markets = [dict(r)['market'] for r in markets_rows]
    
    # Get all unique vegetables (row headers), ordered alphabetically
    veg_rows = conn.execute(
        'SELECT DISTINCT vegetable FROM market_price_matrix ORDER BY vegetable'
    ).fetchall()
    vegetables = [dict(r)['vegetable'] for r in veg_rows]
    
    # Get all price data
    all_prices = conn.execute(
        "SELECT vegetable, market, price, updated_at FROM market_price_matrix WHERE LOWER(market) NOT IN ('beginning', 'koyambedu')"
    ).fetchall()
    conn.close()
    
    # Build the matrix dict
    data = {}
    for veg in vegetables:
        data[veg] = {}
    
    for row in all_prices:
        r = dict(row)
        data[r['vegetable']][r['market']] = {
            'price': r['price'],
            'updated_at': r['updated_at']
        }
    
    return {
        'markets': markets,
        'vegetables': vegetables,
        'data': data
    }


def get_market_spreads():
    """Calculates min, max, avg and spread % for all vegetables in the matrix."""
    conn = get_db_connection()
    # Get all price data
    rows = conn.execute('''
        SELECT vegetable, MIN(price) as min_p, MAX(price) as max_p, AVG(price) as avg_p 
        FROM market_price_matrix 
        WHERE LOWER(market) NOT IN ('beginning', 'koyambedu')
        GROUP BY vegetable
    ''').fetchall()
    conn.close()
    
    spreads = []
    for r in rows:
        d = dict(r)
        min_p = d['min_p']
        max_p = d['max_p']
        # Spread = ((Max - Min) / Min) * 100
        spread_pct = round(((max_p - min_p) / min_p) * 100, 1) if min_p > 0 else 0
        spreads.append({
            'vegetable': d['vegetable'],
            'min': round(min_p, 2),
            'max': round(max_p, 2),
            'avg': round(d['avg_p'], 2),
            'spread': spread_pct
        })
    
    # Sort by highest spread first
    spreads.sort(key=lambda x: x['spread'], reverse=True)
    return spreads


def get_all_vegetables():
    """Returns a list of all distinct vegetable names from the matrix."""
    conn = get_db_connection()
    rows = conn.execute('SELECT DISTINCT vegetable FROM market_price_matrix ORDER BY vegetable').fetchall()
    conn.close()
    return [dict(r)['vegetable'] for r in rows]


def get_all_markets():
    """Returns a list of all distinct market names from the matrix."""
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT market FROM market_price_matrix WHERE LOWER(market) NOT IN ('beginning', 'koyambedu') ORDER BY market").fetchall()
    conn.close()
    return [dict(r)['market'] for r in rows]

def register_user(phone, password, name, email=None):
    try:
        # Hash password with bcrypt
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = get_db_connection()
        conn.execute('INSERT INTO users (phone, password, name, email) VALUES (?, ?, ?, ?)', 
                     (phone, hashed, name, email))
        conn.commit()
        conn.close()

        # --- Store in Excel (plain text kept for admin reference) ---
        data = {'Name': [name], 'Phone': [phone], 'Email': [email if email else ''], 'Password': ['[HASHED]']}
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
    user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
    conn.close()
    if user:
        user_dict = dict(user)
        stored_hash = user_dict['password']
        # Support both old plain-text and new bcrypt passwords
        try:
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                user_dict.pop('password', None)  # Don't send password to frontend
                return user_dict
        except (ValueError, AttributeError):
            # Fallback: plain-text comparison for old accounts
            if password == stored_hash:
                user_dict.pop('password', None)
                return user_dict
    return None

import secrets
import string

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if user:
        user_dict = dict(user)
        user_dict.pop('password', None)
        return user_dict
    return None

def register_user_google(email, name, google_id):
    """Fallback registration for Google OAuth users without a phone number."""
    existing_user = get_user_by_email(email)
    if existing_user:
        return existing_user
        
    random_str = ''.join(secrets.choice(string.digits) for _ in range(10))
    dummy_phone = f"g{random_str[:9]}"
    dummy_password = secrets.token_urlsafe(16)
    
    success = register_user(dummy_phone, dummy_password, name, email)
    if success:
        return get_user_by_email(email)
    return None

def get_disease_info(disease_name):
    conn = get_db_connection()
    info = conn.execute('SELECT * FROM disease_data WHERE disease = ?', (disease_name,)).fetchone()
    conn.close()
    if info:
        return dict(info)
    return None

def save_soil_test(phone, n, p, k, ph, recommendation):
    """Saves soil test results / app data."""
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO soil_tests (phone, n_val, p_val, k_val, ph_val, recommendation) VALUES (?, ?, ?, ?, ?, ?)', 
                     (phone, n, p, k, ph, recommendation))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving soil test: {e}")
        return False

def get_recent_soil_test(phone):
    """Retrieves the most recent soil test for a user."""
    conn = get_db_connection()
    test = conn.execute('SELECT n_val, p_val, k_val, ph_val, recommendation, timestamp FROM soil_tests WHERE phone = ? ORDER BY timestamp DESC LIMIT 1', (phone,)).fetchone()
    conn.close()
    return dict(test) if test else None

# --- Forum Helpers ---
def get_forum_posts(category=None, limit=50):
    conn = get_db_connection()
    if category and category != 'All':
        posts = conn.execute('SELECT * FROM forum_posts WHERE category = ? ORDER BY timestamp DESC LIMIT ?', (category, limit)).fetchall()
    else:
        posts = conn.execute('SELECT * FROM forum_posts ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(p) for p in posts]

def create_forum_post(phone, author_name, title, content, category='General'):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO forum_posts (phone, author_name, title, content, category) VALUES (?, ?, ?, ?, ?)',
                     (phone, author_name, title, content, category))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating forum post: {e}")
        return False

def delete_forum_post(post_id, phone):
    """Deletes a post if the phone matches the author's phone or is an admin."""
    ADMIN_PHONES = ['9876543210', 'admin', '1234567890'] # Example admin numbers
    try:
        conn = get_db_connection()
        # Check if the post belongs to the user
        post = conn.execute('SELECT phone FROM forum_posts WHERE id = ?', (post_id,)).fetchone()
        if not post:
            conn.close()
            return False, "Post not found."
            
        post_data = dict(post)
        if post_data['phone'] != phone and phone not in ADMIN_PHONES:
            conn.close()
            return False, "Unauthorized: You don't own this post."
            
        # Delete associated comments first
        conn.execute('DELETE FROM forum_comments WHERE post_id = ?', (post_id,))
        # Delete the post itself
        conn.execute('DELETE FROM forum_posts WHERE id = ?', (post_id,))
        
        conn.commit()
        conn.close()
        return True, "Post deleted successfully"
    except Exception as e:
        print(f"Error deleting forum post: {e}")
        return False, str(e)

def get_forum_comments(post_id):
    conn = get_db_connection()
    comments = conn.execute('SELECT * FROM forum_comments WHERE post_id = ? ORDER BY timestamp ASC', (post_id,)).fetchall()
    conn.close()
    return [dict(c) for c in comments]

def add_forum_comment(post_id, phone, author_name, content):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO forum_comments (post_id, phone, author_name, content) VALUES (?, ?, ?, ?)',
                     (post_id, phone, author_name, content))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding comment: {e}")
        return False

def like_forum_post(post_id):
    try:
        conn = get_db_connection()
        conn.execute('UPDATE forum_posts SET likes = likes + 1 WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error liking post: {e}")
        return False

# --- Store Helpers ---
def get_store_products(category=None):
    conn = get_db_connection()
    if category and category != 'All':
        products = conn.execute('SELECT * FROM store_products WHERE category = ? AND in_stock = 1', (category,)).fetchall()
    else:
        products = conn.execute('SELECT * FROM store_products WHERE in_stock = 1').fetchall()
    conn.close()
    return [dict(p) for p in products]

def create_order(phone, product_id, quantity=1):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO orders (phone, product_id, quantity) VALUES (?, ?, ?)', (phone, product_id, quantity))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating order: {e}")
        return False

def get_user_orders(phone):
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT o.*, sp.name as product_name, sp.price as product_price, sp.image_url 
        FROM orders o JOIN store_products sp ON o.product_id = sp.id 
        WHERE o.phone = ? ORDER BY o.timestamp DESC
    ''', (phone,)).fetchall()
    conn.close()
    return [dict(o) for o in orders]

# --- Machinery Helpers ---
def get_machinery_listings(type_filter=None):
    conn = get_db_connection()
    if type_filter and type_filter != 'All':
        listings = conn.execute('SELECT * FROM machinery_listings WHERE type = ? AND available = 1', (type_filter,)).fetchall()
    else:
        listings = conn.execute('SELECT * FROM machinery_listings WHERE available = 1').fetchall()
    conn.close()
    return [dict(l) for l in listings]

def create_machinery_listing(owner_phone, owner_name, name, mtype, rate, location, description):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO machinery_listings (owner_phone, owner_name, name, type, rate_per_hour, location, description) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (owner_phone, owner_name, name, mtype, rate, location, description))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating listing: {e}")
        return False

def book_machinery(renter_phone, listing_id, date, hours):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO rental_bookings (renter_phone, listing_id, date, hours) VALUES (?, ?, ?, ?)',
                     (renter_phone, listing_id, date, hours))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error booking machinery: {e}")
        return False

# --- Yield Estimate Helpers ---
def save_yield_estimate(phone, crop, acres, estimated_yield):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO yield_estimates (phone, crop, acres, estimated_yield) VALUES (?, ?, ?, ?)',
                     (phone, crop, acres, estimated_yield))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving yield estimate: {e}")
        return False

# --- Market Trends Helper ---
def get_market_trends(crop):
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT price, timestamp FROM market_prices 
        WHERE crop = ? ORDER BY timestamp DESC LIMIT 30
    ''', (crop,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- User Activity Logging ---
def log_user_activity(phone, action, details=None):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO user_activities (phone, action, details) VALUES (?, ?, ?)',
                     (phone, action, details))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging activity: {e}")
        return False

def get_user_activities(phone, limit=50):
    conn = get_db_connection()
    activities = conn.execute('''
        SELECT * FROM user_activities 
        WHERE phone = ? ORDER BY timestamp DESC LIMIT ?
    ''', (phone, limit)).fetchall()
    conn.close()
    return [dict(a) for a in activities]

def export_all_user_data(phone):
    conn = get_db_connection()
    data = {"profile": {}, "activities": [], "soil_tests": [], "yield_estimates": [], "store_orders": [], "forum_posts": [], "machinery_bookings": []}
    
    # 1. Profile
    user = conn.execute('SELECT phone, name, email FROM users WHERE phone = ?', (phone,)).fetchone()
    if user:
        data['profile'] = dict(user)
    
    # 2. Activities
    activities = conn.execute('SELECT action, details, timestamp FROM user_activities WHERE phone = ? ORDER BY timestamp DESC', (phone,)).fetchall()
    data['activities'] = [dict(a) for a in activities]
    
    # 3. Soil Tests
    soil = conn.execute('SELECT n_val, p_val, k_val, ph_val, recommendation, timestamp FROM soil_tests WHERE phone = ? ORDER BY timestamp DESC', (phone,)).fetchall()
    data['soil_tests'] = [dict(s) for s in soil]
    
    # 4. Yield Estimates
    yield_est = conn.execute('SELECT crop, acres, estimated_yield, timestamp FROM yield_estimates WHERE phone = ? ORDER BY timestamp DESC', (phone,)).fetchall()
    data['yield_estimates'] = [dict(y) for y in yield_est]
    
    # 5. Orders
    orders = conn.execute('''
        SELECT o.quantity, o.status, o.timestamp, sp.name as product_name, sp.price 
        FROM orders o JOIN store_products sp ON o.product_id = sp.id 
        WHERE o.phone = ? ORDER BY o.timestamp DESC
    ''', (phone,)).fetchall()
    data['store_orders'] = [dict(o) for o in orders]
    
    # 6. Forum Posts
    posts = conn.execute('SELECT title, content, category, likes, timestamp FROM forum_posts WHERE phone = ? ORDER BY timestamp DESC', (phone,)).fetchall()
    data['forum_posts'] = [dict(p) for p in posts]
    
    # 7. Machinery Bookings
    bookings = conn.execute('''
        SELECT rb.date, rb.hours, rb.status, rb.timestamp, ml.name as machine_name, ml.rate_per_hour
        FROM rental_bookings rb JOIN machinery_listings ml ON rb.listing_id = ml.id
        WHERE rb.renter_phone = ? ORDER BY rb.timestamp DESC
    ''', (phone,)).fetchall()
    data['machinery_bookings'] = [dict(b) for b in bookings]
    
    conn.close()
    return data


# =============================================
# AGRICULTURAL DATASET QUERY FUNCTIONS
# =============================================

def get_crop_recommendations_from_dataset(soil_type=None, temperature=None, humidity=None, limit=10):
    """Query the ingested crop recommendation history dataset."""
    try:
        conn = get_db_connection()
        query = 'SELECT * FROM crop_recommendations_history WHERE 1=1'
        params = []
        
        if soil_type:
            query += ' AND "Soil Type" = ?'
            params.append(soil_type)
        if temperature is not None:
            query += ' AND "Temperature" BETWEEN ? AND ?'
            params.extend([float(temperature) - 5, float(temperature) + 5])
        if humidity is not None:
            query += ' AND "Humidity" BETWEEN ? AND ?'
            params.extend([float(humidity) - 10, float(humidity) + 10])
            
        query += f' ORDER BY RANDOM() LIMIT ?'
        params.append(limit)
        
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Error querying crop recommendations dataset: {e}")
        return []


def get_fertilizer_recommendations_from_dataset(crop=None, n=None, p=None, k=None, limit=5):
    """Query the ingested fertilizer recommendation history dataset."""
    try:
        conn = get_db_connection()
        query = 'SELECT * FROM fert_recommendations_history WHERE 1=1'
        params = []
        
        if crop:
            query += ' AND "Crop Name" LIKE ?'
            params.append(f'%{crop}%')
        if n is not None:
            query += ' AND "Soil Nitrogen" BETWEEN ? AND ?'
            params.extend([float(n) - 20, float(n) + 20])
        if p is not None:
            query += ' AND "Soil Phosphorus" BETWEEN ? AND ?'
            params.extend([float(p) - 15, float(p) + 15])
        if k is not None:
            query += ' AND "Soil Potassium" BETWEEN ? AND ?'
            params.extend([float(k) - 20, float(k) + 20])
            
        query += f' ORDER BY RANDOM() LIMIT ?'
        params.append(limit)
        
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Error querying fertilizer dataset: {e}")
        return []


def get_dataset_stats():
    """Returns a summary of how many records are in each ingested dataset table."""
    try:
        conn = get_db_connection()
        stats = {}
        for table in ['crop_recommendations_history', 'fert_recommendations_history']:
            try:
                row = conn.execute(f'SELECT count(*) as cnt FROM {table}').fetchone()
                stats[table] = dict(row)['cnt']
            except Exception:
                stats[table] = 0
        conn.close()
        return stats
    except Exception as e:
        print(f"Error getting dataset stats: {e}")
        return {}

