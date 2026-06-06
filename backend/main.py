from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.youtube_service import search_youtube_recordings

app = FastAPI(title="Blind Aria API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://blind-aria-react.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Blind Aria API"}


@app.get("/search")
async def search(q: str = ""):
    print(f"Search query: {q}")

    recordings = await search_youtube_recordings(q)

    return {
        "recordings": recordings
    }