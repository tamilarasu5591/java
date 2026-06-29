import requests

BASE_URL = "http://localhost:5000/api"

try:
    print("1. Testing /api/send_email_otp")
    r1 = requests.post(f"{BASE_URL}/send_email_otp", json={"email": "test@test.com"})
    print(r1.json())
    otp = r1.json().get('otp_mock')

    print(f"\n2. Testing /api/verify_email_otp with {otp}")
    r2 = requests.post(f"{BASE_URL}/verify_email_otp", json={"email": "test@test.com", "otp": otp})
    print(r2.json())

    print("\n3. Testing /api/register")
    r3 = requests.post(f"{BASE_URL}/register", json={
        "name": "Test User",
        "email": "test@test.com",
        "phone": "9998887771",
        "password": "password123"
    })
    print(r3.json())
except Exception as e:
    print(f"Test failed: {e}")
