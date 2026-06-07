# backend/app/services/agent_service.py

import re

from pydantic import BaseModel, Field

from app.services.youtube_service import search_youtube_recordings

KNOWN_WORKS = {
    "casta diva": "Casta Diva",
    "vissi d'arte": "Vissi d'arte",
    "vissi d arte": "Vissi d'arte",
    "nessun dorma": "Nessun dorma",
}

DISCOVERY_TARGETS = {
    "verismo": "Vissi d'arte",
    "dramatic soprano": "Casta Diva",
    "1920": "Casta Diva",
    "puccini": "Nessun dorma",
    "obscure": "Nessun dorma",
}

PERFORMER_EXCLUSION_ALIASES = {
    "callas": ["Callas", "Maria Callas"],
    "pavarotti": ["Pavarotti", "Luciano Pavarotti"],
    "domingo": ["Domingo", "Plácido Domingo"],
}

HISTORICAL_QUERY_SUFFIXES = [
    "historical recording",
    "old recording",
    "1930s soprano",
    "1940s soprano",
    "1950s soprano",
]

RECENT_QUERY_SUFFIXES = [
    "recent recording",
    "modern recording",
    "2010s",
    "2020s",
]

DECADE_QUERY_SUFFIXES = [
    "1950s",
    "1960s",
    "1970s",
    "1980s",
    "1990s",
]


class AgentSearchPlan(BaseModel):
    comparison_target: str
    search_queries: list[str]
    exclude_terms: list[str] = Field(default_factory=list)
    prefer_terms: list[str] = Field(default_factory=list)
    rationale: str = ""


def interpret_prompt(prompt: str) -> str:
    """Step 1: Interpret the natural-language request (mock: keyword matching)."""
    return prompt.strip()


def determine_comparison_target(prompt: str) -> str:
    """Resolve the single musical work the playlist should center on (mocked)."""
    normalized = prompt.lower()

    for keyword, work in KNOWN_WORKS.items():
        if keyword in normalized:
            return work

    for keyword, work in DISCOVERY_TARGETS.items():
        if keyword in normalized:
            return work

    return "Casta Diva"


def extract_exclude_terms(prompt: str) -> list[str]:
    normalized = prompt.lower()
    exclude_terms: list[str] = []

    for match in re.finditer(r"(?:without|avoiding|avoid)\s+([^,.]+)", normalized):
        raw_term = match.group(1).strip()
        performer_key = raw_term.split()[-1]

        if performer_key in PERFORMER_EXCLUSION_ALIASES:
            exclude_terms.extend(PERFORMER_EXCLUSION_ALIASES[performer_key])
        else:
            exclude_terms.append(raw_term.title())

    return list(dict.fromkeys(exclude_terms))


def extract_prefer_terms(prompt: str) -> list[str]:
    normalized = prompt.lower()
    prefer_terms: list[str] = []

    if any(
        term in normalized
        for term in ["old", "historical", "era", "1920", "1930", "1940", "1950"]
    ):
        prefer_terms.extend(["historical", "old", "1930", "1940", "1950"])

    if any(term in normalized for term in ["recent", "modern", "2010", "2020"]):
        prefer_terms.extend(["recent", "modern", "2010", "2020"])

    if "decade" in normalized:
        prefer_terms.extend(["1950", "1960", "1970", "1980", "1990"])

    if "live" in normalized:
        prefer_terms.append("live")

    if "studio" in normalized:
        prefer_terms.append("studio")

    return list(dict.fromkeys(prefer_terms))


def build_search_queries(
    comparison_target: str,
    prompt: str,
    count: int,
) -> list[str]:
    normalized = prompt.lower()
    queries = [comparison_target]

    wants_historical = any(
        term in normalized
        for term in ["old", "historical", "era", "1920", "1930", "1940", "1950"]
    )
    wants_recent = any(
        term in normalized for term in ["recent", "modern", "2010", "2020"]
    )
    wants_decades = "decade" in normalized

    if wants_historical:
        queries.extend(
            f"{comparison_target} {suffix}" for suffix in HISTORICAL_QUERY_SUFFIXES
        )

    if wants_recent:
        queries.extend(
            f"{comparison_target} {suffix}" for suffix in RECENT_QUERY_SUFFIXES
        )

    if wants_decades:
        queries.extend(
            f"{comparison_target} {suffix}" for suffix in DECADE_QUERY_SUFFIXES
        )

    if "live" in normalized:
        queries.append(f"{comparison_target} live recording")

    if "studio" in normalized:
        queries.append(f"{comparison_target} studio recording")

    if "contrasting" in normalized or "different" in normalized:
        queries.append(f"{comparison_target} opera aria")

    unique_queries = list(dict.fromkeys(queries))
    return unique_queries[: max(count, 3)]


