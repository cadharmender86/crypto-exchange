# BitNova Frontend

The BitNova frontend is the web application for the BitNova crypto-exchange platform. It is built with Next.js, React, TypeScript and Tailwind CSS and communicates with the BitNova FastAPI backend.

> **Development status:** Authentication and dashboard integration are working. Trading UI components are currently presentation-focused. The order book, matching engine, order APIs and live trading flow are planned backend capabilities and should not be considered production trading functionality yet.

## Tech Stack

- **Next.js 16.3.0** — application framework
- **React 19.2.8** — UI library
- **TypeScript** — type safety
- **Tailwind CSS** — styling
- **FastAPI** — backend API
- **PostgreSQL** — backend database
- **JWT Bearer tokens** — authenticated API requests

## Project Structure

```text
frontend/
├── README.md
├── package.json
├── next.config.ts
├── tsconfig.json
├── postcss.config.mjs
├── public/
└── src/
    ├── app/
    │   ├── page.tsx
    │   ├── login/
    │   ├── register/
    │   ├── dashboard/
    │   ├── markets/
    │   ├── buy-sell/
    │   ├── otc/
    │   └── fees/
    ├── components/
    └── lib/
        ├── api.ts
        └── marketData.ts
```

## Prerequisites

Install the following before starting development:

- Node.js 20+ recommended
- npm
- BitNova backend running locally
- PostgreSQL configured for the backend

## Environment Configuration

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

`NEXT_PUBLIC_API_URL` is used by the frontend API client as the base URL. If it is not defined, the application currently falls back to `http://127.0.0.1:8000/api/v1`.

Do not commit `.env.local` or real credentials/secrets.

## Installation

From the repository root:

```powershell
npm install --prefix frontend
```

Or from the frontend directory:

```powershell
cd frontend
npm install
```

## Run Development Server

From the repository root:

```powershell
npm run dev
```

The root project script starts the frontend using the `frontend` directory.

Alternatively:

```powershell
cd frontend
npm run dev
```

The application is normally available at:

```text
http://localhost:3000
```

## Production Build

From the repository root:

```powershell
npm run build
npm run start
```

Or from `frontend/`:

```powershell
npm run build
npm run start
```

## Backend Integration

The frontend API client is located at:

```text
src/lib/api.ts
```

The current API integration includes:

| Function | Backend endpoint | Purpose |
|---|---|---|
| `login()` | `POST /api/v1/auth/login` | Authenticate user |
| `register()` | `POST /api/v1/auth/register` | Create user account |
| `getHealth()` | `GET /api/v1/health` | Backend health check |
| `getAssets()` | `GET /api/v1/assets` | Retrieve supported assets |
| `getAccounts()` | `GET /api/v1/accounts` | Retrieve authenticated account balances |
| `getWallets()` | `GET /api/v1/wallets` | Retrieve authenticated wallets |
| `getDeposits()` | `GET /api/v1/deposits` | Retrieve authenticated deposits |

Authenticated requests use:

```http
Authorization: Bearer <access_token>
```

Access and refresh tokens are currently stored in browser `localStorage` under the keys:

```text
bitnova_access_token
bitnova_refresh_token
```

## Current Frontend Features

### Public pages

- Homepage
- Market ticker
- Hero/marketing sections
- Features and security sections
- Products section
- Login
- Registration

### Authenticated functionality

- Login through the FastAPI authentication API
- JWT token storage
- Dashboard
- Account balances
- Wallet information
- Deposit information
- Logout

### Current market presentation

The homepage currently uses local market data from:

```text
src/lib/marketData.ts
```

This data is presentation/demo data and is not yet a live exchange market feed.

## Trading Status

The current Buy/Sell component provides the initial trading UI but does not yet execute real orders.

The production trading flow will be implemented after the backend trading engine is ready:

```text
Buy/Sell UI
    ↓
Order API
    ↓
Balance reservation
    ↓
Order book
    ↓
Matching engine
    ↓
Trade execution
    ↓
Ledger settlement
    ↓
Updated account balances
```

Planned trading backend APIs include concepts such as:

