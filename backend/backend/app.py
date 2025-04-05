from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io

from backend.ollama_wrapper import OllamaWrapper
from backend.language_detector import LanguageDetector
from backend.tts.engine import TTSEngine

app = Flask(__name__)
CORS(app)

# Initialize components
ollama_wrapper = OllamaWrapper()
language_detector = LanguageDetector()
tts_engine = TTSEngine()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'en')
        model = data.get('model')  # Get model from request
        
        # Auto-detect source language if not specified
        if source_lang == 'auto':
            try:
                source_lang = language_detector.detect_language(text)
            except Exception as e:
                return jsonify({'error': f'Language detection failed: {str(e)}'}), 500
        
        try:
            translated_text = ollama_wrapper.translate(text, source_lang, target_lang, model)
            return jsonify({'translated_text': translated_text})
        except Exception as e:
            return jsonify({'error': f'Translation failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/detect-language', methods=['POST'])
def detect_language():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        try:
            detected_lang = language_detector.detect_language(text)
            return jsonify({'detected_language': detected_lang})
        except Exception as e:
            return jsonify({'error': f'Language detection failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data or 'lang' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        text = data['text']
        lang = data['lang']
        
        try:
            audio_data = tts_engine.text_to_speech(text, lang)
            return send_file(
                io.BytesIO(audio_data),
                mimetype='audio/wav',
                as_attachment=True,
                download_name='speech.wav'
            )
        except Exception as e:
            return jsonify({'error': f'Text-to-speech failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check if model is available
    if not ollama_wrapper.check_model_availability():
        print("Warning: Gemma model is not available. Please ensure Ollama is running and the model is loaded.")
    
    app.run(debug=True, port=5002) 