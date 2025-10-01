import os
import sys
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import Base, get_database
from app.core.dependencies import get_current_active_user
from app.core.config import settings
from app.models.models import User, Warehouse, Product
from app.schemas.schemas import User as UserSchema

# Load environment variables
load_dotenv()

# Test database configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

# Create test engine and session
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_database():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def create_test_user() -> UserSchema:
    """Create a test user for authentication"""
    return UserSchema(
        id=1,
        email="test@example.com",
        created_at="2023-01-01T00:00:00",
        is_admin=False
    )

def override_get_current_active_user():
    """Override authentication dependency for testing"""
    return create_test_user()

# Create a minimal FastAPI app for testing (without ML dependencies)
def create_test_app():
    app = FastAPI(
        title="Test Inventory Management API",
        version="1.0.0",
        description="Test API"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include only core API routers without ML dependencies
    from app.api import auth, products, stock_movements, stock_transfers, warehouses, scraped_products
    
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    app.include_router(products.router, prefix=settings.API_V1_STR)
    app.include_router(stock_movements.router, prefix=settings.API_V1_STR)
    app.include_router(stock_transfers.router, prefix=settings.API_V1_STR)
    app.include_router(warehouses.router, prefix=settings.API_V1_STR)
    app.include_router(scraped_products.router, prefix=settings.API_V1_STR)
    
    # Override dependencies
    app.dependency_overrides[get_database] = override_get_database
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    
    return app

# Create the test app
test_app = create_test_app()

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    return test_engine

@pytest.fixture(scope="session")
def tables(engine):
    """Create database tables for testing"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(tables, engine):
    """Create a database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client() -> Generator:
    """Create test client"""
    with TestClient(test_app) as c:
        yield c

@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client"""
    return client

@pytest.fixture
def test_user(db_session):
    """Create a test user in the database"""
    from app.core.security import get_password_hash
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session):
    """Create an admin user in the database"""
    from app.core.security import get_password_hash
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_warehouse(db_session):
    """Create a test warehouse"""
    warehouse = Warehouse(
        name="Test Warehouse",
        location="Test Location",
        description="Test warehouse for testing"
    )
    db_session.add(warehouse)
    db_session.commit()
    db_session.refresh(warehouse)
    return warehouse

@pytest.fixture
def test_product(db_session, test_user):
    """Create a test product"""
    product = Product(
        name="Test Product",
        sku="TEST001",
        description="Test product description",
        unit_price=10.50,
        unit_of_measure="piece",
        category="Test Category",
        created_by=test_user.id
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product

@pytest.fixture
def multiple_warehouses(db_session):
    """Create multiple test warehouses"""
    warehouses = []
    for i in range(3):
        warehouse = Warehouse(
            name=f"Warehouse {i+1}",
            location=f"Location {i+1}",
            description=f"Test warehouse {i+1}"
        )
        db_session.add(warehouse)
        warehouses.append(warehouse)
    
    db_session.commit()
    for warehouse in warehouses:
        db_session.refresh(warehouse)
    return warehouses

@pytest.fixture
def multiple_products(db_session, test_user):
    """Create multiple test products"""
    products = []
    for i in range(5):
        product = Product(
            name=f"Product {i+1}",
            sku=f"TEST00{i+1}",
            description=f"Test product {i+1}",
            unit_price=10.0 + i,
            unit_of_measure="piece",
            category=f"Category {(i % 2) + 1}",
            created_by=test_user.id
        )
        db_session.add(product)
        products.append(product)
    
    db_session.commit()
    for product in products:
        db_session.refresh(product)
    return products