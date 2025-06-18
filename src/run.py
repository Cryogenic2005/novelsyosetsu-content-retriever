import os
from dotenv import load_dotenv

from app import App

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    configs = {
        "storage_path": os.path.join(os.path.dirname(os.path.dirname(__file__)), "chapters"),
        "api_key": api_key,
        "fullscreen": True,
    }
    
    app = App(**configs)
    app.run()