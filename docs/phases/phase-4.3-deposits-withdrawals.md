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

### Implemented API
```http
POST /api/v1/deposits
GET  /api/v1/deposits
GET  /api/v1/deposits/{deposit_id}
```

### Implemented request
```json
{
  "wallet_address_id": "...",
  "asset_id": "...",
  "network": "ETHEREUM",
  "blockchain_tx_hash": "...",
  "amount": "100.00"
}
```

### Rules
- Authentication required.
- Asset must exist and be active.
- `deposit_enabled` must be true.
- Network must be validated against the wallet address and asset.
- Wallet address must belong to the authenticated user.
- Amount must be greater than zero.
- Decimal precision must be enforced.
- Financial state changes must be atomic.
- Deposit settlement must be represented in the ledger.
- Duplicate blockchain transactions must be handled idempotently.
- Failures must roll back completely.

### Deposit validation completed
- Valid deposit creation
- Duplicate blockchain transaction idempotency
- Deposit confirmation progression
- Prevention of credit before confirmation
- Exactly-once confirmed settlement/credit
- Insufficient treasury protection
- API authentication and authorization
- Cross-user deposit access protection
- Wallet/address ownership protection
- Invalid amount rejection

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
- [x] Create deposit
- [x] Reject invalid deposit
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
- [x] Duplicate deposit transaction
- [ ] Duplicate idempotency key for withdrawals
- [ ] Database constraint race
- [x] Rollback after ledger failure for deposits
- [x] Rollback after balance failure for deposits

### Concurrency
- [ ] Two simultaneous withdrawals
- [ ] Competing withdrawals near the balance limit
- [ ] Concurrent idempotent withdrawal requests

## 9. Definition of Done
- [x] Deposit schemas/service/API
- [ ] Withdrawal schemas/service/API
- [x] Migration for deposits
- [ ] Migration for withdrawals if required
- [x] Ledger integration for deposits
- [ ] Ledger integration for withdrawals
- [x] Atomic balance updates for deposits
- [ ] Atomic balance updates for withdrawals
- [x] Asset capability validation for deposits
- [ ] Asset capability validation for withdrawals
- [x] Network/address validation for deposits
- [ ] Network/address validation for withdrawals
- [x] Authorization / IDOR protection for deposits
- [ ] Authorization / IDOR protection for withdrawals
- [x] IntegrityError → controlled `409` where applicable
- [x] Deposit idempotency
- [ ] Withdrawal idempotency
- [ ] Concurrent withdrawal protection
- [x] Deposit rollback tests
- [ ] Withdrawal rollback tests
- [ ] Full Phase 4 regression tests after withdrawals
- [ ] `git diff --check`
- [ ] Clean working tree
- [ ] Commit and push

## Out of Scope

Blockchain provider integration, confirmation monitoring, reconciliation, and transaction lifecycle management belong to Phase 4.4.

## Implementation Rule
First establish a correct internal financial state machine and ledger/balance behavior. Add external blockchain-provider integration only when explicitly required by the implementation plan.
