from google import genai

class GeminiClient:
    PROMPT_TEMPLATE = '''
    You are a professional Japanese web novel translator. Translate the given novel chapter title and content.

    Strictly follow these instructions:
    - Translate everything to English (including the title).
    - Do NOT include any Japanese characters in the output.
    - Do NOT add explanations or commentary.
    - Maintain the paragraph structure (one paragraph per line).
    - Return the output exactly in the format below.

    Output format:
    Title: [Translated title]
    [Translated paragraph 1]
    [Translated paragraph 2]
    ...

    If the translation is incomplete due to token limits, please clearly write: "[Translation Incomplete]" at the end.

    Input:
    Title: {title}
    Content:
    {content}
    '''
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def translate_chapter(self, title: str, content: str) -> str:
        """
        Translate the chapter content to the target language using Google Gemini.

        Args:
            title (str): The title of the chapter.
            content (str): The content of the chapter.

        Returns:
            str: The translated content.
        """
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=self.PROMPT_TEMPLATE.format(title=title, content=content)
        )

        return response.text if response.text else "Translation failed."