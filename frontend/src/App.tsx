import React, { useState, useEffect, useCallback } from 'react';
import { ArrowsRightLeftIcon, SpeakerWaveIcon, ClipboardDocumentIcon } from '@heroicons/react/24/outline';
import SettingsModal from './components/SettingsModal';

interface Language {
  code: string;
  name: string;
}

interface Model {
  name: string;
  size: number;
  digest: string;
}

const SUPPORTED_LANGUAGES: Language[] = [
  { code: 'en', name: 'English' },
  { code: 'ru', name: 'Russian' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'nl', name: 'Dutch' },
  { code: 'pl', name: 'Polish' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'ar', name: 'Arabic' },
  { code: 'hi', name: 'Hindi' },
  { code: 'tr', name: 'Turkish' },
];

function App() {
  const [sourceText, setSourceText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [sourceLang, setSourceLang] = useState<Language>(SUPPORTED_LANGUAGES[1]); // Russian
  const [targetLang, setTargetLang] = useState<Language>(SUPPORTED_LANGUAGES[0]); // English
  const [isTranslating, setIsTranslating] = useState(false);
  const [showCopied, setShowCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('gemma:7b');

  useEffect(() => {
    // Check for saved dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setIsDarkMode(savedDarkMode);
    
    // Apply dark mode class to document
    if (savedDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const handleDarkModeChange = (isDark: boolean) => {
    setIsDarkMode(isDark);
    localStorage.setItem('darkMode', isDark.toString());
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const handleSwapLanguages = useCallback(() => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    setSourceText(translatedText);
    setTranslatedText(sourceText);
  }, [sourceLang, targetLang, sourceText, translatedText]);

  const handleTranslate = useCallback(async () => {
    if (!sourceText.trim()) return;
    
    setIsTranslating(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5002/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: sourceText,
          source_lang: sourceLang.code,
          target_lang: targetLang.code,
          model: selectedModel,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Translation failed');
      }
      
      const data = await response.json();
      setTranslatedText(data.translated_text);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during translation');
    } finally {
      setIsTranslating(false);
    }
  }, [sourceText, sourceLang.code, targetLang.code, selectedModel]);

  const handleTextToSpeech = async (text: string, lang: string) => {
    try {
      const response = await fetch('http://localhost:5002/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          lang,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Text-to-speech failed');
      }
      
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during text-to-speech');
    }
  };

  const handleCopyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setShowCopied(true);
    setTimeout(() => setShowCopied(false), 2000);
  };

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Ctrl+Enter to translate
      if (e.ctrlKey && e.key === 'Enter' && sourceText.trim()) {
        handleTranslate();
      }
      // Ctrl+Shift+Enter to swap languages
      if (e.ctrlKey && e.shiftKey && e.key === 'Enter') {
        handleSwapLanguages();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [sourceText, handleSwapLanguages, handleTranslate]);

  // Add effect to fetch models
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch('http://localhost:11434/api/tags');
        if (!response.ok) {
          throw new Error('Failed to fetch models');
        }
        const data = await response.json();
        setModels(data.models);
        // Set first model as default if available
        if (data.models && data.models.length > 0) {
          setSelectedModel(data.models[0].name);
        }
      } catch (err) {
        console.error('Error fetching models:', err);
      }
    };

    fetchModels();
  }, []);

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Navigation */}
      <nav className="border-b border-gray-200">
        <div className="max-w-[1920px] mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <div className="text-2xl font-bold text-blue-600">ConText</div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Model:</span>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="text-sm font-medium bg-transparent border border-gray-200 rounded px-2 py-1 focus:ring-1 focus:ring-blue-500"
                  >
                    {models.map((model) => (
                      <option key={model.digest} value={model.name}>
                        {model.name}
                      </option>
                    ))}
                  </select>
                </div>
                <span className="text-sm text-gray-500">Secure translations via local LLM powered by Ollama</span>
              </div>
            </div>
            <a 
              href="https://github.com/KazKozDev/ConText"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
            >
              KazKozDev
            </a>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Translation Area */}
        <div className="flex-1 grid grid-cols-2 gap-0 bg-white border border-gray-200">
          {/* Source Text */}
          <div className="border-r border-gray-200 flex flex-col">
            <div className="flex items-center justify-between p-2 border-b border-gray-200">
              <select
                value={sourceLang.code}
                onChange={(e) => setSourceLang(SUPPORTED_LANGUAGES.find(lang => lang.code === e.target.value) || SUPPORTED_LANGUAGES[0])}
                className="text-sm font-medium bg-transparent border-none focus:ring-0"
              >
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
              <button
                onClick={() => handleTextToSpeech(sourceText, sourceLang.code)}
                className="p-1 text-gray-500 hover:text-gray-700"
                disabled={!sourceText}
              >
                <SpeakerWaveIcon className="h-5 w-5" />
              </button>
            </div>
            <div className="relative flex-1 flex flex-col">
              <textarea
                value={sourceText}
                onChange={(e) => setSourceText(e.target.value)}
                placeholder="Escribe o pega el texto aquí"
                className="flex-1 w-full p-4 text-lg border-none focus:ring-0 resize-none"
              />
              <button
                onClick={handleTranslate}
                disabled={!sourceText || isTranslating}
                className="absolute bottom-4 right-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <span>Enter</span>
                {isTranslating && (
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white"></div>
                )}
              </button>
            </div>
          </div>

          {/* Target Text */}
          <div className="flex flex-col">
            <div className="flex items-center justify-between p-2 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <select
                  value={targetLang.code}
                  onChange={(e) => setTargetLang(SUPPORTED_LANGUAGES.find(lang => lang.code === e.target.value) || SUPPORTED_LANGUAGES[1])}
                  className="text-sm font-medium bg-transparent border-none focus:ring-0"
                >
                  {SUPPORTED_LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleSwapLanguages}
                  className="p-1 text-gray-500 hover:text-gray-700"
                >
                  <ArrowsRightLeftIcon className="h-5 w-5" />
                </button>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleTextToSpeech(translatedText, targetLang.code)}
                  className="p-1 text-gray-500 hover:text-gray-700"
                  disabled={!translatedText}
                >
                  <SpeakerWaveIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => handleCopyToClipboard(translatedText)}
                  className="p-1 text-gray-500 hover:text-gray-700"
                  disabled={!translatedText}
                >
                  <ClipboardDocumentIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
            <div className="relative flex-1 p-4">
              <div className="text-lg h-full">
                {translatedText || (
                  <span className="text-gray-400">Traducción</span>
                )}
              </div>
              {isTranslating && (
                <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        isDarkMode={isDarkMode}
        onDarkModeChange={handleDarkModeChange}
      />
    </div>
  );
}

export default App; 