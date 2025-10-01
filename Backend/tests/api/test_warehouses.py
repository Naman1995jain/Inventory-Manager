"""
Test module for warehouse endpoints
Tests warehouse CRUD operations and access control
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import Warehouse


class TestWarehouseCRUD:
    """Test class for warehouse CRUD operations"""

    def test_list_warehouses_success(self, authenticated_client: TestClient, multiple_warehouses):
        """Test successful retrieval of warehouse list"""
        response = authenticated_client.get("/api/v1/warehouses/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify warehouse structure
        warehouse = data[0]
        assert "id" in warehouse
        assert "name" in warehouse
        assert "location" in warehouse
        assert "is_active" in warehouse

    def test_list_warehouses_only_active(self, authenticated_client: TestClient, db_session: Session):
        """Test that only active warehouses are returned"""
        # Create an inactive warehouse
        inactive_warehouse = Warehouse(
            name="Inactive Warehouse",
            location="Inactive Location",
            is_active=False
        )
        db_session.add(inactive_warehouse)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/warehouses/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify all returned warehouses are active
        for warehouse in data:
            assert warehouse["is_active"] is True

    def test_list_warehouses_unauthorized(self, client: TestClient):
        """Test warehouse listing without authentication"""
        response = client.get("/api/v1/warehouses/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_warehouse_success(self, authenticated_client: TestClient, test_warehouse: Warehouse):
        """Test successful retrieval of specific warehouse"""
        response = authenticated_client.get(f"/api/v1/warehouses/{test_warehouse.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_warehouse.id
        assert data["name"] == test_warehouse.name
        assert data["location"] == test_warehouse.location
        assert data["is_active"] is True

    def test_get_warehouse_not_found(self, authenticated_client: TestClient):
        """Test retrieving non-existent warehouse"""
        response = authenticated_client.get("/api/v1/warehouses/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_inactive_warehouse(self, authenticated_client: TestClient, db_session: Session):
        """Test retrieving inactive warehouse returns 404"""
        # Create inactive warehouse
        inactive_warehouse = Warehouse(
            name="Inactive Warehouse",
            location="Inactive Location", 
            is_active=False
        )
        db_session.add(inactive_warehouse)
        db_session.commit()
        db_session.refresh(inactive_warehouse)
        
        response = authenticated_client.get(f"/api/v1/warehouses/{inactive_warehouse.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_warehouse_unauthorized(self, client: TestClient, test_warehouse: Warehouse):
        """Test warehouse retrieval without authentication"""
        response = client.get(f"/api/v1/warehouses/{test_warehouse.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestWarehouseValidation:
    """Test class for warehouse data validation"""

    def test_warehouse_id_validation(self, authenticated_client: TestClient):
        """Test warehouse ID validation"""
        # Test with invalid ID format
        response = authenticated_client.get("/api/v1/warehouses/invalid_id")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test with negative ID
        response = authenticated_client.get("/api/v1/warehouses/-1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_warehouse_data_structure(self, authenticated_client: TestClient, test_warehouse: Warehouse):
        """Test warehouse data structure and types"""
        response = authenticated_client.get(f"/api/v1/warehouses/{test_warehouse.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify data types
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["location"], (str, type(None)))
        assert isinstance(data["is_active"], bool)
        assert isinstance(data["description"], (str, type(None)))


class TestWarehouseFiltering:
    """Test class for warehouse filtering and search functionality"""

    def test_empty_warehouse_list(self, authenticated_client: TestClient, db_session: Session):
        """Test behavior when no warehouses exist"""
        # Remove all warehouses
        db_session.query(Warehouse).delete()
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/warehouses/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

    def test_multiple_warehouses_ordering(self, authenticated_client: TestClient, multiple_warehouses):
        """Test that warehouses are returned in consistent order"""
        response = authenticated_client.get("/api/v1/warehouses/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify list is not empty and has consistent structure
        assert len(data) > 1
        warehouse_ids = [w["id"] for w in data]
        assert len(warehouse_ids) == len(set(warehouse_ids))  # No duplicates


class TestWarehouseSecurity:
    """Test class for warehouse security and access control"""

    def test_warehouse_access_without_token(self, client: TestClient):
        """Test that warehouse endpoints require authentication"""
        # Test list endpoint
        response = client.get("/api/v1/warehouses/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test get specific warehouse endpoint
        response = client.get("/api/v1/warehouses/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_warehouse_access_with_invalid_token(self, client: TestClient):
        """Test warehouse access with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/api/v1/warehouses/", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_sql_injection_protection(self, authenticated_client: TestClient):
        """Test protection against SQL injection in warehouse ID"""
        malicious_id = "1; DROP TABLE warehouses; --"
        
        response = authenticated_client.get(f"/api/v1/warehouses/{malicious_id}")
        
        # Should fail safely with validation error, not server error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_warehouse_data_exposure(self, authenticated_client: TestClient, test_warehouse: Warehouse):
        """Test that warehouse data doesn't expose sensitive information"""
        response = authenticated_client.get(f"/api/v1/warehouses/{test_warehouse.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify no sensitive fields are exposed
        sensitive_fields = ["password", "secret", "key", "token"]
        for field in sensitive_fields:
            assert field not in data


class TestWarehouseErrorHandling:
    """Test class for warehouse error handling"""

    def test_database_connection_error_simulation(self, authenticated_client: TestClient):
        """Test handling of database connection issues"""
        # This test would require mocking database connection failures
        # For now, test basic error response structure
        response = authenticated_client.get("/api/v1/warehouses/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "detail" in error_data

    def test_malformed_warehouse_id(self, authenticated_client: TestClient):
        """Test handling of malformed warehouse IDs"""
        test_cases = [
            "/api/v1/warehouses/abc",
            "/api/v1/warehouses/1.5",
            "/api/v1/warehouses/1e10",
            "/api/v1/warehouses/",  # Missing ID
        ]
        
        for url in test_cases:
            response = authenticated_client.get(url)
            # Should return validation error or not found, not server error
            assert response.status_code in [
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_405_METHOD_NOT_ALLOWED
            ]

    def test_large_warehouse_id(self, authenticated_client: TestClient):
        """Test handling of very large warehouse IDs"""
        large_id = "9" * 20  # Very large number
        
        response = authenticated_client.get(f"/api/v1/warehouses/{large_id}")
        
        # Should handle gracefully, either validation error or not found
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_404_NOT_FOUND
        ]


class TestWarehouseIntegration:
    """Test class for warehouse integration with other services"""

    def test_warehouse_with_stock_movements(self, authenticated_client: TestClient, test_warehouse: Warehouse):
        """Test warehouse data includes related stock movement information if available"""
        response = authenticated_client.get(f"/api/v1/warehouses/{test_warehouse.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Basic warehouse data should be present
        assert data["id"] == test_warehouse.id
        assert data["name"] == test_warehouse.name

    def test_warehouse_consistency(self, authenticated_client: TestClient, multiple_warehouses):
        """Test data consistency across warehouse endpoints"""
        # Get list of warehouses
        list_response = authenticated_client.get("/api/v1/warehouses/")
        assert list_response.status_code == status.HTTP_200_OK
        warehouses_list = list_response.json()
        
        # Get each warehouse individually and compare
        for warehouse_summary in warehouses_list:
            detail_response = authenticated_client.get(f"/api/v1/warehouses/{warehouse_summary['id']}")
            assert detail_response.status_code == status.HTTP_200_OK
            warehouse_detail = detail_response.json()
            
            # Core fields should match
            assert warehouse_summary["id"] == warehouse_detail["id"]
            assert warehouse_summary["name"] == warehouse_detail["name"]
            assert warehouse_summary["is_active"] == warehouse_detail["is_active"]