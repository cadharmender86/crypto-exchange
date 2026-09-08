from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import (APIRouter, Depends, HTTPException, Request, status)
from app.schemas.auth import LoginRequest
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rate_limiter import login_rate_limiter
from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.services.account_service import AccountService
from app.services.email_otp_service import EmailOTPService
from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import (
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    ChangePasswordRequest,
)
from app.schemas.email_otp import (
    VerifyEmailRequest,
    VerifyEmailResponse,
    ResendEmailOtpRequest,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        password_hash,
    )


# ---------------------------------------------------------------------------
# CHANGE PASSWORD
# ---------------------------------------------------------------------------

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    if verify_password(request.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Choose a new password that differs from your current password",
        )

    current_user.password_hash = hash_password(request.new_password)
    await db.commit()

    return {"message": "Password updated successfully"}


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        days=settings.refresh_token_expire_days
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )


# ---------------------------------------------------------------------------
# REGISTER
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    email = request.email.strip().lower()

    # Check existing user
    result = await db.execute(
        select(User).where(User.email == email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create user
    user = User(
        email=email,
        password_hash=hash_password(request.password),
        is_active=True,
        is_verified=False,
    )

    db.add(user)
    await db.flush()

    # Create default wallets/accounts
    await AccountService.create_customer_accounts(
        db=db,
        user_id=user.id,
    )

    try:
        await db.commit()
        await db.refresh(user)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Generate email verification OTP
    await EmailOTPService.generate_register_otp(
        db=db,
        user=user,
    )

    return RegisterResponse(
        user_id=user.id,
        email=user.email,
        email_verified=user.is_verified,
        kyc_status="NOT_STARTED",
        message="Registration successful. Please verify your email with the OTP sent.",
    )

# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Normalize email
    email = payload.email.strip().lower()

    # --------------------------------------------------------
    # Login brute-force protection
    # --------------------------------------------------------
    client_ip = request.client.host if request.client else "unknown"

    rate_limit_key = f"login:{client_ip}:{email}"

    allowed, retry_after = login_rate_limiter.check(rate_limit_key)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    # Find user
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    # Don't reveal if email exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Account active?
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before signing in.",
        )

    # Verify password
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWTs
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Update last login
    if hasattr(user, "last_login_at"):
        user.last_login_at = datetime.now(timezone.utc)

    await db.commit()

    # Reset rate limiter after successful login
    login_rate_limiter.clear(rate_limit_key)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )

# ---------------------------------------------------------------------------
# REFRESH TOKEN
# ---------------------------------------------------------------------------

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(
        request.refresh_token
    )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    result = await db.execute(
        select(User).where(
            User.id == user_uuid
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive",
        )

    new_access_token = create_access_token(
        user.id
    )

    new_refresh_token = create_refresh_token(
        user.id
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )

@router.post("/resend-email-otp")
async def resend_email_otp(
    payload: ResendEmailOtpRequest,
    db: AsyncSession = Depends(get_db),
):
    await EmailOTPService.resend_register_otp(
        db=db,
        email=payload.email,
    )
    return {"message": "OTP sent successfully."}

@router.post(
    "/verify-email",
    response_model=VerifyEmailResponse,
)
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        await EmailOTPService.verify_register_otp(
            db=db,
            email=payload.email,
            otp=payload.otp,
        )

        return VerifyEmailResponse(
            message="Email verified successfully."
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )