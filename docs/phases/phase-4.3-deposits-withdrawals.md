# Phase 4.3 — Deposits & Withdrawals

## Status
**In Progress**

## Completed

### Deposits
- Deposit model
- Deposit migration
- Deposit service
- Deposit API
- Wallet/address ownership validation
- Asset/network validation
- Idempotency
- Ledger settlement
- Atomic balance updates
- Authorization / IDOR protection
- Input validation
- Rollback and concurrency tests
- API security tests

## Remaining

### Withdrawals
- Withdrawal model
- Withdrawal migration
- Withdrawal schemas
- Withdrawal service
- Withdrawal API
- Withdrawal address validation
- Asset/network validation
- Withdrawal-enabled validation
- Available → locked balance movement
- Ledger integration
- Idempotency
- Concurrent withdrawal protection
- Rollback handling
- Authorization / IDOR protection
- Input validation
- Regression tests

## Objective
Build customer-facing deposit and withdrawal infrastructure on top of users, assets, accounts, wallets, wallet addresses, balances, and the ledger.

## 1. Deposits

### Proposed API
```http
POST /api/v1/deposits
```

### Proposed request
```json
{
  "asset_id": "...",
  "network": "ETHEREUM",
  "address": "0x...",
  "amount": "100.00"
}
```

### Rules
- Authentication required.
- Asset must exist and be active.
- `deposit_enabled` must be true.
- Network must be valid.
- Address must match the selected network.
- Amount must be greater than zero.
- Decimal precision must be enforced.
- Financial state changes must be atomic.
- Deposit must be represented in the ledger.
- Failures must roll back completely.

## 2. Withdrawals

### Proposed API
```http
POST /api/v1/withdrawals
GET  /api/v1/withdrawals
GET  /api/v1/withdrawals/{withdrawal_id}
```

### Proposed request
```json
{
  "asset_id": "...",
  "network": "ETHEREUM",
  "address": "0x...",
  "amount": "25.00"
}
```

### Rules
- Authentication required.
- Asset must exist and be active.
- `withdrawal_enabled` must be true.
- Destination network/address must be valid.
- Amount must be positive and within precision.
- Available balance must be sufficient.
- Balance must be locked/debited atomically.
- Fees must be represented separately if applicable.
- Withdrawal state and ledger entries must be recorded.
- Failures must roll back.

## 3. Authorization / IDOR
A user must never be able to withdraw another user's funds, modify another user's withdrawal, or bypass ownership using another user's wallet/address.

Ownership must be derived from the authenticated user, not trusted request parameters.

## 4. Concurrency
Two simultaneous withdrawals must not spend the same available balance. Use transaction-safe locking consistent with the existing financial architecture.

## 5. Idempotency
Repeated requests with the same idempotency key must not create duplicate financial transactions. Concurrent duplicate requests must be handled safely.

## 6. Error Handling
Expected controlled errors include `401`, `400`, `404`, `403`, and `409` depending on the documented condition. Raw SQL/database errors and stack traces must never be exposed.

## 7. Transaction Model

### Deposit
```text
request
  ↓
validate asset/address/network
  ↓
create transaction
  ↓
credit account
  ↓
create ledger entries
  ↓
commit
```

### Withdrawal
```text
request
  ↓
validate asset/network/address
  ↓
lock account
  ↓
verify available balance
  ↓
debit/lock funds
  ↓
create withdrawal transaction
  ↓
create ledger entries
  ↓
commit
```

Any failure rolls back the complete operation.

## 8. Testing Plan
### Functional
- [ ] Create deposit
- [ ] Reject invalid deposit
- [ ] Create withdrawal
- [ ] Reject invalid withdrawal
- [ ] List withdrawals
- [ ] Retrieve own withdrawal

### Authorization
- [ ] User A cannot access User B withdrawal
- [ ] User A cannot withdraw from User B account
- [ ] User A cannot use User B wallet as an authorization bypass

### Balance
- [ ] Exact-balance withdrawal
- [ ] Insufficient balance
- [ ] Fee handling
- [ ] Locked balance behavior
- [ ] Total balance invariant

### Integrity
- [ ] Duplicate transaction
- [ ] Duplicate idempotency key
- [ ] Database constraint race
- [ ] Rollback after ledger failure
- [ ] Rollback after balance failure

### Concurrency
- [ ] Two simultaneous withdrawals
- [ ] Competing withdrawals near the balance limit
- [ ] Concurrent idempotent requests

## 9. Definition of Done
- [ ] Deposit schemas/service/API
- [ ] Withdrawal schemas/service/API
- [ ] Migration if required
- [ ] Ledger integration
- [ ] Atomic balance updates
- [ ] Asset capability validation
- [ ] Network/address validation
- [ ] Authorization / IDOR protection
- [ ] IntegrityError → controlled `409` where applicable
- [ ] Idempotency
- [ ] Concurrent withdrawal protection
- [ ] Rollback tests
- [ ] Full Phase 4 regression tests
- [ ] `git diff --check`
- [ ] Clean working tree
- [ ] Commit and push


## Out of Scope

Blockchain provider integration, confirmation monitoring,
reconciliation, and transaction lifecycle management belong to Phase 4.4.


## Implementation Rule
First establish a correct internal financial state machine and ledger/balance behavior. Add external blockchain-provider integration only when explicitly required by the implementation plan.
