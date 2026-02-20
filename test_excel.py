import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

import db_helper

def test_excel_storage():
    phone = "1234567890"
    password = "password123"
    name = "Excel Test User"
    
    print(f"Testing registration for {name} ({phone})...")
    # Using a different phone to avoid sqlite unique constraint if it already exists
    # but db_helper already handles basic registration.
    
    # We can use a random phone to ensure it works
    import random
    random_phone = str(random.randint(1000000000, 9999999999))
    
    success = db_helper.register_user(random_phone, password, name)
    if success:
        print("Registration successful!")
        excel_path = os.path.join('backend', 'login_data.xlsx')
        if os.path.exists(excel_path):
            print(f"Success! {excel_path} created.")
            import pandas as pd
            df = pd.read_excel(excel_path)
            print("Current Excel contents:")
            print(df.tail())
        else:
            print(f"Failure! {excel_path} not found.")
    else:
        print("Registration failed (user might already exist in SQLite or other error).")

if __name__ == "__main__":
    test_excel_storage()
