import os

USER_DECK_URL = os.getenv("USER_DECK_URL", "http://localhost:8001")
CARD_URL = os.getenv("CARD_URL", "http://localhost:8002")
GAME_URL = os.getenv("GAME_URL", "http://localhost:8003")

PUBLIC_PATHS = {
    ("POST", "/register"),
    ("POST", "/login"),
}
