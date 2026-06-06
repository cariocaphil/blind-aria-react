from supabase import create_client
from supabase import Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("Missing SUPABASE_URL")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Missing SUPABASE_SERVICE_ROLE_KEY")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)


def create_session(
    aria_query: str,
    recordings: list[dict],
) -> str:
    session_result = (
        supabase.table("sessions")
        .insert(
            {
                "aria_query": aria_query,
            }
        )
        .execute()
    )

    session_id = session_result.data[0]["id"]

    session_items = [
        {
            "session_id": session_id,
            "position": index,
            "recording_id": recording["id"],
            "aria_title": recording["ariaTitle"],
            "video_id": recording["videoId"],
            "performer": recording["performer"],
            "year": recording["year"],
        }
        for index, recording in enumerate(recordings)
    ]

    (
        supabase.table("session_items")
        .insert(session_items)
        .execute()
    )

    return session_id


def get_session(session_id: str):
    session = (
        supabase.table("sessions")
        .select("*")
        .eq("id", session_id)
        .single()
        .execute()
    )

    items = (
        supabase.table("session_items")
        .select("*")
        .eq("session_id", session_id)
        .order("position")
        .execute()
    )

    return {
        "id": session.data["id"],
        "ariaQuery": session.data["aria_query"],
        "recordings": items.data,
    }