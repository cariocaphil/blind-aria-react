// src/components/BlindRecordingCard.tsx

type Recording = {
    id: string;
    ariaTitle: string;
    videoId: string;
    performer: string;
    year: string;
  };
  
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
  
        <iframe
          width="560"
          height="315"
          src={`https://www.youtube.com/embed/${recording.videoId}`}
          title={`Version ${versionNumber}`}
          allow="autoplay; encrypted-media; picture-in-picture"
          allowFullScreen
        />
  
        <div style={{ marginTop: '1rem' }}>
          {isRevealed ? (
            <p>
              <strong>{recording.performer}</strong> ({recording.year})
            </p>
          ) : (
            <button onClick={() => onReveal(recording.id)}>
              Reveal performer
            </button>
          )}
        </div>
      </section>
    );
  }