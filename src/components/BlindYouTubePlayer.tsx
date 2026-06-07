import { useEffect, useRef, useState } from 'react';
import '../App.css';

type BlindYouTubePlayerProps = {
  videoId: string;
  versionNumber: number;
  isActive: boolean;
  onPlay: () => void;
  onPause: () => void;
};

declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

let youtubeApiPromise: Promise<void> | null = null;

function loadYouTubeApi(): Promise<void> {
  if (window.YT?.Player) {
    return Promise.resolve();
  }

  if (!youtubeApiPromise) {
    youtubeApiPromise = new Promise((resolve) => {
      window.onYouTubeIframeAPIReady = () => resolve();

      const script = document.createElement('script');
      script.id = 'youtube-iframe-api';
      script.src = 'https://www.youtube.com/iframe_api';
      document.body.appendChild(script);
    });
  }

  return youtubeApiPromise;
}

export function BlindYouTubePlayer({
  videoId,
  versionNumber,
  isActive,
  onPlay,
  onPause,
}: BlindYouTubePlayerProps) {
  const playerRef = useRef<any>(null);
  const [isReady, setIsReady] = useState(false);

  const containerId = `youtube-player-${videoId}-${versionNumber}`;

  useEffect(() => {
    let isMounted = true;

    loadYouTubeApi().then(() => {
      if (!isMounted) return;

      playerRef.current = new window.YT.Player(containerId, {
        videoId,
        width: '1',
        height: '1',
        playerVars: {
          controls: 0,
          modestbranding: 1,
          rel: 0,
        },
        events: {
          onReady: () => {
            if (isMounted) setIsReady(true);
          },
        },
      });
    });

    return () => {
      isMounted = false;
      playerRef.current?.destroy?.();
    };
  }, [videoId, containerId]);

  useEffect(() => {
    if (!isActive) {
      playerRef.current?.pauseVideo?.();
    }
  }, [isActive]);

  function handlePlay() {
    onPlay();
    playerRef.current?.playVideo?.();
  }

  function handlePause() {
    playerRef.current?.pauseVideo?.();
    onPause();
  }

  return (
    <div>
      <div
        id={containerId}
        style={{
          width: '1px',
          height: '1px',
          opacity: 0,
          pointerEvents: 'none',
          position: 'absolute',
        }}
      />
      <div className="recording-controls">
        <button onClick={handlePlay} disabled={!isReady || isActive}>
         Play blind
        </button>

        <button onClick={handlePause} disabled={!isReady || !isActive}>
          Pause
        </button>
      </div>
    </div>
  );
}