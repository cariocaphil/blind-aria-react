// src/pages/SearchPage.tsx

import { useState } from 'react';
import type { Recording } from '../types/Recording';
import { searchRecordings } from '../services/searchService';
import { BlindRecordingCard } from '../components/BlindRecordingCard';

export function SearchPage() {
  const [query, setQuery] = useState('Casta Diva');
  const [results, setResults] = useState<Recording[]>([]);
  const [revealedIds, setRevealedIds] = useState<string[]>([]);

  async function handleSearch() {
    const foundRecordings = await searchRecordings(query);
    setResults(foundRecordings);
    setRevealedIds([]);
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

        <button onClick={handleSearch}>Search</button>
      </div>

      {results.map((recording, index) => (
        <BlindRecordingCard
          key={recording.id}
          recording={recording}
          versionNumber={index + 1}
          isRevealed={revealedIds.includes(recording.id)}
          onReveal={reveal}
        />
      ))}
    </main>
  );
}