<!--
Top-level README for Inventory-Manager
Contains concise setup & run instructions for both Backend (FastAPI) and Frontend (Next.js)
-->

# Inventory Manager

A full-stack Inventory Management application:

- Backend: FastAPI + SQLAlchemy + PostgreSQL — REST API with JWT authentication, product management, stock movements and transfers.
- Frontend: Next.js (TypeScript) + Tailwind — UI for authentication, product CRUD, stock movement tracking and dashboard.

This repository contains two main folders: `Backend/` and `Frontend/`.


## 🗄️ Database Schema

Below is the database diagram showing the main tables and relationships used by the application. The image file is located at `images/database.png` in the `Backend` folder.

![Database Schema](Backend/images/database.png)

Key entities:
- `products`: product catalog and attributes
- `warehouses`: storage locations
- `stock_movements`: immutable ledger of inventory changes (purchases, sales, adjustments)
- `stock_transfers`: transfers between warehouses, referencing related movements
- `users`: application users and authentication data

This diagram helps visualize foreign keys and cardinality between tables (for example, each `stock_movement` links to a `product` and a `warehouse`). Use this when reviewing or extending the database schema.

## Quick start (development)

Prerequisites:

- macOS / Linux / Windows (WSL)
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 12+

Summary (run backend and frontend in two terminals):

```bash
# Terminal A: start backend
cd Backend
# (optional) source .venv/bin/activate
pip install -r requirements.txt
# create and configure your PostgreSQL DB, then
source .venv/bin/activate
python scripts/setup_database.py
python main:app 

# Terminal B: start frontend
cd Frontend
npm run build
npm install
cp .env.local.example .env.local
# change API_URL inside .env.local if needed
npm run dev
```

Open the frontend at http://localhost:3000 and the backend API docs at http://localhost:8000/docs

## Repository layout

- Backend/
  - `main.py` — FastAPI app entry point
  - `app/`
    - `api/` — routers (auth, products, stock_movements, stock_transfers, warehouses)
    - `core/` — config, database session, security utilities
    - `models/` — SQLAlchemy models
    - `schemas/` — Pydantic schemas
    - `services/` — business logic
  - `scripts/` — helper scripts (e.g. DB setup)
  - `tests/` — pytest test suite and fixtures
  - `requirements.txt` — Python dependencies

- Frontend/
  - `package.json` — scripts and dependencies
  - `src/` — Next.js app (App Router)
    - `app/` — pages and routes (dashboard, login, products...)
    - `components/` — UI components
    - `context/` — Auth context
    - `lib/` — API client + services
    - `types/` — TS types

## Backend — Setup and run (detailed)

1. Create virtual environment (recommended):

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate  # zsh / bash
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Required environment variables

Create a `.env` file in `Backend/` (you can copy/inspect values in `Backend/README.md`). Example:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/inventory_db
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/inventory_test_db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
SECRET_KEY=replace-with-a-secure-random-string-of-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BCRYPT_ROUNDS=12
```

4. Create databases in PostgreSQL:

```sql
CREATE DATABASE inventory_db;
CREATE DATABASE inventory_test_db;
```

5. Initialize DB (script provided):

```bash
python scripts/setup_database.py
```

6. Run development server:

```bash
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs (OpenAPI/Swagger)

Common backend commands

```bash
# run tests
cd Backend
pytest -v

# run with explicit host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend — Setup and run (detailed)

1. Install dependencies and copy environment file:

```bash
cd Frontend
npm install
cp .env.local.example .env.local
# Edit .env.local and set API_URL if backend runs elsewhere (default: http://localhost:8000/api/v1)
```

2. Start dev server:

```bash
npm run dev
```

3. Build for production:

```bash
npm run build
npm run start
```

Notes for frontend developers

- Axios instance is in `src/lib/api.ts` and reads `process.env.API_URL`.
- Auth context (`src/context/AuthContext.tsx`) stores JWT in cookies and automatically attaches it to requests.

## Environment variable examples

Backend `.env` example (Backend/.env):

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/inventory_db
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/inventory_test_db

# App
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# JWT
SECRET_KEY=your-very-secret-key-please-change
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Security
BCRYPT_ROUNDS=12
```

Frontend `.env.local` example (Frontend/.env.local):

```env
API_URL=http://localhost:8000/api/v1
NODE_ENV=development
```

## API snapshot & examples

All backend endpoints are prefixed with `/api/v1` by default.

Authentication

- Register: POST /api/v1/auth/register
- Login: POST /api/v1/auth/login  (returns `access_token`)

Products

- List: GET /api/v1/products/?page=1&page_size=20&search=term
- Create: POST /api/v1/products/  (requires Authorization: Bearer <token>)
- Get: GET /api/v1/products/{id}
- Update: PUT /api/v1/products/{id}
- Delete (soft): DELETE /api/v1/products/{id}

Example: login (curl)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

## Tests

Backend: `pytest` is configured. Tests rely on fixtures in `Backend/tests/conftest.py` which set up a clean test DB (make sure `TEST_DATABASE_URL` is set).

```bash
cd Backend
pytest -v
```

Frontend: No unit tests included by default in this snapshot. Add tests with Jest + React Testing Library if needed.

## Development tips

- Use the backend OpenAPI docs to test endpoints while developing frontend features.
- Keep secrets out of version control. Use `.env` and add to `.gitignore`.
- When debugging auth, inspect cookies (frontend stores token in cookie named `token`).

