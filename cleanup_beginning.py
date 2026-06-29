"""Remove the 'Beginning' market column from the market_price_matrix table."""
import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'database.sqlite')

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Show what we're deleting
cursor.execute("SELECT * FROM market_price_matrix WHERE LOWER(market) = 'beginning'")
rows = cursor.fetchall()
print(f"Found {len(rows)} rows with market='Beginning'")

# Delete them
cursor.execute("DELETE FROM market_price_matrix WHERE LOWER(market) = 'beginning'")
conn.commit()
print(f"Deleted {cursor.rowcount} rows. 'Beginning' column removed.")

conn.close()
