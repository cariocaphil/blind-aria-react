# backend/app/services/youtube_service.py

import html
import os

import httpx
import isodate
from dotenv import load_dotenv

from app.services.recording_metadata import enrich_recording_metadata

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

MIN_DURATION_SECONDS = 30
MAX_DURATION_SECONDS = 30 * 60


async def search_youtube_recordings(query: str):
    if not YOUTUBE_API_KEY:
        raise RuntimeError("Missing YOUTUBE_API_KEY")

    candidates = await search_youtube_candidates(query)
    verified_recordings = await verify_youtube_recordings(candidates)

    return verified_recordings[:5]


async def search_youtube_candidates(query: str):
    params = {
        "part": "snippet",
        "q": f"{query} opera aria",
        "type": "video",
        "maxResults": 15,
        "key": YOUTUBE_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(YOUTUBE_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

    candidates = []

    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = html.unescape(item["snippet"]["title"])

        candidates.append(
            {
                "id": video_id,
                "ariaTitle": query,
                "videoId": video_id,
                "performer": title,
                "year": "unknown",
            }
        )

    return candidates


async def verify_youtube_recordings(candidates):
    if not candidates:
        return []

    video_ids = [candidate["videoId"] for candidate in candidates]

    params = {
        "part": "snippet,status,contentDetails",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(YOUTUBE_VIDEOS_URL, params=params)
        response.raise_for_status()
        data = response.json()

    verified_by_id = {}

    for item in data.get("items", []):
        video_id = item["id"]
        status = item.get("status", {})
        content_details = item.get("contentDetails", {})
        snippet = item.get("snippet", {})

        privacy_status = status.get("privacyStatus")
        is_embeddable = status.get("embeddable", False)
        duration_raw = content_details.get("duration", "PT0S")
        duration_seconds = parse_duration_seconds(duration_raw)

        if privacy_status != "public":
            continue

        if not is_embeddable:
            continue

        if duration_seconds < MIN_DURATION_SECONDS:
            continue

        if duration_seconds > MAX_DURATION_SECONDS:
            continue

        verified_by_id[video_id] = {
            "title": html.unescape(snippet.get("title", "")),
            "description": html.unescape(snippet.get("description", "")),
            "publishedAt": snippet.get("publishedAt", ""),
            "channelTitle": html.unescape(snippet.get("channelTitle", "")),
            "durationSeconds": duration_seconds,
        }

    verified_recordings = []

    for candidate in candidates:
        video_id = candidate["videoId"]

        if video_id not in verified_by_id:
            continue

        metadata = verified_by_id[video_id]
        verified_recordings.append(
            enrich_recording_metadata(
                video_id=video_id,
                aria_title=candidate["ariaTitle"],
                source_title=metadata["title"],
                source_description=metadata["description"],
                published_at=metadata["publishedAt"],
                channel_title=metadata["channelTitle"],
            )
        )

    return verified_recordings


def parse_duration_seconds(duration_raw: str) -> int:
    duration = isodate.parse_duration(duration_raw)
    return int(duration.total_seconds())