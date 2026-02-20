import sqlite3
import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'ProductPriceIndex.csv')
DB_FILE = os.path.join(BASE_DIR, 'backend', 'database.sqlite')

def import_data():
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        return

    print("Reading CSV...")
    df = pd.read_csv(CSV_FILE)
    
    # Cleaning data
    # productname -> crop
    # farmprice ($1.16) -> price (float)
    # date -> timestamp
    
    print("Processing records...")
    df['crop'] = df['productname']
    
    # Cleaning function for currency strings
    def clean_currency(val):
        if pd.isna(val): return 0.0
        s = str(val).strip().replace('$', '').replace(',', '')
        if not s or s == '-': return 0.0
        try:
            return float(s)
        except:
            return 0.0

    df['price'] = df['farmprice'].apply(clean_currency)
    df['atlanta_retail'] = df['atlantaretail'].apply(clean_currency)
    df['chicago_retail'] = df['chicagoretail'].apply(clean_currency)
    df['la_retail'] = df['losangelesretail'].apply(clean_currency)
    df['new_york_retail'] = df['newyorkretail'].apply(clean_currency)
    df['average_spread'] = df['averagespread']
    
    df['market'] = "Global Index"
    df['trend'] = "stable"
    df['phone'] = None
    
    # Select only needed columns for SQLite
    cols = ['crop', 'price', 'atlanta_retail', 'chicago_retail', 'la_retail', 'new_york_retail', 'average_spread', 'market', 'trend', 'phone']
    to_db = df[cols]
    
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        print("Clearing existing market data...")
        cursor.execute("DELETE FROM market_prices")
        
        print(f"Inserting {len(to_db)} records into market_prices...")
        to_db.to_sql('market_prices', conn, if_exists='append', index=False)
        conn.commit()
        print("Success: Market data imported.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import_data()
