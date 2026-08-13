# Phase 3 — Financial Core

## Status
**Completed**

## Objective
Establish assets, accounts, balances, ledger concepts, and transfers.

## Assets
Assets define supported instruments and capabilities including active state, deposit/withdrawal/trading flags, asset type, and decimal precision.

## Accounts
Customer accounts associate users with assets and maintain:
- available balance
- locked balance
- total balance
- status

## Ledger
The ledger provides the accounting foundation for financial state changes. Financial mutations should be represented through ledger operations rather than arbitrary balance mutation.

## Transfers
Transfers enforce destination existence, sufficient funds, self-transfer prevention, transactional consistency, and authorization.

## Invariants
```text
total_balance = available_balance + locked_balance
```

Financial mutations must preserve ledger/balance consistency.

> Historical working summary based on the current repository architecture and financial/security tests.
