from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import os
import sys
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('context-backend')

# Get the script's directory or the pyinstaller _MEIPASS value if frozen
if getattr(sys, 'frozen', False):
    # Running as a bundled app
    bundle_dir = sys._MEIPASS
    logger.info(f"Running in bundled mode, bundle_dir: {bundle_dir}")
else:
    # Running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Running in development mode, bundle_dir: {bundle_dir}")

# Add the bundle directory to the path for imports
sys.path.insert(0, os.path.dirname(bundle_dir))
logger.info(f"Added to path: {os.path.dirname(bundle_dir)}")

try:
    logger.info("Importing backend modules...")
    from backend.ollama_wrapper import OllamaWrapper
    from backend.language_detector import LanguageDetector
    from backend.tts.engine import TTSEngine
    from backend.parser import is_valid_url, method3_readability, clean_text
    from backend.youtube_transcription import get_transcript
    logger.info("Backend modules imported successfully")
except Exception as e:
    logger.error(f"Error importing modules: {str(e)}")
    logger.error(traceback.format_exc())
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Initialize components
try:
    logger.info("Initializing backend components...")
    ollama_wrapper = OllamaWrapper()
    language_detector = LanguageDetector()
    tts_engine = TTSEngine()
    logger.info("Backend components initialized successfully")
except Exception as e:
    logger.error(f"Error initializing components: {str(e)}")
    logger.error(traceback.format_exc())
    # Continue without failing - the error will show up when the components are used

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Health check endpoint called")
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

@app.route("/detect-language", methods=["POST"])
@app.route("/detect_language", methods=["POST"])
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

@app.route('/scrape-url', methods=['POST'])
def scrape_url():
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url']
        
        if not is_valid_url(url):
            return jsonify({'error': 'Invalid URL'}), 400
        
        try:
            # Use readability parser as it usually gives the best results
            content = method3_readability(url)
            
            if not content or content.startswith("Ошибка"):
                return jsonify({'error': 'Failed to extract content from URL'}), 500
                
            # Clean the scraped text
            clean_content = clean_text(content)
            
            return jsonify({'content': clean_content})
        except Exception as e:
            return jsonify({'error': f'Scraping failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        lang = data.get('lang', 'en')
        model = data.get('model')  # Get model from request
        
        if not text.strip():
            return jsonify({'error': 'Empty text provided'}), 400
        
        try:
            # Create a more effective prompt for generating summaries
            prompt = f"""Generate a concise summary of the following text in {lang}. 
The summary should capture the main points and important information.
Focus on summarizing the content, not translating it.
Make the summary informative and about 2-3 sentences long.

Text to summarize:
{text}

Summary:"""
            
            summary = ollama_wrapper.generate(prompt, model)
            return jsonify({'summary': summary})
        except Exception as e:
            return jsonify({'error': f'Summarization failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/youtube-transcript', methods=['POST'])
def youtube_transcript():
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'No YouTube URL provided'}), 400
        
        url = data['url']
        
        try:
            transcript = get_transcript(url)
            return jsonify({'content': transcript})
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Failed to get YouTube transcript: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check if model is available
    try:
        logger.info("Checking if Ollama model is available...")
        if not ollama_wrapper.check_model_availability():
            logger.warning("Warning: Gemma model is not available. Please ensure Ollama is running and the model is loaded.")
        else:
            logger.info("Ollama model is available")
    except Exception as e:
        logger.error(f"Error checking model availability: {str(e)}")
        logger.error(traceback.format_exc())
    
    # Run the Flask app with error handling
    try:
        # Check if running in a packaged environment
        is_packaged = getattr(sys, 'frozen', False)
        logger.info(f"Is packaged: {is_packaged}")
        
        # In packaged environment, don't use debug mode
        debug_mode = False if is_packaged else True
        
        # Determine port to use
        port = int(os.environ.get('PORT', 5002))
        
        # Print startup message
        logger.info(f"Starting Flask server on port {port}, debug={'ON' if debug_mode else 'OFF'}")
        
        app.run(debug=debug_mode, port=port, host='127.0.0.1')
    except Exception as e:
        logger.error(f"Error starting Flask server: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1) 