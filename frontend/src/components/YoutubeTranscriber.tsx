import React, { useState } from 'react';
import { VideoCameraIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';

interface YoutubeTranscriberProps {
  onTranscriptContent: (content: string) => void;
}

const YoutubeTranscriber: React.FC<YoutubeTranscriberProps> = ({ onTranscriptContent }) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleTranscribe = async () => {
    if (!url.trim()) {
      setError('Please enter a YouTube URL');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5002/youtube-transcript', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get transcript');
      }

      const data = await response.json();
      
      // Clean up transcript before passing to parent
      const processedContent = data.content.trim();
      
      if (!processedContent) {
        throw new Error('No transcript content available');
      }

      onTranscriptContent(processedContent);
      setIsModalOpen(false);
      setUrl('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while getting transcript');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* YouTube icon button */}
      <button
        onClick={() => setIsModalOpen(true)}
        className="flex items-center justify-center rounded-full w-8 h-8 text-gray-600 hover:text-red-600 hover:bg-red-50 transition-colors"
        title="Get YouTube transcript"
      >
        <VideoCameraIcon className="h-5 w-5" />
      </button>

      {/* Modal dialog */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6 w-full max-w-md mx-auto">
            <h3 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Get YouTube Transcript</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                YouTube URL
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 dark:bg-gray-800 dark:text-white"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleTranscribe();
                  }
                }}
              />
            </div>

            {error && (
              <div className="mb-4 text-red-500 text-sm">{error}</div>
            )}

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setError(null);
                  setUrl('');
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 dark:bg-gray-800 dark:text-white dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={handleTranscribe}
                disabled={isLoading || !url.trim()}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 flex items-center space-x-1 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Getting transcript...</span>
                  </>
                ) : (
                  <>
                    <ArrowDownTrayIcon className="h-4 w-4" />
                    <span>Get Transcript</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default YoutubeTranscriber; 