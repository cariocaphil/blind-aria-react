// src/pages/SearchPage.tsx

import { useState } from 'react';
import type { Recording } from '../types/Recording';
import { searchRecordings } from '../services/searchService';
import { BlindRecordingCard } from '../components/BlindRecordingCard';
import { createSession } from '../services/sessionService';
import { useNavigate } from 'react-router-dom';

export function SearchPage() {
  const [query, setQuery] = useState('Casta Diva');
  const [results, setResults] = useState<Recording[]>([]);
  const [revealedIds, setRevealedIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [sessionLink, setSessionLink] = useState<string | null>(null);
  const [activeRecordingId, setActiveRecordingId] = useState<string | null>(
    null
  );
  const navigate = useNavigate();

  async function handleSearch() {
    setIsLoading(true);
    setSessionLink(null);

    try {
      const searchResponse = await searchRecordings(query);
      setResults(searchResponse.recordings);
      setRevealedIds([]);
      setActiveRecordingId(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateSession() {
    if (results.length === 0) return;
  
    setIsCreatingSession(true);
  
    try {
      const response = await createSession(query, results);
  
      navigate(`/session/${response.sessionId}`);
    } finally {
      setIsCreatingSession(false);
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

      {results.length > 0 && (
        <div>
          <button onClick={handleCreateSession} disabled={isCreatingSession}>
            {isCreatingSession ? 'Creating session...' : 'Create shared session'}
          </button>

          {sessionLink && (
            <p>
              Session link copied:{' '}
              <a href={sessionLink} target="_blank" rel="noreferrer">
                {sessionLink}
              </a>
            </p>
          )}
        </div>
      )}

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