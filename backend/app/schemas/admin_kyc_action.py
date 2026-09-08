from pydantic import BaseModel, Field


class RejectKYCRequest(BaseModel):
    reason: str = Field(
        min_length=10,
        max_length=500,
    )


class ApproveKYCResponse(BaseModel):
    message: str
    status: str