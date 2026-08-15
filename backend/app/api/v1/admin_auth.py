from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.api.v1.auth import verify_password
from app.core.config import settings
from app.core.rate_limiter import login_rate_limiter
from app.models.admin import (
    AdminPermission,
    AdminRole,
    AdminUser,
    AuditLog,
    admin_role_permissions,
    admin_user_roles,
)
from app.schemas.auth import RefreshTokenRequest, TokenResponse

router = APIRouter(prefix="/admin/auth", tags=["Admin Authentication"])
admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/auth/login")
MAX_FAILED_LOGINS = 5


def _token(user_id: UUID, token_type: str, lifetime: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + lifetime).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_admin_access_token(admin_user_id: UUID) -> str:
    return _token(admin_user_id, "admin_access", timedelta(minutes=settings.access_token_expire_minutes))


def create_admin_refresh_token(admin_user_id: UUID) -> str:
    return _token(admin_user_id, "admin_refresh", timedelta(days=settings.refresh_token_expire_days))


def decode_admin_token(token: str, expected_type: str = "admin_access") -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if payload.get("type") != expected_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token type")
    return payload


async def get_current_admin(
    token: str = Depends(admin_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    payload = decode_admin_token(token)
    try:
        admin_id = UUID(payload.get("sub"))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token") from exc

    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    admin = result.scalar_one_or_none()
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin account not found")
    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin account is inactive")
    if admin.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin account is locked")
    return admin


async def get_admin_permissions(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> set[str]:
    result = await db.execute(
        select(AdminPermission.name)
        .join(admin_role_permissions, admin_role_permissions.c.permission_id == AdminPermission.id)
        .join(AdminRole, AdminRole.id == admin_role_permissions.c.role_id)
        .join(admin_user_roles, admin_user_roles.c.role_id == AdminRole.id)
        .where(admin_user_roles.c.admin_user_id == admin.id, AdminRole.is_active.is_(True))
    )
    return set(result.scalars().all())


def require_permission(permission: str):
    async def dependency(
        admin: AdminUser = Depends(get_current_admin),
        permissions: set[str] = Depends(get_admin_permissions),
    ) -> AdminUser:
        if permission not in permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient admin permissions")
        return admin
    return dependency


@router.post("/login", response_model=TokenResponse)
async def admin_login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    email = form_data.username.strip().lower()
    client_ip = request.client.host if request.client else "unknown"
    rate_limit_key = f"admin-login:{client_ip}:{email}"

    allowed, retry_after = login_rate_limiter.check(rate_limit_key)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many admin login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    result = await db.execute(select(AdminUser).where(AdminUser.email == email))
    admin = result.scalar_one_or_none()

    if admin is None or not verify_password(form_data.password, admin.password_hash):
        if admin is not None and admin.is_active and not admin.is_locked:
            admin.failed_login_attempts += 1
            if admin.failed_login_attempts >= MAX_FAILED_LOGINS:
                admin.is_locked = True
            db.add(admin)
            db.add(AuditLog(
                admin_user_id=admin.id,
                action="ADMIN_LOGIN",
                resource_type="ADMIN_USER",
                resource_id=str(admin.id),
                result="LOCKED" if admin.is_locked else "FAILED",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent"),
            ))
            await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin account is inactive")
    if admin.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin account is locked")

    admin.last_login_at = datetime.now(timezone.utc)
    admin.failed_login_attempts = 0
    db.add(AuditLog(
        admin_user_id=admin.id,
        action="ADMIN_LOGIN",
        resource_type="ADMIN_USER",
        resource_id=str(admin.id),
        result="SUCCESS",
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent"),
    ))
    await db.commit()
    login_rate_limiter.clear(rate_limit_key)

    return TokenResponse(
        access_token=create_admin_access_token(admin.id),
        refresh_token=create_admin_refresh_token(admin.id),
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def admin_refresh(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_admin_token(request.refresh_token, "admin_refresh")
    try:
        admin_id = UUID(payload.get("sub"))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    admin = result.scalar_one_or_none()
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin account not found")
    if not admin.is_active or admin.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin account is unavailable")

    return TokenResponse(
        access_token=create_admin_access_token(admin.id),
        refresh_token=create_admin_refresh_token(admin.id),
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me")
async def admin_me(
    admin: AdminUser = Depends(get_current_admin),
    permissions: set[str] = Depends(get_admin_permissions),
):
    return {
        "admin_id": str(admin.id),
        "email": admin.email,
        "full_name": admin.full_name,
        "permissions": sorted(permissions),
        "roles": sorted(role.name for role in admin.roles),
    }