## Contributing

1. Fork
2. Create a topic branch
3. Add tests for new features/bug fixes
4. Open a pull request with a clear description

## License

MIT — see LICENSE file if present.

---

If you'd like, I can also:

- Add example `.env` files in `Backend/` and `Frontend/` (gitignored) or
- Add a small `Makefile` or top-level scripts to start both services with a single command.
# Inventory Manager

A full-stack Inventory Management application with a FastAPI backend and a Next.js (TypeScript + Tailwind) frontend.

This repository contains two main folders:

- `Backend/` — FastAPI application providing a REST API for authentication, product management, stock movements, and stock transfers. Includes tests and scripts for initializing the database.
- `Frontend/` — Next.js frontend (App Router) that communicates with the backend API and presents a dashboard, product management UI, and auth flows.

## Quick Overview

- Backend: FastAPI, SQLAlchemy, PostgreSQL, JWT auth, pytest test-suite.
- Frontend: Next.js 14, TypeScript, Tailwind CSS, Axios for API calls, React Context for auth.

## Table of Contents

- Features
- Project structure
- Prerequisites
- Setup (Backend)
- Setup (Frontend)
- Running (Development)
- Running (Production)
- Tests
- Environment variables
- Contributing
- License

## Features

- JWT-based authentication (register/login)
- Product CRUD with pagination, search and stock-aware sorting
- Immutable stock movement ledger and stock transfer support
- Multi-warehouse inventory tracking
- OpenAPI (Swagger) documentation for backend
- Frontend with protected routes and token handling

## Project Structure

Root contains two folders: `Backend/` and `Frontend/`.

- Backend/
  - `main.py` - FastAPI application entrypoint
  - `app/` - application package
    - `api/` - route handlers (auth, products, stock_movements, stock_transfers, warehouses)
    - `core/` - configuration, database, security utilities
    - `models/` - SQLAlchemy models
    - `schemas/` - Pydantic schemas
    - `services/` - business logic
  - `scripts/` - helper scripts (database setup)
  - `tests/` - pytest test suite
  - `requirements.txt` - Python dependencies

- Frontend/
  - `package.json` - scripts and dependencies
  - `src/` - Next.js app code
    - `app/` - pages and app routes (dashboard, login, products, etc.)
    - `components/` - UI components
    - `context/` - auth context
    - `lib/` - axios client and services
    - `types/` - TypeScript types

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 12+
- Git

## Setup and Run

Below are minimal steps to get the full stack running locally.

### Backend (development)

1. Open a terminal and go to the backend folder:

```bash
cd Backend
```

2. (Optional) Activate the provided virtual environment if present:

```bash
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Create PostgreSQL databases (example names used by the project):

```sql
CREATE DATABASE inventory_db;
CREATE DATABASE inventory_test_db;
```

5. Configure `.env` (Backend/.env). Example entries are included in `Backend/README.md` — ensure `DATABASE_URL`, `SECRET_KEY`, and `API_PORT` are set.

6. Initialize or migrate the database (project includes `scripts/setup_database.py`):

```bash
python scripts/setup_database.py
```

7. Run the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000` and Swagger UI at `http://localhost:8000/docs`.

### Frontend (development)

1. Open a terminal and go to the frontend folder:

```bash
cd Frontend
```

2. Install dependencies:

```bash
npm install
```

3. Copy or create your environment file for the frontend:

```bash
cp .env.local.example .env.local
# Edit .env.local and set API_URL (e.g. API_URL=http://localhost:8000/api/v1)
```

4. Start the frontend dev server:

```bash
npm run dev
```

Open the frontend at `http://localhost:3000`.

## Running in Production

- Backend: containerize or run with a production ASGI server (uvicorn/gunicorn) and configure a process manager or container runtime. Configure `CORS` and `SECRET_KEY` properly.
- Frontend: build with `npm run build` and serve with `npm run start` or deploy to a static hosting provider that supports Next.js.

## Tests

Backend tests use `pytest`. From the `Backend/` folder run:

```bash
pytest -v
```

Some tests require a test database configured in `TEST_DATABASE_URL` environment variable. See `Backend/pytest.ini` and `Backend/tests/conftest.py` for fixtures (the repo includes `clean_db` fixtures used in tests).

Frontend: use your preferred tooling (React testing library / Jest) if added. None are included by default in this repository snapshot.

## Environment Variables

Backend expects a `.env` file with values such as:

- DATABASE_URL (e.g. postgresql://user:pass@localhost:5432/inventory_db)
- API_HOST / API_PORT
- SECRET_KEY (JWT signing key)
- ALGORITHM (e.g. HS256)
- ACCESS_TOKEN_EXPIRE_MINUTES

Frontend expects `.env.local` containing:

- API_URL (e.g. http://localhost:8000/api/v1)

## API Reference

The backend exposes API endpoints prefixed with `/api/v1`. Key endpoints include:

- `POST /api/v1/auth/register` - register user
- `POST /api/v1/auth/login` - login and receive JWT token
- `GET/POST/PUT/DELETE /api/v1/products` - product CRUD
- `GET/POST /api/v1/stock-movements` - stock movements
- `GET/POST /api/v1/stock-transfers` - transfers between warehouses

Visit the running server's `/docs` to view the full OpenAPI docs.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes and add tests
4. Open a pull request

## License

This project is provided under the MIT License.
