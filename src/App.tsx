// src/App.tsx

import { useState } from 'react';
import { searchRecordings } from './services/searchService';
import { BlindRecordingCard } from './components/BlindRecordingCard';

export default function App() {
  const [query, setQuery] = useState('Casta Diva');
  const [searched, setSearched] = useState(false);
  const [revealedIds, setRevealedIds] = useState<string[]>([]);

  const results = searched ? searchRecordings(query) : [];

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

        <button onClick={() => setSearched(true)}>Search</button>
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