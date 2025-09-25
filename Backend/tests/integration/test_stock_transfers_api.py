import pytest
from fastapi.testclient import TestClient
from app.models import StockTransfer, StockMovement, MovementType


@pytest.mark.integration
class TestStockTransfersAPI:
    """Integration tests for stock transfers endpoints"""

    def setup_initial_stock(self, db_session, product_id, warehouse_id, quantity, user_id):
        """Helper method to set up initial stock in warehouse"""
        initial_movement = StockMovement(
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=MovementType.PURCHASE,
            quantity=quantity,
            reference_number="INITIAL_STOCK",
            created_by=user_id
        )
        db_session.add(initial_movement)
        db_session.commit()

    def test_create_stock_transfer_success(self, authenticated_client: TestClient, db_session, test_product, multiple_warehouses, test_user):
        """Test successful stock transfer creation"""
        # Arrange
        from_warehouse = multiple_warehouses[0]
        to_warehouse = multiple_warehouses[1]
        
        # Set up initial stock in source warehouse
        self.setup_initial_stock(db_session, test_product.id, from_warehouse.id, 100, test_user.id)

        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": from_warehouse.id,
            "to_warehouse_id": to_warehouse.id,
            "quantity": 25,
            "transfer_reference": "TRANS001",
            "notes": "Transfer for distribution"
        }

        # Act
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == transfer_data["product_id"]
        assert data["from_warehouse_id"] == transfer_data["from_warehouse_id"]
        assert data["to_warehouse_id"] == transfer_data["to_warehouse_id"]
        assert data["quantity"] == transfer_data["quantity"]
        assert data["transfer_reference"] == transfer_data["transfer_reference"]
        assert data["notes"] == transfer_data["notes"]
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

        # Verify in database
        db_transfer = db_session.query(StockTransfer).filter(
            StockTransfer.transfer_reference == transfer_data["transfer_reference"]
        ).first()
        assert db_transfer is not None
        assert db_transfer.created_by == test_user.id

    def test_create_stock_transfer_same_warehouse(self, authenticated_client: TestClient, test_product, test_warehouse):
        """Test creating stock transfer with same source and destination"""
        # Arrange
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": test_warehouse.id,
            "to_warehouse_id": test_warehouse.id,  # Same warehouse
            "quantity": 10
        }

        # Act
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Source and destination warehouses must be different" in data["detail"]

    def test_create_stock_transfer_insufficient_stock(self, authenticated_client: TestClient, test_product, multiple_warehouses):
        """Test creating stock transfer with insufficient stock"""
        # Arrange
        from_warehouse = multiple_warehouses[0]
        to_warehouse = multiple_warehouses[1]

        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": from_warehouse.id,
            "to_warehouse_id": to_warehouse.id,
            "quantity": 1000  # More than available
        }

        # Act
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Insufficient stock" in data["detail"]

    def test_create_stock_transfer_invalid_product(self, authenticated_client: TestClient, multiple_warehouses):
        """Test creating stock transfer with invalid product"""
        # Arrange
        transfer_data = {
            "product_id": 99999,  # Non-existent product
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 10
        }

        # Act
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Product not found" in data["detail"]

    def test_create_stock_transfer_invalid_warehouse(self, authenticated_client: TestClient, test_product, test_warehouse):
        """Test creating stock transfer with invalid warehouse"""
        # Arrange - invalid destination warehouse
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": test_warehouse.id,
            "to_warehouse_id": 99999,  # Non-existent warehouse
            "quantity": 10
        }

        # Act
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Destination warehouse not found" in data["detail"]

    def test_create_stock_transfer_unauthorized(self, client: TestClient, test_product, multiple_warehouses):
        """Test creating stock transfer without authentication"""
        # Arrange
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 10
        }

        # Act
        response = client.post("/api/v1/stock-transfers/", json=transfer_data)

        # Assert
        assert response.status_code == 403

    def test_get_stock_transfers_list(self, authenticated_client: TestClient, db_session, test_product, multiple_warehouses, test_user):
        """Test getting paginated list of stock transfers"""
        # Arrange - create some stock transfers
        from_warehouse = multiple_warehouses[0]
        to_warehouse = multiple_warehouses[1]
        
        # Set up initial stock
        self.setup_initial_stock(db_session, test_product.id, from_warehouse.id, 200, test_user.id)

        transfers_data = [
            {"quantity": 20, "reference": "TRANS001", "notes": "First transfer"},
            {"quantity": 15, "reference": "TRANS002", "notes": "Second transfer"},
            {"quantity": 10, "reference": "TRANS003", "notes": "Third transfer"}
        ]

        for data in transfers_data:
            transfer = StockTransfer(
                product_id=test_product.id,
                from_warehouse_id=from_warehouse.id,
                to_warehouse_id=to_warehouse.id,
                quantity=data["quantity"],
                transfer_reference=data["reference"],
                notes=data["notes"],
                status="pending",
                created_by=test_user.id
            )
            db_session.add(transfer)
        db_session.commit()

        # Act
        response = authenticated_client.get("/api/v1/stock-transfers/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert len(data["items"]) <= data["page_size"]
        assert data["total"] >= len(transfers_data)

    def test_get_stock_transfers_with_search(self, authenticated_client: TestClient, db_session, test_product, multiple_warehouses, test_user):
        """Test getting stock transfers with search filter"""
        # Arrange - create transfer with searchable reference
        from_warehouse = multiple_warehouses[0]
        to_warehouse = multiple_warehouses[1]
        
        self.setup_initial_stock(db_session, test_product.id, from_warehouse.id, 100, test_user.id)

        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=from_warehouse.id,
            to_warehouse_id=to_warehouse.id,
            quantity=10,
            transfer_reference="SEARCHABLE_TRANSFER",
            notes="Special transfer",
            status="pending",
            created_by=test_user.id
        )
        db_session.add(transfer)
        db_session.commit()

        # Act
        response = authenticated_client.get("/api/v1/stock-transfers/?search=SEARCHABLE")

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Should find transfers with "SEARCHABLE" in reference
        matching_items = [item for item in data["items"] if "SEARCHABLE" in (item.get("transfer_reference") or "")]
        assert len(matching_items) > 0

    def test_get_stock_transfers_unauthorized(self, client: TestClient):
        """Test getting stock transfers without authentication"""
        # Act
        response = client.get("/api/v1/stock-transfers/")

        # Assert
        assert response.status_code == 403

    def test_get_stock_transfer_by_id(self, authenticated_client: TestClient, db_session, test_product, multiple_warehouses, test_user):
        """Test getting specific stock transfer by ID"""
        # Arrange - create a stock transfer
        from_warehouse = multiple_warehouses[0]
        to_warehouse = multiple_warehouses[1]
        
        self.setup_initial_stock(db_session, test_product.id, from_warehouse.id, 50, test_user.id)

        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=from_warehouse.id,
            to_warehouse_id=to_warehouse.id,
            quantity=10,
            transfer_reference="GET_TEST",
            status="pending",
            created_by=test_user.id
        )
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)

        # Act
        response = authenticated_client.get(f"/api/v1/stock-transfers/{transfer.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transfer.id
        assert data["product_id"] == test_product.id
        assert data["from_warehouse_id"] == from_warehouse.id
        assert data["to_warehouse_id"] == to_warehouse.id
        assert data["quantity"] == 10
        assert data["status"] == "pending"

    def test_update_stock_transfer_complete(self, authenticated_client: TestClient, db_session, test_product, multiple_warehouses, test_user):
        """Test completing a stock transfer"""
        # Arrange - create pending transfer
        from_warehouse = multiple_warehouses[0]
        to_warehouse = multiple_warehouses[1]
        
        self.setup_initial_stock(db_session, test_product.id, from_warehouse.id, 100, test_user.id)

        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=from_warehouse.id,
            to_warehouse_id=to_warehouse.id,
            quantity=25,
            transfer_reference="COMPLETE_TEST",
            status="pending",
            created_by=test_user.id
        )
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)

        update_data = {
            "status": "completed"
        }

        # Act
        response = authenticated_client.put(f"/api/v1/stock-transfers/{transfer.id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

        # Verify stock movements were created
        movements = db_session.query(StockMovement).filter(
            StockMovement.reference_number == f"TRANSFER-{transfer.id}"
        ).all()
        assert len(movements) == 2  # One outbound, one inbound

        # Check outbound movement
        outbound = next((m for m in movements if m.quantity < 0), None)
        assert outbound is not None
        assert outbound.warehouse_id == from_warehouse.id
        assert outbound.quantity == -25

        # Check inbound movement
        inbound = next((m for m in movements if m.quantity > 0), None)
        assert inbound is not None
        assert inbound.warehouse_id == to_warehouse.id
        assert inbound.quantity == 25

    def test_update_stock_transfer_cancel(self, authenticated_client: TestClient, db_session, test_product, multiple_warehouses, test_user):
        """Test cancelling a stock transfer"""
        # Arrange - create pending transfer
        from_warehouse = multiple_warehouses[0]
        to_warehouse = multiple_warehouses[1]

        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=from_warehouse.id,
            to_warehouse_id=to_warehouse.id,
            quantity=10,
            transfer_reference="CANCEL_TEST",
            status="pending",
            created_by=test_user.id
        )
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)

        update_data = {
            "status": "cancelled"
        }

        # Act
        response = authenticated_client.put(f"/api/v1/stock-transfers/{transfer.id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

        # Verify no stock movements were created
        movements = db_session.query(StockMovement).filter(
            StockMovement.reference_number == f"TRANSFER-{transfer.id}"
        ).all()
        assert len(movements) == 0

    def test_update_stock_transfer_not_found(self, authenticated_client: TestClient):
        """Test updating non-existent stock transfer"""
        # Arrange
        update_data = {"status": "completed"}

        # Act
        response = authenticated_client.put("/api/v1/stock-transfers/99999", json=update_data)

        # Assert
        assert response.status_code == 404

    def test_update_stock_transfer_invalid_status(self, authenticated_client: TestClient, db_session, test_product, multiple_warehouses, test_user):
        """Test updating stock transfer with invalid status"""
        # Arrange - create pending transfer
        from_warehouse = multiple_warehouses[0]
        to_warehouse = multiple_warehouses[1]

        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=from_warehouse.id,
            to_warehouse_id=to_warehouse.id,
            quantity=10,
            status="pending",
            created_by=test_user.id
        )
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)

        update_data = {
            "status": "invalid_status"
        }

        # Act
        response = authenticated_client.put(f"/api/v1/stock-transfers/{transfer.id}", json=update_data)

        # Assert
        assert response.status_code == 422

    def test_stock_transfer_lifecycle(self, authenticated_client: TestClient, db_session, test_product, multiple_warehouses, test_user):
        """Test complete stock transfer lifecycle"""
        # Arrange
        from_warehouse = multiple_warehouses[0]
        to_warehouse = multiple_warehouses[1]
        
        # Set up initial stock
        self.setup_initial_stock(db_session, test_product.id, from_warehouse.id, 200, test_user.id)

        # Create transfer
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": from_warehouse.id,
            "to_warehouse_id": to_warehouse.id,
            "quantity": 30,
            "transfer_reference": "LIFECYCLE_TEST"
        }

        # Act 1: Create transfer
        create_response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        assert create_response.status_code == 201
        created_transfer = create_response.json()
        transfer_id = created_transfer["id"]

        # Act 2: Get transfer
        get_response = authenticated_client.get(f"/api/v1/stock-transfers/{transfer_id}")
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "pending"

        # Act 3: Complete transfer
        complete_response = authenticated_client.put(f"/api/v1/stock-transfers/{transfer_id}", 
                                                   json={"status": "completed"})
        assert complete_response.status_code == 200
        completed_transfer = complete_response.json()
        assert completed_transfer["status"] == "completed"

        # Verify stock changes
        product_response = authenticated_client.get(f"/api/v1/products/{test_product.id}")
        assert product_response.status_code == 200
        product_data = product_response.json()
        
        # Find stock in both warehouses
        from_stock = next((ws for ws in product_data["warehouse_stock"] 
                          if ws["warehouse_id"] == from_warehouse.id), None)
        to_stock = next((ws for ws in product_data["warehouse_stock"] 
                        if ws["warehouse_id"] == to_warehouse.id), None)
        
        assert from_stock["current_stock"] == 170  # 200 - 30
        assert to_stock["current_stock"] == 30     # 0 + 30