from google import genai

class GeminiClient:
    PROMPT_TEMPLATE = '''
    You are a model for translating Japanese web novels. You will be given the contents of a chapter in Japanese, and your task is to translate it into English. The translation should be accurate, fluent, and maintain the original meaning and context of the text.

    Strictly follow these instructions:
    - Translate the title and the entire chapter content into English. Ensure every part of the text is translated.
    - Do NOT include any non-English text in the output.
    - Do NOT include any additional explanations or comments in the output.
    - Maintain the paragraph structure (one paragraph per line).
    - Return only the translated text without any additional formatting or metadata.
    
    Here is the chapter content to translate:
    {content}
    '''
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def translate_chapter(self, content: str) -> str:
        """
        Translate the chapter content to the target language using Google Gemini.

        Args:
            content (str): The contents of the chapter.

        Returns:
            str: The translated content.
        """
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self.PROMPT_TEMPLATE.format(content=content)
        )

        return response.text if response.text else "Translation failed."