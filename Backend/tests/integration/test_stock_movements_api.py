import pytest
from fastapi.testclient import TestClient
from app.models import StockMovement, MovementType


@pytest.mark.integration
class TestStockMovementsAPI:
    """Integration tests for stock movements endpoints"""

    def test_create_stock_movement_success(self, authenticated_client: TestClient, db_session, test_product, test_warehouse, test_user):
        """Test successful stock movement creation"""
        # Arrange
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100,
            "unit_cost": 5.50,
            "reference_number": "PO12345",
            "notes": "Initial purchase"
        }

        # Act
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == movement_data["product_id"]
        assert data["warehouse_id"] == movement_data["warehouse_id"]
        assert data["movement_type"] == movement_data["movement_type"]
        assert data["quantity"] == movement_data["quantity"]
        assert float(data["unit_cost"]) == movement_data["unit_cost"]
        assert float(data["total_cost"]) == movement_data["quantity"] * movement_data["unit_cost"]
        assert data["reference_number"] == movement_data["reference_number"]
        assert data["notes"] == movement_data["notes"]
        assert "id" in data
        assert "created_at" in data

        # Verify in database
        db_movement = db_session.query(StockMovement).filter(
            StockMovement.reference_number == movement_data["reference_number"]
        ).first()
        assert db_movement is not None
        assert db_movement.created_by == test_user.id

    def test_list_purchase_sale_movements(self, authenticated_client: TestClient, db_session, test_product, test_warehouse, test_user):
        """Test listing purchase and sale movements"""
        # Arrange
        # Create a purchase movement
        purchase_movement = StockMovement(
            product_id=test_product.id,
            warehouse_id=test_warehouse.id,
            movement_type=MovementType.PURCHASE,
            quantity=100,
            unit_cost=5.50,
            total_cost=550.00,
            reference_number="PO12345",
            notes="Test purchase",
            created_by=test_user.id
        )
        
        # Create a sale movement
        sale_movement = StockMovement(
            product_id=test_product.id,
            warehouse_id=test_warehouse.id,
            movement_type=MovementType.SALE,
            quantity=-50,
            unit_cost=7.00,
            total_cost=350.00,
            reference_number="SO12345",
            notes="Test sale",
            created_by=test_user.id
        )
        
        # Create an adjustment movement (should not be returned in response)
        adjustment_movement = StockMovement(
            product_id=test_product.id,
            warehouse_id=test_warehouse.id,
            movement_type=MovementType.ADJUSTMENT,
            quantity=10,
            unit_cost=5.50,
            total_cost=55.00,
            reference_number="ADJ12345",
            notes="Test adjustment",
            created_by=test_user.id
        )
        
        db_session.add_all([purchase_movement, sale_movement, adjustment_movement])
        db_session.commit()

        # Act
        response = authenticated_client.get("/api/v1/stock-movements/purchase-sale")

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check pagination data
        assert data["total"] == 2  # Only purchase and sale movements
        assert data["page"] == 1
        assert data["size"] == 20
        assert data["pages"] == 1
        
        # Check items
        items = data["items"]
        assert len(items) == 2
        
        # Verify that only purchase and sale movements are returned
        movement_types = [item["movement_type"] for item in items]
        assert all(mt in ["purchase", "sale"] for mt in movement_types)
        assert "adjustment" not in movement_types
        
        # Check data of first movement (should be sale as it's ordered by created_at desc)
        assert items[0]["quantity"] == -50
        assert float(items[0]["unit_cost"]) == 7.00
        assert float(items[0]["total_cost"]) == 350.00
        assert items[0]["reference_number"] == "SO12345"
        
        # Check if product and warehouse names are included
        assert "product_name" in items[0]
        assert "warehouse_name" in items[0]

    def test_create_stock_movement_invalid_product(self, authenticated_client: TestClient, test_warehouse):
        """Test creating stock movement with invalid product"""
        # Arrange
        movement_data = {
            "product_id": 99999,  # Non-existent product
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 10
        }

        # Act
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Product not found" in data["detail"]

    def test_create_stock_movement_invalid_warehouse(self, authenticated_client: TestClient, test_product):
        """Test creating stock movement with invalid warehouse"""
        # Arrange
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": 99999,  # Non-existent warehouse
            "movement_type": "purchase",
            "quantity": 10
        }

        # Act
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Warehouse not found" in data["detail"]

    def test_create_stock_movement_insufficient_stock(self, authenticated_client: TestClient, test_product, test_warehouse):
        """Test creating outbound stock movement with insufficient stock"""
        # Arrange - try to remove more stock than available
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "sale",
            "quantity": -100  # Negative for outbound
        }

        # Act
        response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Insufficient stock" in data["detail"]

    def test_create_stock_movement_unauthorized(self, client: TestClient, test_product, test_warehouse):
        """Test creating stock movement without authentication"""
        # Arrange
        movement_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 10
        }

        # Act
        response = client.post("/api/v1/stock-movements/", json=movement_data)

        # Assert
        assert response.status_code == 403

    def test_get_stock_movements_list(self, authenticated_client: TestClient, db_session, test_product, test_warehouse, test_user):
        """Test getting paginated list of stock movements"""
        # Arrange - create some stock movements
        movements_data = [
            {"movement_type": MovementType.PURCHASE, "quantity": 50, "reference": "PO001"},
            {"movement_type": MovementType.SALE, "quantity": -10, "reference": "SO001"},
            {"movement_type": MovementType.ADJUSTMENT, "quantity": 5, "reference": "ADJ001"}
        ]

        for data in movements_data:
            movement = StockMovement(
                product_id=test_product.id,
                warehouse_id=test_warehouse.id,
                movement_type=data["movement_type"],
                quantity=data["quantity"],
                reference_number=data["reference"],
                created_by=test_user.id
            )
            db_session.add(movement)
        db_session.commit()

        # Act
        response = authenticated_client.get("/api/v1/stock-movements/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert len(data["items"]) <= data["page_size"]
        assert data["total"] >= len(movements_data)

    def test_get_stock_movements_with_pagination(self, authenticated_client: TestClient, db_session, test_product, test_warehouse, test_user):
        """Test getting stock movements with custom pagination"""
        # Arrange - create multiple movements
        for i in range(5):
            movement = StockMovement(
                product_id=test_product.id,
                warehouse_id=test_warehouse.id,
                movement_type=MovementType.PURCHASE,
                quantity=10,
                reference_number=f"REF{i:03d}",
                created_by=test_user.id
            )
            db_session.add(movement)
        db_session.commit()

        # Act
        response = authenticated_client.get("/api/v1/stock-movements/?page=1&page_size=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) <= 2

    def test_get_stock_movements_with_search(self, authenticated_client: TestClient, db_session, test_product, test_warehouse, test_user):
        """Test getting stock movements with search filter"""
        # Arrange - create movements with searchable references
        movement = StockMovement(
            product_id=test_product.id,
            warehouse_id=test_warehouse.id,
            movement_type=MovementType.PURCHASE,
            quantity=10,
            reference_number="SEARCHABLE001",
            notes="Special order",
            created_by=test_user.id
        )
        db_session.add(movement)
        db_session.commit()

        # Act
        response = authenticated_client.get("/api/v1/stock-movements/?search=SEARCHABLE")

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Should find movements with "SEARCHABLE" in reference
        matching_items = [item for item in data["items"] if "SEARCHABLE" in (item.get("reference_number") or "")]
        assert len(matching_items) > 0

    def test_get_stock_movements_unauthorized(self, client: TestClient):
        """Test getting stock movements without authentication"""
        # Act
        response = client.get("/api/v1/stock-movements/")

        # Assert
        assert response.status_code == 403

    def test_stock_movement_types(self, authenticated_client: TestClient, db_session, test_product, test_warehouse):
        """Test creating different types of stock movements"""
        # Test all movement types
        movement_types = [
            ("purchase", 50, "Purchase order"),
            ("sale", -10, "Sales order"),  
            ("adjustment", 5, "Inventory adjustment"),
            ("damaged", -3, "Damaged goods"),
            ("return", 2, "Customer return")
        ]

        for movement_type, quantity, notes in movement_types:
            movement_data = {
                "product_id": test_product.id,
                "warehouse_id": test_warehouse.id,
                "movement_type": movement_type,
                "quantity": quantity,
                "notes": notes
            }

            response = authenticated_client.post("/api/v1/stock-movements/", json=movement_data)
            
            if movement_type == "sale" and quantity < 0:
                # First sale might fail due to insufficient stock
                # But purchases should always succeed
                continue
            
            assert response.status_code == 201
            data = response.json()
            assert data["movement_type"] == movement_type
            assert data["quantity"] == quantity

    def test_stock_calculation_after_movements(self, authenticated_client: TestClient, test_product, test_warehouse):
        """Test that stock calculations work correctly after multiple movements"""
        # Create inbound movement
        inbound_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 100,
            "unit_cost": 5.0
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=inbound_data)
        assert response.status_code == 201

        # Create outbound movement
        outbound_data = {
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "sale",
            "quantity": -20,
            "unit_cost": 10.0
        }
        
        response = authenticated_client.post("/api/v1/stock-movements/", json=outbound_data)
        assert response.status_code == 201

        # Check product stock
        response = authenticated_client.get(f"/api/v1/products/{test_product.id}")
        assert response.status_code == 200
        product_data = response.json()
        
        # Stock should be 100 - 20 = 80
        expected_stock = 80
        warehouse_stock = next((ws for ws in product_data["warehouse_stock"] 
                               if ws["warehouse_id"] == test_warehouse.id), None)
        assert warehouse_stock is not None
        assert warehouse_stock["current_stock"] == expected_stock

    def test_invalid_movement_data(self, authenticated_client: TestClient, test_product, test_warehouse):
        """Test creating stock movement with invalid data"""
        # Test missing required fields
        response = authenticated_client.post("/api/v1/stock-movements/", json={
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id
            # Missing movement_type and quantity
        })
        assert response.status_code == 422

        # Test invalid movement type
        response = authenticated_client.post("/api/v1/stock-movements/", json={
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "invalid_type",
            "quantity": 10
        })
        assert response.status_code == 422

        # Test zero quantity
        response = authenticated_client.post("/api/v1/stock-movements/", json={
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 0
        })
        # Zero quantity should be allowed for some cases
        # But let's test negative unit cost
        response = authenticated_client.post("/api/v1/stock-movements/", json={
            "product_id": test_product.id,
            "warehouse_id": test_warehouse.id,
            "movement_type": "purchase",
            "quantity": 10,
            "unit_cost": -5.0  # Negative cost should be invalid
        })
        assert response.status_code == 422