from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from app.models import UserCreate, UserResponse, TokenResponse
from app.auth import hash_password, verify_password, create_jwt, decode_jwt
import app.storage as storage

router = APIRouter(prefix="", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: UserCreate) -> UserResponse:
    for user in storage.users.values():
        if user["username"] == body.username:
            raise HTTPException(status_code=409, detail="Username already exists")
    uid = storage.next_user_id()
    storage.users[uid] = {
        "id": uid,
        "username": body.username,
        "hashed_password": hash_password(body.password),
    }
    return UserResponse(id=uid, username=body.username)


@router.post("/login", response_model=TokenResponse)
def login(body: UserCreate) -> TokenResponse:
    for user in storage.users.values():
        if user["username"] == body.username:
            if verify_password(body.password, user["hashed_password"]):
                token = create_jwt({"sub": user["id"], "username": user["username"]})
                return TokenResponse(access_token=token, token_type="bearer")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/profile", response_model=UserResponse)
def profile(authorization: Optional[str] = Header(None)) -> UserResponse:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization[7:]
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    uid = payload["sub"]
    user = storage.users.get(uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user["id"], username=user["username"])
