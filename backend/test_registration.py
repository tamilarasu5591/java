import db_helper
import pandas as pd
import os

# Test Data
phone = "9876543210"
password = "testpassword"
name = "Test User"

print(f"Registering user: {name}, {phone}")
success = db_helper.register_user(phone, password, name)

if success:
    print("Registration successful.")
else:
    print("Registration failed (User might already exist).")

# Verify Data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, 'login_data.xlsx')

print(f"\nReading sheet from {EXCEL_FILE}:")
try:
    if not os.path.exists(EXCEL_FILE):
        print(f"VERIFICATION FAILED: {EXCEL_FILE} does not exist.")
    else:
        df = pd.read_excel(EXCEL_FILE)
        print(df)
        
        # Check if user is in df, handling float vs string issues
        def normalize_phone(p):
            try:
                # If it's a float like 9876543210.0, convert to int then str
                if isinstance(p, (float, int)):
                    return str(int(p))
                return str(p).strip().split('.')[0] # handle float-string '9876543210.0'
            except:
                return str(p)

        df['phone_clean'] = df['Phone'].apply(normalize_phone)
        is_present = not df[(df['phone_clean'] == str(phone)) & (df['Name'] == name)].empty
    if is_present:
        print("\nVERIFICATION PASSED: key details found in Excel.")
    else:
        print("\nVERIFICATION FAILED: User not found in Excel.")
except Exception as e:
    print(f"Error reading Excel: {e}")
