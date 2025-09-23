import pytest
from app.services.product_service import ProductService
from app.models import Product, User, Warehouse
from app.schemas.schemas import ProductCreate, ProductUpdate, PaginationParams

class TestProductService:
    """Test product service functions"""
    
    def setup_method(self):
        """Set up test data"""
        self.sample_product_data = {
            "name": "Test Product",
            "sku": "TEST-001",
            "description": "A test product",
            "unit_price": 10.50,
            "unit_of_measure": "piece",
            "category": "Test Category"
        }
    
    def test_create_product(self, clean_db):
        """Test product creation"""
        # Create a test user first
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        clean_db.add(user)
        clean_db.commit()
        clean_db.refresh(user)
        
        product_service = ProductService(clean_db)
        product_data = ProductCreate(**self.sample_product_data)
        
        product = product_service.create_product(product_data, user.id)
        
        assert product.name == self.sample_product_data["name"]
        assert product.sku == self.sample_product_data["sku"]
        assert product.created_by == user.id
        assert product.is_active is True
    
    def test_create_duplicate_sku(self, clean_db):
        """Test creating product with duplicate SKU"""
        # Create a test user first
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        clean_db.add(user)
        clean_db.commit()
        clean_db.refresh(user)
        
        product_service = ProductService(clean_db)
        product_data = ProductCreate(**self.sample_product_data)
        
        # Create first product
        product_service.create_product(product_data, user.id)
        
        # Try to create second product with same SKU
        duplicate_data = self.sample_product_data.copy()
        duplicate_data["name"] = "Different Product"
        product_data_dup = ProductCreate(**duplicate_data)
        
        with pytest.raises(ValueError, match="Product with this SKU already exists"):
            product_service.create_product(product_data_dup, user.id)
    
    def test_get_product(self, clean_db):
        """Test getting a product by ID"""
        # Create a test user and product
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        clean_db.add(user)
        clean_db.commit()
        clean_db.refresh(user)
        
        product_service = ProductService(clean_db)
        product_data = ProductCreate(**self.sample_product_data)
        created_product = product_service.create_product(product_data, user.id)
        
        # Get the product
        retrieved_product = product_service.get_product(created_product.id)
        
        assert retrieved_product is not None
        assert retrieved_product.id == created_product.id
        assert retrieved_product.name == self.sample_product_data["name"]
    
    def test_get_nonexistent_product(self, clean_db):
        """Test getting a nonexistent product"""
        product_service = ProductService(clean_db)
        
        result = product_service.get_product(999)
        assert result is None
    
    def test_update_product(self, clean_db):
        """Test updating a product"""
        # Create a test user and product
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        clean_db.add(user)
        clean_db.commit()
        clean_db.refresh(user)
        
        product_service = ProductService(clean_db)
        product_data = ProductCreate(**self.sample_product_data)
        created_product = product_service.create_product(product_data, user.id)
        
        # Update the product
        update_data = ProductUpdate(
            name="Updated Product",
            unit_price=20.00
        )
        
        updated_product = product_service.update_product(created_product.id, update_data)
        
        assert updated_product is not None
        assert updated_product.name == "Updated Product"
        assert updated_product.unit_price == 20.00
        assert updated_product.sku == self.sample_product_data["sku"]  # Should remain unchanged
    
    def test_delete_product(self, clean_db):
        """Test soft deleting a product"""
        # Create a test user and product
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        clean_db.add(user)
        clean_db.commit()
        clean_db.refresh(user)
        
        product_service = ProductService(clean_db)
        product_data = ProductCreate(**self.sample_product_data)
        created_product = product_service.create_product(product_data, user.id)
        
        # Delete the product
        success = product_service.delete_product(created_product.id)
        
        assert success is True
        
        # Verify product is soft deleted
        retrieved_product = product_service.get_product(created_product.id)
        assert retrieved_product is None  # Should not be found since it's inactive
        
        # But should still exist in database with is_active=False
        db_product = clean_db.query(Product).filter(Product.id == created_product.id).first()
        assert db_product is not None
        assert db_product.is_active is False
    
    def test_get_products_pagination(self, clean_db):
        """Test getting products with pagination"""
        # Create a test user and multiple products
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True
        )
        clean_db.add(user)
        clean_db.commit()
        clean_db.refresh(user)
        
        product_service = ProductService(clean_db)
        
        # Create 5 products
        for i in range(5):
            product_data = ProductCreate(
                name=f"Product {i}",
                sku=f"SKU-{i:03d}",
                description=f"Description {i}"
            )
            product_service.create_product(product_data, user.id)
        
        # Test pagination
        params = PaginationParams(page=1, page_size=2)
        products, total = product_service.get_products(params)
        
        assert len(products) == 2
        assert total == 5
        
        # Test second page
        params = PaginationParams(page=2, page_size=2)
        products, total = product_service.get_products(params)
        
        assert len(products) == 2
        assert total == 5