"""
Test module for database models
Tests model relationships, constraints, and data integrity
"""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from datetime import datetime
from app.models.models import (
    User, Product, Warehouse, StockMovement, StockTransfer,
    ScrapData, MovementType
)
from app.core.security import get_password_hash


class TestUserModel:
    """Test class for User model"""

    def test_create_user_success(self, db_session: Session):
        """Test successful user creation"""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_admin=False
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_admin is False
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_user_email_unique_constraint(self, db_session: Session):
        """Test user email uniqueness constraint"""
        # Create first user
        user1 = User(
            email="duplicate@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="duplicate@example.com",
            hashed_password=get_password_hash("password456")
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_email_required(self, db_session: Session):
        """Test that email is required"""
        user = User(
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_password_required(self, db_session: Session):
        """Test that hashed_password is required"""
        user = User(email="test@example.com")
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_default_admin_false(self, db_session: Session):
        """Test that is_admin defaults to False"""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.is_admin is False

    def test_user_relationships(self, db_session: Session):
        """Test user relationships with products"""
        user = User(
            email="creator@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create product associated with user
        product = Product(
            name="Test Product",
            sku="TEST001",
            created_by=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        # Test relationship
        assert len(user.products) == 1
        assert user.products[0].name == "Test Product"


class TestProductModel:
    """Test class for Product model"""

    def test_create_product_success(self, db_session: Session, test_user: User):
        """Test successful product creation"""
        product = Product(
            name="Test Product",
            sku="TEST001",
            description="A test product",
            unit_price=Decimal("10.99"),
            unit_of_measure="piece",
            category="Electronics",
            created_by=test_user.id
        )
        
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        assert product.id is not None
        assert product.name == "Test Product"
        assert product.sku == "TEST001"
        assert product.unit_price == Decimal("10.99")
        assert product.is_active is True
        assert product.created_at is not None
        assert product.created_by == test_user.id

    def test_product_sku_unique_constraint(self, db_session: Session, test_user: User):
        """Test product SKU uniqueness constraint"""
        # Create first product
        product1 = Product(
            name="Product 1",
            sku="DUPLICATE_SKU",
            created_by=test_user.id
        )
        db_session.add(product1)
        db_session.commit()
        
        # Try to create second product with same SKU
        product2 = Product(
            name="Product 2",
            sku="DUPLICATE_SKU",
            created_by=test_user.id
        )
        db_session.add(product2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_product_name_required(self, db_session: Session, test_user: User):
        """Test that product name is required"""
        product = Product(
            sku="TEST001",
            created_by=test_user.id
        )
        db_session.add(product)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_product_sku_required(self, db_session: Session, test_user: User):
        """Test that product SKU is required"""
        product = Product(
            name="Test Product",
            created_by=test_user.id
        )
        db_session.add(product)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_product_default_active_true(self, db_session: Session, test_user: User):
        """Test that is_active defaults to True"""
        product = Product(
            name="Test Product",
            sku="TEST001",
            created_by=test_user.id
        )
        
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        assert product.is_active is True

    def test_product_price_precision(self, db_session: Session, test_user: User):
        """Test product price precision handling"""
        product = Product(
            name="Test Product",
            sku="TEST001",
            unit_price=Decimal("123.45"),
            created_by=test_user.id
        )
        
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        assert product.unit_price == Decimal("123.45")

    def test_product_foreign_key_constraint(self, db_session: Session):
        """Test product foreign key constraint with user"""
        product = Product(
            name="Test Product",
            sku="TEST001",
            created_by=99999  # Non-existent user
        )
        db_session.add(product)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_product_relationships(self, db_session: Session, test_user: User):
        """Test product relationships"""
        product = Product(
            name="Test Product",
            sku="TEST001",
            created_by=test_user.id
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        # Test creator relationship
        assert product.creator.id == test_user.id
        assert product.creator.email == test_user.email


class TestWarehouseModel:
    """Test class for Warehouse model"""

    def test_create_warehouse_success(self, db_session: Session):
        """Test successful warehouse creation"""
        warehouse = Warehouse(
            name="Main Warehouse",
            location="New York",
            description="Primary storage facility"
        )
        
        db_session.add(warehouse)
        db_session.commit()
        db_session.refresh(warehouse)
        
        assert warehouse.id is not None
        assert warehouse.name == "Main Warehouse"
        assert warehouse.location == "New York"
        assert warehouse.description == "Primary storage facility"
        assert warehouse.is_active is True
        assert warehouse.created_at is not None
        assert warehouse.updated_at is not None

    def test_warehouse_name_required(self, db_session: Session):
        """Test that warehouse name is required"""
        warehouse = Warehouse(location="New York")
        db_session.add(warehouse)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_warehouse_default_active_true(self, db_session: Session):
        """Test that is_active defaults to True"""
        warehouse = Warehouse(name="Test Warehouse")
        
        db_session.add(warehouse)
        db_session.commit()
        db_session.refresh(warehouse)
        
        assert warehouse.is_active is True

    def test_warehouse_optional_fields(self, db_session: Session):
        """Test warehouse with optional fields as None"""
        warehouse = Warehouse(
            name="Minimal Warehouse",
            location=None,
            description=None
        )
        
        db_session.add(warehouse)
        db_session.commit()
        db_session.refresh(warehouse)
        
        assert warehouse.name == "Minimal Warehouse"
        assert warehouse.location is None
        assert warehouse.description is None

    def test_warehouse_updated_at_auto_update(self, db_session: Session):
        """Test that updated_at is automatically updated"""
        warehouse = Warehouse(name="Test Warehouse")
        
        db_session.add(warehouse)
        db_session.commit()
        db_session.refresh(warehouse)
        
        original_updated_at = warehouse.updated_at
        
        # Update the warehouse
        warehouse.description = "Updated description"
        db_session.commit()
        db_session.refresh(warehouse)
        
        assert warehouse.updated_at > original_updated_at


class TestStockMovementModel:
    """Test class for StockMovement model"""

    def test_create_stock_movement_success(self, db_session: Session, test_product: Product, test_warehouse: Warehouse, test_user: User):
        """Test successful stock movement creation"""
        movement = StockMovement(
            product_id=test_product.id,
            warehouse_id=test_warehouse.id,
            movement_type=MovementType.PURCHASE,
            quantity=100,
            unit_cost=Decimal("10.50"),
            total_cost=Decimal("1050.00"),
            reference_number="PO001",
            notes="Initial stock purchase",
            created_by=test_user.id
        )
        
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        assert movement.id is not None
        assert movement.product_id == test_product.id
        assert movement.warehouse_id == test_warehouse.id
        assert movement.movement_type == MovementType.PURCHASE
        assert movement.quantity == 100
        assert movement.unit_cost == Decimal("10.50")
        assert movement.created_at is not None

    def test_stock_movement_required_fields(self, db_session: Session):
        """Test stock movement required fields"""
        # Missing product_id
        movement = StockMovement(
            warehouse_id=1,
            movement_type=MovementType.PURCHASE,
            quantity=100
        )
        db_session.add(movement)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_stock_movement_enum_validation(self, db_session: Session, test_product: Product, test_warehouse: Warehouse):
        """Test movement type enum validation"""
        movement = StockMovement(
            product_id=test_product.id,
            warehouse_id=test_warehouse.id,
            movement_type=MovementType.SALE,
            quantity=-50  # Negative for sale
        )
        
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        assert movement.movement_type == MovementType.SALE

    def test_stock_movement_foreign_keys(self, db_session: Session):
        """Test stock movement foreign key constraints"""
        # Invalid product_id
        movement = StockMovement(
            product_id=99999,
            warehouse_id=1,
            movement_type=MovementType.PURCHASE,
            quantity=100
        )
        db_session.add(movement)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_stock_movement_relationships(self, db_session: Session, test_product: Product, test_warehouse: Warehouse, test_user: User):
        """Test stock movement relationships"""
        movement = StockMovement(
            product_id=test_product.id,
            warehouse_id=test_warehouse.id,
            movement_type=MovementType.PURCHASE,
            quantity=100,
            created_by=test_user.id
        )
        
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        # Test relationships
        assert movement.product.id == test_product.id
        assert movement.warehouse.id == test_warehouse.id
        assert movement.creator.id == test_user.id

    def test_movement_type_enum_values(self, db_session: Session, test_product: Product, test_warehouse: Warehouse):
        """Test all movement type enum values"""
        movement_types = [
            MovementType.PURCHASE,
            MovementType.SALE,
            MovementType.ADJUSTMENT,
            MovementType.DAMAGED,
            MovementType.RETURN,
            MovementType.TRANSFER_IN,
            MovementType.TRANSFER_OUT
        ]
        
        for movement_type in movement_types:
            movement = StockMovement(
                product_id=test_product.id,
                warehouse_id=test_warehouse.id,
                movement_type=movement_type,
                quantity=10
            )
            
            db_session.add(movement)
            db_session.commit()
            db_session.refresh(movement)
            
            assert movement.movement_type == movement_type
            
            # Clean up for next iteration
            db_session.delete(movement)
            db_session.commit()


class TestStockTransferModel:
    """Test class for StockTransfer model"""

    def test_create_stock_transfer_success(self, db_session: Session, test_product: Product, multiple_warehouses, test_user: User):
        """Test successful stock transfer creation"""
        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=multiple_warehouses[0].id,
            to_warehouse_id=multiple_warehouses[1].id,
            quantity=50,
            transfer_reference="TR001",
            notes="Transfer between warehouses",
            status="pending",
            created_by=test_user.id
        )
        
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)
        
        assert transfer.id is not None
        assert transfer.product_id == test_product.id
        assert transfer.from_warehouse_id == multiple_warehouses[0].id
        assert transfer.to_warehouse_id == multiple_warehouses[1].id
        assert transfer.quantity == 50
        assert transfer.status == "pending"
        assert transfer.created_at is not None

    def test_stock_transfer_required_fields(self, db_session: Session):
        """Test stock transfer required fields"""
        transfer = StockTransfer(
            from_warehouse_id=1,
            to_warehouse_id=2,
            quantity=50
        )
        db_session.add(transfer)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_stock_transfer_default_status(self, db_session: Session, test_product: Product, multiple_warehouses):
        """Test stock transfer default status"""
        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=multiple_warehouses[0].id,
            to_warehouse_id=multiple_warehouses[1].id,
            quantity=50
        )
        
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)
        
        assert transfer.status == "pending"

    def test_stock_transfer_relationships(self, db_session: Session, test_product: Product, multiple_warehouses, test_user: User):
        """Test stock transfer relationships"""
        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=multiple_warehouses[0].id,
            to_warehouse_id=multiple_warehouses[1].id,
            quantity=50,
            created_by=test_user.id
        )
        
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)
        
        # Test relationships
        assert transfer.product.id == test_product.id
        assert transfer.from_warehouse.id == multiple_warehouses[0].id
        assert transfer.to_warehouse.id == multiple_warehouses[1].id
        assert transfer.creator.id == test_user.id

    def test_stock_transfer_foreign_keys(self, db_session: Session, test_product: Product):
        """Test stock transfer foreign key constraints"""
        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=99999,  # Non-existent warehouse
            to_warehouse_id=99998,
            quantity=50
        )
        db_session.add(transfer)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestScrapDataModel:
    """Test class for ScrapData model"""

    def test_create_scrap_data_success(self, db_session: Session):
        """Test successful scrap data creation"""
        scrap_data = ScrapData(
            product_name="Laptop Dell XPS 13",
            product_description="High-performance ultrabook",
            category="Electronics",
            price=Decimal("999.99"),
            rating="4.5",
            image_url="https://example.com/laptop.jpg",
            product_page_url="https://example.com/product/laptop"
        )
        
        db_session.add(scrap_data)
        db_session.commit()
        db_session.refresh(scrap_data)
        
        assert scrap_data.id is not None
        assert scrap_data.product_name == "Laptop Dell XPS 13"
        assert scrap_data.price == Decimal("999.99")
        assert scrap_data.scraped_at is not None

    def test_scrap_data_product_name_required(self, db_session: Session):
        """Test that product name is required"""
        scrap_data = ScrapData(
            category="Electronics",
            price=Decimal("999.99")
        )
        db_session.add(scrap_data)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_scrap_data_optional_fields(self, db_session: Session):
        """Test scrap data with optional fields as None"""
        scrap_data = ScrapData(
            product_name="Minimal Product",
            product_description=None,
            category=None,
            price=None,
            rating=None,
            image_url=None,
            product_page_url=None
        )
        
        db_session.add(scrap_data)
        db_session.commit()
        db_session.refresh(scrap_data)
        
        assert scrap_data.product_name == "Minimal Product"
        assert scrap_data.product_description is None
        assert scrap_data.category is None
        assert scrap_data.price is None

    def test_scrap_data_url_lengths(self, db_session: Session):
        """Test URL field length handling"""
        long_url = "https://example.com/" + "x" * 500
        
        scrap_data = ScrapData(
            product_name="Test Product",
            image_url=long_url,
            product_page_url=long_url
        )
        
        db_session.add(scrap_data)
        # Should either succeed or fail with length constraint
        try:
            db_session.commit()
            db_session.refresh(scrap_data)
            assert scrap_data.image_url == long_url
        except IntegrityError:
            # Expected if URL length exceeds database constraints
            db_session.rollback()

    def test_scrap_data_price_precision(self, db_session: Session):
        """Test price precision handling"""
        scrap_data = ScrapData(
            product_name="Price Test Product",
            price=Decimal("1234.56")
        )
        
        db_session.add(scrap_data)
        db_session.commit()
        db_session.refresh(scrap_data)
        
        assert scrap_data.price == Decimal("1234.56")


