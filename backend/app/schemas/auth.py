from uuid import UUID

from pydantic import  BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128,)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

# class UserResponse(BaseModel):
#     id: UUID
#     email: EmailStr
#     is_active: bool
#     is_verified: bool
#     two_factor_enabled: bool            
