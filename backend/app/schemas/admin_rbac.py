from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AdminPermissionResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None


class AdminRoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    is_active: bool
    permissions: list[AdminPermissionResponse]
    user_count: int


class AdminRoleAssignmentRequest(BaseModel):
    role_ids: list[UUID] = Field(default_factory=list, max_length=20)
    reason: str = Field(min_length=3, max_length=500)


class AdminCreateRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=12, max_length=128)
    role_id: UUID
    reason: str = Field(min_length=3, max_length=500)


class AdminRbacUserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_locked: bool
    roles: list[str]
    last_login_at: str | None = None


class AdminRbacUserListResponse(BaseModel):
    items: list[AdminRbacUserResponse]
    total: int
