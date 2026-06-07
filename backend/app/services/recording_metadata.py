# backend/app/services/recording_metadata.py

import re

RECORDING_YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")
PAREN_YEAR_PATTERN = re.compile(r"\((19\d{2}|20\d{2})\)")

LIVE_TERMS = ("live", "concert", "recital")
STUDIO_TERMS = ("studio",)


def extract_year_from_text(*texts: str) -> str | None:
    for text in texts:
        if not text:
            continue

        paren_match = PAREN_YEAR_PATTERN.search(text)
        if paren_match:
            return paren_match.group(1)

        year_match = RECORDING_YEAR_PATTERN.search(text)
        if year_match:
            return year_match.group(1)

    return None


def extract_publication_year(published_at: str | None) -> str | None:
    if not published_at or len(published_at) < 4:
        return None

    return published_at[:4]


def resolve_year(
    source_title: str,
    source_description: str = "",
    published_at: str | None = None,
) -> str:
    recording_year = extract_year_from_text(source_title, source_description)
    if recording_year:
        return recording_year

    publication_year = extract_publication_year(published_at)
    if publication_year:
        return publication_year

    return "unknown"


def derive_decade(year: str) -> str:
    if not year.isdigit() or len(year) != 4:
        return "unknown"

    decade_start = (int(year) // 10) * 10
    return f"{decade_start}s"


def detect_recording_type(source_title: str, source_description: str = "") -> str:
    combined = f"{source_title} {source_description}".lower()

    if any(term in combined for term in LIVE_TERMS):
        return "live"

    if any(term in combined for term in STUDIO_TERMS):
        return "studio"

    return "unknown"


def extract_performer(source_title: str) -> str:
    title = source_title.strip()
    if not title:
        return "Unknown performer"

    patterns = [
        re.compile(r"^(.+?)\s+sings\b", re.IGNORECASE),
        re.compile(r"^(.+?)\s*[-–:]\s*.+"),
        re.compile(r"^(.+?)\s+in\s+.+", re.IGNORECASE),
    ]

    for pattern in patterns:
        match = pattern.match(title)
        if not match:
            continue

        performer = match.group(1).strip(" \"'")
        if performer and len(performer) <= 60 and performer.lower() != title.lower():
            return performer

    return title


def enrich_recording_metadata(
    *,
    video_id: str,
    aria_title: str,
    source_title: str,
    source_description: str = "",
    published_at: str | None = None,
    channel_title: str = "",
) -> dict:
    year = resolve_year(source_title, source_description, published_at)
    decade = derive_decade(year)
    recording_type = detect_recording_type(source_title, source_description)
    performer = extract_performer(source_title)

    recording = {
        "id": video_id,
        "ariaTitle": aria_title,
        "videoId": video_id,
        "performer": performer,
        "year": year,
        "decade": decade,
        "recordingType": recording_type,
        "sourceTitle": source_title,
    }

    if source_description:
        recording["sourceDescription"] = source_description

    if channel_title:
        recording["channelTitle"] = channel_title

    return recording
