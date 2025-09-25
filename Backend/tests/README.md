# Backend Testing Suite

This comprehensive testing suite provides both unit tests and integration tests for the Inventory Management System backend API.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Test Coverage](#test-coverage)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

## 🔍 Overview

The test suite includes:

- **Unit Tests**: Test individual business logic functions in isolation
- **Integration Tests**: Test complete API endpoints with database interactions
- **Authentication Tests**: Verify security and authentication mechanisms
- **Database Tests**: Ensure proper data persistence and retrieval

## 🏗️ Test Structure

```
tests/
├── __init__.py
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_auth_service.py     # UserService unit tests
│   ├── test_product_service.py  # ProductService unit tests
│   ├── test_stock_service.py    # StockService unit tests
│   └── test_security.py        # Security functions unit tests
├── integration/             # Integration tests
│   ├── __init__.py
│   ├── test_auth_api.py         # Authentication API tests
│   ├── test_products_api.py     # Products API tests
│   ├── test_stock_movements_api.py  # Stock movements API tests
│   ├── test_stock_transfers_api.py  # Stock transfers API tests
│   └── test_warehouses_api.py   # Warehouses API tests
└── conftest.py              # Test configuration and fixtures
```

## ⚙️ Setup

### Prerequisites

1. **Python 3.8+** installed
2. **PostgreSQL** database server running
3. **Virtual environment** (recommended)

### Database Setup

Create a test database:

```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE inventory_test_db;
CREATE USER test_user WITH PASSWORD 'test_password';
GRANT ALL PRIVILEGES ON DATABASE inventory_test_db TO test_user;
```

### Environment Setup

1. **Copy environment file:**
   ```bash
   cp .env.test .env
   ```

2. **Update database connection in .env:**
   ```env
   DATABASE_URL=postgresql://test_user:test_password@localhost/inventory_test_db
   TEST_DATABASE_URL=postgresql://test_user:test_password@localhost/inventory_test_db
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
./run_tests.sh

# Or using pytest directly
pytest
```

### Test Categories

```bash
# Unit tests only (fast)
./run_tests.sh unit

# Integration tests only
./run_tests.sh integration

# Authentication tests only
./run_tests.sh auth

# Run with coverage report
./run_tests.sh coverage

# Fast unit tests only
./run_tests.sh fast
```

### Pytest Options

```bash
# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test file
pytest tests/unit/test_auth_service.py

# Run specific test function
pytest tests/unit/test_auth_service.py::TestUserService::test_create_user_success

# Run tests matching pattern
pytest -k "test_create"

# Run tests with markers
pytest -m "unit"
pytest -m "integration"
pytest -m "auth"
```

## 🏷️ Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual functions and methods in isolation:

- **AuthService**: User creation, authentication, password hashing
- **ProductService**: Product CRUD operations, stock calculations
- **StockService**: Stock movements, transfers, validation logic
- **Security**: JWT tokens, password verification, encryption

### Integration Tests (`@pytest.mark.integration`)

Test complete API workflows:

- **Authentication API**: Registration, login, token validation
- **Products API**: CRUD operations, pagination, search, filtering
- **Stock Movements API**: Creating movements, stock calculations
- **Stock Transfers API**: Warehouse transfers, status management
- **Warehouses API**: Listing, retrieval, validation

### Authentication Tests (`@pytest.mark.auth`)

Security-focused tests:

- JWT token generation and validation
- Password hashing and verification
- Authentication middleware
- Authorization checks

## 📊 Test Coverage

The test suite aims for >80% code coverage:

```bash
# Generate coverage report
./run_tests.sh coverage

# View HTML report
open htmlcov/index.html
```

### Coverage Targets

- **Services**: >90% coverage
- **API Endpoints**: >85% coverage
- **Security Functions**: 100% coverage
- **Database Models**: >80% coverage

## ✍️ Writing New Tests

### Unit Test Template

```python
import pytest
from unittest.mock import Mock, patch
from app.services.your_service import YourService

@pytest.mark.unit
class TestYourService:
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def your_service(self, mock_db):
        return YourService(mock_db)
    
    def test_your_function_success(self, your_service, mock_db):
        # Arrange
        # ... setup test data
        
        # Act
        result = your_service.your_function()
        
        # Assert
        assert result == expected_result
```

### Integration Test Template

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestYourAPI:
    def test_endpoint_success(self, authenticated_client: TestClient, db_session):
        # Arrange
        test_data = {"field": "value"}
        
        # Act
        response = authenticated_client.post("/api/v1/your-endpoint/", json=test_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["field"] == test_data["field"]
```

### Test Fixtures

Common fixtures available in `conftest.py`:

- `client`: Unauthenticated test client
- `authenticated_client`: Pre-authenticated test client
- `db_session`: Database session for each test
- `test_user`: Sample user for testing
- `test_product`: Sample product for testing
- `test_warehouse`: Sample warehouse for testing
- `multiple_warehouses`: Multiple warehouses for testing
- `multiple_products`: Multiple products for testing

### Best Practices

1. **Use descriptive test names**: `test_create_product_with_duplicate_sku_fails`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Mock external dependencies** in unit tests
4. **Use real database** in integration tests
5. **Test both success and failure cases**
6. **Keep tests independent** and idempotent
7. **Use appropriate markers**: `@pytest.mark.unit`, `@pytest.mark.integration`

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check PostgreSQL is running
brew services list | grep postgresql
# or
sudo systemctl status postgresql

# Verify database exists
psql -U test_user -d inventory_test_db -c "\dt"
```

#### Import Errors

```bash
# Ensure PYTHONPATH includes backend directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from backend directory
cd Backend && pytest
```

#### Authentication Errors in Tests

Make sure `conftest.py` properly overrides authentication:

```python
app.dependency_overrides[get_current_active_user] = override_get_current_active_user
```

#### Test Database Not Cleaned

Tests should be isolated. Check that:

- Database transactions are rolled back in `conftest.py`
- Test data doesn't persist between tests
- Fixtures properly clean up resources

#### Slow Test Performance

```bash
# Run only fast unit tests
pytest -m "unit and not slow"

# Use in-memory SQLite for unit tests (if configured)
export TEST_DATABASE_URL="sqlite:///:memory:"
```

### Debug Mode

```bash
# Run tests with detailed output
pytest -v -s --tb=long

# Drop into debugger on failure
pytest --pdb

# Debug specific test
pytest -v -s tests/unit/test_auth_service.py::TestUserService::test_create_user_success
```

### Test Data Inspection

```bash
# Connect to test database to inspect data
psql -U test_user -d inventory_test_db

# List tables
\dt

# Query test data
SELECT * FROM users;
SELECT * FROM products;
SELECT * FROM stock_movements;
```

## 📈 Performance Considerations

- **Unit tests** should complete in <50ms each
- **Integration tests** should complete in <500ms each
- **Full test suite** should complete in <60 seconds
- Use **database transactions** for test isolation
- **Mock external services** to avoid network delays
- **Parallel test execution** can be enabled with pytest-xdist:
  ```bash
  pip install pytest-xdist
  pytest -n auto
  ```

## 🔄 Continuous Integration

For CI/CD pipelines, use:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with JUnit output
pytest --junitxml=test-results.xml

# Run with coverage for reporting
pytest --cov=app --cov-report=xml --cov-report=term
```

## 📝 Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Ensure >80% coverage** for new code
3. **Add both unit and integration tests**
4. **Update this README** if adding new test categories
5. **Run full test suite** before committing

---

Happy Testing! 🧪✨