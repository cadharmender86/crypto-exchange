# BitNova Mobile

Flutter mobile client for the BitNova digital asset exchange.

The mobile application is a client of the shared BitNova backend API used by the web application. It does not connect directly to PostgreSQL, Redis, wallets, or blockchain nodes.

## Technology

- Flutter
- Dart
- Material 3
- REST API
- WebSocket support planned for real-time market data
- `flutter_secure_storage` for sensitive local tokens

## Current Status

### Implemented

- Flutter application foundation
- BitNova application shell
- Login
- Registration
- Session persistence
- Secure access-token storage
- Logout
- Authenticated API client
- Account/balance integration
- Wallet integration
- Asset/market listing
- Pull-to-refresh dashboard
- API base URL configuration

### In Development

- Deposit flow
- Withdrawal flow
- Transaction history
- Market detail screens
- Trading UI
- Real-time WebSocket market data
- Push notifications
- Biometric authentication
- Advanced account/security settings

## Architecture

```text
                 BitNova Mobile
                       │
                       │ HTTPS / REST
                       │
                       ▼
              BitNova Backend API
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
        PostgreSQL    Redis   Blockchain
```

The mobile app follows a client/service separation:

```text
lib/
├── config/       API/environment configuration
├── models/       API/domain models
├── screens/      User-facing screens
├── services/     API, authentication and storage services
└── main.dart     Application bootstrap
```

## Backend API

The default API prefix is:

```text
/api/v1
```

The current mobile client integrates with API areas including:

```text
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/assets
GET  /api/v1/accounts
GET  /api/v1/wallets
GET  /api/v1/wallets/{wallet_id}
```

The exact request/response contract is owned by the backend. The mobile client should be updated when backend API contracts change.

## API Configuration

### Android emulator

The default development API is:

```text
http://10.0.2.2:8000/api/v1
```

`10.0.2.2` maps the Android emulator to the development machine's localhost.

### Physical device

Use the development machine's LAN address or a deployed HTTPS API:

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.x.x:8000/api/v1
```

### Deployed API

```powershell
flutter run --dart-define=API_BASE_URL=https://api.example.com/api/v1
```

Never hard-code production credentials or secrets into the application.

## Prerequisites

Install:

- Flutter SDK
- Dart SDK bundled with Flutter
- Android Studio and Android SDK for Android development
- Xcode for iOS development on macOS

Verify the local installation:

```powershell
flutter doctor
```

## Setup

From the repository root:

```powershell
cd mobile
flutter pub get
```

If Android/iOS platform folders have not yet been generated:

```powershell
flutter create . --platforms android,ios
flutter pub get
```

Then run:

```powershell
flutter run
```

## Testing

Run Flutter tests with:

```powershell
flutter test
```

Analyze the project with:

```powershell
flutter analyze
```

Format Dart files with:

```powershell
dart format lib test
```

## Authentication

Login uses the backend's OAuth2-compatible form-data endpoint:

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```

The access token is stored using secure storage and sent to authenticated API endpoints as:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

The application must never store passwords in local storage.

## Security

Because this application handles financial operations:

- Use HTTPS for production APIs.
- Store authentication tokens only in secure platform storage.
- Never embed database credentials in the application.
- Never embed blockchain private keys or seed phrases in the application.
- Do not rely on client-side authorization for financial operations.
- Perform authorization and balance validation on the backend.
- Require appropriate server-side controls for withdrawals.
- Clear authentication data during logout.
- Avoid logging access tokens, passwords, withdrawal secrets, or other sensitive data.

## Planned Navigation

```text
Authentication
│
├── Login
├── Register
└── Security / 2FA

Authenticated App
│
├── Home
│   ├── Portfolio
│   └── Markets
├── Wallet
│   ├── Assets
│   ├── Deposit
│   ├── Withdrawal
│   └── Transactions
├── Trade
│   ├── Markets
│   ├── Order Book
│   ├── Buy / Sell
│   ├── Open Orders
│   └── Order History
└── Profile
    ├── Account
    ├── KYC
    ├── Security
    └── Sessions
```

## Development Rules

1. Reuse the shared backend API; do not duplicate financial business logic in Flutter.
2. Keep API models separate from UI widgets.
3. Keep authentication and secure storage in services.
4. Never commit `.env` files, credentials, tokens, or signing secrets.
5. Add tests for authentication, parsing, error handling, and financial UI workflows.
6. Use mock/test APIs for development instead of real customer funds.

## Release Preparation

Before an Android or iOS production release, verify:

- Production HTTPS API endpoint
- Secure token handling
- App signing configuration
- Release build configuration
- Crash/error monitoring
- Push notification configuration
- Privacy policy and terms
- Store compliance requirements
- KYC/AML and withdrawal controls on the backend
- Production API rate limits and monitoring

## Relationship to Other Applications

```text
crypto-exchange/
│
├── backend/     Shared FastAPI API and financial services
├── frontend/    Next.js web application
└── mobile/      Flutter Android/iOS application
```

Web and mobile are separate clients, but both use the same backend and financial data model.
