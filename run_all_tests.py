import requests
import json
import os

BASE_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:8000"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def print_result(name, success, details=""):
    if success:
        print(f"{GREEN}[PASS]{RESET} {name} {details}")
    else:
        print(f"{RED}[FAIL]{RESET} {name} - {details}")

def run_all_tests():
    print("Starting Comprehensive API Tests...")
    
    # 1. Test Base Route
    try:
        r = requests.get(FRONTEND_URL)
        print_result("Base Route (/)", r.status_code == 200)
    except Exception as e:
        print_result("Base Route (/)", False, str(e))

    # 2. Test Registration (Using a random phone to avoid unique constraint)
    import random
    test_phone = f"999{random.randint(1000000, 9999999)}"
    test_email = f"test_{test_phone}@example.com"
    token = None
    
    try:
        reg_data = {
            "name": "E2E Test User",
            "phone": test_phone,
            "password": "password123",
            "email": test_email
        }
        r = requests.post(f"{BASE_URL}/register", json=reg_data)
        if r.status_code == 200:
            print_result("Registration", True)
            token = r.json().get('token')
        else:
            print_result("Registration", False, r.text)
    except Exception as e:
        print_result("Registration", False, str(e))

    # 3. Test Login
    try:
        login_data = {
            "phone": test_phone,
            "password": "password123"
        }
        r = requests.post(f"{BASE_URL}/login", json=login_data)
        if r.status_code == 200:
            print_result("Login", True)
            if not token:
                token = r.json().get('token')
        else:
            print_result("Login", False, r.text)
    except Exception as e:
        print_result("Login", False, str(e))

    if not token:
        print("Cannot continue authenticated tests without a valid token.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 4. Test Chat API
    try:
        r = requests.post(f"{BASE_URL}/chat", headers=headers, json={"message": "Hello"})
        if r.status_code == 200 and "response" in r.json():
            print_result("Chat API", True)
        else:
            print_result("Chat API", False, r.text)
    except Exception as e:
        print_result("Chat API", False, str(e))

    # 5. Test Market Prices
    try:
        r = requests.get(f"{BASE_URL}/market_prices", headers=headers)
        if r.status_code == 200 and isinstance(r.json(), list):
            print_result("Market Prices", True)
        else:
            print_result("Market Prices", False, r.text)
    except Exception as e:
        print_result("Market Prices", False, str(e))

    # 6. Test Weather API
    try:
        r = requests.get(f"{BASE_URL}/weather?city=Chennai", headers=headers)
        if r.status_code == 200 and "temp" in r.json():
            print_result("Weather API", True)
        else:
            print_result("Weather API", False, r.text)
    except Exception as e:
        print_result("Weather API", False, str(e))

    # 7. Test Crop Recommendation
    try:
        rec_data = {"N": 100, "P": 50, "K": 50, "ph": 6.5}
        r = requests.post(f"{BASE_URL}/recommend", headers=headers, json=rec_data)
        if r.status_code == 200 and "recommended_crop" in r.json():
            print_result("Crop Recommendation", True)
        else:
            print_result("Crop Recommendation", False, r.text)
    except Exception as e:
        print_result("Crop Recommendation", False, str(e))

    # 8. Test Yield Estimate
    try:
        yield_data = {"crop": "Rice", "acres": 2}
        r = requests.post(f"{BASE_URL}/yield_estimate", headers=headers, json=yield_data)
        if r.status_code == 200 and "estimated_yield" in r.json():
            print_result("Yield Estimate", True)
        else:
            print_result("Yield Estimate", False, r.text)
    except Exception as e:
        print_result("Yield Estimate", False, str(e))

    # 9. Test Government Schemes Check
    try:
        scheme_data = {"state": "TN", "land_acres": 2, "income": 50000, "crop": "Rice"}
        r = requests.post(f"{BASE_URL}/scheme_check", headers=headers, json=scheme_data)
        if r.status_code == 200 and "eligible_schemes" in r.json():
            print_result("Schemes Check", True)
        else:
            print_result("Schemes Check", False, r.text)
    except Exception as e:
        print_result("Schemes Check", False, str(e))

    # 10. Test Store API (Get Products)
    try:
        r = requests.get(f"{BASE_URL}/store/products", headers=headers)
        if r.status_code == 200 and isinstance(r.json(), list):
            print_result("Store API", True)
            products = r.json()
            # 11. Test Order Creation
            if products:
                order_data = {"product_id": products[0]['id'], "quantity": 1}
                r_order = requests.post(f"{BASE_URL}/store/order", headers=headers, json=order_data)
                print_result("Create Store Order", r_order.status_code == 201)
        else:
            print_result("Store API", False, r.text)
    except Exception as e:
        print_result("Store API", False, str(e))

    # 12. Test Machinery API (Get Listings)
    try:
        r = requests.get(f"{BASE_URL}/machinery", headers=headers)
        if r.status_code == 200 and isinstance(r.json(), list):
            print_result("Machinery API", True)
            machinery = r.json()
            # 13. Test Equipment Booking
            if machinery:
                book_data = {"listing_id": machinery[0]['id'], "date": "2026-03-10", "hours": 4}
                r_book = requests.post(f"{BASE_URL}/machinery/book", headers=headers, json=book_data)
                print_result("Book Machinery", r_book.status_code == 201)
        else:
            print_result("Machinery API", False, r.text)
    except Exception as e:
        print_result("Machinery API", False, str(e))

    # 14. Test Carbon Calculator
    try:
        carbon_data = {"land_acres": 5, "practices": ["organic_farming", "drip_irrigation"]}
        r = requests.post(f"{BASE_URL}/carbon_calculator", headers=headers, json=carbon_data)
        if r.status_code == 200 and "total_co2_saved" in r.json():
            print_result("Carbon Calculator", True)
        else:
            print_result("Carbon Calculator", False, r.text)
    except Exception as e:
        print_result("Carbon Calculator", False, str(e))

    # 15. Test Translate API
    try:
        translate_data = {"texts": ["Hello", "Weather", "Market"], "lang": "ta"}
        r = requests.post(f"{BASE_URL}/translate", headers=headers, json=translate_data)
        if r.status_code == 200:
            data = r.json()
            if "translations" in data and len(data["translations"]) == 3:
                print_result("Translate API", True, f"Success (returned {len(data['translations'])} translations)")
            else:
                print_result("Translate API", False, f"Unexpected response: {r.text}")
        else:
            print_result("Translate API", False, r.text)
    except Exception as e:
        print_result("Translate API", False, str(e))

    # 15. Check Frontend Pages Availability
    print("\nChecking HTML Pages accessibility...")
    pages = [
        "index.html", "login.html", "dashboard.html", "market.html", 
        "weather.html", "disease.html", "community.html", "schemes.html", 
        "store.html", "machinery.html", "profile.html"
    ]
    for page in pages:
        try:
            r = requests.get(f"{FRONTEND_URL}/{page}")
            if r.status_code == 200:
                print_result(f"Page: {page}", True)
            else:
                print_result(f"Page: {page}", False, f"Status: {r.status_code}")
        except Exception as e:
            print_result(f"Page: {page}", False, str(e))

    print("\nTests Completed.")

if __name__ == "__main__":
    run_all_tests()
