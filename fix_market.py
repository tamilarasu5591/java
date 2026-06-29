import sqlite3
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'backend', 'database.sqlite')

def fix_market_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    crops = [
        "Tomato", "Onion", "Potato", "Brinjal", "Carrot", 
        "Cabbage", "Cauliflower", "Ginger", "Garlic", "Chilli", 
        "Rice (Paddy)", "Wheat", "Maize", "Cotton", "Sugarcane",
        "Banana", "Mango", "Grapes", "Apple", "Turmeric"
    ]
    
    new_entries = []
    
    print("Generating new market entries with realistic prices and spread < 100%...")
    
    # We will generate 100 realistic records
    for i in range(100):
        crop = random.choice(crops)
        
        # Farm price per kg (or quintal equivalent for grains)
        if crop in ["Rice (Paddy)", "Wheat", "Maize", "Cotton"]:
            farm_price = random.uniform(2000, 5000)  # per quintal
        elif crop in ["Sugarcane"]:
            farm_price = random.uniform(300, 400)    # per quintal
        else:
            farm_price = random.uniform(15, 120)     # per kg

        # Mandi retail prices (markup between 10% and 80% to keep average spread < 100%)
        atl_retail = farm_price * (1 + random.uniform(0.1, 0.8))
        chi_retail = farm_price * (1 + random.uniform(0.1, 0.8))
        la_retail = farm_price * (1 + random.uniform(0.1, 0.8))
        ny_retail = farm_price * (1 + random.uniform(0.1, 0.8))
        
        avg_price = (atl_retail + chi_retail + la_retail + ny_retail) / 4
        
        # Spread calculation
        spread_val = ((avg_price - farm_price) / farm_price) * 100
        spread_str = f"{spread_val:.2f}%"
        
        trend = random.choice(["up", "down", "stable"])
        market = "Local Mandi"
        
        new_entries.append((
            crop, 
            round(float(farm_price), 2), 
            round(float(atl_retail), 2), 
            round(float(chi_retail), 2), 
            round(float(la_retail), 2), 
            round(float(ny_retail), 2), 
            spread_str, 
            trend, 
            market
        ))

    try:
        # Check if the extended columns exist. If not, maybe it's still using the old schema. 
        # But import_market_data.py has them.
        cursor.execute("DELETE FROM market_prices")
        conn.commit()
        
        # The schema in DB uses:
        # id, crop, price, market, trend, phone
        # WAIT! import_market_data.py DOES NOT ALTER the table if it's already there! 
        # Let's see the columns of market_prices table.
        cursor.execute("PRAGMA table_info(market_prices)")
        cols = [col[1] for col in cursor.fetchall()]
        print("Existing columns:", cols)
        
        if 'atlanta_retail' in cols:
            cursor.executemany('''
                INSERT INTO market_prices (crop, price, atlanta_retail, chicago_retail, la_retail, new_york_retail, average_spread, trend, market) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', new_entries)
        else:
            # Table doesn't have those columns?! Let's drop and recreate if needed.
            print("Table doesn't have new columns, recreating...")
            cursor.execute("DROP TABLE IF EXISTS market_prices")
            cursor.execute('''
                CREATE TABLE market_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop TEXT NOT NULL,
                    price REAL NOT NULL,
                    atlanta_retail REAL,
                    chicago_retail REAL,
                    la_retail REAL,
                    new_york_retail REAL,
                    average_spread TEXT,
                    market TEXT,
                    trend TEXT,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.executemany('''
                INSERT INTO market_prices (crop, price, atlanta_retail, chicago_retail, la_retail, new_york_retail, average_spread, trend, market) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', new_entries)
            
        conn.commit()
        print(f"Successfully added {len(new_entries)} fixed market price entries.")
    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    fix_market_data()
