# BitNova Documentation

Welcome to the BitNova Crypto Exchange project documentation.

This directory contains the project's roadmap, implementation phases, architecture documentation, security notes, and other technical documentation.

## Documentation Structure

```text
docs/
├── README.md
├── roadmap.md
└── phases/
    ├── README.md
    ├── phase-1-foundation.md
    ├── phase-2-authentication.md
    ├── phase-3-financial-core.md
    ├── phase-3b-integrity.md
    ├── phase-4.1-wallets.md
    ├── phase-4.2-wallet-addresses.md
    └── phase-4.3-deposits-withdrawals.md
```

## Roadmap

The main project roadmap is maintained in [`roadmap.md`](roadmap.md).

## Phase Documentation

Detailed phase documentation is maintained under [`phases/`](phases/).

See the [Phase Documentation Index](phases/README.md).

## Current Progress

| Phase | Area | Status |
|---|---|---|
| 1 | Foundation & Core API | Completed |
| 2 | Authentication & User Security | Completed |
| 3 | Financial Core | Completed |
| 3B | Financial Integrity & Concurrency | Completed |
| 4.1 | Wallets | Completed |
| 4.2 | Wallet Addresses | Completed |
| 4.3 | Deposits & Withdrawals | In Progress |
| 4.4 | Blockchain Transaction Lifecycle | Planned |
| 4.5 | Trading / Order Management | Planned |
| 4.6 | Production Operations | Planned |
| 4.7 | API Security & Abuse Protection | Baseline completed |

## Documentation Rules

### 1. Documentation lives with the code

Project documentation should be committed to Git alongside the implementation.

### 2. Completed phases must be documented

When a phase is completed, update its phase document with:

- final implementation scope
- important API changes
- database migrations
- security controls
- test results
- known limitations
- Git commit reference

### 3. Roadmap stays current

When a phase changes status, update [`roadmap.md`](roadmap.md).

Use:

- `Planned`
- `In Progress`
- `Completed`
- `Blocked`
- `Deferred`

### 4. Do not document secrets

Never commit passwords, JWT secrets, API keys, internal authentication keys, database credentials, private keys, wallet seed phrases, or production credentials.

### 5. Documentation must match the implementation

Do not mark functionality as completed until the implementation and relevant tests have actually passed.

## Phase Completion Workflow

```text
Plan
  ↓
Implement
  ↓
Test
  ↓
Security Review
  ↓
Database/Migration Review
  ↓
Update Documentation
  ↓
git diff --check
  ↓
Commit
  ↓
Push to GitHub
```

## Git History

Use clear commit messages, for example:

```text
feat: add wallet addresses
feat: implement deposits
feat: implement withdrawals
docs: update phase 4.3
fix: prevent duplicate withdrawal
test: add withdrawal concurrency tests
```

## Source of Truth

The repository is the source of truth for the current implementation.

If documentation and implementation disagree, resolve the discrepancy before considering the phase complete.
