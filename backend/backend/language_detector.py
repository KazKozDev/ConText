import requests
from langdetect import detect, DetectorFactory
from typing import Optional, Dict

# Set seed for consistent results
DetectorFactory.seed = 0

class LanguageDetector:
    def __init__(self, model="gemma:latest", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.supported_languages = {
            'en': 'English',
            'ru': 'Russian',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'nl': 'Dutch',
            'pl': 'Polish',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'tr': 'Turkish',
        }

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text using Ollama API.
        Returns the ISO 639-1 language code.
        """
        prompt = "Detect the language of the following text and respond with only the ISO 639-1 language code: " + text
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        
        # Extract the language code from the response
        # The response might be in different formats, so we'll try to handle them
        response_text = response.json()["response"].strip().lower()
        
        # Try to find a language code in the response
        for lang_code in self.supported_languages:
            if lang_code in response_text:
                return lang_code
        
        # If no valid language code was found, raise an error
        raise ValueError(f"Invalid language code: {response_text}")

    def is_supported_language(self, lang_code: str) -> bool:
        """
        Check if the language code is supported.
        """
        return lang_code in self.supported_languages 