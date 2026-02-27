from fastapi import FastAPI
from app.routers import games

app = FastAPI(title="Game Service", version="1.0.0")

app.include_router(games.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
