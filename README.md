<!--
Top-level README for Inventory-Manager
Contains concise setup & run instructions for both Backend (FastAPI) and Frontend (Next.js)
-->

# Inventory Manager

A full-stack Inventory Management application with AI-powered recommendations and web scraping capabilities:

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL — REST API with JWT authentication, product management, stock movements, transfers, web scraping, and AI-powered product recommendations
- **Frontend**: Next.js (TypeScript) + Tailwind — UI for authentication, product CRUD, stock movement tracking, dashboard, and recommendation system
- **AI Features**: Sentence transformer embeddings for semantic product similarity, hybrid recommendation engine with price/category/description matching
- **Data Ingestion**: Automated web scraper for external product catalogs with respectful crawling (robots.txt compliance)

This repository contains two main folders: `Backend/` and `Frontend/`.


## 🗄️ Database Schema

Below is the database diagram showing the main tables and relationships used by the application. The image file is located at `images/database.png` in the `Backend` folder.

![Database Schema](images/database.png)

Key entities:
- `products`: product catalog and attributes
- `warehouses`: storage locations
- `stock_movements`: immutable ledger of inventory changes (purchases, sales, adjustments)
- `stock_transfers`: transfers between warehouses, referencing related movements
- `users`: application users and authentication data

This diagram helps visualize foreign keys and cardinality between tables (for example, each `stock_movement` links to a `product` and a `warehouse`). Use this when reviewing or extending the database schema.

## 🔁 Application Flow

The diagram below illustrates the high-level flow between the Frontend, Backend (FastAPI) and the Database. It highlights where authentication happens, where product CRUD and stock movements are processed, and how transfers propagate between warehouses. The image file is located at `images/Flow.png`.

![Application Flow](images/Flow.png)

This flow diagram is helpful for new contributors and reviewers to quickly understand request paths, authentication, and how inventory changes travel through the system.

## 🤖 AI & Data Features

### Web Scraping System
The application includes an automated web scraper that:
- **Respectfully crawls** external e-commerce sites (checks robots.txt compliance)
- **Extracts product data** including names, descriptions, categories, prices, ratings, and images
- **Stores data** in a separate `scrapdata` table for analysis and recommendations
- **Avoids duplicates** by checking product URLs before insertion
- **Rate limits** requests to be polite to external servers

### AI-Powered Recommendations
The recommendation engine provides multiple recommendation types:
- **Price-based**: Find products in similar price ranges (configurable tolerance)
- **Category-based**: Discover products in the same category
- **Description-based**: Semantic similarity using sentence transformer embeddings (AI)
- **Hybrid mode**: Combines all methods with configurable weights for optimal results

The AI system uses:
- **Sentence Transformers** (all-MiniLM-L6-v2) for semantic understanding
- **Cosine similarity** for finding similar products
- **Cached embeddings** stored as NumPy arrays for fast performance
- **Normalized features** for fair comparison across different data types

### Recommendation diagram

A high-level diagram of the recommendation engine and data flow (price & category matching, description embeddings, and hybrid scoring):

![Recommendation Diagram](images/recommendation.drawio.png)


### Data Pipeline
1. Run scraper: `python scripts/scrape_and_store.py`
2. Generate embeddings: `python scripts/setup_recommendations.py`
3. Access via API: `/recommendations/{product_id}` or `/scraped-products/search`

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
python scripts/create_databases.py
python scripts/setup_database.py

# Optional: Populate with sample data and setup AI
python scripts/scrape_and_store.py    # Scrapes external products
python scripts/setup_recommendations.py  # Sets up AI embeddings

python main.py

