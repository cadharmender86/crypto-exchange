# BitNova Exchange

Backend API for a digital asset exchange built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, and asynchronous Python.

The project is being developed incrementally with a strong focus on financial integrity, authorization, security, idempotency, and production readiness.

## Project Status

### Completed

- Phase 1 — Core backend foundation
- Phase 2 — Authentication and users
- Phase 3 — Financial core
- Phase 3B — Financial integrity and concurrent transfer testing
- Phase 4 Security — Authentication, authorization, abuse, and production-security testing
- Phase 4.1 — Wallets

### In Progress

- Phase 4.2 — Blockchain addresses

### Planned

- Deposits
- Withdrawals
- Blockchain monitoring

## Architecture

```text
User
 │
 ├── Wallet
 │    │
 │    └── Blockchain Addresses
 │
 └── Account
      │
      ├── Available Balance
      ├── Locked Balance
      │
      └── Ledger
           ├── Transactions
           └── Entries
```

The distinction is intentional:

- **Wallet** represents the user's custody/blockchain container.
- **Wallet Address** represents an address on a blockchain network.
- **Account** represents the user's financial balance for an asset.
- **Ledger** provides the financial transaction record.

## Technology Stack

- Python 3.10+
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- AsyncPG
- Alembic
- Pydantic
- Pydantic Settings
- JWT authentication
- `python-jose`
- Passlib
- Argon2 / bcrypt
- HTTPX

## Project Structure

```text
crypto-exchange/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── v1/
│   │   │       ├── accounts.py
│   │   │       ├── assets.py
│   │   │       ├── auth.py
│   │   │       ├── health.py
│   │   │       ├── internal.py
│   │   │       ├── ledger.py
│   │   │       ├── router.py
│   │   │       ├── transfers.py
│   │   │       ├── users.py
│   │   │       └── wallets.py
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   ├── .env
│   └── requirements.txt
└── README.md
```

## Core Features

### Authentication

- User registration
- Password hashing
- Login
- Access JWTs
- Refresh JWTs
- Token expiration
- JWT algorithm validation
- Invalid signature rejection
- Non-existent-user rejection
- Access/refresh token type separation

Access tokens contain:

```text
sub
type
iat
exp
```

### Authorization

Authenticated endpoints use the current authenticated user rather than trusting a user ID supplied by the client.

This protects against IDOR-style attacks.

```text
User A
  │
  └── GET /api/v1/users/{User B ID}
                 │
                 └── rejected
```

Wallet ownership follows the same principle.

## Financial Accounts

Accounts are associated with:

```text
user_id
asset_id
account_type
```

Balances are represented using:

```text
available_balance
locked_balance
```

The database enforces uniqueness for:

```text
user_id + asset_id + account_type
```

## Ledger

Financial transactions use ledger transactions and ledger entries.

The ledger service validates that financial transactions maintain balanced debit/credit totals.

Financial mutation is kept separate from read-only ledger queries.

## Transfers

Transfers support:

- Balance validation
- Atomic database transactions
- Balance updates
- Ledger entries
- Transaction references
- Idempotency protection
- Concurrent transfer protection

A transfer contains:

```text
from_user
to_user
asset
amount
```

## Idempotency

Transfer requests require an `Idempotency-Key`.

The current implementation:

- Requires an idempotency key
- Limits the key to 100 characters
- Hashes request data
- Detects reuse with a different request
- Stores the resulting transaction
- Prevents duplicate financial processing

## Wallets

Phase 4.1 introduced customer wallets.

Current wallet fields:

```text
id
user_id
wallet_type
status
created_at
updated_at
```

Wallet uniqueness is enforced using:

```text
user_id + wallet_type
```

Current API:

```http
POST /api/v1/wallets
GET  /api/v1/wallets
GET  /api/v1/wallets/{wallet_id}
```

Wallet ownership is enforced, so a user cannot access another user's wallet.

## Blockchain Address Architecture

The planned address architecture separates assets from networks.

For example:

```text
Asset: USDT

Networks:
    TRC20
    ERC20
    BEP20
```

The intended model is:

```text
Wallet
 │
 └── WalletAddress
      ├── Asset
      ├── Network
      ├── Address
      ├── Address Type
      └── Status
```

This prevents incorrectly treating assets and networks as the same entity.

Blockchain address functionality is currently under development in Phase 4.2.

## Security

Security testing covers:

- Missing and malformed JWTs
- Invalid JWT signatures
- Expired JWTs
- Wrong JWT algorithms
- Non-existent users
- Refresh/access token separation
- Cross-user profile access
- Cross-user account access
- Cross-user ledger access
- Cross-user wallet access
- Security headers
- CORS
- Internal endpoint protection
- HTTP method abuse
- Information leakage
- Malformed JSON
- Oversized headers
- Login abuse
- Error disclosure
- Swagger/OpenAPI exposure

Login rate limiting has been implemented and tested. Repeated failed login attempts produce HTTP `429`.

## Security Headers

