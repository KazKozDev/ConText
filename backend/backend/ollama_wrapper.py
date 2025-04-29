import requests
import time
from typing import List
import logging

# Import chunk configuration constants
try:
    from .config import CHUNK_SIZE, CHUNK_OVERLAP
except ImportError:
    # Fallback defaults if config not present
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 100

logger = logging.getLogger('context-backend')

class OllamaWrapper:
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

    def translate(self, text: str, source_lang: str, target_lang: str, model: str = None) -> str:
        """
        Translate text from source language to target language using Ollama API.
        """
        if source_lang not in self.supported_languages:
            raise ValueError(f"Invalid language code: {source_lang}")
        if target_lang not in self.supported_languages:
            raise ValueError(f"Invalid language code: {target_lang}")

        # Always perform chunked translation to preserve full text fidelity
        return self._translate_text(text, source_lang, target_lang, model)

    def generate(self, prompt: str, model: str = None) -> str:
        """
        Generate a response to a prompt using the Ollama API.
        """
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model or self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": -1}
            }
        )
        response.raise_for_status()
        
        return response.json()["response"].strip()

    def check_model_availability(self) -> bool:
        """
        Check if the model is available in Ollama.
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json()["models"]
            return any(model["name"] == self.model for model in models)
        except Exception:
            return False 

    # ---------------------- Internal helpers ---------------------- #

    def _split_text(self, text: str) -> List[str]:
        """Split a long text into manageable chunks preserving sentence boundaries."""
        if len(text) <= CHUNK_SIZE:
            return [text]

        chunks = []
        pos = 0
        text_len = len(text)

        while pos < text_len:
            end_pos = min(pos + CHUNK_SIZE, text_len)

            # Try to find sentence boundary going backwards up to CHUNK_OVERLAP
            if end_pos < text_len:
                boundary_found = False
                for i in range(end_pos, max(pos, end_pos - CHUNK_OVERLAP), -1):
                    if text[i - 1] in '.!?\n':
                        end_pos = i
                        boundary_found = True
                        break
                if not boundary_found:
                    # As fallback look forward until next boundary within overlap
                    for i in range(end_pos, min(text_len, end_pos + CHUNK_OVERLAP)):
                        if text[i - 1] in '.!?\n':
                            end_pos = i
                            break

            chunk = text[pos:end_pos].strip()
            chunks.append(chunk)
            pos = end_pos

        # Debug: log chunk sizes
        try:
            logger.debug(f"Chunking complete: {len(chunks)} chunks, sizes: {[len(c) for c in chunks]}")
        except Exception:
            pass

        return chunks

    def _translate_text(self, text: str, source_lang: str, target_lang: str, model: str = None) -> str:
        """Translate text that may be split into chunks and reassemble the result."""
        # Split into chunks if necessary
        chunks = self._split_text(text)

        translated_chunks: List[str] = []

        for idx, chunk in enumerate(chunks):
            prompt = (
                f"Translate this text from {source_lang} to {target_lang}. "
                f"Return only the translation, no explanations or additional text: {chunk}"
            )

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model or self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": -1}
                }
            )
            response.raise_for_status()
            translated_chunk = response.json()["response"].strip()
            translated_chunks.append(translated_chunk)

            # Small sleep to avoid overwhelming the API
            if len(chunks) > 1:
                time.sleep(0.2)

        # Reassemble, ensure proper spacing
        return " ".join(translated_chunks).replace("  ", " ").strip() 