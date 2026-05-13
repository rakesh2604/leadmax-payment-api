# Leadmax Payment API

Django REST API for user registration, JWT auth, bank accounts (up to three per user), transfers between accounts, and transaction history. Built for classroom-style assignments and small demos; deployable to [Render](https://render.com) with the included Blueprint.

## Tech stack

- Python 3.12+
- Django 6
- Django REST Framework
- **djangorestframework-simplejwt** (access + refresh tokens)
- SQLite (default database)
- Gunicorn + WhiteNoise (production / Render)

## Features (assignment coverage)

| Area | Endpoints / behaviour |
|------|------------------------|
| **Users** | `POST /api/users/` register · `GET /api/users/` list (authenticated) · `GET/PUT/DELETE /api/users/<id>/` profile & self-service (read/update/delete **only your own** `id`) |
| **Auth** | `POST /api/auth/login/` access + refresh · `POST /api/auth/refresh/` new access · access **5 min**, refresh **1 day** |
| **Bank accounts** | `POST/GET /api/accounts/` · `DELETE /api/accounts/<id>/` · `POST /api/accounts/<id>/topup/` · max **3** accounts per user · `account_number` **globally unique** |
| **Payments** | `POST /api/payments/` transfer · `GET /api/payments/history/` · success updates balances + `SUCCESS` row; insufficient funds records `FAILED` without changing balances |

## Local setup

```bash
git clone <repo-url>
cd leadmax-payment
py -3 -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

py -3 -m pip install -r requirements.txt
py -3 manage.py migrate
py -3 manage.py createsuperuser   # optional, for /admin/
py -3 manage.py runserver
```

### Environment variables

| Variable | Purpose |
|----------|---------|
| `DJANGO_DEBUG` | `1` / `true` for local dev (default when not on Render). `0` for production behaviour. |
| `DJANGO_SECRET_KEY` | Required when `DJANGO_DEBUG` is off. |
| `RENDER` | Set to `true` on Render (default); used to infer debug defaults. |
| `RENDER_EXTERNAL_HOSTNAME` | Set on Render web services for `ALLOWED_HOSTS` / CSRF. |

Without `DJANGO_DEBUG` and without `RENDER`, the app assumes **local development** and enables debug-friendly defaults.

## Render deployment

- **Blueprint:** `render.yaml` — `buildCommand: bash build.sh`, `startCommand: bash render_start.sh`, Python **3.12.8**.
- **Build:** installs dependencies, runs `collectstatic`.
- **Start:** runs migrations, then Gunicorn bound to `$PORT`.
- Set **`DJANGO_SECRET_KEY`** in the Render dashboard (or use Blueprint `generateValue` as in `render.yaml`).

Do not set `DATABASE_URL` unless you intentionally switch off SQLite; the project is configured for **SQLite** on disk (`db.sqlite3`).

## Authentication

1. **Register:** `POST /api/users/` with JSON body (no `Authorization` header).
2. **Login:** `POST /api/auth/login/` with `email` and `password` → JSON includes `access` and `refresh`.
3. **Call APIs:** `Authorization: Bearer <access_token>`.
4. **Refresh:** `POST /api/auth/refresh/` with body `{ "refresh": "<refresh_token>" }` when access expires (5 minutes).

All JSON APIs except registration, login, refresh, and `GET /` (API index) require a valid access token.

## API reference

Base URL examples use `http://127.0.0.1:8000` — replace with your host.

### Users

**Register** — `POST /api/users/`

```json
{
  "email": "user@example.com",
  "first_name": "Ada",
  "last_name": "Lovelace",
  "password": "hunter2345"
}
```

**Response** `201`: user fields (no password).

**List users** — `GET /api/users/` — `200`, requires Bearer token.

**Profile** — `GET /api/users/<id>/` — only allowed when `<id>` is the authenticated user’s id (`403` otherwise).

**Update** — `PUT /api/users/<id>/` (partial updates via typical client patterns) — own user only. Optional `password` in body to change password.

**Delete** — `DELETE /api/users/<id>/` — own user only, `204`.

### Auth

**Login** — `POST /api/auth/login/`

```json
{ "email": "user@example.com", "password": "hunter2345" }
```

**Response** `200`:

```json
{
  "refresh": "<jwt>",
  "access": "<jwt>"
}
```

**Refresh** — `POST /api/auth/refresh/`

```json
{ "refresh": "<refresh_token>" }
```

**Response** `200`: new `access` (and optionally rotated refresh, depending on SimpleJWT defaults).

### Bank accounts

**Create** — `POST /api/accounts/`

```json
{
  "bank_name": "SBI",
  "account_name": "Primary",
  "account_number": "11111111",
  "balance": "5000.00"
}
```

`balance` is optional (defaults to `0`). Must be ≥ 0. `account_number` must be unique across all accounts.

**List mine** — `GET /api/accounts/` — `200`.

**Delete mine** — `DELETE /api/accounts/<id>/` — `204` or `404`.

**Top-up** — `POST /api/accounts/<id>/topup/`

```json
{ "amount": "100.00" }
```

**Response** `200`: `detail`, `new_balance`.

### Payments

**Transfer** — `POST /api/payments/`

```json
{
  "sender_account_id": 1,
  "receiver_account_id": 2,
  "amount": "50.00"
}
```

Rules:

- Sender must belong to the authenticated user.
- Sender and receiver must differ (enforced in serializer).
- Transfer runs in a **single database transaction** with row-level locks (`select_for_update`) so balances cannot drift under concurrency (SQLite-supported).
- If balance is insufficient, balances are **not** changed; a `Transaction` row is stored with status `FAILED` and the API returns `400` with `transaction_id` and `available_balance`.
- On success, both balances update and a `SUCCESS` transaction is stored; response `201`.

**History** — `GET /api/payments/history/` — transactions where you are sender or receiver (via owned accounts).

## Payment workflow (summary)

```text
Client POST /api/payments/ with sender/receiver IDs + amount
        │
        ├─ Serializer rejects same account / bad shape → 400, no DB transfer
        │
        ├─ Sender not yours or missing → 404, no balance change
        │
        ├─ Receiver missing → 404, no balance change
        │
        └─ Atomic block (locked sender & receiver rows)
                ├─ balance < amount → insert FAILED txn, 400
                └─ else debit sender, credit receiver, insert SUCCESS txn → 201
```

## Business rules & assumptions

- **Currency:** Balances and amounts are decimal values with two fractional digits; no multi-currency support.
- **SQLite:** Fine for demos; for heavy production load or multiple app instances, move to PostgreSQL and a shared database.
- **Receiver visibility:** Any authenticated user can send to any existing bank account by id (receiver account numbers are not secret). Tighten with “contacts” or “allowed payees” if you need privacy.
- **Failed payments:** Insufficient funds always persist a `FAILED` `Transaction` for audit. Missing receiver/sender does **not** create a row (invalid request before a coherent transfer exists).
- **User list:** `GET /api/users/` returns all users to any authenticated client; restrict to staff or friends if needed.

## License

Use and modify for learning purposes unless otherwise stated by the repository owner.
