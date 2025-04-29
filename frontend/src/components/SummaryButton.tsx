import React, { useState } from 'react';
import { DocumentTextIcon } from '@heroicons/react/24/outline';

interface SummaryButtonProps {
  text: string;
  lang: string;
  model: string;
  onSummaryGenerated?: (summary: string) => void;
}

const SummaryButton: React.FC<SummaryButtonProps> = ({ text, lang, model, onSummaryGenerated }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSummarize = async () => {
    if (!text.trim()) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5002/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          lang,
          model,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate summary');
      }

      const data = await response.json();
      
      if (onSummaryGenerated) {
        onSummaryGenerated(data.summary);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while generating summary');
      console.error('Summary error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleSummarize}
      className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
      disabled={!text.trim() || isLoading}
      title="Generate summary"
    >
      {isLoading ? (
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600"></div>
      ) : (
        <DocumentTextIcon className="h-5 w-5" />
      )}
    </button>
  );
};

export default SummaryButton; 