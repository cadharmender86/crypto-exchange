# BitNova Dashboard Portfolio Overview - Development Specification

## Purpose

The BitNova Dashboard is the user's portfolio and account management area.

The dashboard provides:

- Portfolio visibility
- Asset balances
- Quick financial actions
- Trading activity summary
- Transaction history

The Dashboard answers:

- What assets does the user own?
- What is the current portfolio value?
- What actions can the user perform?
- What financial activity happened recently?

The Dashboard is a portfolio management interface. Trading execution belongs to the Trade module.

---

# Dashboard Structure

```
Dashboard
|
├── Portfolio Summary
|
├── Quick Actions
|
├── Coin Balance
|
├── Open Orders
|
├── Trade History
|
└── Transaction History
```

---

# Portfolio Summary

## Components

```
Portfolio Summary
|
├── Total Portfolio Value
├── INR Balance
├── Crypto Holdings
├── Profit / Loss
└── 30 Days Trading Volume
```

## Total Portfolio Value

Displays total user asset value converted into INR.

Formula:

```
Total Portfolio Value = INR Balance + Crypto Assets INR Value
```

## INR Balance

Displays:

- Available INR
- Locked INR

Locked balance will support future trading reservation and withdrawals.

## Crypto Holdings

Displays:

- Asset quantity
- INR value
- Portfolio allocation percentage

## Profit / Loss

Displays:

- Today's P&L
- 24 hour change
- Overall portfolio performance

## 30 Days Trading Volume

Displays total buy and sell volume during the last 30 days.

---

# Quick Actions

Primary user actions:

```
[ Deposit ]
[ Withdraw ]
[ Buy Crypto ]
[ Sell Crypto ]
```

## Deposit

Future flow:

```
Select Asset
    ↓
Generate Address
    ↓
Blockchain Transfer
    ↓
Confirmation
    ↓
Balance Update
```

## Withdraw

Future flow:

```
Select Asset
    ↓
Enter Address
    ↓
Enter Amount
    ↓
Security Verification
    ↓
Processing
```

---

# Coin Balance

Displays all user assets.

Table:

```
Asset
Available Balance
Locked Balance
INR Value
Action
```

Actions:

- Trade
- Deposit
- Withdraw

---

# Open Orders

Available after order-book implementation.

Displays:

```
Pair
Side
Order Type
Price
Quantity
Filled
Status
Cancel
```

---

# Trade History

Displays completed trades.

Fields:

```
Pair
Buy/Sell
Price
Quantity
Fee
Time
```

---

# Transaction History

Contains:

```
Transaction History
|
├── Deposits
├── Withdrawals
├── Transfers
└── Ledger Entries
```

---

# Backend API Mapping

## Available APIs

Currently supported:

```
/accounts
/wallets
/deposits
/ledger
```

Used for:

- Portfolio Summary
- Coin Balance
- Deposits
- Transaction History

## Future APIs

Required for trading features:

```
POST   /orders
GET    /orders
DELETE /orders/{id}

GET /trades
GET /portfolio
GET /profit-loss
GET /volume
```

---

# Frontend Components

Recommended structure:

```
frontend/src/components/dashboard/

├── DashboardLayout.tsx
├── PortfolioSummary.tsx
├── QuickActions.tsx
├── CoinBalance.tsx
├── OpenOrders.tsx
├── TradeHistory.tsx
└── TransactionHistory.tsx
```

---

# UI Guidelines

BitNova Dashboard should follow:

- Professional dark exchange theme
- Strong visual hierarchy
- Large financial numbers
- Clean cards
- Responsive layout
- Clear transaction statuses

Status examples:

```
Completed
Pending
Failed
Open
Cancelled
```

---

# Development Roadmap

## Phase 1

Implement using existing backend:

- Portfolio Summary UI
- Quick Actions UI
- Coin Balance
- Transaction History

## Phase 2

Wallet workflows:

- Deposit UI
- Withdrawal UI
- Transfer UI

## Phase 3

After trading engine:

- Open Orders
- Trade History
- Trading Volume
- Profit/Loss calculation

## Phase 4

Advanced analytics:

- Portfolio charts
- Asset allocation
- Performance analytics
- Notifications

---

# Architecture Decision

Dashboard responsibility:

```
Dashboard
=
Portfolio Management
+
Account Overview
+
Financial Activity
```

Trading responsibility:

```
Trade Page
=
Charts
+
Order Book
+
Buy/Sell Execution
+
Market Activity
```
