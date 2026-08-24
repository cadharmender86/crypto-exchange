from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class LedgerTransaction(Base):
    __tablename__ = "ledger_transactions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    reference: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="POSTED",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    deposits: Mapped[list["Deposit"]] = relationship(
        "Deposit",
        back_populates="ledger_transaction",
        lazy="selectin",
        order_by="Deposit.created_at.desc()",
    )

    withdrawals: Mapped[list["Withdrawal"]] = relationship(
        "Withdrawal",
        back_populates="ledger_transaction",
        lazy="selectin",
        order_by="Withdrawal.created_at.desc()",
    )

    ledger_entries: Mapped[list["LedgerEntry"]] = relationship(
        "LedgerEntry",
        back_populates="ledger_transaction",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    fiat_deposits: Mapped[list["FiatDeposit"]] = relationship(
        "FiatDeposit",
        back_populates="ledger_transaction",
        lazy="selectin",
        order_by="FiatDeposit.created_at.desc()",
    )