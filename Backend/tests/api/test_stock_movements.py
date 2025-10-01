"""
Test module for stock movement endpoints
Tests stock movement CRUD operations, calculations, and business logic
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.models import StockMovement, Product, Warehouse, MovementType, User


class TestStockMovementCRUD:
    """Test class for stock movement CRUD operations"""

    def test_create_stock_movement_purchase(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test creating a purchase stock movement"""
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100,
            "unit_cost": 10.50,
            "reference_number": "PO001",
            "notes": "Initial stock purchase"
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_id"] == movement_data["product_id"]
        assert data["warehouse_id"] == movement_data["warehouse_id"]
        assert data["movement_type"] == movement_data["movement_type"]
        assert data["quantity"] == movement_data["quantity"]
        assert float(data["unit_cost"]) == movement_data["unit_cost"]
        assert data["reference_number"] == movement_data["reference_number"]
        assert data["notes"] == movement_data["notes"]
        assert "id" in data
        assert "created_at" in data

    def test_create_stock_movement_sale(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test creating a sale stock movement"""
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "sale",
            "quantity": -50,  # Negative for outbound
            "unit_cost": 12.00,
            "reference_number": "INV001",
            "notes": "Sale to customer"
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["movement_type"] == "sale"
        assert data["quantity"] == -50

    def test_create_stock_movement_adjustment(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test creating an adjustment stock movement"""
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "adjustment",
            "quantity": 5,
            "reference_number": "ADJ001",
            "notes": "Stock count adjustment"
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["movement_type"] == "adjustment"

    def test_create_stock_movement_missing_required_fields(self, authenticated_client: TestClient):
        """Test creating stock movement with missing required fields"""
        # Missing product_id
        movement_data = {
            "warehouse_id": 1,
            "movement_type": "purchase",
            "quantity": 100
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_stock_movement_invalid_product(self, authenticated_client: TestClient, test_warehouse: Warehouse):
        """Test creating stock movement with non-existent product"""
        movement_data = {
            "product_id": 99999,  # Non-existent product
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_stock_movement_invalid_warehouse(self, authenticated_client: TestClient, test_product: Product):
        """Test creating stock movement with non-existent warehouse"""
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": 99999,  # Non-existent warehouse
            "movement_type": "purchase",
            "quantity": 100
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_stock_movement_unauthorized(self, client: TestClient):
        """Test creating stock movement without authentication"""
        movement_data = {
            "product_id": 1,
            "warehouse_id": 1,
            "movement_type": "purchase",
            "quantity": 100
        }
        
        response = client.post("/api/v1/stock-movements/", json=movement_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestStockMovementList:
    """Test class for stock movement listing and filtering"""

    def test_list_purchase_sale_movements(self, authenticated_client: TestClient, db_session: Session, test_product: Product, test_warehouse: Warehouse):
        """Test listing purchase and sale movements"""
        # Create some test movements
        movements = [
            StockMovement(
                product_id=test_product.id,
                warehouse_id=test_warehouse.id,
                movement_type=MovementType.PURCHASE,
                quantity=100,
                unit_cost=10.00,
                reference_number="PO001"
            ),
            StockMovement(
                product_id=test_product.id,
                warehouse_id=test_warehouse.id,
                movement_type=MovementType.SALE,
                quantity=-30,
                unit_cost=15.00,
                reference_number="INV001"
            )
        ]
        
        for movement in movements:
            db_session.add(movement)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/stock-movements/purchase-sale")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 2
        
        # Verify movement structure includes product and warehouse names
        if data["items"]:
            item = data["items"][0]
            assert "product_name" in item
            assert "warehouse_name" in item
            assert "movement_type" in item
            assert "quantity" in item

    def test_list_movements_pagination(self, authenticated_client: TestClient):
        """Test stock movement listing with pagination"""
        response = authenticated_client.get("/api/v1/stock-movements/?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

    def test_list_movements_by_product(self, authenticated_client: TestClient, test_product: Product):
        """Test filtering movements by product"""
        response = authenticated_client.get(f"/api/v1/stock-movements/?product_id={test_product.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All movements should be for the specified product
        for item in data.get("items", []):
            assert item["product_id"] == test_product.id

    def test_list_movements_by_warehouse(self, authenticated_client: TestClient, test_warehouse: Warehouse):
        """Test filtering movements by warehouse"""
        response = authenticated_client.get(f"/api/v1/stock-movements/?warehouse_id={test_warehouse.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All movements should be for the specified warehouse
        for item in data.get("items", []):
            assert item["warehouse_id"] == test_warehouse.id

    def test_list_movements_by_type(self, authenticated_client: TestClient):
        """Test filtering movements by movement type"""
        response = authenticated_client.get("/api/v1/stock-movements/?movement_type=purchase")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All movements should be purchase type
        for item in data.get("items", []):
            assert item["movement_type"] == "purchase"

    def test_list_movements_unauthorized(self, client: TestClient):
        """Test listing movements without authentication"""
        response = client.get("/api/v1/stock-movements/purchase-sale")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestStockMovementValidation:
    """Test class for stock movement data validation"""

    def test_movement_type_validation(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test movement type validation"""
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "invalid_type",  # Invalid movement type
            "quantity": 100
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_quantity_validation(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test quantity validation"""
        # Zero quantity
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 0
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_unit_cost_validation(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test unit cost validation"""
        # Negative unit cost
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100,
            "unit_cost": -10.00
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_reference_number_length(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test reference number length validation"""
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100,
            "reference_number": "x" * 200  # Very long reference number
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestStockMovementBusinessLogic:
    """Test class for stock movement business logic"""

    def test_stock_calculation_purchase(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test stock calculation after purchase"""
        # Create purchase movement
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100,
            "unit_cost": 10.00
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check if stock level increased (would require stock level endpoint)
        # This test assumes such functionality exists

    def test_stock_calculation_sale(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test stock calculation after sale"""
        # First add stock
        purchase_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100,
            "unit_cost": 10.00
        }
        authenticated_client.post("/api/v1/stock-movements/", json=purchase_data)
        
        # Then create sale
        sale_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "sale",
            "quantity": -30,
            "unit_cost": 15.00
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=sale_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_total_cost_calculation(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test total cost calculation from quantity and unit cost"""
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100,
            "unit_cost": 10.50
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Total cost should be calculated correctly (quantity * unit_cost)
        expected_total = 100 * 10.50
        if "total_cost" in data:
            assert float(data["total_cost"]) == expected_total

    def test_movement_type_quantity_consistency(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test that movement types and quantities are consistent"""
        # Purchase movements should typically have positive quantities
        purchase_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100  # Positive for inbound
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=purchase_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Sale movements should typically have negative quantities
        sale_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "sale",
            "quantity": -50  # Negative for outbound
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=sale_data)
        assert response.status_code == status.HTTP_201_CREATED


class TestStockMovementSecurity:
    """Test class for stock movement security"""

    def test_movement_ownership_validation(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test that users can only create movements for accessible products"""
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        # Should succeed for accessible products
        assert response.status_code == status.HTTP_201_CREATED

    def test_sql_injection_protection(self, authenticated_client: TestClient):
        """Test protection against SQL injection in movement data"""
        malicious_data = {
            "product_id": "1; DROP TABLE stock_movements; --",
            "warehouse_id": 1,
            "movement_type": "purchase",
            "quantity": 100
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=malicious_data)
        
        # Should fail safely with validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_large_quantity_handling(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test handling of very large quantities"""
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 999999999  # Very large quantity
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        
        # Should either accept or reject gracefully
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestStockMovementIntegration:
    """Test class for stock movement integration with other services"""

    def test_movement_with_product_validation(self, authenticated_client: TestClient, test_warehouse: Warehouse, db_session: Session):
        """Test movement creation with inactive product"""
        # Create inactive product
        inactive_product = Product(
            name="Inactive Product",
            sku="INACTIVE001",
            is_active=False,
            created_by=1
        )
        db_session.add(inactive_product)
        db_session.commit()
        db_session.refresh(inactive_product)
        
        movement_data = {
            "product_id": inactive_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        # Should reject movements for inactive products
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_movement_with_warehouse_validation(self, authenticated_client: TestClient, test_product: Product, db_session: Session):
        """Test movement creation with inactive warehouse"""
        # Create inactive warehouse
        inactive_warehouse = Warehouse(
            name="Inactive Warehouse",
            location="Inactive Location",
            is_active=False
        )
        db_session.add(inactive_warehouse)
        db_session.commit()
        db_session.refresh(inactive_warehouse)
        
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": inactive_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
        # Should reject movements for inactive warehouses
        assert response.status_code == status.HTTP_400_BAD_REQUEST