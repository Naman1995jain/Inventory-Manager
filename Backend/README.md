# Inventory Management System API

A comprehensive RESTful API for inventory management built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**. This system provides secure authentication, product management, and stock tracking capabilities with immutable audit trails.

## 🚀 Features

- **🔐 JWT Authentication**: Secure user registration and login
- **📦 Product Management**: Full CRUD operations with pagination and search
- **🏭 Multi-Warehouse Support**: Track inventory across multiple locations
- **📊 Stock Movements**: Immutable ledger for all inventory changes
- **🔄 Stock Transfers**: Move inventory between warehouses
- **🔍 Advanced Search & Filtering**: Search products with date filters and sorting
- **📋 Comprehensive API Documentation**: Auto-generated with FastAPI/Swagger
- **🧪 Full Test Suite**: Unit and integration tests with pytest
- **🔒 Security**: Password hashing, JWT tokens, and protected endpoints

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI 0.117+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **Testing**: pytest with async support
- **API Documentation**: OpenAPI/Swagger (auto-generated)
- **Environment Management**: python-dotenv
- **Database Migrations**: Alembic (ready for future use)

## 📁 Project Structure

```
NewBackend/
├── app/
│   ├── __init__.py
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── products.py        # Product CRUD endpoints
│   │   ├── stock_movements.py # Stock movement endpoints
│   │   └── stock_transfers.py # Stock transfer endpoints
│   ├── core/                  # Core configuration and dependencies
│   │   ├── __init__.py
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # Database configuration
│   │   ├── dependencies.py    # FastAPI dependencies
│   │   └── security.py        # Security utilities
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── models.py          # Database models
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py         # Request/response schemas
│   └── services/              # Business logic
│       ├── __init__.py
│       ├── auth_service.py    # Authentication business logic
│       ├── product_service.py # Product business logic
│       └── stock_service.py   # Stock management logic
├── scripts/
│   └── setup_database.py     # Database setup script
├── tests/                     # Test suite
│   ├── conftest.py           # Test configuration
│   ├── test_auth.py          # Authentication tests
│   ├── test_products.py      # Product tests
│   └── test_api.py           # API integration tests
├── .env                      # Environment variables
├── .venv/                    # Virtual environment
├── main.py                   # FastAPI application entry point
├── pytest.ini               # pytest configuration
└── requirements.txt          # Python dependencies
```

## 🔧 Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Git

### 1. Clone and Setup

```bash
cd /path/to/your/workspace/NewBackend
```

### 2. Virtual Environment

```bash
# Virtual environment is already created
source .venv/bin/activate  # On macOS/Linux
# .venv\\Scripts\\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

Ensure PostgreSQL is running and create the database:

```sql
CREATE DATABASE inventory_db;
CREATE DATABASE inventory_test_db;  -- For testing
```

### 5. Configure Environment

The `.env` file is already configured with:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:dragon@localhost:5432/inventory_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=inventory_db
DB_USER=postgres
DB_PASSWORD=dragon

# Application Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# JWT Authentication Configuration
SECRET_KEY=your-super-secret-jwt-key-change-in-production-minimum-32-characters-new-backend
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**⚠️ Important**: Change the `SECRET_KEY` for production use!

### 6. Initialize Database

```bash
python scripts/setup_database.py
```

### 7. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepassword123
```

#### Login (JSON)
```http
POST /api/v1/auth/login-json
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepassword123"
}
```

### Product Management

All product endpoints require authentication via `Authorization: Bearer <token>` header.

#### Create Product
```http
POST /api/v1/products/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Laptop Computer",
  "sku": "LAPTOP-001",
  "description": "High-performance laptop",
  "unit_price": 999.99,
  "unit_of_measure": "piece",
  "category": "Electronics"
}
```

#### List Products (with Pagination & Search)
```http
GET /api/v1/products/?page=1&page_size=20&search=laptop&sort_by=name_asc
Authorization: Bearer <token>
```

Query Parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `sort_by`: `name_asc|name_desc|stock_asc|stock_desc|created_asc|created_desc`
- `search`: Search term for name, SKU, description, or category
- `created_from_date`: Filter from date (ISO format)
- `created_to_date`: Filter to date (ISO format)

#### Get Product Details
```http
GET /api/v1/products/{product_id}
Authorization: Bearer <token>
```

Returns product details with stock distribution across warehouses.

#### Update Product
```http
PUT /api/v1/products/{product_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Product Name",
  "unit_price": 1299.99
}
```

#### Delete Product (Soft Delete)
```http
DELETE /api/v1/products/{product_id}
Authorization: Bearer <token>
```

### Stock Management

#### Record Stock Movement
```http
POST /api/v1/stock-movements/
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": 1,
  "warehouse_id": 1,
  "movement_type": "purchase",
  "quantity": 50,
  "unit_cost": 100.00,
  "reference_number": "PO-2023-001",
  "notes": "Initial stock purchase"
}
```