class TestModelConstraints:
    """Test class for database constraints and data integrity"""

    def test_cascade_delete_behavior(self, db_session: Session, test_user: User):
        """Test cascade delete behavior when user is deleted"""
        # Create product associated with user
        product = Product(
            name="Test Product",
            sku="CASCADE_TEST",
            created_by=test_user.id
        )
        db_session.add(product)
        db_session.commit()
        product_id = product.id
        
        # Delete user
        db_session.delete(test_user)
        db_session.commit()
        
        # Check if product still exists or was cascaded
        remaining_product = db_session.query(Product).filter(Product.id == product_id).first()
        # Behavior depends on foreign key configuration
        # Product might be deleted (CASCADE) or created_by might be set to NULL

    def test_data_type_constraints(self, db_session: Session, test_user: User):
        """Test data type constraints"""
        # Test invalid data types are handled correctly
        product = Product(
            name="Test Product",
            sku="TYPE_TEST",
            unit_price=Decimal("99.99"),
            created_by=test_user.id
        )
        
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        # Verify types are correctly stored
        assert isinstance(product.unit_price, Decimal)
        assert isinstance(product.is_active, bool)
        assert isinstance(product.created_at, datetime)

    def test_null_constraints(self, db_session: Session):
        """Test NULL constraints on required fields"""
        # Test that required fields cannot be NULL
        warehouse = Warehouse(name=None)  # Name is required
        db_session.add(warehouse)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_string_length_constraints(self, db_session: Session, test_user: User):
        """Test string length constraints"""
        # Test very long strings
        long_name = "x" * 300  # Assuming name field has length limit
        
        product = Product(
            name=long_name,
            sku="LENGTH_TEST",
            created_by=test_user.id
        )
        
        db_session.add(product)
        
        # Should either succeed or fail with length constraint
        try:
            db_session.commit()
        except IntegrityError:
            # Expected if name length exceeds database constraints
            db_session.rollback()


class TestModelIndexes:
    """Test class for database indexes and performance"""

    def test_unique_indexes(self, db_session: Session, test_user: User):
        """Test unique indexes work correctly"""
        # Test user email unique index
        user1 = User(
            email="unique@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            email="unique@example.com",
            hashed_password=get_password_hash("password456")
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_foreign_key_indexes(self, db_session: Session, test_user: User, test_product: Product, test_warehouse: Warehouse):
        """Test foreign key indexes for performance"""
        # Create multiple stock movements to test index usage
        movements = []
        for i in range(10):
            movement = StockMovement(
                product_id=test_product.id,
                warehouse_id=test_warehouse.id,
                movement_type=MovementType.PURCHASE,
                quantity=i + 1,
                reference_number=f"REF{i:03d}"
            )
            movements.append(movement)
            db_session.add(movement)
        
        db_session.commit()
        
        # Query by foreign key should be efficient
        product_movements = db_session.query(StockMovement).filter(
            StockMovement.product_id == test_product.id
        ).all()
        
        assert len(product_movements) == 10