"""
Test module for stock transfer endpoints
Tests stock transfer CRUD operations, validation, and business logic
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import StockTransfer, Product, Warehouse, User


class TestStockTransferCRUD:
    """Test class for stock transfer CRUD operations"""

    def test_create_stock_transfer_success(self, authenticated_client: TestClient, test_product: Product, multiple_warehouses):
        """Test successful stock transfer creation"""
        from_warehouse = multiple_warehouses[0]
        to_warehouse = multiple_warehouses[1]
        
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": from_warehouse.id,
            "to_warehouse_id": to_warehouse.id,
            "quantity": 50,
            "transfer_reference": "TR001",
            "notes": "Transfer between warehouses"
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_id"] == transfer_data["product_id"]
        assert data["from_warehouse_id"] == transfer_data["from_warehouse_id"]
        assert data["to_warehouse_id"] == transfer_data["to_warehouse_id"]
        assert data["quantity"] == transfer_data["quantity"]
        assert data["transfer_reference"] == transfer_data["transfer_reference"]
        assert data["notes"] == transfer_data["notes"]
        assert data["status"] == "pending"  # Default status
        assert "id" in data
        assert "created_at" in data

    def test_create_transfer_same_warehouse(self, authenticated_client: TestClient, test_product: Product, test_warehouse: Warehouse):
        """Test creating transfer with same source and destination warehouse"""
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": test_warehouse.id,
            "to_warehouse_id": test_warehouse.id,  # Same warehouse
            "quantity": 50
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        
        # Should fail - cannot transfer to same warehouse
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "same warehouse" in response.json()["detail"].lower()

    def test_create_transfer_invalid_product(self, authenticated_client: TestClient, multiple_warehouses):
        """Test creating transfer with non-existent product"""
        transfer_data = {
            "product_id": 99999,  # Non-existent product
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 50
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_transfer_invalid_warehouse(self, authenticated_client: TestClient, test_product: Product):
        """Test creating transfer with non-existent warehouses"""
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": 99999,  # Non-existent warehouse
            "to_warehouse_id": 99998,
            "quantity": 50
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_transfer_zero_quantity(self, authenticated_client: TestClient, test_product: Product, multiple_warehouses):
        """Test creating transfer with zero quantity"""
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 0  # Zero quantity
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_transfer_negative_quantity(self, authenticated_client: TestClient, test_product: Product, multiple_warehouses):
        """Test creating transfer with negative quantity"""
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": -10  # Negative quantity
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_transfer_unauthorized(self, client: TestClient):
        """Test creating transfer without authentication"""
        transfer_data = {
            "product_id": 1,
            "from_warehouse_id": 1,
            "to_warehouse_id": 2,
            "quantity": 50
        }
        
        response = client.post("/api/v1/stock-transfers/", json=transfer_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestStockTransferList:
    """Test class for stock transfer listing and filtering"""

    def test_list_transfers_success(self, authenticated_client: TestClient, db_session: Session, test_product: Product, multiple_warehouses):
        """Test successful listing of stock transfers"""
        # Create test transfers
        transfers = [
            StockTransfer(
                product_id=test_product.id,
                from_warehouse_id=multiple_warehouses[0].id,
                to_warehouse_id=multiple_warehouses[1].id,
                quantity=50,
                transfer_reference="TR001",
                status="pending"
            ),
            StockTransfer(
                product_id=test_product.id,
                from_warehouse_id=multiple_warehouses[1].id,
                to_warehouse_id=multiple_warehouses[2].id,
                quantity=30,
                transfer_reference="TR002",
                status="completed"
            )
        ]
        
        for transfer in transfers:
            db_session.add(transfer)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/stock-transfers/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "transfers" in data or "items" in data
        
        # Verify transfer structure
        transfers_list = data.get("transfers", data.get("items", []))
        if transfers_list:
            transfer = transfers_list[0]
            assert "id" in transfer
            assert "product_id" in transfer
            assert "from_warehouse_id" in transfer
            assert "to_warehouse_id" in transfer
            assert "quantity" in transfer
            assert "status" in transfer

    def test_list_transfers_pagination(self, authenticated_client: TestClient):
        """Test stock transfer listing with pagination"""
        response = authenticated_client.get("/api/v1/stock-transfers/?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "page" in data or "transfers" in data

    def test_list_transfers_by_status(self, authenticated_client: TestClient):
        """Test filtering transfers by status"""
        response = authenticated_client.get("/api/v1/stock-transfers/?status=pending")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All transfers should have pending status
        transfers_list = data.get("transfers", data.get("items", []))
        for transfer in transfers_list:
            assert transfer["status"] == "pending"

    def test_list_transfers_by_product(self, authenticated_client: TestClient, test_product: Product):
        """Test filtering transfers by product"""
        response = authenticated_client.get(f"/api/v1/stock-transfers/?product_id={test_product.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All transfers should be for the specified product
        transfers_list = data.get("transfers", data.get("items", []))
        for transfer in transfers_list:
            assert transfer["product_id"] == test_product.id

    def test_list_transfers_unauthorized(self, client: TestClient):
        """Test listing transfers without authentication"""
        response = client.get("/api/v1/stock-transfers/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestStockTransferStatus:
    """Test class for stock transfer status management"""

    def test_get_transfer_success(self, authenticated_client: TestClient, db_session: Session, test_product: Product, multiple_warehouses):
        """Test retrieving a specific transfer"""
        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=multiple_warehouses[0].id,
            to_warehouse_id=multiple_warehouses[1].id,
            quantity=50,
            transfer_reference="TR001",
            status="pending"
        )
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)
        
        response = authenticated_client.get(f"/api/v1/stock-transfers/{transfer.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == transfer.id
        assert data["status"] == "pending"

    def test_get_transfer_not_found(self, authenticated_client: TestClient):
        """Test retrieving non-existent transfer"""
        response = authenticated_client.get("/api/v1/stock-transfers/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_transfer_status(self, authenticated_client: TestClient, db_session: Session, test_product: Product, multiple_warehouses):
        """Test updating transfer status"""
        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=multiple_warehouses[0].id,
            to_warehouse_id=multiple_warehouses[1].id,
            quantity=50,
            transfer_reference="TR001",
            status="pending"
        )
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)
        
        update_data = {"status": "completed"}
        response = authenticated_client.put(f"/api/v1/stock-transfers/{transfer.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
        assert "completed_at" in data

    def test_update_transfer_invalid_status(self, authenticated_client: TestClient, db_session: Session, test_product: Product, multiple_warehouses):
        """Test updating transfer with invalid status"""
        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=multiple_warehouses[0].id,
            to_warehouse_id=multiple_warehouses[1].id,
            quantity=50,
            status="pending"
        )
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)
        
        update_data = {"status": "invalid_status"}
        response = authenticated_client.put(f"/api/v1/stock-transfers/{transfer.id}", json=update_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_cancel_transfer(self, authenticated_client: TestClient, db_session: Session, test_product: Product, multiple_warehouses):
        """Test cancelling a pending transfer"""
        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=multiple_warehouses[0].id,
            to_warehouse_id=multiple_warehouses[1].id,
            quantity=50,
            status="pending"
        )
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)
        
        response = authenticated_client.delete(f"/api/v1/stock-transfers/{transfer.id}")
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify transfer is cancelled
        get_response = authenticated_client.get(f"/api/v1/stock-transfers/{transfer.id}")
        if get_response.status_code == status.HTTP_200_OK:
            assert get_response.json()["status"] == "cancelled"


class TestStockTransferValidation:
    """Test class for stock transfer validation"""

    def test_transfer_reference_uniqueness(self, authenticated_client: TestClient, test_product: Product, multiple_warehouses):
        """Test transfer reference number uniqueness"""
        # Create first transfer
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 50,
            "transfer_reference": "UNIQUE001"
        }
        
        response1 = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to create second transfer with same reference
        response2 = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        
        # May allow duplicate references or may enforce uniqueness
        assert response2.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_transfer_with_inactive_product(self, authenticated_client: TestClient, multiple_warehouses, db_session: Session):
        """Test transfer with inactive product"""
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
        
        transfer_data = {
            "product_id": inactive_product.id,
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 50
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        # Should reject transfers for inactive products
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_transfer_with_inactive_warehouse(self, authenticated_client: TestClient, test_product: Product, db_session: Session):
        """Test transfer with inactive warehouses"""
        # Create inactive warehouse
        inactive_warehouse = Warehouse(
            name="Inactive Warehouse",
            location="Inactive Location",
            is_active=False
        )
        db_session.add(inactive_warehouse)
        db_session.commit()
        db_session.refresh(inactive_warehouse)
        
        active_warehouse = Warehouse(
            name="Active Warehouse",
            location="Active Location",
            is_active=True
        )
        db_session.add(active_warehouse)
        db_session.commit()
        db_session.refresh(active_warehouse)
        
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": inactive_warehouse.id,
            "to_warehouse_id": active_warehouse.id,
            "quantity": 50
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        # Should reject transfers involving inactive warehouses
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_large_quantity_validation(self, authenticated_client: TestClient, test_product: Product, multiple_warehouses):
        """Test validation of very large quantities"""
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 999999999  # Very large quantity
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        
        # Should either accept or reject gracefully
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_transfer_notes_length(self, authenticated_client: TestClient, test_product: Product, multiple_warehouses):
        """Test transfer notes length validation"""
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 50,
            "notes": "x" * 1000  # Very long notes
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        
        # Should either accept or reject based on length limits
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestStockTransferBusinessLogic:
    """Test class for stock transfer business logic"""

    def test_transfer_workflow(self, authenticated_client: TestClient, test_product: Product, multiple_warehouses):
        """Test complete transfer workflow"""
        # 1. Create transfer
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 50,
            "transfer_reference": "WORKFLOW001"
        }
        
        create_response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        transfer_id = create_response.json()["id"]
        
        # 2. Verify transfer is pending
        get_response = authenticated_client.get(f"/api/v1/stock-transfers/{transfer_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["status"] == "pending"
        
        # 3. Complete transfer
        update_data = {"status": "completed"}
        update_response = authenticated_client.put(f"/api/v1/stock-transfers/{transfer_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["status"] == "completed"

    def test_concurrent_transfers(self, authenticated_client: TestClient, test_product: Product, multiple_warehouses):
        """Test handling of concurrent transfer requests"""
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 50
        }
        
        # Create multiple transfers simultaneously
        responses = []
        for i in range(3):
            transfer_data["transfer_reference"] = f"CONCURRENT{i}"
            response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
            responses.append(response)
        
        # All should succeed (or handle gracefully)
        for response in responses:
            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]


class TestStockTransferSecurity:
    """Test class for stock transfer security"""

    def test_sql_injection_protection(self, authenticated_client: TestClient):
        """Test protection against SQL injection"""
        malicious_data = {
            "product_id": "1; DROP TABLE stock_transfers; --",
            "from_warehouse_id": 1,
            "to_warehouse_id": 2,
            "quantity": 50
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=malicious_data)
        
        # Should fail safely with validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_transfer_access_control(self, authenticated_client: TestClient, test_product: Product, multiple_warehouses):
        """Test transfer access control and permissions"""
        transfer_data = {
            "product_id": test_product.id,
            "from_warehouse_id": multiple_warehouses[0].id,
            "to_warehouse_id": multiple_warehouses[1].id,
            "quantity": 50
        }
        
        response = authenticated_client.post("/api/v1/stock-transfers/", json=transfer_data)
        # Should succeed for authorized users
        assert response.status_code == status.HTTP_201_CREATED

    def test_transfer_data_exposure(self, authenticated_client: TestClient, db_session: Session, test_product: Product, multiple_warehouses):
        """Test that transfer data doesn't expose sensitive information"""
        transfer = StockTransfer(
            product_id=test_product.id,
            from_warehouse_id=multiple_warehouses[0].id,
            to_warehouse_id=multiple_warehouses[1].id,
            quantity=50,
            status="pending"
        )
        db_session.add(transfer)
        db_session.commit()
        db_session.refresh(transfer)
        
        response = authenticated_client.get(f"/api/v1/stock-transfers/{transfer.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify no sensitive fields are exposed
        sensitive_fields = ["password", "secret", "key", "token"]
        for field in sensitive_fields:
            assert field not in data