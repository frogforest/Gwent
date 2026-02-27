import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.auth import decode_jwt
from app.config import CARD_URL, GAME_URL, PUBLIC_PATHS, USER_DECK_URL

app = FastAPI(title="API Gateway", version="1.0.0")

_ROUTE_MAP = [
    ("/register", USER_DECK_URL),
    ("/login", USER_DECK_URL),
    ("/profile", USER_DECK_URL),
    ("/decks", USER_DECK_URL),
    ("/cards", CARD_URL),
    ("/games", GAME_URL),
]


def _resolve_upstream(path: str) -> str:
    for prefix, base in _ROUTE_MAP:
        if path == prefix or path.startswith(prefix + "/"):
            return base + path
    return ""


async def _check_auth(request: Request) -> bool:
    key = (request.method, request.url.path)
    if key in PUBLIC_PATHS:
        return True
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return False
    return decode_jwt(auth[7:]) is not None


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy(request: Request, path: str) -> Response:
    full_path = "/" + path

    if not await _check_auth(request):
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized"},
        )

    upstream_url = _resolve_upstream(full_path)
    if not upstream_url:
        return JSONResponse(
            status_code=404,
            content={"detail": "Route not found"},
        )

    body = await request.body()
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=upstream_url,
            params=dict(request.query_params),
            headers=headers,
            content=body,
            timeout=10.0,
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
        media_type=resp.headers.get("content-type"),
    )
