// src/pages/SearchPage.tsx

import { useState } from 'react';
import type { Recording } from '../types/Recording';
import { searchRecordings } from '../services/searchService';
import { BlindRecordingCard } from '../components/BlindRecordingCard';

export function SearchPage() {
  const [query, setQuery] = useState('Casta Diva');
  const [results, setResults] = useState<Recording[]>([]);
  const [revealedIds, setRevealedIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeRecordingId, setActiveRecordingId] = useState<string | null>(
    null
  );

  async function handleSearch() {
    setIsLoading(true);

    try {
      const searchResponse = await searchRecordings(query);
      setResults(searchResponse.recordings);
      setRevealedIds([]);
      setActiveRecordingId(null);
    } finally {
      setIsLoading(false);
    }
  }

  function reveal(id: string) {
    setRevealedIds((current) =>
      current.includes(id) ? current : [...current, id]
    );
  }

  return (
    <main>
      <h1>Blind Aria</h1>

      <div>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />

        <button onClick={handleSearch} disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {results.map((recording, index) => (
        <BlindRecordingCard
          key={recording.id}
          recording={recording}
          versionNumber={index + 1}
          isRevealed={revealedIds.includes(recording.id)}
          isActive={activeRecordingId === recording.id}
          onPlay={() => setActiveRecordingId(recording.id)}
          onPause={() => setActiveRecordingId(null)}
          onReveal={reveal}
        />
      ))}
    </main>
  );
}