The application includes:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy
Referrer-Policy: no-referrer
```

HSTS is expected to be enabled at the HTTPS production deployment layer.

## CORS

CORS is configured through environment settings.

Example:

```env
CORS_ORIGINS=http://localhost:3000
```

Multiple origins can be provided as a comma-separated list.

Production deployments should explicitly configure trusted frontend origins.

## Swagger / OpenAPI

Swagger UI is enabled during development:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

For production, documentation endpoints are disabled.

The application uses environment-aware configuration:

```python
docs_url=None if is_production else "/docs"
redoc_url=None if is_production else "/redoc"
openapi_url=None if is_production else "/openapi.json"
```

Therefore:

```text
development → Swagger enabled
production  → Swagger disabled
```

## Environment Configuration

Create a `.env` file in the backend directory.

Example:

```env
APP_NAME=BitNova Exchange API
APP_VERSION=0.1.0
ENVIRONMENT=development
DEBUG=true

DATABASE_URL=postgresql+asyncpg://bitnova:bitnova_password@localhost:5432/bitnova
REDIS_URL=redis://localhost:6379/0

CORS_ORIGINS=http://localhost:3000

JWT_SECRET_KEY=CHANGE_THIS_TO_A_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

INTERNAL_TEST_DEPOSIT_KEY=CHANGE_THIS_TO_A_RANDOM_SECRET
```

Never commit real secrets.

## Database

BitNova uses PostgreSQL and Alembic for database migrations.

Check the current migration:

```powershell
alembic current
```

Check migration heads:

```powershell
alembic heads
```

Apply migrations:

```powershell
alembic upgrade head
```

Rollback one migration:

```powershell
alembic downgrade -1
```

## Running the Backend

From the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
http://127.0.0.1:8000/api/v1/health
```

Development Swagger:

```text
http://127.0.0.1:8000/docs
```

## Authentication Example

Login uses OAuth2-compatible form data:

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```

Example:

```text
username=user1@example.com
password=YOUR_PASSWORD
```

The response contains:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Use the access token:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

## Testing

Authentication security:

```powershell
python .\tests\test_phase4_auth_security.py
```

Authorization:

```powershell
python .\tests\test_phase4_authorization.py
```

API security:

```powershell
python .\tests\test_phase4_api_security.py
```

## Financial Integrity

Financial operations are designed around atomic database transactions.

Conceptually:

```text
BEGIN TRANSACTION

Debit source
Credit destination
Create ledger transaction
Create ledger entries
Create idempotency record

COMMIT
```

If an error occurs:

```text
ROLLBACK
```

The intended invariant is:

```text
No partial balance update
No partial ledger transaction
No orphaned idempotency record
```

Concurrent transfers have also been tested.

## Development-only Deposits

A development/test deposit endpoint exists for controlled testing.

It is protected separately using:

```http
X-Internal-Key
```

It must not be treated as a customer-facing deposit API.

Production deployments should keep this functionality disabled or tightly restricted.

## Production Considerations

Before production deployment, configure:

- HTTPS
- HSTS
- Strong JWT secret
- Production database credentials
- Restricted CORS origins
- Redis configuration
- Login rate limiting
- Monitoring and alerting
- Secure secret management
- Database backups
- Database connection limits
- API reverse proxy
- Restricted internal endpoints
- Disabled Swagger/OpenAPI
- Blockchain node/provider credentials
- Withdrawal security controls
- Blockchain transaction monitoring

## Roadmap

### Phase 4.1 — Wallets

Completed:

- Wallet model
- Wallet migration
- Wallet service
- Wallet API
- Ownership authorization
- Duplicate protection

### Phase 4.2 — Blockchain Addresses

In progress:

- Wallet addresses
- Asset/network association
- Address uniqueness
- Address ownership
- Network validation
- Address status

### Phase 4.3 — Deposits

Planned:

- Deposit records
- Deposit lifecycle
- Blockchain transaction references
- Deposit confirmations
- Ledger crediting

### Phase 4.4 — Withdrawals

Planned:

- Withdrawal requests
- Balance locking
- Withdrawal validation
- Fees
- Withdrawal states
- Blockchain transaction submission

### Phase 4.5 — Blockchain Monitoring

Planned:

- Blockchain transaction monitoring
- Confirmation tracking
- Deposit detection
- Withdrawal tracking
- Reconciliation
- Failure handling

## Design Principles

### 1. Database constraints are part of the security model

Application validation alone is not sufficient. Critical uniqueness and integrity rules should also exist in PostgreSQL.

### 2. Financial operations are atomic

Balance changes and ledger mutations should succeed or fail together.

### 3. User identity comes from authentication

Sensitive endpoints should not trust a client-provided `user_id` when the authenticated identity is already available.

### 4. Idempotency protects financial APIs

Retrying a request should not accidentally create duplicate financial transactions.

### 5. Wallets and balances are separate concepts

A blockchain wallet/address is not the same thing as an exchange account balance.

### 6. Production configuration must differ from development

Development conveniences such as Swagger and test deposits should not automatically remain exposed in production.

## License

This project is currently under development.

License information should be added before public distribution.