# Terminal B: start frontend
cd Frontend
npm install
cp .env.local.example .env.local
# change API_URL inside .env.local if needed
npm run dev
```

Open the frontend at http://localhost:3000 and the backend API docs at http://localhost:8000/docs

### Testing AI Features
After setup, test the recommendation system:
- Visit `/docs` and try `/recommendations/{product_id}` endpoints
- Search scraped products via `/scraped-products/search?query=book`
- Test different recommendation types: `price`, `category`, `description`, `hybrid`

## Repository layout

- **Backend/**
  - `main.py` — FastAPI app entry point
  - `app/`
    - `api/` — routers (auth, products, stock_movements, stock_transfers, warehouses, scraped_products, recommendations)
    - `core/` — config, database session, security utilities
    - `models/` — SQLAlchemy models (includes ScrapData for external products)
    - `schemas/` — Pydantic schemas
    - `services/` — business logic (includes recommendation_service for AI)
  - `scripts/` — helper scripts (DB setup, scraping, AI embeddings)
    - `scrape_and_store.py` — Web scraper for external product data
    - `setup_recommendations.py` — AI embedding generation and caching
  - `data/embeddings/` — Cached AI embeddings and metadata (generated)
  - `tests/` — pytest test suite and fixtures
  - `requirements.txt` — Python dependencies (includes sentence-transformers, scikit-learn)

- **Frontend/**
  - `package.json` — scripts and dependencies
  - `src/` — Next.js app (App Router)
    - `app/` — pages and routes (dashboard, login, products, recommendations...)
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
cd scripts  ./setup_admin.sh  #for macos 
cd scripts  bash setup_admin.sh #for windows 
```

6. Run development server:

```bash
python main.py
```

API docs: http://localhost:8000/docs (OpenAPI/Swagger)

Common backend commands

```bash
# run tests
cd Backend
pytest -v

# run with explicit host/port
python main.py
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

## Running in Production

- Backend: containerize or run with a production ASGI server (uvicorn/gunicorn) and configure a process manager or container runtime. Configure `CORS` and `SECRET_KEY` properly.
- Frontend: build with `npm run build` and serve with `npm run start` or deploy to a static hosting provider that supports Next.js.

## 🐳 Docker Deployment

The easiest way to deploy the full application stack is using Docker and Docker Compose.

### Quick Docker Start

For production deployment, use the automated deployment script:

```bash
./docker-deploy.sh prod
```

### Manual Docker Commands

Alternatively, you can run Docker Compose manually:

```bash
# Production mode (default)
docker-compose up --build

# Development mode with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Services

The Docker setup includes:

- **Backend API** (port 8000): FastAPI application with automatic database initialization
- **Frontend** (port 3000): Next.js application with optimized production build
- **PostgreSQL** (port 5432): Database with persistent storage
- **pgAdmin** (port 8080): Database administration tool (optional, for development)

### Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. **Important**: Change the default passwords and secret keys before production deployment!

### Access Points

After deployment, access your application at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **pgAdmin** (development): http://localhost:8080

For detailed Docker deployment instructions, troubleshooting, and advanced configuration, see [DOCKER-DEPLOYMENT.md](DOCKER-DEPLOYMENT.md).

## Environment Variables
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


## Changing admin credentials

If a developer needs to change the default admin email or password, update both the compose environment and the admin creation script so values remain consistent.

Where to change

- `docker-compose.yml` — update `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables, or create a top-level `.env` file that Docker Compose reads.
- `Backend/scripts/create_admin_user.py` — this script reads environment variables and will create or update the admin user. If you change defaults inside this script, keep them in sync with your compose/env values.

Images

Two images in the repository illustrate the admin UI and an in-container screenshot: `images/admin.png` and `images/adminindocker.png`.

![change in add_admin_user.py](images/admin.png) 
![change in docker file](images/adminindocker.png) 


Safe workflows

1) Run the script locally (preferred for devs):

```bash
# set environment values in your shell
export ADMIN_EMAIL="new-admin@example.com"
export ADMIN_PASSWORD="a-strong-password"

# run the script to create/update the admin
python Backend/scripts/create_admin_user.py
```

2) With Docker Compose:

```bash
# put ADMIN_EMAIL / ADMIN_PASSWORD into a top-level .env (gitignore it)
docker compose down
docker compose up -d --force-recreate backend

# OR run the creation script inside the backend container without restarting
docker compose run --rm backend python scripts/create_admin_user.py
```

Security notes

- Do not commit credentials to source control. Use `.env` and add it to `.gitignore`.
- Passwords are truncated to 72 bytes before hashing in the create script — avoid relying on longer passwords.
- Rotate `SECRET_KEY` (environment / `Backend/app/core/config.py`) if you rotate admin credentials or suspect compromise.

### Getting Help

- **Issues**: Create an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions about architecture or implementation approaches
- **Testing Help**: Refer to [Backend/tests/README.md](Backend/tests/README.md) for detailed testing guidance
