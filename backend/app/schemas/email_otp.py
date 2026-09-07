from pydantic import BaseModel, EmailStr, Field


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)


class ResendEmailOtpRequest(BaseModel):
    email: EmailStr


class VerifyEmailResponse(BaseModel):
    message: str