import pytest
from unittest.mock import patch, MagicMock
from backend.ollama_wrapper import OllamaWrapper

@pytest.fixture
def ollama_wrapper():
    return OllamaWrapper()

def test_translate_success(ollama_wrapper):
    with patch('requests.post') as mock_post:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'response': 'Translated text'
        }
        mock_post.return_value = mock_response

        result = ollama_wrapper.translate('Hello', 'en', 'ru')
        
        assert result == 'Translated text'
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert call_args['json']['prompt'] == 'Translate the following text from English to Russian: Hello'
        assert call_args['json']['model'] == 'llama2'

def test_translate_error(ollama_wrapper):
    with patch('requests.post') as mock_post:
        # Mock error response
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception('API Error')
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            ollama_wrapper.translate('Hello', 'en', 'ru')
        
        assert str(exc_info.value) == 'API Error'

def test_translate_invalid_language(ollama_wrapper):
    with pytest.raises(ValueError) as exc_info:
        ollama_wrapper.translate('Hello', 'invalid', 'ru')
    
    assert str(exc_info.value) == 'Invalid language code: invalid' 