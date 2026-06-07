# backend/app/routes/agent.py

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.agent_service import generate_comparison_playlist

router = APIRouter()


class GeneratePlaylistRequest(BaseModel):
    prompt: str
    count: int = Field(default=5, ge=1, le=10)


@router.post("/generate-playlist")
async def generate_playlist(request: GeneratePlaylistRequest):
    result = await generate_comparison_playlist(
        prompt=request.prompt,
        count=request.count,
    )

    response = {
        "comparisonTarget": result["comparisonTarget"],
        "recordings": result["recordings"],
    }

    if "searchPlan" in result:
        response["searchPlan"] = result["searchPlan"]

    return response
