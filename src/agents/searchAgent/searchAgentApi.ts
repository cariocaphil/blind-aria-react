import type { Recording } from '../../types/Recording';

const SEARCH_API_URL = import.meta.env.VITE_SEARCH_API_URL;

export type GeneratePlaylistRequest = {
  prompt: string;
  count: number;
};

export type GeneratePlaylistResponse = {
  comparisonTarget: string;
  recordings: Recording[];
};

export async function generatePlaylist(
  request: GeneratePlaylistRequest
): Promise<GeneratePlaylistResponse> {
  if (!SEARCH_API_URL) {
    throw new Error('Search API URL is not configured');
  }

  const response = await fetch(`${SEARCH_API_URL}/api/agent/generate-playlist`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to generate playlist');
  }

  return response.json();
}
