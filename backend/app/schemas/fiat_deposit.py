from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.fiat_deposit import FiatDepositStatus



# -------------------------------------------------------
# User Request Model
# -------------------------------------------------------

class CreateFiatDepositRequest(BaseModel):
    bank_account_id: UUID
    amount: Decimal = Field(gt=0)
    utr_number: str = Field(min_length=8, max_length=50)
    remarks: str | None = Field(default=None, max_length=500)



# -------------------------------------------------------
# Deposit Response
# -------------------------------------------------------

class FiatDepositResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    bank_account_id: UUID

    ledger_transaction_id: UUID | None = None

    currency: str
    amount: Decimal
    utr_number: str

    status: FiatDepositStatus

    remarks: str | None = None
    rejection_reason: str | None = None

    approved_by_admin_id: UUID | None = None
    approved_at: datetime | None = None

    provider_metadata: dict | None = None

    created_at: datetime
    updated_at: datetime


# -------------------------------------------------------
# Deposit List Response
# -------------------------------------------------------

class FiatDepositListResponse(BaseModel):
    items: list[FiatDepositResponse]
    total: int


# -------------------------------------------------------
# Approve Deposit Response
# -------------------------------------------------------

class ApproveDepositResponse(BaseModel):
    success: bool = True
    message: str = "Deposit approved successfully."

    deposit: FiatDepositResponse


# -------------------------------------------------------
# Reject Deposit Request
# -------------------------------------------------------

class RejectDepositRequest(BaseModel):
    rejection_reason: str = Field(
        ...,
        min_length=5,
        max_length=500,
    )


# -------------------------------------------------------
# Reject Deposit Response
# -------------------------------------------------------

class RejectDepositResponse(BaseModel):
    success: bool = True
    message: str = "Deposit rejected successfully."

    deposit: FiatDepositResponse