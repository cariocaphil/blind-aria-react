import { useState } from 'react';
import { mockRecordings } from './data/mockRecordings';

export default function App() {
  const [query, setQuery] = useState('Casta Diva');
  const [searched, setSearched] = useState(false);
  const [revealedIds, setRevealedIds] = useState<string[]>([]);

  const results = searched
    ? mockRecordings.filter((recording) =>
        recording.ariaTitle.toLowerCase().includes(query.toLowerCase())
      )
    : [];

  function reveal(id: string) {
    setRevealedIds((current) => [...current, id]);
  }

  return (
    <main>
      <h1>Blind Aria</h1>

      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={() => setSearched(true)}>Search</button>

      {results.map((recording, index) => {
        const isRevealed = revealedIds.includes(recording.id);

        return (
          <section key={recording.id}>
            <h2>Version {index + 1}</h2>

            <iframe
              width="560"
              height="315"
              src={`https://www.youtube.com/embed/${recording.videoId}`}
              allow="autoplay; encrypted-media; picture-in-picture"
              allowFullScreen
            />

            {isRevealed ? (
              <p>
                {recording.performer}, {recording.year}
              </p>
            ) : (
              <button onClick={() => reveal(recording.id)}>Reveal</button>
            )}
          </section>
        );
      })}
    </main>
  );
}