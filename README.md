# ConText - Local Secure Translations

ConText is a secure translation application that runs entirely locally using Ollama LLMs. It provides a clean, modern interface similar to popular translation services while ensuring your data never leaves your computer.

## Features

- 🔒 Fully local translation using Ollama LLMs
- 🌐 Support for multiple languages
- 🎯 Clean, modern interface
- 🔄 Real-time translation
- 🔊 Text-to-speech support
- 📋 Easy copy/paste functionality
- 🔄 Language swap feature
- ⌨️ Keyboard shortcuts support

## Prerequisites

- Python 3.8+
- Node.js 16+
- [Ollama](https://ollama.ai) installed and running

## Setup

1. Clone the repository:
```bash
git clone https://github.com/KazKozDev/ConText.git
cd ConText
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

## Running the Application

1. Start Ollama server:
```bash
ollama serve
```

2. Start the backend server (in a new terminal):
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m backend.app
```

3. Start the frontend development server (in a new terminal):
```bash
cd frontend
npm start
```

The application will be available at http://localhost:3000

## Keyboard Shortcuts

- `Ctrl + Enter`: Translate text
- `Ctrl + Shift + Enter`: Swap languages

## License

MIT License

## Author

KazKozDev 