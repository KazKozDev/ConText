import React, { useState, useEffect, useCallback } from 'react';
import { ArrowsRightLeftIcon, SpeakerWaveIcon, ClipboardDocumentIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import SettingsModal from './components/SettingsModal';
import UrlScraper from './components/UrlScraper';
import SummaryButton from './components/SummaryButton';
import YoutubeTranscriber from './components/YoutubeTranscriber';

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
  const [sourceLang, setSourceLang] = useState<Language>(SUPPORTED_LANGUAGES[1]); // Source language: Russian
  const [targetLang, setTargetLang] = useState<Language>(SUPPORTED_LANGUAGES[0]); // Target language: English
  const [isTranslating, setIsTranslating] = useState(false);
  const [showCopied, setShowCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(true); // Enable dark mode by default
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('gemma:7b');
  const [sourceSummary, setSourceSummary] = useState('');
  const [targetSummary, setTargetSummary] = useState('');
  const [showSourceSummary, setShowSourceSummary] = useState(false);
  const [showTargetSummary, setShowTargetSummary] = useState(false);

  useEffect(() => {
    // Check saved dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode') !== 'false';
    setIsDarkMode(savedDarkMode);
    
    // Apply dark mode CSS
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
      // Keyboard shortcut: Ctrl+Enter to translate
      if (e.ctrlKey && e.key === 'Enter' && sourceText.trim()) {
        handleTranslate();
      }
      // Keyboard shortcut: Ctrl+Shift+Enter to swap languages
      if (e.ctrlKey && e.shiftKey && e.key === 'Enter') {
        handleSwapLanguages();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [sourceText, handleSwapLanguages, handleTranslate]);

  // Fetch available models on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch('http://localhost:11434/api/tags');
        if (!response.ok) {
          throw new Error('Failed to fetch models');
        }
        const data = await response.json();
        setModels(data.models);
        // Use first model as default if available
        if (data.models && data.models.length > 0) {
          setSelectedModel(data.models[0].name);
        }
      } catch (err) {
        console.error('Error fetching models:', err);
      }
    };

    fetchModels();
  }, []);

  // Handle content scraped from URL
  const handleScrapedContent = (content: string) => {
    setSourceText(content);
    setSourceSummary('');
    setShowSourceSummary(false);
  };

  // Handle YouTube transcript content
  const handleTranscriptContent = (content: string) => {
    setSourceText(content);
    setSourceSummary('');
    setShowSourceSummary(false);
    // Reset translation on new transcript
    setTranslatedText('');
    setTargetSummary('');
    setShowTargetSummary(false);
  };

  // Generate summary for source
  const handleSourceSummary = (summary: string) => {
    setSourceSummary(summary);
    setShowSourceSummary(true);
  };

  // Generate summary for target
  const handleTargetSummary = (summary: string) => {
    setTargetSummary(summary);
    setShowTargetSummary(true);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-[1920px] mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <div className="flex items-center">
                <span className="text-2xl font-bold text-yellow-300 dark:text-yellow-300">ConText</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500 dark:text-gray-400">Secure Local Translations</span>
              </div>
            </div>
            <a 
              href="https://github.com/KazKozDev/ConText"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            >
              KazKozDev
            </a>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Translation Area */}
        <div className="flex-1 grid grid-cols-2 gap-0 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
          {/* Source Text */}
          <div className="border-r border-gray-200 dark:border-gray-800 flex flex-col">
            <div className="flex items-center justify-between p-2 border-b border-gray-200 dark:border-gray-800">
              <select
                value={sourceLang.code}
                onChange={(e) => setSourceLang(SUPPORTED_LANGUAGES.find(lang => lang.code === e.target.value) || SUPPORTED_LANGUAGES[0])}
                className="text-sm font-medium bg-transparent border-none focus:ring-0 dark:text-white h-8"
              >
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
              <div className="flex items-center space-x-2">
                <UrlScraper onScrapedContent={handleScrapedContent} />
                <YoutubeTranscriber onTranscriptContent={handleTranscriptContent} />
                <SummaryButton 
                  text={sourceText} 
                  lang={sourceLang.code}
                  model={selectedModel} 
                  onSummaryGenerated={handleSourceSummary}
                />
                <button
                  onClick={() => handleTextToSpeech(sourceText, sourceLang.code)}
                  className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                  disabled={!sourceText}
                >
                  <SpeakerWaveIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => handleCopyToClipboard(sourceText)}
                  className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                  disabled={!sourceText}
                >
                  <ClipboardDocumentIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setIsSettingsOpen(true)}
                  className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                >
                  <Cog6ToothIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
            <div className="relative flex-1 flex flex-col">
              {showSourceSummary ? (
                <div className="flex-1 flex flex-col">
                  <div className="p-2 bg-blue-50 dark:bg-blue-900 border-b border-blue-200 dark:border-blue-800 flex justify-between items-center">
                    <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Summary in {sourceLang.name}</span>
                    <button 
                      onClick={() => setShowSourceSummary(false)}
                      className="text-blue-500 hover:text-blue-700 text-sm"
                    >
                      Back to text
                    </button>
                  </div>
                  <div className="p-4 text-lg overflow-auto dark:text-white flex-1">
                    {sourceSummary}
                  </div>
                </div>
              ) : (
                <>
                  <textarea
                    value={sourceText}
                    onChange={(e) => setSourceText(e.target.value)}
                    placeholder="Enter or paste text here"
                    className="flex-1 w-full p-4 text-lg border-none focus:ring-0 resize-none dark:bg-gray-900 dark:text-white"
                  />
                  {/* Character count bottom-left */}
                  <div
                    className="absolute bottom-4 left-4 text-xs bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 px-2 py-0.5 rounded select-none"
                  >
                    {sourceText.length.toLocaleString()} chars
                  </div>
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
                </>
              )}
            </div>
          </div>

          {/* Target Text */}
          <div className="flex flex-col">
            <div className="flex items-center justify-between p-2 border-b border-gray-200 dark:border-gray-800">
              <div className="flex items-center space-x-2">
                <select
                  value={targetLang.code}
                  onChange={(e) => setTargetLang(SUPPORTED_LANGUAGES.find(lang => lang.code === e.target.value) || SUPPORTED_LANGUAGES[1])}
                  className="text-sm font-medium bg-transparent border-none focus:ring-0 dark:text-white h-8"
                >
                  {SUPPORTED_LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleSwapLanguages}
                  className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                >
                  <ArrowsRightLeftIcon className="h-5 w-5" />
                </button>
              </div>
              <div className="flex items-center space-x-2">
                <SummaryButton 
                  text={translatedText} 
                  lang={targetLang.code}
                  model={selectedModel} 
                  onSummaryGenerated={handleTargetSummary}
                />
                <button
                  onClick={() => handleTextToSpeech(translatedText, targetLang.code)}
                  className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                  disabled={!translatedText}
                >
                  <SpeakerWaveIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => handleCopyToClipboard(translatedText)}
                  className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                  disabled={!translatedText}
                >
                  <ClipboardDocumentIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
            <div className="relative flex-1">
              {showTargetSummary ? (
                <div className="flex-1 flex flex-col h-full">
                  <div className="p-2 bg-blue-50 dark:bg-blue-900 border-b border-blue-200 dark:border-blue-800 flex justify-between items-center">
                    <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Summary in {targetLang.name}</span>
                    <button 
                      onClick={() => setShowTargetSummary(false)}
                      className="text-blue-500 hover:text-blue-700 text-sm"
                    >
                      Back to text
                    </button>
                  </div>
                  <div className="p-4 text-lg overflow-auto dark:text-white flex-1">
                    {targetSummary}
                  </div>
                </div>
              ) : (
                <div className="p-4 h-full">
                  <div className="text-lg h-full dark:text-white">
                    {translatedText || (
                      <span className="text-gray-400 dark:text-gray-500">Translation</span>
                    )}
                  </div>
                  {/* Character count for translated text */}
                  {translatedText && (
                    <div className="absolute bottom-4 left-4 text-xs bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 px-2 py-0.5 rounded select-none">
                      {translatedText.length.toLocaleString()} chars
                    </div>
                  )}
                  {isTranslating && (
                    <div className="absolute inset-0 flex items-center justify-center bg-white dark:bg-gray-900 bg-opacity-75 dark:bg-opacity-75">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                  )}
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
        models={models}
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
      />
    </div>
  );
}

export default App; 