import os
import sys
import hashlib
from dotenv import load_dotenv

# load env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', '..', '.env'))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import ai_prompt
from ai_prompt import MASTER_PROMPT
import rag_helper

message_lower = "how to grow paddy?"
context = ""
context += f"\n\n{rag_helper.search_knowledge_base(message_lower)}\n"

full_prompt = f"User Query: {message_lower}\n{context}"

gemini_api_key = os.getenv('GEMINI_API_KEY')
print("Keys:", "Gemini=" + str(bool(gemini_api_key)))

if gemini_api_key:
    try:
        from google import genai
        client = genai.Client(api_key=gemini_api_key)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=MASTER_PROMPT
            )
        )
        print("GEMINI SUCCESS:")
        print(response.text)
    except Exception as e:
        import traceback
        traceback.print_exc()
