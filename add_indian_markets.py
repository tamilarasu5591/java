import sqlite3
import random
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'database.sqlite')

def add_new_markets():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Target markets
    new_markets = ["Koyambedu", "Oddanchatram", "Salem", "Erode"]
    
    # Get all distinct vegetables and their average price
    cursor.execute('SELECT vegetable, AVG(price) FROM market_price_matrix GROUP BY vegetable')
    rows = cursor.fetchall()
    
    for veg, avg_price in rows:
        base_price = avg_price if avg_price else 30.0
        
        for market in new_markets:
            # Generate a realistic price near the base average
            sample_price = round(base_price * random.uniform(0.9, 1.1), 2)
            
            # Upsert into database
            cursor.execute('''
                INSERT OR REPLACE INTO market_price_matrix (vegetable, market, price, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (veg, market, sample_price))
            
    conn.commit()
    conn.close()
    print("Successfully added sample Indian market prices for Koyambedu, Oddanchatram, Salem, and Erode.")

if __name__ == '__main__':
    if os.path.exists(DB_FILE):
        add_new_markets()
    else:
        print(f"Database file not found at {DB_FILE}")
