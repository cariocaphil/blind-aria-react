import { useState } from 'react';

import type { Recording } from '../../types/Recording';
import { generatePlaylist } from './searchAgentApi';
import '../../App.css';

type SearchAgentPanelProps = {
  onRecordingsGenerated: (recordings: Recording[]) => void;
};

export function SearchAgentPanel({
  onRecordingsGenerated,
}: SearchAgentPanelProps) {
  const [prompt, setPrompt] = useState('');
  const [count, setCount] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await generatePlaylist({
        prompt: trimmedPrompt,
        count,
      });

      onRecordingsGenerated(response.recordings);
    } catch {
      setError('Failed to generate playlist. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="search-agent-panel">
      <h2>Search Agent</h2>
      <p className="search-agent-description">
        Describe a comparison playlist in natural language.
        The agent will choose a work (or use the one you specify) and generate multiple recordings for blind comparison.
      </p>

      <textarea
        className="search-agent-prompt"
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        placeholder="Find 5 versions of Vissi d'arte"
        rows={3}
        disabled={isLoading}
      />

      <div className="search-agent-controls">
        <label className="search-agent-count">
          Recordings
          <select
            value={count}
            onChange={(event) => setCount(Number(event.target.value))}
            disabled={isLoading}
          >
            {[3, 4, 5, 6, 7, 8, 9, 10].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>

        <button
          onClick={handleGenerate}
          disabled={isLoading || !prompt.trim()}
        >
          {isLoading ? 'Generating...' : 'Generate Playlist'}
        </button>
      </div>

      {error && <p className="search-agent-error">{error}</p>}
    </section>
  );
}
