// src/services/searchService.ts

import { mockRecordings } from '../data/mockRecordings';

export async function searchRecordings(query: string) {
  return mockRecordings.filter((recording) =>
    recording.ariaTitle.toLowerCase().includes(query.toLowerCase())
  );
}