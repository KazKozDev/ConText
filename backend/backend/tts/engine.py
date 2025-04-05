import io
import torch
import numpy as np
from TTS.api import TTS

class TTSEngine:
    def __init__(self, model="tts_models/en/ljspeech/tacotron2-DDC", device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.tts = TTS(model).to(device)
        self.supported_languages = {
            'en': 'English',  # Only English is supported by Tacotron2-DDC
        }

    def text_to_speech(self, text: str, language: str) -> bytes:
        """
        Convert text to speech using Tacotron2-DDC.
        Returns the audio data as bytes in WAV format.
        """
        if language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        
        # Generate audio using TTS
        wav = self.tts.tts(text=text)
        
        # Convert numpy array to WAV bytes
        wav_bytes = io.BytesIO()
        self.tts.synthesizer.save_wav(wav, wav_bytes)
        return wav_bytes.getvalue() 