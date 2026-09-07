from uuid import UUID

from pydantic import  BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128,)

class RegisterResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    email_verified: bool
    kyc_status: str
    message: str    

class RefreshTokenRequest(BaseModel):
    refresh_token: str

from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str    

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


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
