# backend/app/services/youtube_service.py

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


async def search_youtube_recordings(query: str):
    if not YOUTUBE_API_KEY:
        raise RuntimeError("Missing YOUTUBE_API_KEY")

    params = {
        "part": "snippet",
        "q": f"{query} opera aria",
        "type": "video",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(YOUTUBE_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

    recordings = []

    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]

        recordings.append(
            {
                "id": video_id,
                "ariaTitle": query,
                "videoId": video_id,
                "performer": title,
                "year": "unknown",
            }
        )

    return recordings