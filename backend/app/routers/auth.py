"""
auth.py — Authentication router. Handles user registration, login, OAuth flows,
and profile retrieval/update.  Provides get_current_user dependency for protecting
other routes.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.oauth import exchange_code, get_auth_url, get_user_info
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import (
    OAuthCodePayload,
    PasswordChange,
    Token,
    UserCreate,
    UserProfile,
    UserProfileUpdate,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency that extracts and validates the current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


# ---------- Email / password auth ----------

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account and return a JWT token."""
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), name=payload.name)
    db.add(user)
    await db.flush()
    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return a JWT token."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token)


# ---------- Profile ----------

@router.get("/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserProfile)
async def update_me(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile fields."""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.flush()
    return current_user


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the current user's password (email/password users only)."""
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth users cannot set a password here",
        )
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(payload.new_password)
    await db.flush()


# ---------- OAuth ----------

@router.get("/{provider}", response_model=dict)
async def oauth_redirect(provider: str):
    """Return the OAuth authorization URL for the given provider."""
    if provider not in ("google", "microsoft", "github"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported provider: {provider}")
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/{provider}"
    try:
        auth_url = get_auth_url(provider, redirect_uri)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"auth_url": auth_url}


@router.post("/{provider}/callback", response_model=Token)
async def oauth_callback(
    provider: str,
    payload: OAuthCodePayload,
    db: AsyncSession = Depends(get_db),
):
    """Exchange OAuth code for access token, create/link user, return JWT."""
    if provider not in ("google", "microsoft", "github"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported provider: {provider}")

    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/{provider}"

    try:
        access_token = await exchange_code(provider, payload.code, redirect_uri)
        user_info = await get_user_info(provider, access_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"OAuth error: {exc}")

    email = user_info.get("email", "")
    oauth_id = user_info.get("oauth_id", "")
    name = user_info.get("name", "")
    avatar_url = user_info.get("avatar_url", "")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve email from OAuth provider",
        )

    # 1. Try to find by oauth_id + provider
    result = await db.execute(
        select(User).where(User.oauth_provider == provider, User.oauth_id == oauth_id)
    )
    user = result.scalar_one_or_none()

    # 2. If not found, try by email
    if not user:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

    if user:
        # Existing user — update OAuth fields
        user.oauth_provider = provider
        user.oauth_id = oauth_id
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
        if name and not user.name:
            user.name = name
    else:
        # New user — create without password
        user = User(
            email=email,
            name=name,
            display_name=name,
            avatar_url=avatar_url,
            oauth_provider=provider,
            oauth_id=oauth_id,
            preferences={},
        )
        db.add(user)

    await db.flush()
    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token)
