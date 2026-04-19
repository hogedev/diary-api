from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from ...models.user import User
from ...services.auth_service import create_token, hash_password, verify_password
from ..deps import DbSession

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DbSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_token(user)
    return TokenResponse(access_token=token, username=user.username)


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db: DbSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.username == body.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user = User(username=body.username, hashed_password=hash_password(body.password))
    db.add(user)
    await db.flush()
    await db.refresh(user)
    token = create_token(user)
    return TokenResponse(access_token=token, username=user.username)
