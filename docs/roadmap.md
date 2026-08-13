# BitNova Crypto Exchange — Project Roadmap

## Purpose
This roadmap documents the implementation plan and completed milestones for the BitNova digital-asset exchange backend.

> Phases 4.1 and 4.2 are confirmed from the implemented repository history and test results. Phases 1–3 are working historical summaries based on the current architecture and available project history and should be refined if the original specifications differ.

## Phase Status

| Phase | Area | Status |
|---|---|---|
| 1 | Foundation & Core API | Completed |
| 2 | Authentication & User Security | Completed |
| 3 | Financial Core — Accounts, Ledger & Transfers | Completed |
| 3B | Financial Integrity & Concurrency | Completed |
| 4.1 | Wallets | Completed |
| 4.2 | Wallet Addresses & Authorization Hardening | Completed |
| 4.3 | Deposits & Withdrawals | Planned |
| 4.4 | Transaction Lifecycle & Blockchain Integration | Planned |
| 4.5 | Trading / Order Management | Planned |
| 4.6 | Production Operations & Observability | Planned |
| 4.7 | API Abuse / Production Security | Baseline tests completed; follow-up hardening planned |

## Phase 1 — Foundation
Establish the backend application, database, configuration, migrations, API structure, and health checks.

## Phase 2 — Authentication & Security
Establish registration, login, JWT access/refresh tokens, password hashing, user lifecycle, and authentication enforcement.

## Phase 3 — Financial Core
Establish assets, accounts, ledger concepts, balances, transfers, and the service boundaries required for financial operations.

## Phase 3B — Financial Integrity
Harden financial operations with database constraints, row locking, transaction rollback behavior, idempotency, validation, and concurrency tests.

## Phase 4.1 — Wallets
Create customer wallets with ownership isolation and uniqueness constraints.

Completed commit: `e9069c9eb0a9d3cf7c322109fdd0700306cc8ba6`

## Phase 4.2 — Wallet Addresses
Create wallet addresses associated with wallets and assets, including network/address uniqueness, deposit-enabled validation, controlled `409 Conflict` handling, and authorization/IDOR protection.

Completed commit: `be46bae` — `feat: add wallet addresses`

## Phase 4.3 — Deposits & Withdrawals
Build customer-facing deposit and withdrawal infrastructure on top of wallets, addresses, accounts, balances, and the ledger.

### Planned work
- Deposit service/API
- Withdrawal service/API
- Asset capability validation
- Wallet/address ownership validation
- Network validation
- Atomic balance updates
- Ledger integration
- Withdrawal balance locking
- Idempotency
- Controlled database errors
- Rollback and concurrency tests

### Definition of Done
- [ ] Deposit service/API
- [ ] Withdrawal service/API
- [ ] Schemas and migrations if required
- [ ] Ledger integration
- [ ] Atomic balance updates
- [ ] Authorization and IDOR protection
- [ ] Input validation
- [ ] IntegrityError handling
- [ ] Idempotency
- [ ] Concurrent withdrawal protection
- [ ] Rollback tests
- [ ] Full regression tests
- [ ] `git diff --check`
- [ ] Clean working tree
- [ ] Commit and push

## Phase 4.4 — Transaction Lifecycle & Blockchain Integration
Pending/confirmed/failed blockchain transactions, confirmations, provider interaction, reconciliation, and operational state transitions.

## Phase 4.5 — Trading / Order Management
Order creation, validation, balance holds, matching, execution, fees, and trade ledger integration.

## Phase 4.6 — Production Operations
Observability, structured logging, metrics, health/readiness checks, deployment configuration, secrets management, and production database practices.

## Phase 4.7 — API Abuse / Production Security
Existing security coverage includes security headers, CORS, internal endpoint protection, authentication enforcement, method abuse, information leakage, malformed JSON, idempotency-key abuse, login rate limiting, error disclosure, and documentation exposure.

### Known follow-ups
- Disable Swagger/OpenAPI in production configuration.
- HSTS is expected when the API is actually served over HTTPS.
- Improve oversized idempotency-key test coverage so validation is exercised with valid authentication.

## Engineering Rules
1. Financial state changes must be atomic.
2. Authorization is derived server-side from the authenticated user.
3. Database constraints remain the final integrity boundary.
4. Race conditions are tested, not assumed away.
5. API errors must not expose stack traces or raw database details.
6. Development-only endpoints must never become customer-facing financial APIs.
7. Each phase ends with implementation, tests, security review, migration review, clean Git diff, commit, and push.
