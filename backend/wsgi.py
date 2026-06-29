from waitress import serve
from app import app
import os

if __name__ == '__main__':
    # Production settings for Waitress
    port = int(os.environ.get("PORT", os.environ.get("FLASK_PORT", 8000)))
    print(f"Starting AgriVistara Production Server on http://0.0.0.0:{port}")
    print("Serving with Waitress (Production WSGI)")
    
    serve(app, host='0.0.0.0', port=port, threads=6)
