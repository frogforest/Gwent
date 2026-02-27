from fastapi import FastAPI
from app.routers import users, decks

app = FastAPI(title="User & Deck Service", version="1.0.0")

app.include_router(users.router)
app.include_router(decks.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
