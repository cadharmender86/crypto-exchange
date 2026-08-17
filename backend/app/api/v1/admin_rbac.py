from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.api.v1.admin_auth import get_current_admin, require_permission
from app.models.admin import (
    AdminPermission,
    AdminRole,
    AdminUser,
    AuditLog,
    admin_user_roles,
)
from app.schemas.admin_rbac import (
    AdminPermissionResponse,
    AdminRbacUserListResponse,
    AdminRbacUserResponse,
    AdminRoleAssignmentRequest,
    AdminRoleResponse,
)


router = APIRouter(prefix="/admin/rbac", tags=["Admin RBAC"])

async def require_super_admin(
    admin: AdminUser,
    db: AsyncSession,
) -> AdminUser:
    result = await db.execute(
        select(AdminRole)
        .join(admin_user_roles, admin_user_roles.c.role_id == AdminRole.id)
        .where(
            admin_user_roles.c.admin_user_id == admin.id,
            AdminRole.name == "SUPER_ADMIN",
            AdminRole.is_active.is_(True),
        )
    )

    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SUPER_ADMIN can manage administrator accounts",
        )

    return admin

async def require_super_admin_dependency(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    return await require_super_admin(admin, db)

@router.get("/roles", response_model=list[AdminRoleResponse])
async def list_roles(
    _: AdminUser = Depends(require_super_admin_dependency),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AdminRole).order_by(AdminRole.name))
    roles = result.scalars().unique().all()
    return [
        AdminRoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_active=role.is_active,
            permissions=[AdminPermissionResponse.model_validate(p) for p in role.permissions],
            user_count=len(role.users),
        )
        for role in roles
    ]


@router.get("/permissions", response_model=list[AdminPermissionResponse])
async def list_permissions(
    _: AdminUser = Depends(require_permission("ADMIN_MANAGE")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AdminPermission).order_by(AdminPermission.name))
    return [AdminPermissionResponse.model_validate(p) for p in result.scalars().all()]


@router.get("/admins", response_model=AdminRbacUserListResponse)
async def list_admins(
    search: str | None = Query(None, min_length=1, max_length=255),
    _: AdminUser = Depends(require_permission("ADMIN_MANAGE")),
    db: AsyncSession = Depends(get_db),
):
    query = select(AdminUser).order_by(AdminUser.created_at.desc())
    if search:
        query = query.where(AdminUser.email.ilike(f"%{search.strip()}%"))
    result = await db.execute(query)
    admins = result.scalars().unique().all()
    return AdminRbacUserListResponse(
        items=[
            AdminRbacUserResponse(
                id=admin.id,
                email=admin.email,
                full_name=admin.full_name,
                is_active=admin.is_active,
                is_locked=admin.is_locked,
                roles=[role.name for role in admin.roles],
                last_login_at=admin.last_login_at.isoformat() if admin.last_login_at else None,
            )
            for admin in admins
        ],
        total=len(admins),
    )


@router.patch("/admins/{admin_id}/roles")
async def assign_roles(
    admin_id: UUID,
    payload: AdminRoleAssignmentRequest,
    request: Request,
    actor: AdminUser = Depends(require_permission("ADMIN_MANAGE")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin account not found")

    role_result = await db.execute(select(AdminRole).where(AdminRole.id.in_(payload.role_ids)))
    roles = role_result.scalars().all()
    if len(roles) != len(set(payload.role_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more roles not found")
    if not roles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one role is required")
    if any(not role.is_active for role in roles):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive roles cannot be assigned")

    old_roles = [role.name for role in target.roles]
    target.roles = list(roles)
    db.add(AuditLog(
        admin_user_id=actor.id,
        action="ADMIN_ROLES_UPDATED",
        resource_type="ADMIN_USER",
        resource_id=str(target.id),
        old_value={"roles": old_roles},
        new_value={"roles": [role.name for role in roles]},
        result="SUCCESS",
        reason=payload.reason,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    ))
    await db.commit()
    await db.refresh(target)
    return {"admin_id": str(target.id), "roles": [role.name for role in target.roles]}
