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
python script/create_databases.py
python scripts/setup_database.py
python main.py

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
python scripts/create_databases.py
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
docker-compose up -d

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

2. Edit `.env` with your configuration:
   ```bash
   nano .env
   ```

3. **Important**: Change the default passwords and secret keys before production deployment!

### Access Points

After deployment, access your application at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **pgAdmin** (development): http://localhost:8080

For detailed Docker deployment instructions, troubleshooting, and advanced configuration, see [DOCKER-DEPLOYMENT.md](DOCKER-DEPLOYMENT.md).

## 🧪 Testing Suite

The project includes a comprehensive testing suite for the backend API, ensuring reliability, security, and functionality of all critical components.

### Test Architecture

The testing suite is organized into two main categories:

- **Unit Tests**: Test individual business logic functions in isolation with mocked dependencies
- **Integration Tests**: Test complete API endpoints with real database interactions

### Test Structure

```
Backend/tests/
├── unit/                        # Unit tests (business logic isolation)
│   ├── test_auth_service.py     # UserService unit tests
│   ├── test_product_service.py  # ProductService unit tests  
│   ├── test_stock_service.py    # StockService unit tests
│   └── test_security.py        # Security functions unit tests
├── integration/                 # Integration tests (API endpoints)
│   ├── test_auth_api.py         # Authentication API tests
│   ├── test_products_api.py     # Products API tests
│   ├── test_stock_movements_api.py  # Stock movements API tests
│   ├── test_stock_transfers_api.py  # Stock transfers API tests
│   └── test_warehouses_api.py   # Warehouses API tests
├── conftest.py                  # Test configuration and fixtures
└── README.md                    # Detailed testing documentation
```

### Quick Test Commands

```bash
cd Backend

# Run all tests
./run_tests.sh

# Run specific test categories
./run_tests.sh unit          # Fast unit tests only
./run_tests.sh integration   # API integration tests only
./run_tests.sh coverage      # Generate coverage report

# Using pytest directly
pytest -v                    # All tests with verbose output
pytest -m unit              # Unit tests only  
pytest -m integration       # Integration tests only
pytest --cov=app            # Run with coverage
```

### Test Coverage

The testing suite provides comprehensive coverage:

- **Unit Tests**: 50+ isolated function tests covering:
  - Authentication service (user creation, login, validation)
  - Product service (CRUD operations, SKU validation, stock calculations)  
  - Stock service (movements, transfers, inventory validation)
  - Security functions (JWT tokens, password hashing)

- **Integration Tests**: 40+ API endpoint tests covering:
  - Complete authentication workflows (register, login, token validation)
  - Product management with pagination, search, and filtering
  - Stock movement creation and validation
  - Stock transfer workflows between warehouses
  - Warehouse management and data consistency

- **Coverage Targets**: >80% overall, >90% for business services, 100% for security functions

### Database Testing

Tests use an isolated test database to ensure:

- **Test Isolation**: Each test runs in a transaction that rolls back
- **Clean State**: Fresh database state for every test
- **Real Database**: Integration tests use actual PostgreSQL (not mocks)
- **Performance**: Fast execution with proper database cleanup

### Test Features

#### Comprehensive Scenarios
- ✅ **Success Paths**: Normal operation workflows
- ✅ **Error Handling**: Invalid data, missing resources, permission errors  
- ✅ **Edge Cases**: Boundary conditions, race conditions, data constraints
- ✅ **Security**: Authentication bypass attempts, invalid tokens, authorization

#### Professional Testing Practices
- ✅ **Test Fixtures**: Reusable test data and mock objects
- ✅ **Mocking**: External dependencies isolated in unit tests
- ✅ **Authentication Testing**: Both authenticated and unauthenticated scenarios
- ✅ **Data Validation**: Schema validation and business rule enforcement

### Environment Setup for Testing

1. **Test Database Setup**:
   ```sql
   CREATE DATABASE inventory_test_db;
   CREATE USER test_user WITH PASSWORD 'test_password';
   GRANT ALL PRIVILEGES ON DATABASE inventory_test_db TO test_user;
   ```

