from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Blind Aria API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Blind Aria API"}


@app.get("/search")
def search(q: str = ""):
    print(f"Search query: {q}")

    return {
        "recordings": [
            {
                "id": "api-1",
                "ariaTitle": "Casta Diva",
                "videoId": "I9ozDKsSEI4",
                "performer": "API Performer A",
                "year": "1958",
            },
            {
                "id": "api-2",
                "ariaTitle": "Casta Diva",
                "videoId": "N_Dw0OjpDfw",
                "performer": "API Performer B",
                "year": "1965",
            },
            {
                "id": "api-3",
                "ariaTitle": "Casta Diva",
                "videoId": "wvBuCLjByaE",
                "performer": "API Performer C",
                "year": "1972",
            },
        ]
    }