import pytest
from unittest.mock import patch, MagicMock
from backend.language_detector import LanguageDetector

def test_detect_language_success():
    detector = LanguageDetector()
    
    # Mock the response from Ollama
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "en"}
    mock_response.raise_for_status.return_value = None
    
    with patch('requests.post', return_value=mock_response):
        result = detector.detect_language("Hello, world!")
        assert result == "en"

def test_detect_language_invalid_response():
    detector = LanguageDetector()
    
    # Mock the response from Ollama with an invalid language code
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "invalid"}
    mock_response.raise_for_status.return_value = None
    
    with patch('requests.post', return_value=mock_response):
        with pytest.raises(ValueError) as exc_info:
            detector.detect_language("Hello, world!")
        assert "Invalid language code" in str(exc_info.value)

def test_is_supported_language():
    detector = LanguageDetector()
    assert detector.is_supported_language("en") is True
    assert detector.is_supported_language("ru") is True
    assert detector.is_supported_language("xx") is False 