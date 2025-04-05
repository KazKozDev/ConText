import pytest
from unittest.mock import patch, MagicMock
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_translate_endpoint_success(client):
    with patch('backend.app.ollama_wrapper.translate') as mock_translate:
        mock_translate.return_value = 'Translated text'
        
        response = client.post('/translate', json={
            'text': 'Hello',
            'source_lang': 'en',
            'target_lang': 'ru'
        })
        
        assert response.status_code == 200
        assert response.json == {'translated_text': 'Translated text'}
        mock_translate.assert_called_once_with('Hello', 'en', 'ru')

def test_translate_endpoint_missing_fields(client):
    response = client.post('/translate', json={})
    
    assert response.status_code == 400
    assert 'error' in response.json

def test_translate_endpoint_error(client):
    with patch('backend.app.ollama_wrapper.translate') as mock_translate:
        mock_translate.side_effect = Exception('Translation failed')
        
        response = client.post('/translate', json={
            'text': 'Hello',
            'source_lang': 'en',
            'target_lang': 'ru'
        })
        
        assert response.status_code == 500
        assert 'error' in response.json

def test_tts_endpoint_success(client):
    with patch('backend.app.tts_engine.text_to_speech') as mock_tts:
        mock_tts.return_value = b'audio_data'
        
        response = client.post('/tts', json={
            'text': 'Hello',
            'lang': 'en'
        })
        
        assert response.status_code == 200
        assert response.data == b'audio_data'
        assert response.mimetype == 'audio/wav'
        assert response.headers['Content-Disposition'] == 'attachment; filename=speech.wav'
        mock_tts.assert_called_once_with('Hello', 'en')

def test_tts_endpoint_missing_fields(client):
    response = client.post('/tts', json={})
    
    assert response.status_code == 400
    assert 'error' in response.json

def test_tts_endpoint_error(client):
    with patch('backend.app.tts_engine.text_to_speech') as mock_tts:
        mock_tts.side_effect = Exception('TTS failed')
        
        response = client.post('/tts', json={
            'text': 'Hello',
            'lang': 'en'
        })
        
        assert response.status_code == 500
        assert 'error' in response.json 