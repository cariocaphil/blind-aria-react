import type { Recording } from '../types/Recording';
import { BlindYouTubePlayer } from './BlindYouTubePlayer';
import '../App.css';

type BlindRecordingCardProps = {
  recording: Recording;
  versionNumber: number;
  isRevealed: boolean;
  isActive: boolean;
  onPlay: () => void;
  onPause: () => void;
  onReveal: (id: string) => void;
};

export function BlindRecordingCard({
  recording,
  versionNumber,
  isRevealed,
  isActive,
  onPlay,
  onPause,
  onReveal,
}: BlindRecordingCardProps) {
  return (
    <section className="recording-card">
  <h2>Version {versionNumber}</h2>

  {!isRevealed ? (
    <div className="recording-content">
      <BlindYouTubePlayer
        videoId={recording.videoId}
        versionNumber={versionNumber}
        isActive={isActive}
        onPlay={onPlay}
        onPause={onPause}
      />

      <button
        className="reveal-button"
        onClick={() => onReveal(recording.id)}
      >
        Reveal performer
      </button>
    </div>
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