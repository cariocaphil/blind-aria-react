// src/components/BlindYouTubePlayer.tsx

import { useEffect, useRef, useState } from 'react';

type BlindYouTubePlayerProps = {
  videoId: string;
  versionNumber: number;
};

declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

export function BlindYouTubePlayer({
  videoId,
  versionNumber,
}: BlindYouTubePlayerProps) {
  const playerRef = useRef<any>(null);
  const containerId = `youtube-player-${videoId}-${versionNumber}`;
  const [isReady, setIsReady] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    function createPlayer() {
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
          onReady: () => setIsReady(true),
          onStateChange: (event: any) => {
            if (event.data === window.YT.PlayerState.PLAYING) {
              setIsPlaying(true);
            }

            if (
              event.data === window.YT.PlayerState.PAUSED ||
              event.data === window.YT.PlayerState.ENDED
            ) {
              setIsPlaying(false);
            }
          },
        },
      });
    }

    if (window.YT?.Player) {
      createPlayer();
    } else {
      const existingScript = document.getElementById('youtube-iframe-api');

      if (!existingScript) {
        const script = document.createElement('script');
        script.id = 'youtube-iframe-api';
        script.src = 'https://www.youtube.com/iframe_api';
        document.body.appendChild(script);
      }

      window.onYouTubeIframeAPIReady = createPlayer;
    }

    return () => {
      playerRef.current?.destroy?.();
    };
  }, [videoId, containerId]);

  function play() {
    playerRef.current?.playVideo?.();
  }

  function pause() {
    playerRef.current?.pauseVideo?.();
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

      <button onClick={play} disabled={!isReady || isPlaying}>
        Play blind
      </button>

      <button onClick={pause} disabled={!isReady || !isPlaying}>
        Pause
      </button>
    </div>
  );
}