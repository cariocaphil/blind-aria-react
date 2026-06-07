# backend/app/services/agent_service.py

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


def interpret_prompt(prompt: str) -> str:
    """Step 1: Interpret the natural-language request (mock: keyword matching)."""
    return prompt.strip()


def determine_comparison_target(prompt: str) -> str:
    """Step 2: Resolve the single musical work the playlist should center on (mocked)."""
    normalized = prompt.lower()

    for keyword, work in KNOWN_WORKS.items():
        if keyword in normalized:
            return work

    for keyword, work in DISCOVERY_TARGETS.items():
        if keyword in normalized:
            return work

    return "Casta Diva"


def generate_search_queries(comparison_target: str, prompt: str) -> list[str]:
    """Step 3: Build YouTube search queries for the comparison target."""
    queries = [comparison_target]

    normalized = prompt.lower()
    if "decade" in normalized or "historical" in normalized:
        queries.append(f"{comparison_target} historical recording")
    if "avoid" in normalized or "without" in normalized:
        queries.append(f"{comparison_target} opera aria")

    return queries


async def fetch_recordings_for_queries(
    queries: list[str],
    comparison_target: str,
) -> list[dict]:
    """Step 4: Reuse existing YouTube search and verification pipeline."""
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
    """Step 5: Deduplicate and select up to count verified recordings."""
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
    """Orchestrate prompt interpretation and playlist generation."""
    interpreted = interpret_prompt(prompt)
    comparison_target = determine_comparison_target(interpreted)
    search_queries = generate_search_queries(comparison_target, interpreted)
    candidates = await fetch_recordings_for_queries(search_queries, comparison_target)
    recordings = select_recordings(candidates, count)

    return {
        "comparisonTarget": comparison_target,
        "recordings": recordings,
    }
