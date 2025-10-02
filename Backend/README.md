# Inventory Management System API

A comprehensive RESTful API for inventory management built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**. This system provides secure authentication, product management, and stock tracking capabilities with immutable audit trails.

## 🚀 Features

- **🔐 JWT Authentication**: Secure user registration and login
- **📦 Product Management**: Full CRUD operations with pagination and search
- **🏭 Multi-Warehouse Support**: Track inventory across multiple locations
- **📊 Stock Movements**: Immutable ledger for all inventory changes
- **🔄 Stock Transfers**: Move inventory between warehouses
- **🔍 Advanced Search & Filtering**: Search products with date filters and sorting
- **🤖 AI-Powered Recommendations**: Semantic similarity using sentence transformers
- **🕷️ Web Scraping System**: Automated external product data collection
- **📋 Comprehensive API Documentation**: Auto-generated with FastAPI/Swagger
- **🧪 Full Test Suite**: Unit and integration tests with pytest
- **🔒 Security**: Password hashing, JWT tokens, and protected endpoints

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI 0.117+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **AI/ML**: Sentence Transformers (all-MiniLM-L6-v2), scikit-learn, NumPy
- **Web Scraping**: Beautiful Soup, Requests with robots.txt compliance
- **Testing**: pytest with async support
- **API Documentation**: OpenAPI/Swagger (auto-generated)
- **Environment Management**: python-dotenv
- **Database Migrations**: Alembic (ready for future use)

## 📁 Project Structure
```
Backend/                        # Backend FastAPI service
├── app/                        # Application package
│   ├── __init__.py
│   ├── api/                    # HTTP route handlers (endpoints)
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── products.py         # Product CRUD and listing endpoints
│   │   ├── recommendations.py  # Recommendation/search endpoints
│   │   ├── scraped_products.py # Scraped product import endpoints
│   │   ├── stock_movements.py  # Stock movement ledger endpoints
│   │   ├── stock_transfers.py  # Warehouse transfer endpoints
│   │   └── warehouses.py       # Warehouse management endpoints
│   ├── core/                   # Core config, DB and dependencies
│   │   ├── __init__.py
│   │   ├── config.py           # App settings / environment
│   │   ├── database.py         # SQLAlchemy DB setup and session
│   │   ├── dependencies.py     # FastAPI dependency providers
│   │   ├── logger.py           # Structured logging setup
│   │   ├── permissions.py      # Permission checks and decorators
│   │   └── security.py         # JWT, password hashing, auth helpers
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── models.py           # All DB model classes
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── services/               # Business logic layer
│       ├── __init__.py
│       ├── auth_service.py     # User registration/login logic
│       ├── product_service.py  # Product-related business rules
│       ├── recommendation_service.py # Embeddings / similarity logic
│       └── stock_service.py    # Stock movement and transfer logic
├── conftest.py                 # Pytest fixtures for backend tests
├── docker-entrypoint.sh        # Docker container entrypoint script
├── Dockerfile                  # Docker build for backend service
├── main.py                     # FastAPI app entrypoint (uvicorn launcher)
├── README.md                   # This file (backend README)
├── requirements.txt            # Python dependencies
├── run_tests.sh                # Helper script to run tests inside env
├── scripts/                    # Utility scripts (DB setup, scraping, seeding)
│   ├── add_admin_column.py     # DB alter helper
│   ├── create_admin_user.py    # Create admin user script
│   ├── create_databases.py     # Create DBs for dev/test
│   ├── migrate_user_table.py   # Small migration helper
│   ├── scrape_and_store.py     # Scraper that stores product data
│   ├── setup_admin.sh          # Shell helper to bootstrap admin
│   ├── setup_database.py       # Initialize DB schema & seed data
│   └── setup_recommendations.py# Prepare embeddings/ML artifacts
├── data/                       # Non-code data (embeddings, metadata)
│   └── embeddings/
│       ├── price_features.npy
│       ├── product_embeddings.npy
│       └── product_metadata.pkl
├── fail2ban/                   # Security configs for fail2ban
│   ├── filter.d/
│   │   └── fastapi-auth.conf
│   └── jail.d/
│       └── fastapi-auth.conf
├── logs/                       # Runtime logs
│   └── app.log
└── tests/                      # Test suite (unit + integration)
    ├── __init__.py
    ├── conftest.py
    ├── api/                    # API integration tests
    │   ├── __init__.py
    │   ├── conftest.py
    │   ├── test_auth_simple.py
    │   ├── test_auth.py
    │   ├── test_products.py
    │   ├── test_scraped_products.py
    │   ├── test_stock_movements.py
    │   └── test_stock_transfers.py
    ├── models/                 # Model unit tests
    └── services/               # Service/business logic tests
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
#if you went create database using script then run this cmd 
python script/create_databases.py
#then Initialize Database 
python scripts/setup_database.py
```

