from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.core.config import settings
from app.core.rate_limiter import login_rate_limiter
from app.models.admin import AdminRole, AdminUser, AuditLog
from app.models.admin import admin_user_roles
from app.models.admin import admin_role_permissions
from app.models.admin import AdminPermission
from app.api.v1.auth import hash_password, verify_password
from app.schemas.auth import TokenResponse


router = APIRouter(prefix="/admin/auth", tags=["Admin Authentication"])

admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/auth/login")


def create_admin_access_token(admin_user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(admin_user_id),
        "type": "admin_access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_admin_refresh_token(admin_user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(admin_user_id),
        "type": "admin_refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_admin_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if payload.get("type") != "admin_access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_current_admin(
    token: str = Depends(admin_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    payload = decode_admin_token(token)
    raw_id = payload.get("sub")

    try:
        admin_id = UUID(raw_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(AdminUser).where(AdminUser.id == admin_id)
    )
    admin = result.scalar_one_or_none()

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        .where(
            admin_user_roles.c.admin_user_id == admin.id,
            AdminRole.is_active.is_(True),
        )
    )
    return set(result.scalars().all())


def require_permission(permission: str):
    async def dependency(
        admin: AdminUser = Depends(get_current_admin),
        permissions: set[str] = Depends(get_admin_permissions),
    ) -> AdminUser:
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient admin permissions",
            )
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
    }
