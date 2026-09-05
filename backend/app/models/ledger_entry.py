from __future__ import annotations

from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SqlEnum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

# IMPORTANT: Base comes from app.models.base, not app.core.database
from app.models.base import Base

class LedgerEntryType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    
class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Matches PostgreSQL column transaction_id
    transaction_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ledger_transactions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    account_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    entry_type: Mapped[LedgerEntryType] = mapped_column(
        SqlEnum(LedgerEntryType, name="ledger_entry_type_enum"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        nullable=False,
    )

    # Relationship name must match ledger_transaction.py
    ledger_transaction: Mapped["LedgerTransaction"] = relationship(
        "LedgerTransaction",
        back_populates="ledger_entries",
    )

    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="ledger_entries",
        )