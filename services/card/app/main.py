from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.routers import cards
from app.seed import seed_cards


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    seed_cards()
    yield


app = FastAPI(title="Card Catalog Service", version="1.0.0", lifespan=lifespan)

app.include_router(cards.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
