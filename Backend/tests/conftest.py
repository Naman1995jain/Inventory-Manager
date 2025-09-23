import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.core.database import get_database, Base
from app.core.config import settings
import os

# Test database URL
TEST_DATABASE_URL = settings.TEST_DATABASE_URL or settings.DATABASE_URL.replace("inventory_db", "inventory_test_db")

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_database():
    """Override the get_database dependency for testing"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_database] = override_get_database

@pytest.fixture(scope="session")
def setup_test_database():
    """Set up the test database"""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def test_db():
    """Create a database session for testing"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def clean_db(test_db):
    """Clean the database before each test"""
    # Delete all data but keep tables
    for table in reversed(Base.metadata.sorted_tables):
        test_db.execute(table.delete())
    test_db.commit()
    yield test_db

@pytest_asyncio.fixture
async def client():
    """Create an async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }

@pytest.fixture
def sample_product_data():
    """Sample product data for testing"""
    return {
        "name": "Test Product",
        "sku": "TEST-001",
        "description": "A test product",
        "unit_price": 10.50,
        "unit_of_measure": "piece",
        "category": "Test Category"
    }

@pytest.fixture
def sample_warehouse_data():
    """Sample warehouse data for testing"""
    return {
        "name": "Test Warehouse",
        "location": "Test Location",
        "description": "A test warehouse"
    }