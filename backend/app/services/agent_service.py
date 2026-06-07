# backend/app/services/agent_service.py

from app.models.search_plan import AgentSearchPlan
from app.services.planners.factory import get_search_planner
from app.services.planners.rule_based_planner import (
    RuleBasedSearchPlanner,
    determine_comparison_target,
)
from app.services.youtube_service import search_youtube_recordings

__all__ = [
    "AgentSearchPlan",
    "create_search_plan",
    "determine_comparison_target",
    "filter_excluded_recordings",
    "generate_comparison_playlist",
    "rank_by_preferred_terms",
    "select_recordings",
]


def create_search_plan(prompt: str, count: int) -> AgentSearchPlan:
    """Synchronous helper for rule-based planning and tests."""
    return RuleBasedSearchPlanner().build_plan(prompt, count)


def recording_searchable_text(recording: dict) -> str:
    return " ".join(
        [
            recording.get("performer", ""),
            recording.get("ariaTitle", ""),
            recording.get("year", ""),
            recording.get("decade", ""),
            recording.get("recordingType", ""),
            recording.get("sourceTitle", ""),
        ]
    ).lower()


def recording_matches_excluded_terms(recording: dict, exclude_terms: list[str]) -> bool:
    performer = recording.get("performer", "").lower()

    if any(term.lower() in performer for term in exclude_terms):
        return True

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

    recording_type = recording.get("recordingType", "unknown").lower()
    year = recording.get("year", "unknown")
    decade = recording.get("decade", "unknown")

    for term in prefer_terms:
        normalized_term = term.lower()

        if normalized_term in {"live", "studio"} and recording_type == normalized_term:
            return True

        if normalized_term.isdigit() and len(normalized_term) == 4:
            if year == normalized_term or decade.startswith(normalized_term[:3]):
                return True

        if normalized_term.endswith("0s") and decade == normalized_term:
            return True

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
    planner = get_search_planner()
    plan = await planner.create_plan(prompt, count)
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
