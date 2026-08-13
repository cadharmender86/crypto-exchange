
### `docs/phases/README.md`

```markdown
# BitNova Phase Documentation

This directory contains detailed documentation for each implementation phase of the BitNova Crypto Exchange.

## Phase Index

| Phase | Document | Status |
|---|---|---|
| 1 | [Foundation & Core API](phase-1-foundation.md) | Completed |
| 2 | [Authentication & User Security](phase-2-authentication.md) | Completed |
| 3 | [Financial Core](phase-3-financial-core.md) | Completed |
| 3B | [Financial Integrity & Concurrency](phase-3b-integrity.md) | Completed |
| 4.1 | [Wallets](phase-4.1-wallets.md) | Completed |
| 4.2 | [Wallet Addresses](phase-4.2-wallet-addresses.md) | Completed |
| 4.3 | [Deposits & Withdrawals](phase-4.3-deposits-withdrawals.md) | Planned |

## Phase 1 — Foundation

[Open Phase 1 documentation](phase-1-foundation.md)

Focus:

- FastAPI foundation
- Database
- Alembic
- Configuration
- API structure
- Health checks

**Status:** Completed

---

## Phase 2 — Authentication & User Security

[Open Phase 2 documentation](phase-2-authentication.md)

Focus:

- User registration
- Login
- Password hashing
- JWT access tokens
- Refresh tokens
- Authentication security
- Rate limiting

**Status:** Completed

---

## Phase 3 — Financial Core

[Open Phase 3 documentation](phase-3-financial-core.md)

Focus:

- Assets
- Customer accounts
- Balances
- Ledger
- Transfers
- Financial service layer

**Status:** Completed

---

## Phase 3B — Financial Integrity

[Open Phase 3B documentation](phase-3b-integrity.md)

Focus:

- Database integrity
- Transaction rollback
- Row locking
- Idempotency
- Input validation
- Concurrent financial operations

**Status:** Completed

---

## Phase 4.1 — Wallets

[Open Phase 4.1 documentation](phase-4.1-wallets.md)

Focus:

- Customer wallets
- Wallet ownership
- Wallet status
- Wallet uniqueness
- Wallet API

**Status:** Completed

---

## Phase 4.2 — Wallet Addresses

[Open Phase 4.2 documentation](phase-4.2-wallet-addresses.md)

Focus:

- Blockchain wallet addresses
- Asset/network association
- Address uniqueness
- Deposit capability validation
- Authorization
- IDOR protection
- Controlled `409 Conflict` handling

**Status:** Completed**

Commit:

```text
be46bae feat: add wallet addresses