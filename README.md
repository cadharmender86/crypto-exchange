# BitNova Crypto Exchange

BitNova is a digital asset exchange platform under active development, consisting of a shared backend API, a web application, and a Flutter mobile application.

## Applications

```text
crypto-exchange/
│
├── backend/     FastAPI + PostgreSQL financial backend
├── frontend/    Next.js web application
└── mobile/      Flutter Android/iOS application
```

All customer-facing applications use the same backend API. Financial rules, authorization, balances, ledger operations, wallet ownership and blockchain-related operations remain server-side responsibilities.

## Architecture

```text
                         ┌─────────────────┐
                         │   Web Browser    │
                         │ Next.js Frontend │
                         └────────┬────────┘
                                  │
                                  │ HTTPS / REST
                                  │
┌─────────────────┐               ▼
│ Flutter Mobile  │───────► BitNova Backend API
│ Android / iOS   │               │
└─────────────────┘               │
                           ┌───────┼────────┐
                           ▼       ▼        ▼
                       PostgreSQL Redis  Blockchain
```

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- AsyncPG
- Alembic
- Pydantic
- JWT authentication
- Redis

### Web

- Next.js
- React
- TypeScript
- Tailwind CSS

### Mobile

- Flutter
- Dart
- Material 3
- Secure local token storage
- REST API
- WebSocket support planned

## Current Backend Capabilities

The backend currently provides foundational exchange functionality including:

- User registration and authentication
- JWT access/refresh tokens
- Authorization using the authenticated user
- Assets
- Financial accounts
- Available/locked balances
- Ledger transactions and entries
- Internal transfers
- Idempotency protection
- Customer wallets
- Wallet ownership authorization
- Blockchain-address architecture in development

Current API areas include:

```text
/api/v1/auth
/api/v1/users
/api/v1/assets
/api/v1/accounts
/api/v1/wallets
/api/v1/wallet-addresses
/api/v1/deposits
/api/v1/transfers
/api/v1/ledger
```

Refer to `backend/README.md` for the detailed backend status, security model, migrations and development commands.

## Mobile Status

The Flutter application currently includes:

- Application foundation
- Login and registration
- Secure token storage
- Session persistence
- Authenticated API client
- Account/balance integration
- Wallet integration
- Asset listing
- Dashboard refresh

Planned mobile areas:

- Deposits
- Withdrawals
- Transaction history
- Markets
- Trading
- Order book
- WebSocket real-time prices
- Push notifications
- Biometric authentication
- Security/session management

See `mobile/README.md` for Flutter setup and development instructions.

## Web Status

The Next.js frontend is being developed as the browser client of the same backend API.

See `frontend/README.md` for frontend setup and API integration information.

## Development Setup

### 1. Clone

```powershell
git clone https://github.com/cadharmender86/crypto-exchange.git
cd crypto-exchange
```

### 2. Backend

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend development API:

```text
http://127.0.0.1:8000
```

Development OpenAPI documentation:

```text
http://127.0.0.1:8000/docs
```

### 3. Web frontend

```powershell
cd frontend
npm install
npm run dev
```

Normally available at:

```text
http://localhost:3000
```

### 4. Flutter mobile

```powershell
cd mobile
flutter pub get
flutter run
```

For an Android emulator, the default backend URL is:

```text
http://10.0.2.2:8000/api/v1
```

Override it when required:

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.x.x:8000/api/v1
```

## API Contract

The backend is the source of truth for API contracts.

Typical authentication flow:

```text
Register
   │
   ▼
Login
   │
   ▼
Access + Refresh Token
   │
   ▼
Authenticated API calls
```

Clients send:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Do not place financial business logic in the web or mobile clients that should be enforced by the backend.

## Security Principles

- Authentication identity comes from the validated JWT.
- Authorization is enforced server-side.
- Financial mutations are atomic.
- Ledger operations must remain financially balanced.
- Idempotency protects retryable financial requests.
- Wallet ownership is checked server-side.
- Database constraints reinforce application validation.
- Secrets must remain outside source control.
- Production must use HTTPS and restricted CORS.
- Development-only endpoints must never become unrestricted customer APIs.
- Mobile applications must never contain private blockchain keys or database credentials.

## Repository Development Model

Development is incremental and organized around backend phases and client integration.

```text
Backend foundation
      │
      ├── Authentication
      ├── Financial accounts
      ├── Ledger
      ├── Transfers
      ├── Wallets
      ├── Blockchain addresses
      ├── Deposits
      └── Withdrawals
             │
             ▼
       Shared API contract
          ┌────┴────┐
          ▼         ▼
       Web App   Mobile App
```

## Branching

Feature work should be developed on dedicated branches and merged through pull requests after appropriate testing.

Example:

```text
feature/flutter-mobile-foundation
```

## Testing

Backend tests cover authentication, authorization, API security and financial integrity.

Web and mobile applications should add unit, integration and end-to-end coverage as functionality is introduced.

Before merging, run the relevant project checks:

```text
backend → Python tests / security tests
frontend → lint / build
mobile → flutter analyze / flutter test
```

## Production Roadmap

Major remaining areas include:

1. Blockchain address management
2. Deposit processing and confirmations
3. Withdrawal processing and security controls
4. Blockchain monitoring and reconciliation
5. Trading engine/order management
6. Real-time market data
7. Web trading experience
8. Flutter trading experience
9. Notifications
10. Production observability and deployment hardening

## License

This project is currently under development. License information should be added before public distribution.
