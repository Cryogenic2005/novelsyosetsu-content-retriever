import argparse
import csv
import os
import asyncio
from dotenv import load_dotenv

from translate_handler import translate_chapters

if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
    SRC_DIR = os.path.join(ROOT_DIR, "src")
    
    # Load environment variables
    load_dotenv(os.path.join(ROOT_DIR, ".env"))
    api_key = os.getenv("GEMINI_API_KEY", None)
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    # Argument parser setup
    parser = argparse.ArgumentParser(description="Translate chapters of a Japanese web novel using Google Gemini.")
    parser.add_argument("--novel_name", type=str, required=True,
                        help="The name of the novel (used for directory structure)")
    parser.add_argument("--novel_link", type=str, default=None,
                        help="The link to the novel on ncode.syosetu.com. If not provided, the script will look for the novel with the given name in the storage catalog.")
    parser.add_argument("--chapters", type=int, nargs='+', default=[1], 
                        help="List of chapter indices to translate (default: [1])")
    parser.add_argument("--cooldown_time", type=int, default=5,
                        help="Time in seconds to wait between requests (default: 5)")
    parser.add_argument("--storage_path", type=str, default=None,
                        help="Path to the storage directory where novel data is stored (default: '../chapters')")
    parser.add_argument("--verbosity", type=int, default=1,
                        help="Verbosity level (0: silent, 1: basic info, 2: detailed info)")
    args = parser.parse_args()
    
    novel_name = args.novel_name
    novel_link = args.novel_link
    chapters = args.chapters
    cooldown_time = args.cooldown_time
    storage_path = args.storage_path if args.storage_path else os.path.join(ROOT_DIR, "chapters")
    verbosity = args.verbosity
    
    if not novel_link: # Assume existing novel in storage
        novel_catalog_path = os.path.join(storage_path, "novels.csv")
        
        # Check if the novel catalog exists
        if not os.path.exists(novel_catalog_path):
            raise FileNotFoundError(f"Novel catalog file not found at {novel_catalog_path}.")
        
        # Read the novel catalog to find the link
        with open(novel_catalog_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Name'] == novel_name:
                    novel_link = row['Link']
                    break
            else:
                raise ValueError(f"Novel '{novel_name}' not found in catalog.")
                    
    # Validate novel link
    elif not novel_link.startswith('https://ncode.syosetu.com/'):
        raise ValueError("Novel link must start with 'https://ncode.syosetu.com/'")
    
    # Ensure chapter indices are positive integers
    if not all(isinstance(idx, int) and idx > 0 for idx in chapters):
        raise ValueError("Chapter indices must be positive integers.")

    # Translate chapters asynchronously
    asyncio.run(translate_chapters(api_key, novel_link, novel_name, 
                                   chapter_idxs=chapters,
                                   cooldown_time=cooldown_time,
                                   verbosity=verbosity))