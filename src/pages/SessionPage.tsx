import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import { BlindRecordingCard } from '../components/BlindRecordingCard';
import { getSession } from '../services/sessionService';
import type { Recording } from '../types/Recording';
import { SessionPresence } from '../components/SessionPresence';

type Session = {
  id: string;
  ariaQuery: string;
  recordings: Recording[];
};

export default function SessionPage() {
  const { sessionId } = useParams();

  const [session, setSession] = useState<Session | null>(null);
  const [revealedIds, setRevealedIds] = useState<string[]>([]);
  const [activeRecordingId, setActiveRecordingId] = useState<string | null>(
    null
  );

  useEffect(() => {
    if (!sessionId) return;

    getSession(sessionId).then((data) => {
        console.log('Loaded session:', data);
        setSession(data);
      });
  }, [sessionId]);

  function reveal(id: string) {
    setRevealedIds((current) =>
      current.includes(id) ? current : [...current, id]
    );
  }

  if (!session) {
    return <main>Loading session...</main>;
  }

  return (
    <main>
      <h1>Blind Comparison</h1>

      <h2>{session.ariaQuery}</h2>

      <SessionPresence sessionId={session.id} />

      <p>
      {session.recordings.length} anonymous recordings
      </p>

      <Link to="/">Create another session / Back to search page</Link>

      {session.recordings.map((recording, index) => (
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