2. **Environment Configuration**:
   ```bash
   # Copy test environment template
   cp Backend/.env.test Backend/.env
   
   # Update database connection for testing
   TEST_DATABASE_URL=postgresql://test_user:test_password@localhost/inventory_test_db
   ```

3. **Install Test Dependencies**:
   ```bash
   cd Backend
   pip install -r requirements.txt  # Includes pytest, pytest-cov, httpx
   ```

### Running Specific Tests

```bash
# Run tests for specific functionality
pytest tests/unit/test_auth_service.py                    # Auth service only
pytest tests/integration/test_products_api.py             # Products API only
pytest -k "test_create_product"                           # All product creation tests
pytest -k "test_auth" --tb=short                         # All auth-related tests

# Run with different output formats
pytest --junitxml=test-results.xml                        # CI/CD compatible output
pytest --html=test-report.html --self-contained-html      # HTML report
```

### Test Performance

- **Unit Tests**: <50ms per test (fast feedback loop)
- **Integration Tests**: <500ms per test (real database operations)
- **Full Suite**: <60 seconds (comprehensive validation)
- **Parallel Execution**: Support for `pytest-xdist` for faster CI/CD

### Continuous Integration Ready

The test suite is designed for CI/CD pipelines:

```yaml
# Example GitHub Actions usage
- name: Run Backend Tests
  run: |
    cd Backend
    pip install -r requirements.txt
    pytest --cov=app --cov-report=xml --junitxml=test-results.xml
```

### Test Documentation

For detailed testing documentation, setup instructions, and best practices, see:
- **[Backend/tests/README.md](Backend/tests/README.md)** - Comprehensive testing guide
- **[Backend/pytest.ini](Backend/pytest.ini)** - Pytest configuration  
- **[Backend/conftest.py](Backend/conftest.py)** - Test fixtures and setup

### Frontend Testing

Frontend testing setup is available for extension:
- **Recommended**: Jest + React Testing Library + Testing Library for user interactions
- **Coverage**: Component rendering, user interactions, API integration  
- **Setup**: `npm install --save-dev @testing-library/react jest jest-environment-jsdom`

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

We welcome contributions to the Inventory Manager project! Please follow these guidelines:

### Development Workflow

1. **Fork the repository** and create a feature branch from `main`
2. **Set up the development environment** following the setup instructions above
3. **Implement your changes** following the existing code patterns and conventions

### Testing Requirements

**All contributions must include appropriate tests:**

- **New Features**: Add both unit tests and integration tests
- **Bug Fixes**: Add regression tests to prevent the issue from recurring  
- **API Changes**: Update integration tests to reflect new behavior
- **Service Logic**: Ensure unit test coverage for business logic changes

### Running Tests Before Submission

```bash
cd Backend

# Run full test suite
./run_tests.sh

# Run tests with coverage (must be >80%)
./run_tests.sh coverage

# Run specific test categories
./run_tests.sh unit        # Fast feedback during development
./run_tests.sh integration # Full API validation
```

### Code Quality Standards

- **Backend**: Follow PEP 8 Python style guidelines
- **Frontend**: Use TypeScript strict mode and follow React best practices
- **Tests**: Write clear, descriptive test names and include both success and failure scenarios
- **Documentation**: Update README files and API documentation for significant changes

### Pull Request Process

1. **Ensure all tests pass** and coverage remains above 80%
2. **Update documentation** if you've made API changes
3. **Write a clear PR description** explaining the changes and their impact
4. **Reference any related issues** using GitHub's linking syntax

### Review Criteria

Pull requests will be reviewed for:

- ✅ **Test Coverage**: All new code covered by appropriate tests
- ✅ **Code Quality**: Clean, readable, and maintainable code
- ✅ **API Compatibility**: No breaking changes unless explicitly discussed  
- ✅ **Security**: No introduction of security vulnerabilities
- ✅ **Performance**: No significant performance regressions

### Getting Help

- **Issues**: Create an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions about architecture or implementation approaches
- **Testing Help**: Refer to [Backend/tests/README.md](Backend/tests/README.md) for detailed testing guidance
