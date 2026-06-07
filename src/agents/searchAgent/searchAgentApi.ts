import type { Recording } from '../../types/Recording';

const SEARCH_API_URL = import.meta.env.VITE_SEARCH_API_URL;

export type SearchPlan = {
  comparisonTarget: string;
  searchQueries: string[];
  excludeTerms: string[];
  preferTerms: string[];
  rationale?: string;
};

export type GeneratePlaylistRequest = {
  prompt: string;
  count: number;
};

export type GeneratePlaylistResponse = {
  comparisonTarget: string;
  recordings: Recording[];
  searchPlan?: SearchPlan;
};

type RawSearchPlan = {
  comparison_target?: string;
  comparisonTarget?: string;
  search_queries?: string[];
  searchQueries?: string[];
  exclude_terms?: string[];
  excludeTerms?: string[];
  prefer_terms?: string[];
  preferTerms?: string[];
  rationale?: string;
};

function normalizeSearchPlan(raw: RawSearchPlan | undefined): SearchPlan | undefined {
  if (!raw) {
    return undefined;
  }

  return {
    comparisonTarget: raw.comparisonTarget ?? raw.comparison_target ?? '',
    searchQueries: raw.searchQueries ?? raw.search_queries ?? [],
    excludeTerms: raw.excludeTerms ?? raw.exclude_terms ?? [],
    preferTerms: raw.preferTerms ?? raw.prefer_terms ?? [],
    rationale: raw.rationale,
  };
}

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

  const data = await response.json();

  return {
    comparisonTarget: data.comparisonTarget,
    recordings: data.recordings,
    searchPlan: normalizeSearchPlan(data.searchPlan),
  };
}
