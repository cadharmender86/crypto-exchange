from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.admin_auth import require_permission
from app.core.database import get_db
from app.models.admin import AdminUser, AuditLog

router = APIRouter(
    prefix="/audit-logs",
    tags=["Admin Audit Logs"],
)

@router.get("")
@router.get("/")
async def list_audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    resource_type: str | None = None,
    resource_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(require_permission("AUDIT_READ")),
):
    query = select(AuditLog)

    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    if resource_id:
        query = query.where(AuditLog.resource_id == str(resource_id))

    logs = await db.scalars(
        query.order_by(AuditLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    return list(logs)