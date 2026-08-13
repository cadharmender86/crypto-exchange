# Phase 4.1 — Wallets

## Status
**Completed**

## Objective
Introduce customer wallets as the parent container for blockchain wallet addresses.

## Data Model
`wallets`
- `id`
- `user_id`
- `wallet_type`
- `status`
- `created_at`
- `updated_at`

## Constraint
Unique `(user_id, wallet_type)`.

## API
```http
POST /api/v1/wallets
GET  /api/v1/wallets
GET  /api/v1/wallets/{wallet_id}
```

## Authorization
Wallet access is scoped to the authenticated user. Cross-user wallet access returns a non-disclosing not-found response.

## Migration
`59e0499f0cbc`

## Milestone
`e9069c9eb0a9d3cf7c322109fdd0700306cc8ba6` — Implement Phase 4.1 wallets