Movement Types:
- `purchase`: Incoming stock
- `sale`: Outgoing stock (negative quantity)
- `adjustment`: Stock adjustments
- `damaged`: Damaged goods
- `return`: Customer returns
- `transfer_in`: Transfer from another warehouse
- `transfer_out`: Transfer to another warehouse

#### List Stock Movements
```http
GET /api/v1/stock-movements/?page=1&page_size=20
Authorization: Bearer <token>
```

#### Create Stock Transfer
```http
POST /api/v1/stock-transfers/
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": 1,
  "from_warehouse_id": 1,
  "to_warehouse_id": 2,
  "quantity": 10,
  "transfer_reference": "TRANS-001",
  "notes": "Moving to secondary warehouse"
}
```

#### Complete Stock Transfer
```http
PUT /api/v1/stock-transfers/{transfer_id}/complete
Authorization: Bearer <token>
```

#### Cancel Stock Transfer
```http
PUT /api/v1/stock-transfers/{transfer_id}/cancel
Authorization: Bearer <token>
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Categories

- **Unit Tests**: Test individual functions and services
- **Integration Tests**: Test API endpoints end-to-end
- **Authentication Tests**: Test security and JWT functionality

## 🔐 Security Features

1. **Password Security**: Bcrypt hashing with configurable rounds
2. **JWT Authentication**: Secure token-based authentication
3. **Protected Endpoints**: All CRUD operations require authentication
4. **Input Validation**: Pydantic schemas validate all inputs
5. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
6. **CORS Configuration**: Configurable cross-origin resource sharing

## 📈 Scalability Discussion

### Current Architecture Strengths

1. **Microservice-Ready**: Clean separation of concerns with service layer
2. **Database Optimization**: Indexed fields for fast queries
3. **Stateless Authentication**: JWT tokens enable horizontal scaling
4. **Immutable Audit Trail**: Stock movements provide complete history

### Scaling Strategies for Larger Audiences

#### 1. **Database Scaling**

**Read Replicas & Sharding**
- Implement read replicas for query-heavy operations (product searches, reports)
- Shard by warehouse_id or tenant_id for multi-tenant scenarios
- Use connection pooling (pgbouncer) for efficient connection management

```python
# Example read replica configuration
class DatabaseConfig:
    WRITE_DB_URL = "postgresql://..."
    READ_DB_URL = "postgresql://read-replica..."
```

**Caching Layer**
- Redis for frequently accessed data (product details, user sessions)
- Cache product listings and search results with TTL
- Implement cache invalidation strategies

```python
# Example caching implementation
@cached(ttl=300)  # 5-minute cache
def get_product_list(filters):
    return product_service.get_products(filters)
```

#### 2. **Application Scaling**

**Horizontal Scaling**
- Containerize with Docker for easy deployment
- Use Kubernetes for orchestration and auto-scaling
- Implement health checks and graceful shutdowns

```yaml
# Example Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inventory-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: inventory-api
```

**API Gateway & Load Balancing**
- Implement API Gateway (Kong, AWS API Gateway) for:
  - Rate limiting
  - Request routing
  - Authentication offloading
  - API versioning

**Background Job Processing**
- Use Celery + Redis for async tasks:
  - Stock level notifications
  - Report generation
  - Bulk imports/exports
  - Email notifications

```python
# Example background task
@celery.task
def generate_inventory_report(user_id, filters):
    # Generate report asynchronously
    pass
```

#### 3. **Performance Optimizations**

**Database Query Optimization**
- Implement query optimization with eager loading
- Use database-level pagination for large datasets
- Add composite indexes for complex search queries

```python
# Example optimized query
def get_products_optimized(filters):
    return db.query(Product)\
        .options(joinedload(Product.stock_movements))\
        .filter(Product.is_active == True)\
        .order_by(Product.created_at.desc())\
        .offset(offset).limit(limit)
```

**Response Compression & CDN**
- Enable gzip compression for API responses
- Use CDN for static assets and cached responses
- Implement ETags for conditional requests

#### 4. **Monitoring & Observability**

**Application Monitoring**
- Implement structured logging with correlation IDs
- Use APM tools (New Relic, Datadog) for performance monitoring
- Set up alerts for critical metrics (response time, error rate)

**Business Metrics**
- Track inventory turnover rates
- Monitor stock movement patterns
- Alert on low stock levels or unusual activities

```python
# Example monitoring decorator
@monitor_performance
@log_business_event
def create_stock_movement(movement_data):
    # Business logic
    pass
```

### Implementation Priorities

1. **Phase 1**: Caching layer and read replicas
2. **Phase 2**: Containerization and horizontal scaling
3. **Phase 3**: Background job processing
4. **Phase 4**: Advanced monitoring and analytics

This architecture provides a solid foundation for scaling from hundreds to millions of users while maintaining data consistency and audit capabilities.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review the test cases for usage examples
3. Create an issue in the repository

---

**Built with ❤️ using FastAPI and PostgreSQL**