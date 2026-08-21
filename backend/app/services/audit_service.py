from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import AuditLog, AdminUser


class AuditService:
    """Centralized audit logging for BitNova admin actions."""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        *,
        admin: AdminUser | None,
        action: str,
        resource_type: str,
        resource_id: UUID | str | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        result: str = "SUCCESS",
        reason: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:

        audit = AuditLog(
            admin_user_id=admin.id if admin else None,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            old_value=old_value,
            new_value=new_value,
            result=result,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(audit)
        await db.flush()

        return audit