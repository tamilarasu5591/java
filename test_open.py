import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
openai_api_key = os.getenv('OPENAI_API_KEY')
print("OpenAI KEY:", bool(openai_api_key))

try:
    import openai
    client = openai.OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("SUCCESS GPT!", response.choices[0].message.content)
except Exception as e:
    import traceback
    traceback.print_exc()
