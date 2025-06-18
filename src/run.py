import os
from dotenv import load_dotenv

from app import App

if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    
    load_dotenv(os.path.join(parent_dir, ".env"))
    api_key = os.getenv("GEMINI_API_KEY")
    
    configs = {
        "storage_path": os.path.join(os.path.dirname(os.path.dirname(__file__)), "chapters"),
        "api_key": api_key,
        "maximized": True,
        "fullscreen": False,
        "novel": "Shangri-La_Frontier",
        "chapter": 615,
    }
    
    app = App(**configs)
    app.run()