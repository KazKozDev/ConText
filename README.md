# ConText - Local Secure Translation Tool

ConText is a desktop app for secure, local text translation using Ollama LLMs. It supports language detection, text-to-speech, web scraping, text summarization, and YouTube transcript extraction, all processed locally.

![Cover](https://github.com/user-attachments/assets/0ceb293d-ab8f-4739-8c15-eecc6b72d857)

### Features

| Feature | Description |
|---------|-------------|
| Local translation | Process translations using Ollama models locally |
| Language detection | Automatically identify the language of input text |
| Text-to-speech | Convert text to WAV audio files |
| Web content scraping | Extract text from websites for translation |
| Text summarization | Create concise summaries of longer texts |
| YouTube transcript retrieval | Get transcripts from YouTube videos |
| Multiple language support | Translate between various languages |
| Configurable text chunking | Customize text processing parameters |

### Prerequisites

- Python 3.8+
- Ollama installed and running

### Setup

1. Clone the repository:
```bash
git clone https://github.com/KazKozDev/ConText.git cd ConText
```

2. Set up the backend:
```bash
cd backend 
python -m venv venv 
source venv/bin/activate # On Windows: venv\Scripts\activate 
pip install -r requirements.txt
```

### Running

1. Start Ollama:
```bash
ollama serve
```

2. Start the backend:
```bash
cd backend 
source venv/bin/activate # On Windows: venv\Scripts\activate 
python app.py
```

Backend runs on http://localhost:5002.

### API Reference

| Endpoint | Function | Description |
|----------|----------|-------------|
| /health | Server status | Check if the server is running properly |
| /translate | Translate text | Convert text between languages |
| /detect-language | Detect language | Identify the language of input text |
| /tts | Text-to-speech | Convert text to audio format |
| /scrape-url | Scrape web content | Extract text from web pages |
| /summarize | Summarize text | Create concise summaries of texts |
| /youtube-transcript | YouTube transcript | Extract transcripts from YouTube videos |

### Example Usage

Translate English to Spanish:

```bash
curl -X POST http://localhost:5002/translate \ 
-H "Content-Type: application/json" \ 
-d '{"text": "Hello, world!", "source_lang": "en", "target_lang": "es"}'
```

Response:

```json
{"translated_text": "¡Hola, mundo!"}
```

---

If you like this project, please give it a star ⭐

For questions, feedback, or support, reach out to:

[Artem KK](https://www.linkedin.com/in/kazkozdev/) | MIT [LICENSE](LICENSE)
