# Phase 4.2 — Wallet Addresses & Authorization Hardening

## Status
**Completed and pushed**

## Objective
Associate blockchain addresses with wallets and assets while enforcing ownership, uniqueness, network, and deposit capability rules.

## Data Model
`wallet_addresses`
- `id`
- `wallet_id`
- `asset_id`
- `network`
- `address`
- `address_type`
- `status`
- `created_at`
- `updated_at`

## Constraints
- Unique `(network, address)`
- Unique `(wallet_id, asset_id, network)`

## Indexes
`asset_id`, `wallet_id`, `status`

## Validation
Address creation requires the selected asset to have `deposit_enabled=True`.

## Error Handling
Database uniqueness failures are converted to controlled `409 Conflict` responses.

Example:
```json
{"detail":"Blockchain address already exists"}
```

## Authorization
Users can only access addresses belonging to their own wallet.

## Migration
`eca6531ff399_add_wallet_addresses.py`

Down revision: `59e0499f0cbc`

## Testing
Validated wallet-address schemas, service, API, deposit-enabled validation, IntegrityError handling, duplicate-address `409`, authenticated access, and Phase 4.2 IDOR authorization.

## Authorization Results
- [x] Own accounts
- [x] Own profile
- [x] Cross-user profile protection
- [x] Own ledger
- [x] Cross-user ledger → `403`
- [x] User 1 → User 2 transfer
- [x] User 2 → User 1 transfer
- [x] Non-existent destination rejection
- [x] Self-transfer rejection
- [x] Unauthenticated access rejection

## Commit
`be46bae feat: add wallet addresses`