```text
POST   /api/v1/orders
GET    /api/v1/orders
GET    /api/v1/orders/{id}
DELETE /api/v1/orders/{id}
GET    /api/v1/orderbook/{symbol}
GET    /api/v1/trades/{symbol}
GET    /api/v1/ticker/{symbol}
```

These endpoints should only be added to the frontend after they are implemented and tested in the backend.

## Development Roadmap

### Completed / working

- [x] Next.js frontend structure
- [x] Homepage
- [x] Login page
- [x] Registration page
- [x] API client
- [x] JWT authentication integration
- [x] Dashboard
- [x] Accounts integration
- [x] Wallet integration
- [x] Deposit integration
- [x] Homepage responsive layout improvements

### In progress / next

- [ ] Complete wallet UI
- [ ] Deposit workflow UI
- [ ] Withdrawal workflow UI
- [ ] Transaction/ledger history UI
- [ ] Market page backed by backend market data
- [ ] Backend trading-pair and order models
- [ ] Order book
- [ ] Matching engine
- [ ] Trade settlement and ledger integration
- [ ] Order APIs
- [ ] Real Buy/Sell execution
- [ ] Open orders
- [ ] Trade history
- [ ] Real-time WebSocket market updates

## API Client Guidelines

Use the shared API client instead of calling `fetch()` directly from individual pages when communicating with the backend.

Example:

```ts
import { getAccounts } from "@/lib/api";

const token = getAccessToken();
if (token) {
  const accounts = await getAccounts(token);
}
```

Keep API types in `src/lib/api.ts` or split them into dedicated type modules as the application grows.

## Authentication Guidelines

- Do not hard-code user credentials.
- Do not expose secrets in client-side code.
- Do not put private API keys in `NEXT_PUBLIC_*` variables.
- Handle expired/invalid tokens consistently.
- Clear local authentication state on logout.
- Before production deployment, review whether browser `localStorage` remains appropriate for the final authentication architecture.

## UI Development Guidelines

- Keep reusable UI in `src/components/`.
- Keep page-specific composition inside `src/app/`.
- Keep API communication in the API layer rather than embedding backend URLs throughout components.
- Reuse the existing BitNova dark visual language.
- Use responsive layouts for desktop, tablet and mobile.
- Do not represent unavailable backend functionality as completed/live functionality.

## Local Development Workflow

1. Start PostgreSQL.
2. Start the FastAPI backend.
3. Verify the backend health endpoint.
4. Start the Next.js frontend.
5. Open `http://localhost:3000`.
6. Test registration/login.
7. Verify dashboard data is loaded from the backend.
8. Check browser and backend logs when debugging API issues.

Recommended terminals:

```text
Terminal 1 → FastAPI backend → http://127.0.0.1:8000
Terminal 2 → Next.js frontend → http://localhost:3000
```

## Troubleshooting

### Next.js says it cannot find `app` or `pages`

Make sure Next.js is being started from the `frontend` application context. The repository root uses scripts that delegate to `frontend`.

### Login returns 404 for `/auth/login`

Check `frontend/.env.local` and make sure the API base URL includes `/api/v1`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

Restart Next.js after changing environment variables.

### Login returns 401

The frontend reached the backend successfully, but the credentials were rejected. Verify the user account and backend authentication state.

### Chrome console shows `chrome-extension://...` errors

If the error originates from a `chrome-extension://` URL, test the application in Incognito mode or disable the offending browser extension. Such an error is not necessarily caused by the BitNova application.

### Frontend loads but API calls fail

Verify:

```text
Frontend → http://localhost:3000
Backend  → http://127.0.0.1:8000
API base → http://127.0.0.1:8000/api/v1
```

Also check the FastAPI terminal for the actual request path and HTTP status.

## Security Notice

BitNova is an exchange application and financial operations require stronger controls than a normal web application. Before production use, the frontend/backend integration should undergo security review covering authentication, authorization, token storage, CSRF/XSS protections, transaction signing/confirmation, rate limiting, audit logging, and sensitive-data handling.

The current frontend should be treated as a development-stage application until those controls and the complete trading/ledger architecture are implemented and tested.
