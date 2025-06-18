import os
import time

from .retriever import retrieve_html, parse_html
from .gemini_client import GeminiClient

def translate_chapters(api_key: str,
                       novel_link: str,
                       novel_name: str,
                       chapter_idxs: list[int] = [1],
                       verbosity: int = 1,
                       cooldown_time: int = 5) -> None:
    """Translate chapters of a Japanese web novel using Google Gemini.
        
    :param str api_key: API key for Google Gemini.
    :param str novel_link: The link to the novel on ncode.syosetu.com.
    :param str novel_name: The name of the novel (used for directory structure).
    :param list[int] chapter_idxs: List of chapter indices to translate (default: [1]).
    :param int verbosity: Verbosity level (0: silent, 1: basic info, 2: detailed info).
    :param int cooldown_time: Time in seconds to wait between requests to avoid rate limiting (default: 5).
    :raises ValueError: If the novel link does not start with 'https://ncode.syosetu.com/'.
    :raises Exception: If there is an error retrieving or parsing the HTML content.
    :return: None
    """    
    
    # Clean novel link
    novel_link = novel_link.rstrip('/')
    if not novel_link.startswith('https://ncode.syosetu.com/'):
        raise ValueError("Novel link must start with 'https://ncode.syosetu.com/'")
    
    # Define paths for the files
    raw_html_dir = f"chapters/{novel_name}/raw_html"
    raw_content_dir = f"chapters/{novel_name}/raw_content"
    translation_dir = f"chapters/{novel_name}/translation"

    # Ensure directories exist
    os.makedirs(raw_html_dir, exist_ok=True)
    os.makedirs(raw_content_dir, exist_ok=True)
    os.makedirs(translation_dir, exist_ok=True)

    # Headers for the HTTP request
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://ncode.syosetu.com/',
    }
    
    # Initialize the Gemini client
    client = GeminiClient(api_key)
    
    for idx in chapter_idxs:
        # Only set to True whenever a call is made to the Gemini API
        # OR a GET request is made to the novel link
        # This is to avoid rate limiting issues
        rate_limit_flag = False
        
        # Construct file paths
        filename = f"Chapter_{idx}"
        path_to_raw_html = os.path.join(raw_html_dir, f"{filename}.html")
        path_to_raw_content = os.path.join(raw_content_dir, f"{filename}.txt")
        path_to_translation = os.path.join(translation_dir, f"{filename}_translated.txt")
    
        if verbosity >= 2: print(f"=== Processing Chapter {idx}: {filename} ===")
    
        # Only retrieve HTML if it does not already exist
        if verbosity >= 2: print(f"1. Retrieving chapter {idx} HTML content...", end=' ')
        html = None
        if not os.path.exists(path_to_raw_html):
            rate_limit_flag = True
            html = retrieve_html(f"{novel_link}/{idx}", headers=headers)
            if not html:
                return "Failed to retrieve HTML content."
        
            with open(path_to_raw_html, "w", encoding="utf-8") as file:
                file.write(html)
        else:
            with open(path_to_raw_html, "r", encoding="utf-8") as file:
                html = file.read()
        if verbosity >= 2: print("Done.")
                
        # Only parse and translate if raw content does not already exist
        if verbosity >= 2: print(f"2. Parsing chapter {idx} content from HTML...", end=' ')
        title, text = None, None
        if not os.path.exists(path_to_raw_content):
            title, text = parse_html(html)
            if not (title and text):
                return "Failed to parse HTML content."
            
            with open(path_to_raw_content, "w", encoding="utf-8") as file:
                file.write(f"{title}\n\n{text}")
        else:
            with open(path_to_raw_content, "r", encoding="utf-8") as file:
                lines = file.readlines()
                title = lines[0].strip()
                text = ''.join(lines[2:]).strip()
        if verbosity >= 2: print("Done.")
                
        # Only translate if translation does not already exist
        if verbosity >= 2: print(f"3. Translating chapter {idx} content...", end=' ')
        if not os.path.exists(path_to_translation):
            rate_limit_flag = True
            translated_text = client.translate_chapter(title, text)

            with open(path_to_translation, "w", encoding="utf-8") as file:
                file.write(translated_text)
        if verbosity >= 2: print("Done.")
                
        if verbosity >= 1: print(f"=== Chapter {idx} processed successfully: {filename} ===\n")
        
        # Wait 'cooldown_time' seconds before the next request to avoid rate limiting
        # But skip if this is the last chapter
        if idx != chapter_idxs[-1] and rate_limit_flag:
            if verbosity >= 2: print("*** Waiting for 10 seconds before the next request... ***\n")
            time.sleep(cooldown_time)