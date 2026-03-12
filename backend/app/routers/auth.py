"""
auth.py — Authentication router. Handles user registration, login, OAuth flows,
email verification, and profile retrieval/update.  Provides get_current_user
dependency for protecting other routes.
"""
import base64
import random
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.oauth import exchange_code, get_auth_url, get_user_info
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.models.email_verification import EmailVerification
from app.models.user import User
from app.schemas.user import (
    OAuthCodePayload,
    PasswordChange,
    Token,
    UserCreate,
    UserProfile,
    UserProfileUpdate,
    UserRead,
    VerifyEmailRequest,
)
from app.services.email_service import send_verification_email

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


# ---------- Helpers ----------

def _generate_code() -> str:
    """Generate a random 6-digit verification code."""
    return f"{random.randint(100000, 999999)}"


async def _create_and_send_code(user: User, db: AsyncSession) -> None:
    """Create a verification code and send it to the user's email."""
    code = _generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    verification = EmailVerification(
        user_id=user.id,
        code=code,
        expires_at=expires_at,
    )
    db.add(verification)
    await db.flush()

    await send_verification_email(user.email, code)


# ---------- Email / password auth ----------

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account, send verification email, and return a JWT token."""
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), name=payload.name)
    db.add(user)
    await db.flush()

    # Send verification email
    await _create_and_send_code(user, db)

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


# ---------- Email verification ----------

@router.post("/verify-email", response_model=UserProfile)
async def verify_email(
    payload: VerifyEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify email with a 6-digit code."""
    if current_user.email_verified:
        return current_user

    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(EmailVerification)
        .where(
            EmailVerification.user_id == current_user.id,
            EmailVerification.code == payload.code,
            EmailVerification.expires_at > now,
        )
        .order_by(EmailVerification.created_at.desc())
        .limit(1)
    )
    verification = result.scalar_one_or_none()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )

    current_user.email_verified = True
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.post("/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
async def resend_verification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resend the verification email with a new code."""
    if current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified",
        )

    # Rate limit: check if a code was sent in the last 60 seconds
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
    result = await db.execute(
        select(EmailVerification)
        .where(
            EmailVerification.user_id == current_user.id,
            EmailVerification.created_at > cutoff,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait 60 seconds before requesting a new code",
        )

    await _create_and_send_code(current_user, db)


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


@router.post("/me/avatar", response_model=UserProfile)
async def upload_avatar(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload an avatar image (jpg/png/webp, max 2MB). Stored as base64 data URI."""
    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
    MAX_SIZE = 2 * 1024 * 1024  # 2MB

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar must be JPEG, PNG, or WebP",
        )

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar must be under 2MB",
        )

    b64 = base64.b64encode(content).decode("utf-8")
    data_uri = f"data:{file.content_type};base64,{b64}"

    current_user.avatar_url = data_uri
    await db.flush()
    await db.refresh(current_user)
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
        # OAuth users are auto-verified
        user.email_verified = True
    else:
        # New user — create without password, auto-verified
        user = User(
            email=email,
            name=name,
            display_name=name,
            avatar_url=avatar_url,
            oauth_provider=provider,
            oauth_id=oauth_id,
            email_verified=True,
            preferences={},
        )
        db.add(user)

    await db.flush()
    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token)
