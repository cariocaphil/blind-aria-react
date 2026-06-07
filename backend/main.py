from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.routes.agent import router as agent_router
from app.services.session_service import create_session, get_session
from app.services.youtube_service import search_youtube_recordings


class CreateSessionRequest(BaseModel):
    ariaQuery: str
    recordings: list[dict]


app = FastAPI(title="Blind Aria API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://blind-aria-react.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router, prefix="/api/agent")


@app.get("/")
def root():
    return {"message": "Blind Aria API"}


@app.get("/search")
async def search(q: str = ""):
    print(f"Search query: {q}")

    recordings = await search_youtube_recordings(q)

    return {"recordings": recordings}


@app.post("/sessions")
def create_listening_session(request: CreateSessionRequest):
    session_id = create_session(
        aria_query=request.ariaQuery,
        recordings=request.recordings,
    )

    return {"sessionId": session_id}


@app.get("/sessions/{session_id}")
def read_listening_session(session_id: str):
    return get_session(session_id)