import type { Recording } from '../types/Recording';
import { BlindYouTubePlayer } from './BlindYouTubePlayer';

type BlindRecordingCardProps = {
  recording: Recording;
  versionNumber: number;
  isRevealed: boolean;
  onReveal: (id: string) => void;
};

export function BlindRecordingCard({
  recording,
  versionNumber,
  isRevealed,
  onReveal,
}: BlindRecordingCardProps) {
  return (
    <section
      style={{
        border: '1px solid #ccc',
        borderRadius: '8px',
        padding: '1rem',
        marginBottom: '1.5rem',
      }}
    >
      <h2>Version {versionNumber}</h2>

      {!isRevealed ? (
        <>
          <BlindYouTubePlayer
            videoId={recording.videoId}
            versionNumber={versionNumber}
          />

          <button onClick={() => onReveal(recording.id)}>
            Reveal performer
          </button>
        </>
      ) : (
        <>
          <iframe
            width="560"
            height="315"
            src={`https://www.youtube.com/embed/${recording.videoId}`}
            title={`Version ${versionNumber}`}
            allow="autoplay; encrypted-media; picture-in-picture"
            allowFullScreen
          />

          <p>
            <strong>{recording.performer}</strong> ({recording.year})
          </p>
        </>
      )}
    </section>
  );
}