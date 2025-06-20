import os
import time
import asyncio

from .scraper import scrape_chapter
from .gemini_client import GeminiClient

_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://ncode.syosetu.com/',
}

async def translate_chapters(api_key: str,
                             novel_link: str,
                             novel_name: str,
                             chapter_idxs: list[int] = [1],
                             storage_path: str = "chapters",
                             verbosity: int = 1,
                             cooldown_time: int = 5) -> None:
    """Translate chapters of a Japanese web novel using Google Gemini (asynchronously).
        
    :param str api_key: API key for Google Gemini.
    :param str novel_link: The link to the novel on ncode.syosetu.com.
    :param str novel_name: The name of the novel (used for directory structure).
    :param list[int] chapter_idxs: List of chapter indices to translate (default: [1]).
    :param str storage_path: Path to store the raw HTML, raw content, and translations (default: "chapters").
    :param int verbosity: Verbosity level (0: silent, 1: basic info, 2: detailed info).
    :param int cooldown_time: Time in seconds to wait between requests to avoid rate limiting (default: 5).
    :raises ValueError: If the novel link does not start with 'https://ncode.syosetu.com/'.
    :raises Exception: If there is an error retrieving or parsing the HTML content.
    :return: None
    """    
    
    # Clean novel link
    novel_link = novel_link.rstrip('/')
    if not novel_link.startswith('https://ncode.syosetu.com'):
        raise ValueError(f"Novel link must start with 'https://ncode.syosetu.com'. Provided: {novel_link}")

    # Define paths for the files
    raw_html_dir = f"{storage_path}/{novel_name}/raw_html"
    raw_content_dir = f"{storage_path}/{novel_name}/raw_content"
    translation_dir = f"{storage_path}/{novel_name}/translation"

    # Ensure directories exist
    os.makedirs(raw_html_dir, exist_ok=True)
    os.makedirs(raw_content_dir, exist_ok=True)
    os.makedirs(translation_dir, exist_ok=True)
    
    # Initialize the Gemini client
    client = GeminiClient(api_key)

    for idx in chapter_idxs:
        if verbosity >= 2: print(f"=== Processing Chapter {idx} ===")        
        
        start_time = time.time()
        status = await _translate_chapter(client,
                                          novel_link=novel_link,
                                          idx=idx,
                                          raw_html_dir=raw_html_dir,
                                          raw_content_dir=raw_content_dir,
                                          translation_dir=translation_dir,
                                          verbosity=verbosity)
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if verbosity >= 2: print("Done.")
        if verbosity >= 1: print(f"Chapter {idx} processed successfully in {elapsed_time:.2f} seconds")
        
        if status is None:
            continue  # Skip if translation already exists
        
        # Wait 'cooldown_time' seconds to avoid rate limiting
        # But skip if this is the last chapter
        if idx != chapter_idxs[-1]:
            if verbosity >= 2: print(f"Waiting for {cooldown_time} seconds before the next request...\n")
            await asyncio.sleep(cooldown_time)
            
async def _translate_chapter(client: GeminiClient,
                             novel_link: str,
                             idx: int,
                             raw_html_dir: str,
                             raw_content_dir: str,
                             translation_dir: str,
                             verbosity: int = 1) -> bool | None:
    """
    Translate a single chapter of a Japanese web novel using Google Gemini.
    
    :param client: Instance of GeminiClient for translation.
    :param novel_link: The link to the novel on ncode.syosetu.com.
    :param idx: Chapter index to translate.
    :param raw_html_dir: Directory to save raw HTML files.
    :param raw_content_dir: Directory to save raw content files.
    :param translation_dir: Directory to save translated files.
    :param verbosity: Verbosity level (0: silent, 1: basic info, 2: detailed info).
    :return: True if translation was successful, False if it failed, None if translation already exists.
    """
    
    # Construct file paths
    url = f"{novel_link}/{idx}/"
    filename = f"Chapter_{idx}"
    path_to_raw_html = os.path.join(raw_html_dir, f"{filename}.html")
    path_to_raw_content = os.path.join(raw_content_dir, f"{filename}.txt")
    path_to_translation = os.path.join(translation_dir, f"{filename}_translated.txt")
    
    # Check if the translation already exists
    if os.path.exists(path_to_translation):
        if verbosity >= 1: print(f"Translation for chapter {idx} already exists. Skipping...")
        return None
    
    # Step 1: Scrape the chapter HTML content
    if verbosity >= 2: print(f"1. Scraping chapter {idx} HTML content...", end=' ')
    content = await asyncio.to_thread(scrape_chapter, url, _REQUEST_HEADERS,
                                      verbosity=verbosity-1,
                                      html_save_dir=path_to_raw_html,
                                      content_save_dir=path_to_raw_content)
    
    if not content:
        if verbosity >= 1: print(f"Failed to retrieve or parse HTML content for chapter {idx}. Skipping...")
        return False
    
    if verbosity >= 2: print("Done.")
    if verbosity >= 2: print(f"3. Translating chapter {idx} content...", end=' ')
    
    translated_text = await asyncio.to_thread(client.translate_chapter, content)        
    if not translated_text:
        if verbosity >= 1: print(f"Translation failed for chapter {idx}.")
        return False
    
    with open(path_to_translation, "w", encoding="utf-8") as file:
        file.write(translated_text)
    
    return True