## 🗄️ Database Schema

Below is the database diagram showing the main tables and relationships used by the application. The image file is located at `images/database.png` in the `Backend` folder.

![Database Schema](/images/database.png)

Key entities:
- `products`: product catalog and attributes
- `warehouses`: storage locations
- `stock_movements`: immutable ledger of inventory changes (purchases, sales, adjustments)
- `stock_transfers`: transfers between warehouses, referencing related movements
- `users`: application users and authentication data

This diagram helps visualize foreign keys and cardinality between tables (for example, each `stock_movement` links to a `product` and a `warehouse`). Use this when reviewing or extending the database schema.

### 7. Run the Application

```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🤖 AI & Scraping Features

### Web Scraping System

The system includes an automated web scraper for external product data collection:

#### Running the Scraper
```bash
# Scrape external products (books.toscrape.com by default)
python scripts/scrape_and_store.py
```

#### Scraper Features
- **Respectful crawling**: Checks and respects robots.txt
- **Rate limiting**: Delays between requests (0.5s default)
- **Duplicate prevention**: Avoids re-scraping existing products
- **Data extraction**: Names, descriptions, categories, prices, ratings, images
- **Error handling**: Graceful handling of network/parsing errors
- **Configurable limits**: Set `SCRAPE_PAGE_LIMIT` environment variable

#### Scraped Data Storage
- Stored in `scrapdata` table separate from user products
- Fields: product_name, product_description, category, price, rating, image_url, product_page_url
- Automatically timestamped with `scraped_at`

### AI-Powered Recommendation System

The recommendation engine provides intelligent product suggestions:

#### Setup AI System
```bash
# Generate embeddings after scraping data
python scripts/setup_recommendations.py
```

#### Recommendation Types

1. **Price-based Recommendations**
   - Find products in similar price ranges
   - Configurable tolerance (±20% default)
   - Uses normalized price features

2. **Category-based Recommendations**
   - Exact category matching
   - Fallback to similar categories if needed

3. **Description-based Recommendations**
   - Semantic similarity using AI embeddings
   - Sentence transformer model (all-MiniLM-L6-v2)
   - Cosine similarity matching

4. **Hybrid Recommendations**
   - Combines all methods with configurable weights
   - Default: 30% price, 30% category, 40% description
   - Customizable via API parameters

#### AI Components

**Embedding Generation**:
- Downloads sentence-transformers model on first run
- Processes product text (title + category + description + price)
- Generates 384-dimensional embeddings
- Caches results as NumPy arrays for performance

**Caching System**:
- `data/embeddings/product_embeddings.npy` - AI embeddings
- `data/embeddings/product_metadata.pkl` - Product metadata
- `data/embeddings/price_features.npy` - Normalized price features
- Automatic cache loading on API startup

**Performance Optimizations**:
- In-memory embedding cache
- Vectorized similarity calculations
- Batch processing for large datasets
- Standardized feature scaling

### Recommendation Diagram

Visual representation of the recommendation pipeline and how price, category, and description embeddings are combined to produce hybrid recommendations:

![Recommendation Diagram](../images/recommendation.drawio.png)


#### API Usage Examples

```bash
# Generate/regenerate embeddings
curl -X POST "http://localhost:8000/recommendations/generate-embeddings"

# Get hybrid recommendations for product ID 1
curl "http://localhost:8000/recommendations/1?recommendation_type=hybrid&limit=10"

# Price-based recommendations with custom tolerance
curl "http://localhost:8000/recommendations/1?recommendation_type=price&price_tolerance=0.3"

# Custom hybrid weights
curl "http://localhost:8000/recommendations/1?recommendation_type=hybrid&price_weight=0.5&category_weight=0.2&description_weight=0.3"
```

## 📚 API Documentation

All API endpoints (except authentication) require authentication via `Authorization: Bearer <token>` header.

### 🔐 Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```
**Response**: User object with id, email, is_admin fields

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```
**Response**: JWT access token and token type

### 📦 Product Management

#### Create Product
```http
POST /products/
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

#### List All Products (Admin/Global View)
```http
GET /products/?page=1&page_size=20&search=laptop&sort_by=name_asc
Authorization: Bearer <token>
```

