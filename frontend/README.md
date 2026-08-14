# BitNova Web Frontend

Next.js web application for the BitNova digital asset exchange.

The web frontend is a client of the shared BitNova backend API. It must not connect directly to PostgreSQL or blockchain infrastructure.

## Technology

- Next.js
- React
- TypeScript
- Tailwind CSS
- REST API integration
- JWT authentication

## Responsibilities

The frontend is responsible for the exchange user interface, including:

- Authentication
- User dashboard
- Account balances
- Wallets
- Assets and markets
- Deposits and withdrawals
- Transaction history
- Trading interfaces
- User/profile and security settings

Financial authorization, balance mutation, ledger operations and blockchain operations remain backend responsibilities.

## Project Structure

```text
frontend/
├── src/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── ...
├── .env.example
├── next.config.ts
├── package.json
├── postcss.config.mjs
└── tsconfig.json
```

## Environment

Copy the example environment file:

```powershell
Copy-Item .env.example .env.local
```

Configure the backend API URL according to the variables defined in `.env.example`.

Never commit `.env.local` or production secrets.

## Install

From the `frontend` directory:

```powershell
npm install
```

## Development

```powershell
npm run dev
```

The development application normally runs at:

```text
http://localhost:3000
```

## Production Build

```powershell
npm run build
npm run start
```

## Quality Checks

Run the available lint/type checks before committing changes:

```powershell
npm run lint
```

If a type-check script is added to `package.json`, run it as part of CI as well.

## Backend Integration

The frontend communicates with the shared API under:

```text
/api/v1
```

Authentication uses the backend's bearer-token flow.

Example:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Important currently available API areas include:

```text
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/assets
GET  /api/v1/accounts
GET  /api/v1/wallets
GET  /api/v1/wallets/{wallet_id}
```

Use the backend OpenAPI documentation during development to confirm the current request and response schemas.

## Architecture

```text
Browser
   │
   ▼
Next.js / React
   │
   │ HTTPS / REST
   ▼
BitNova Backend API
   │
   ├── PostgreSQL
   ├── Redis
   └── Blockchain services
```

The web frontend and Flutter mobile application use the same backend API.

## Security

- Use HTTPS in production.
- Do not store secrets in source code.
- Do not expose database credentials to the browser.
- Do not trust client-side authorization for financial actions.
- Validate API responses and handle expired sessions.
- Keep production API origins explicitly configured.

## Status

The frontend is under active development alongside the backend and Flutter mobile application.
