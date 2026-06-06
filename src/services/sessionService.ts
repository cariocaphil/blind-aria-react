import type { Recording } from '../types/Recording';

const SEARCH_API_URL = import.meta.env.VITE_SEARCH_API_URL;

export type CreateSessionResponse = {
  sessionId: string;
};

export type SessionResponse = {
  id: string;
  ariaQuery: string;
  recordings: Recording[];
};

type RawSessionRecording = {
  id?: string;
  recording_id?: string;
  ariaTitle?: string;
  aria_title?: string;
  videoId?: string;
  video_id?: string;
  performer: string;
  year?: string | null;
};

export async function createSession(
  ariaQuery: string,
  recordings: Recording[]
): Promise<CreateSessionResponse> {
  const response = await fetch(`${SEARCH_API_URL}/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ariaQuery,
      recordings,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to create session');
  }

  return response.json();
}

export async function getSession(sessionId: string): Promise<SessionResponse> {
  const response = await fetch(`${SEARCH_API_URL}/sessions/${sessionId}`);

  if (!response.ok) {
    throw new Error('Failed to load session');
  }

  const data = await response.json();

  return {
    id: data.id,
    ariaQuery: data.ariaQuery,
    recordings: data.recordings.map((recording: RawSessionRecording) => ({
      id: recording.recording_id ?? recording.id ?? '',
      ariaTitle: recording.ariaTitle ?? recording.aria_title ?? '',
      videoId: recording.videoId ?? recording.video_id ?? '',
      performer: recording.performer,
      year: recording.year ?? 'unknown',
    })),
  };
}