def create_search_plan(prompt: str, count: int) -> AgentSearchPlan:
    interpreted = interpret_prompt(prompt)
    comparison_target = determine_comparison_target(interpreted)
    exclude_terms = extract_exclude_terms(interpreted)
    prefer_terms = extract_prefer_terms(interpreted)
    search_queries = build_search_queries(comparison_target, interpreted, count)

    rationale_parts = [f"Center comparison on {comparison_target}."]

    if exclude_terms:
        rationale_parts.append(f"Exclude recordings matching: {', '.join(exclude_terms)}.")

    if prefer_terms:
        rationale_parts.append(f"Prefer recordings matching: {', '.join(prefer_terms)}.")

    if len(search_queries) > 1:
        rationale_parts.append(f"Run {len(search_queries)} targeted YouTube searches.")

    return AgentSearchPlan(
        comparison_target=comparison_target,
        search_queries=search_queries,
        exclude_terms=exclude_terms,
        prefer_terms=prefer_terms,
        rationale=" ".join(rationale_parts),
    )


def recording_searchable_text(recording: dict) -> str:
    return " ".join(
        [
            recording.get("performer", ""),
            recording.get("ariaTitle", ""),
            recording.get("year", ""),
        ]
    ).lower()


def recording_matches_excluded_terms(recording: dict, exclude_terms: list[str]) -> bool:
    searchable_text = recording_searchable_text(recording)
    return any(term.lower() in searchable_text for term in exclude_terms)


def filter_excluded_recordings(
    recordings: list[dict],
    exclude_terms: list[str],
) -> list[dict]:
    if not exclude_terms:
        return recordings

    return [
        recording
        for recording in recordings
        if not recording_matches_excluded_terms(recording, exclude_terms)
    ]


def recording_matches_preferred_terms(
    recording: dict,
    prefer_terms: list[str],
) -> bool:
    if not prefer_terms:
        return False

    searchable_text = recording_searchable_text(recording)
    return any(term.lower() in searchable_text for term in prefer_terms)


def rank_by_preferred_terms(
    recordings: list[dict],
    prefer_terms: list[str],
) -> list[dict]:
    if not prefer_terms:
        return recordings

    preferred = [
        recording
        for recording in recordings
        if recording_matches_preferred_terms(recording, prefer_terms)
    ]
    others = [
        recording
        for recording in recordings
        if not recording_matches_preferred_terms(recording, prefer_terms)
    ]

    return preferred + others


async def fetch_recordings_for_queries(
    queries: list[str],
    comparison_target: str,
) -> list[dict]:
    """Reuse existing YouTube search and verification pipeline."""
    candidates: list[dict] = []

    for query in queries:
        results = await search_youtube_recordings(query)

        for recording in results:
            candidates.append(
                {
                    **recording,
                    "ariaTitle": comparison_target,
                }
            )

    return candidates


def select_recordings(candidates: list[dict], count: int) -> list[dict]:
    """Deduplicate and select up to count verified recordings."""
    seen_video_ids: set[str] = set()
    selected: list[dict] = []

    for recording in candidates:
        video_id = recording["videoId"]

        if video_id in seen_video_ids:
            continue

        seen_video_ids.add(video_id)
        selected.append(recording)

        if len(selected) >= count:
            break

    return selected


async def generate_comparison_playlist(prompt: str, count: int) -> dict:
    """Orchestrate search planning and playlist generation."""
    plan = create_search_plan(prompt, count)
    candidates = await fetch_recordings_for_queries(
        plan.search_queries,
        plan.comparison_target,
    )
    filtered = filter_excluded_recordings(candidates, plan.exclude_terms)
    ranked = rank_by_preferred_terms(filtered, plan.prefer_terms)
    recordings = select_recordings(ranked, count)

    return {
        "comparisonTarget": plan.comparison_target,
        "recordings": recordings,
        "searchPlan": plan.model_dump(),
    }
