from google import genai

class GeminiClient:
    PROMPT_TEMPLATE = '''
    You are a model for translating Japanese web novels. You will be given the contents of a chapter in Japanese, and your task is to translate it into English. The translation should be accurate, fluent, and maintain the original meaning and context of the text.

    Strictly follow these instructions:
    - Translate everything to English.
    - Do NOT include any non-English text in the output.
    - Do NOT add explanations or commentary.
    - Maintain the paragraph structure (one paragraph per line).
    - Return only the translated text in markdown format.
    
    Here is the chapter content to translate:
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