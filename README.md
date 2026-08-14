# BitNova Crypto Exchange

BitNova is a digital-asset exchange project focused on a secure financial backend, wallet infrastructure, balances, ledger operations, and transaction workflows.

## Current Project Status

| Phase | Area | Status |
|---|---|---|
| 1 | Foundation & Core API | Completed |
| 2 | Authentication & User Security | Completed |
| 3 | Financial Core — Accounts, Ledger & Transfers | Completed |
| 3B | Financial Integrity & Concurrency | Completed |
| 4.1 | Wallets | Completed |
| 4.2 | Wallet Addresses & Authorization Hardening | Completed |
| 4.3 | Deposits & Withdrawals | **In Progress — Deposits completed; Withdrawals remaining** |
| 4.4 | Transaction Lifecycle & Blockchain Integration | Planned |
| 4.5 | Trading / Order Management | Planned |
| 4.6 | Production Operations & Observability | Planned |
| 4.7 | API Abuse / Production Security | Baseline tests completed; follow-up hardening planned |

## Phase 4.3 — Deposits & Withdrawals

### Deposits — Completed

- Deposit model and migration
- Deposit service and API
- Asset and network validation
- Wallet/address ownership validation
- Atomic balance and ledger settlement
- Idempotency and duplicate transaction protection
- Authorization / IDOR protection
- Input validation
- Rollback, concurrency, and API security tests

### Withdrawals — Remaining

- Withdrawal model and migration
- Withdrawal schemas, service, and API
- Destination address/network validation
- Withdrawal-enabled asset validation
- Available-to-locked balance movement
- Ledger integration
- Idempotency and concurrent withdrawal protection
- Rollback and authorization tests
- Full regression coverage

Detailed Phase 4.3 documentation: [`docs/phases/phase-4.3-deposits-withdrawals.md`](docs/phases/phase-4.3-deposits-withdrawals.md)

Project roadmap: [`docs/roadmap.md`](docs/roadmap.md)

## Repository Structure

```text
.
├── backend/        # FastAPI backend, services, models, migrations, and tests
├── docs/           # Roadmap and phase documentation
└── ...             # Frontend and project configuration
```

## Backend Development

The backend uses FastAPI, SQLAlchemy, PostgreSQL, Alembic, and asynchronous database operations.

From the backend directory:

```powershell
# activate the virtual environment
.venv\Scripts\Activate.ps1

# run the API
uvicorn app.main:app --reload
```

## Engineering Principles

1. Financial state changes must be atomic.
2. Authorization is derived server-side from the authenticated user.
3. Database constraints remain the final integrity boundary.
4. Race conditions are tested, not assumed away.
5. API errors must not expose stack traces or raw database details.
6. Development-only endpoints must never become customer-facing financial APIs.
7. Each phase ends with implementation, tests, security review, migration review, clean Git diff, commit, and push.

## Documentation

- [`docs/roadmap.md`](docs/roadmap.md) — project roadmap and milestone status
- [`docs/phases/README.md`](docs/phases/README.md) — phase documentation index
- [`docs/phases/phase-4.3-deposits-withdrawals.md`](docs/phases/phase-4.3-deposits-withdrawals.md) — current Phase 4.3 implementation plan and status
