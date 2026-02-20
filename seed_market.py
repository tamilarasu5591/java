import sqlite3
import random

import os

# Local DB File
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'backend', 'database.sqlite')

def seed_market_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    crops = ["Rice", "Wheat", "Maize", "Tomato", "Potato", "Onion", "Brinjal", "Okra", "Cabbage", "Cauliflower", 
             "Spinach", "Carrot", "Cotton", "Sugarcane", "Turmeric", "Chilli", "Ginger", "Garlic", "Banana", "Mango"]
    
    markets = ["Central Mandi", "City Market", "Rural Market", "Wholesale Depot", "Farmers Market", "Regional Hub"]
    
    trends = ["up", "down", "stable"]

    new_entries = []
    
    print("Generating 1000+ market entries...")
    
    for _ in range(1000):
        crop = random.choice(crops)
        base_price = random.randint(1000, 8000) # Random base price
        market = random.choice(markets)
        trend = random.choice(trends)
        phone = f"+91 98{random.randint(10000000, 99999999)}" if random.random() > 0.3 else None # 70% chance of phone
        
        new_entries.append((crop, base_price, market, trend, phone))

    try:
        cursor.executemany('INSERT INTO market_prices (crop, price, market, trend, phone) VALUES (?, ?, ?, ?, ?)', new_entries)
        conn.commit()
        print(f"Successfully added {len(new_entries)} new market price entries.")
    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    seed_market_data()
