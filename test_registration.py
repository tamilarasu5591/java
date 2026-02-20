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
print("\nReading 'Users' sheet from database.xlsx:")
try:
    df = pd.read_excel('database.xlsx', sheet_name='Users')
    print(df)
    
    # Check if user is in df
    is_present = ((df['phone'].astype(str) == phone) & (df['name'] == name)).any()
    if is_present:
        print("\nVERIFICATION PASSED: key details found in Excel.")
    else:
        print("\nVERIFICATION FAILED: User not found in Excel.")
except Exception as e:
    print(f"Error reading Excel: {e}")
