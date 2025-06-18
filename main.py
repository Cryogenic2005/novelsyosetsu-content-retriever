import argparse
import os
from dotenv import load_dotenv

from src.translator import translate_chapters

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    # Argument parser setup
    parser = argparse.ArgumentParser(description="Translate chapters of a Japanese web novel using Google Gemini.")
    parser.add_argument("--novel_link", type=str, required=True,
                        help="The link to the novel on ncode.syosetu.com")
    parser.add_argument("--novel_name", type=str, required=True,
                        help="The name of the novel (used for directory structure)")
    parser.add_argument("--chapters", type=int, nargs='+', default=[1], 
                        help="List of chapter indices to translate (default: [1])")
    parser.add_argument("--cooldown_time", type=int, default=5,
                        help="Time in seconds to wait between requests (default: 5)")
    parser.add_argument("--verbosity", type=int, default=1,
                        help="Verbosity level (0: silent, 1: basic info, 2: detailed info)")
    args = parser.parse_args()
    
    novel_link = args.novel_link
    novel_name = args.novel_name
    chapters = args.chapters
    cooldown_time = args.cooldown_time
    verbosity = args.verbosity
    
    # Validate novel link
    if not novel_link.startswith('https://ncode.syosetu.com/'):
        raise ValueError("Novel link must start with 'https://ncode.syosetu.com/'")
    
    # Ensure chapter indices are positive integers
    if not all(isinstance(idx, int) and idx > 0 for idx in chapters):
        raise ValueError("Chapter indices must be positive integers.")

    # Translate chapters
    translate_chapters(api_key, novel_link, novel_name, 
                       chapter_idxs=chapters,
                       cooldown_time=cooldown_time,
                       verbosity=verbosity)