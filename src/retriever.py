import re

import requests
from bs4 import BeautifulSoup

def retrieve_html(url: str, headers: dict = {}) -> str:
    """
    Retrieve the HTML content of a given URL.

    Args:
        url (str): The URL to retrieve.

    Returns:
        str: The HTML content of the page.
    """
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.RequestException as e:
        print(f"Error retrieving {url}: {e}")
        return None    
    
    return response.text

def parse_html(content: str) -> str | None:
    def extract_title(content: str) -> str | None:
        soup = BeautifulSoup(content, 'html.parser')
        title_container = soup.find('h1', class_='p-novel__title p-novel__title--rensai')
        
        if title_container:
            title = title_container.get_text(strip=True)
            return title
        else:
            print("ERROR: Title not found in the HTML content.")
            return None
    
    def extract_content(content: str) -> str | None:
        soup = BeautifulSoup(content, 'html.parser')

        container = soup.find('div', class_='js-novel-text p-novel__text')
        paragraphs = container.find_all('p', id=re.compile(r'^L\d+'))

        final_lines = []

        for p in paragraphs:
            html = str(p)

            # Convert ruby to base【furigana】
            def ruby_replacer(match):
                base = match.group(1)
                ruby = match.group(2)
                return f'{base}【{ruby}】'

            # Replace ruby tags
            html = re.sub(
                r'<ruby>(.*?)<rp>\(</rp><rt>(.*?)</rt><rp>\)</rp></ruby>',
                ruby_replacer,
                html,
                flags=re.DOTALL
            )

            # Remove remaining tags like <p>, </p>
            text = re.sub(r'<[^>]+>', '', html)

            final_lines.append(text.strip())

        return '\n'.join(final_lines) if final_lines else None
    
    return "{title}\n\n{content}".format(
        title=extract_title(content),
        content=extract_content(content)
    ) or None