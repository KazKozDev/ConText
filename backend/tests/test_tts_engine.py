import pytest
from unittest.mock import patch, MagicMock
from backend.tts.engine import TTSEngine

def test_text_to_speech_success():
    engine = TTSEngine()
    
    # Mock TTS
    mock_tts = MagicMock()
    mock_tts.tts.return_value = [0.0] * 1000  # Dummy audio data
    mock_tts.synthesizer.save_wav = lambda wav, wav_bytes: wav_bytes.write(b"dummy_wav_data")
    engine.tts = mock_tts
    
    result = engine.text_to_speech("Hello, world!", "en")
    assert isinstance(result, bytes)
    assert len(result) > 0
    assert result == b"dummy_wav_data"

def test_text_to_speech_unsupported_language():
    engine = TTSEngine()
    
    with pytest.raises(ValueError) as exc_info:
        engine.text_to_speech("Hello, world!", "xx")
    assert "Unsupported language" in str(exc_info.value)

def test_text_to_speech_api_error():
    engine = TTSEngine()
    
    # Mock TTS with error
    mock_tts = MagicMock()
    mock_tts.tts.side_effect = Exception("TTS Error")
    engine.tts = mock_tts
    
    with pytest.raises(Exception) as exc_info:
        engine.text_to_speech("Hello, world!", "en")
    assert str(exc_info.value) == "TTS Error" 