import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
gemini_api_key = os.getenv('GEMINI_API_KEY')
print("Gemini KEY:", bool(gemini_api_key))

try:
    from google import genai
    client = genai.Client(api_key=gemini_api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents="Hello",
    )
    print("SUCCESS 2.0!", response.text)
except Exception as e:
    import traceback
    traceback.print_exc()
