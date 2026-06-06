import { mockRecordings } from '../data/mockRecordings';
import type { Recording } from '../types/Recording';

export async function searchAria(
  query: string
): Promise<Recording[]> {
  await new Promise((resolve) => setTimeout(resolve, 500));

  return mockRecordings.filter((recording) =>
    recording.ariaTitle.toLowerCase().includes(query.toLowerCase())
  );
}