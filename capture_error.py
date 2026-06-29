import sys
import traceback
import os

print("Testing app.py initialization...")

# Write the actual error to a UTF-8 file so the AI can read it safely
with open('startup_error.txt', 'w', encoding='utf-8') as f:
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
        import app
        f.write("SUCCESS: The app.py loaded perfectly without errors.")
        print("SUCCESS! The backend works.")
    except Exception as e:
        error_msg = traceback.format_exc()
        f.write(error_msg)
        print("CRASHED! Wrote the error to startup_error.txt")
        print(f"Error summary: {e}")
