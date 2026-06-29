import sqlite3
import pandas as pd
import os

def export_db_to_excel():
    db_path = 'd:/tamilarasu/project/backend/database.sqlite'
    output_path = 'd:/tamilarasu/project/live_database.xlsx'
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
        
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    
    # Get all table names
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(query, conn)['name'].tolist()
    
    if not tables:
        print("No tables found in the database.")
        conn.close()
        return
        
    print(f"Found {len(tables)} tables: {', '.join(tables)}")
    print(f"Exporting to {output_path}...")
    
    # Use pandas to write each table to a separate sheet
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for table in tables:
            print(f"  - Exporting table: {table}")
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            # If the dataframe is empty, still write it to keep the sheet
            df.to_excel(writer, sheet_name=table[:31], index=False) # Excel sheet names max 31 chars
            
    conn.close()
    print("Export complete!")

if __name__ == '__main__':
    export_db_to_excel()
