import re

import requests
from bs4 import BeautifulSoup

def _scrape_html(url: str, headers: dict = {}, save_dir: str = None) -> str | None:
    """
    Retrieve the HTML content of a given URL. If `save_dir` is provided,
    the HTML content will be saved to that directory.

    Args:
        url (str): The URL to retrieve.
        headers (dict): Optional headers for the request.
        save_dir (str): Optional directory to save the HTML content.

    Returns:
        str: The HTML content of the page.
    """
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.RequestException as e:
        print(f"Error retrieving {url}: {e}")
        return None    
    
    if save_dir:
        with open(save_dir, 'w', encoding='utf-8') as file:
            file.write(response.text)
    
    return response.text

def _parse_html(content: str, save_dir: str = None) -> str | None:
    '''Parse the HTML content to extract the title and main content of the novel.
    
    Args:
        content (str): The HTML content of the page.
        save_dir (str): Optional directory to save the parsed content.
    
    Returns:
        str: The parsed text containing the title and content of the novel.
    '''
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # === Extract the title of the novel ===
    title_container = soup.find('h1', class_='p-novel__title p-novel__title--rensai')
    title = title_container.get_text(strip=True) if title_container else None

    # === Extract the content of the novel ===
    container = soup.find('div', class_='js-novel-text p-novel__text')
    paragraphs = container.find_all('p', id=re.compile(r'^L\d+'))

    content = ''
    for p in paragraphs:
        html = str(p)
        # Replace ruby tags
        html = re.sub(
            r'<ruby>(.*?)<rp>\(</rp><rt>(.*?)</rt><rp>\)</rp></ruby>',
            lambda m: '{}【{}】'.format(m.group(1), m.group(2)),
            html,
            flags=re.DOTALL
        )

        # Remove remaining tags like <p>, </p>
        text = re.sub(r'<[^>]+>', '', html)
        
        if text:
            content += text.strip() + '\n'
        else:
            content = None
            break
    
    parsed_text = "{title}\n\n{content}".format(
        title=title,
        content=content.strip() if content else ''
    ) if (title and content) else None
    
    if not parsed_text:
        print("ERROR: Failed to parse HTML content.")
        return None
    
    if save_dir:
        with open(save_dir, 'w', encoding='utf-8') as file:
            file.write(parsed_text)
            
    return parsed_text.strip()
    
def scrape_chapter(url, headers: dict = {}, verbosity: int = 1, **kwargs) -> str | None:
    """
    Scrape the chapter content from a given URL.

    Args:
        url (str): The URL of the chapter to scrape.
        headers (dict): Optional headers for the request.
        verbosity (int): Level of verbosity for logging (default is 1).

    Returns:
        str: The scraped chapter content or None if scraping fails.
    """
    
    if verbosity >= 2: print(f"Scraping chapter from {url}...")
    
    html_content = _scrape_html(url, headers, kwargs.get('html_save_dir', None))
    
    if not html_content:
        if verbosity >= 1: print(f"Failed to retrieve HTML content from {url}.")
        return None
    
    if verbosity >= 2: print("HTML content retrieved successfully.")
    
    if verbosity >= 2: print("Parsing HTML content...")
    parsed_content = _parse_html(html_content, kwargs.get('content_save_dir', None))

    if not parsed_content:
        if verbosity >= 1: print("Failed to parse HTML content.")
        return None
    
    if verbosity >= 2: print("HTML content parsed successfully.")
    if verbosity >= 2: print("Scraping completed successfully.")
    
    return parsed_content