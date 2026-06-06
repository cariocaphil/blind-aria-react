import { mockRecordings } from '../data/mockRecordings';

export function searchRecordings(query: string) {
  return mockRecordings.filter((recording) =>
    recording.ariaTitle.toLowerCase().includes(query.toLowerCase())
  );
}