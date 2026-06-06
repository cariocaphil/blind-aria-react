// src/services/searchService.ts

import { mockRecordings } from '../data/mockRecordings';
import type { Recording } from '../types/Recording';

const SEARCH_API_URL = import.meta.env.VITE_SEARCH_API_URL;

export type SearchRecordingsResponse = {
  recordings: Recording[];
};

export async function searchRecordings(
  query: string
): Promise<SearchRecordingsResponse> {
  if (!SEARCH_API_URL) {
    return searchMockRecordings(query);
  }

  try {
    const response = await fetch(
      `${SEARCH_API_URL}/search?q=${encodeURIComponent(query)}`
    );

    if (!response.ok) {
      throw new Error('Search request failed');
    }

    const data = await response.json();

    if (Array.isArray(data)) {
      return {
        recordings: data,
      };
    }

    return data;
  } catch (error) {
    console.warn('Falling back to mock recordings:', error);
    return searchMockRecordings(query);
  }
}

function searchMockRecordings(query: string): SearchRecordingsResponse {
  const recordings = mockRecordings.filter((recording) =>
    recording.ariaTitle.toLowerCase().includes(query.toLowerCase())
  );

  return {
    recordings,
  };
}