import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.sqlite')
EXCEL_PATH = os.path.join(BASE_DIR, '..', 'agricultural_datasets.xlsx')

def ingest_data():
    if not os.path.exists(EXCEL_PATH):
        print(f"Error: {EXCEL_PATH} not found.")
        return

    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    
    print("Reading Excel file (this might take a moment)...")
    try:
        # Load Crop Recommendations
        df_crop = pd.read_excel(EXCEL_PATH, sheet_name='Crop_Recommendation')
        # Load Fertilizer Recommendations
        df_fert = pd.read_excel(EXCEL_PATH, sheet_name='Fert_Recommendation')

        # Use pandas to_sql to easily ingest tables. We replace existing tables to refresh data.
        print("Ingesting Crop Recommendations...")
        df_crop.to_sql('crop_recommendations_history', conn, if_exists='replace', index=False)
        
        print("Ingesting Fertilizer Recommendations...")
        df_fert.to_sql('fert_recommendations_history', conn, if_exists='replace', index=False)
        
        print("Successfully ingested agricultural simulation datasets into SQLite database!")
        
    except Exception as e:
        print(f"Failed to ingest data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    ingest_data()
