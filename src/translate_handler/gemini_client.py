from google import genai
from google.genai import types
from google.genai.types import HarmCategory, HarmBlockThreshold, SafetySetting

class GeminiClient:
    SYSTEM_INSTRUCTION = '''
    You are a model for translating Japanese web novels. You will be given the contents of a chapter in Japanese, and your task is to translate it into English. The translation should be accurate, fluent, and maintain the original meaning and context of the text.

    Strictly follow these instructions:
    - Translate the title and the entire chapter content into English. Ensure every part of the text is translated.
    - Do NOT include any non-English text in the output.
    - Do NOT include any additional explanations or comments in the output.
    - Maintain the paragraph structure (one paragraph per line).
    - Return only the translated text without any additional formatting or metadata.
    '''
    
    PROMPT_TEMPLATE = '''Here is the chapter content to translate:
    {content}
    '''
    
    SAFETY_SETTINGS = [
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=HarmBlockThreshold.BLOCK_NONE
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=HarmBlockThreshold.BLOCK_NONE
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=HarmBlockThreshold.BLOCK_NONE
        ),
        SafetySetting(
            category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=HarmBlockThreshold.BLOCK_NONE
        )
    ]
    
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
            contents=self.PROMPT_TEMPLATE.format(content=content),
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_INSTRUCTION,
                safety_settings=self.SAFETY_SETTINGS
            )
        )
        
        if not response:
            print("No response received from Gemini translation.")
            return None
        
        if not response.text:
            print(f"No text returned from Gemini translation. Response: {response}")
            return None

        return response.text