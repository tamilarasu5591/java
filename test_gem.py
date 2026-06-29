import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

gemini_api_key = os.getenv('GEMINI_API_KEY')
print("GEMINI KEY:", gemini_api_key)

try:
    from google import genai
    client = genai.Client(api_key=gemini_api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Hello",
        config=genai.types.GenerateContentConfig(
            system_instruction="You are a helpful assistant."
        )
    )
    print("SUCCESS FORMAT TEXT!")
except Exception as e:
    import traceback
    traceback.print_exc()
