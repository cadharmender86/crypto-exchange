from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdminPermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None


class AdminRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    is_active: bool
    permissions: list[AdminPermissionResponse]
    user_count: int


class AdminRoleAssignmentRequest(BaseModel):
    role_ids: list[UUID] = Field(default_factory=list, max_length=20)
    reason: str = Field(min_length=3, max_length=500)


class AdminRbacUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_locked: bool
    roles: list[str]
    last_login_at: str | None = None


class AdminRbacUserListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[AdminRbacUserResponse]
    total: int