#### List Owned Products (User's Products Only)
```http
GET /products/owned?page=1&page_size=20&search=laptop&sort_by=name_asc
Authorization: Bearer <token>
```

**Query Parameters for Product Listing**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `sort_by`: `name_asc|name_desc|stock_asc|stock_desc|created_asc|created_desc`
- `search`: Search term for name, SKU, description, or category
- `created_from_date`: Filter from date (ISO format)
- `created_to_date`: Filter to date (ISO format)

#### Get Product Details
```http
GET /products/{product_id}
Authorization: Bearer <token>
```
**Response**: Product details with total stock and warehouse stock distribution

#### Update Product (Owner Only)
```http
PUT /products/{product_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Product Name",
  "sku": "NEW-SKU-001",
  "description": "Updated description",
  "unit_price": 1299.99,
  "unit_of_measure": "piece",
  "category": "Electronics",
  "is_active": true
}
```

#### Delete Product (Owner Only - Soft Delete)
```http
DELETE /products/{product_id}
Authorization: Bearer <token>
```

### 🏭 Warehouse Management

#### List Warehouses
```http
GET /warehouses/
Authorization: Bearer <token>
```
**Response**: List of all active warehouses

#### Get Warehouse Details
```http
GET /warehouses/{warehouse_id}
Authorization: Bearer <token>
```

### 📊 Stock Management

#### Record Stock Movement (Owner Only)
```http
POST /stock-movements/
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

**Movement Types**:
- `purchase`: Incoming stock
- `sale`: Outgoing stock
- `adjustment`: Stock adjustments
- `damaged`: Damaged goods
- `return`: Customer returns
- `transfer_in`: Transfer from another warehouse
- `transfer_out`: Transfer to another warehouse

#### List Stock Movements
```http
GET /stock-movements/?page=1&page_size=20&sort_by=created_desc
Authorization: Bearer <token>
```

#### List Purchase/Sale Movements (Summary)
```http
GET /stock-movements/purchase-sale
Authorization: Bearer <token>
```
**Response**: All purchase and sale movements with product and warehouse names

### 🔄 Stock Transfers

#### Create Stock Transfer (Owner Only)
```http
POST /stock-transfers/
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

#### List Stock Transfers
```http
GET /stock-transfers/?page=1&page_size=20&sort_by=created_desc
Authorization: Bearer <token>
```

#### Complete Stock Transfer (Owner Only)
```http
PUT /stock-transfers/{transfer_id}/complete
Authorization: Bearer <token>
```

### 🛒 Scraped Products (External Data)

#### Search Scraped Products
```http
GET /scraped-products/search?query=laptop
```
**No authentication required** - searches through scraped product data

#### List Scraped Products
```http
GET /scraped-products/?page=1&page_size=50
```
**No authentication required** - paginated list of scraped products

### 🤖 Recommendations & AI

#### Generate Product Embeddings
```http
POST /recommendations/generate-embeddings?force_regenerate=false
```
**Purpose**: Generate ML embeddings for product recommendations

#### Get Recommendations by Product ID
```http
GET /recommendations/{product_id}?recommendation_type=hybrid&limit=10&price_tolerance=0.2
```

**Recommendation Types**:
- `price`: Similar price range products
- `category`: Same category products  
- `description`: AI-based description similarity
- `hybrid`: Combines all methods with weights

**Query Parameters**:
- `recommendation_type`: `price|category|description|hybrid` (default: hybrid)
- `limit`: Max recommendations (1-50, default: 10)
- `price_tolerance`: Price range tolerance (0.1-1.0, default: 0.2)
- `price_weight`: Weight for price scoring in hybrid mode (0.0-1.0, default: 0.3)
- `category_weight`: Weight for category scoring in hybrid mode (0.0-1.0, default: 0.3)
- `description_weight`: Weight for description scoring in hybrid mode (0.0-1.0, default: 0.4)


## 🔐 Security Features

1. **Password Security**: Bcrypt hashing with configurable rounds
2. **JWT Authentication**: Secure token-based authentication
3. **Protected Endpoints**: All CRUD operations require authentication
4. **Input Validation**: Pydantic schemas validate all inputs
5. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
6. **CORS Configuration**: Configurable cross-origin resource sharing

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


## 🆘 Support

For questions or issues:
1. Check the API documentation at `/docs` else `/redoc`
2. Review the test cases for usage examples
3. Create an issue in the repository

---