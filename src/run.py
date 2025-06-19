import argparse
import os
from dotenv import load_dotenv

from app import App

if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    
    load_dotenv(os.path.join(parent_dir, ".env"))
    api_key = os.getenv("GEMINI_API_KEY")
    
    argparser = argparse.ArgumentParser(description="Run the novel translation application.")
    argparser.add_argument("-n", "--novel", type=str, default=None, help="Name of the novel to read.")
    argparser.add_argument("-c", "--chapter", type=int, default=None, help="Chapter number to read.")
    args = argparser.parse_args()
    
    configs = {}
    configs["api_key"] = api_key
    configs["storage_path"] = os.path.join(parent_dir, "chapters")
    configs["maximized"] = True
    configs["fullscreen"] = False
    if args.novel: configs["novel"] = args.novel
    if args.chapter: configs["chapter"] = args.chapter
    
    app = App(**configs)
    app.run()