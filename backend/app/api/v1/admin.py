from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.api.v1.admin_auth import get_current_admin, require_permission
from app.models.admin import AdminUser, AuditLog
from app.models.user import User
from app.schemas.admin import (
    AdminAuditLogResponse,
    AdminDashboardResponse,
    AdminUserDetailResponse,
    AdminUserListResponse,
)


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: str | None = Query(None, min_length=1, max_length=255),
    is_active: bool | None = Query(None),
    is_verified: bool | None = Query(None),
    _: AdminUser = Depends(require_permission("USER_READ")),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if search:
        term = f"%{search.strip().lower()}%"
        filters.append(func.lower(User.email).like(term))
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if is_verified is not None:
        filters.append(User.is_verified == is_verified)

    count_result = await db.execute(
        select(func.count(User.id)).where(*filters)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(User)
        .where(*filters)
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    users = result.scalars().all()

    return AdminUserListResponse(
        items=[AdminUserDetailResponse.model_validate(user) for user in users],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/users/{user_id}", response_model=AdminUserDetailResponse)
async def get_user(
    user_id: UUID,
    _: AdminUser = Depends(require_permission("USER_READ")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return AdminUserDetailResponse.model_validate(user)


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def dashboard(
    _: AdminUser = Depends(require_permission("USER_READ")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            func.count(User.id),
            func.count(User.id).filter(User.is_active.is_(True)),
            func.count(User.id).filter(User.is_verified.is_(True)),
        )
    )
    total, active, verified = result.one()

    return AdminDashboardResponse(
        total_users=total,
        active_users=active,
        verified_users=verified,
    )


@router.get("/audit-logs", response_model=list[AdminAuditLogResponse])
async def audit_logs(
    limit: int = Query(50, ge=1, le=100),
    _: AdminUser = Depends(require_permission("AUDIT_READ")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    return [AdminAuditLogResponse.model_validate(log) for log in result.scalars().all()]
