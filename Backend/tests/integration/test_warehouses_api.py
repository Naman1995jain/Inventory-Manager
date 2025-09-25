import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestWarehousesAPI:
    """Integration tests for warehouses endpoints"""

    def test_get_warehouses_list(self, authenticated_client: TestClient, multiple_warehouses):
        """Test getting list of active warehouses"""
        # Act
        response = authenticated_client.get("/api/v1/warehouses/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(multiple_warehouses)
        
        # Verify warehouse data structure
        if data:
            warehouse = data[0]
            assert "id" in warehouse
            assert "name" in warehouse
            assert "location" in warehouse
            assert "description" in warehouse
            assert "is_active" in warehouse
            assert "created_at" in warehouse
            assert "updated_at" in warehouse

    def test_get_warehouses_only_active(self, authenticated_client: TestClient, db_session, multiple_warehouses):
        """Test that only active warehouses are returned"""
        # Arrange - deactivate one warehouse
        warehouse_to_deactivate = multiple_warehouses[0]
        warehouse_to_deactivate.is_active = False
        db_session.commit()

        # Act
        response = authenticated_client.get("/api/v1/warehouses/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # All returned warehouses should be active
        for warehouse in data:
            assert warehouse["is_active"] is True
        
        # Deactivated warehouse should not be in the list
        deactivated_ids = [w["id"] for w in data if w["id"] == warehouse_to_deactivate.id]
        assert len(deactivated_ids) == 0

    def test_get_warehouses_unauthorized(self, client: TestClient):
        """Test getting warehouses without authentication"""
        # Act
        response = client.get("/api/v1/warehouses/")

        # Assert
        assert response.status_code == 403

    def test_get_warehouse_by_id(self, authenticated_client: TestClient, test_warehouse):
        """Test getting specific warehouse by ID"""
        # Act
        response = authenticated_client.get(f"/api/v1/warehouses/{test_warehouse.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_warehouse.id
        assert data["name"] == test_warehouse.name
        assert data["location"] == test_warehouse.location
        assert data["description"] == test_warehouse.description
        assert data["is_active"] is True

    def test_get_warehouse_not_found(self, authenticated_client: TestClient):
        """Test getting non-existent warehouse"""
        # Act
        response = authenticated_client.get("/api/v1/warehouses/99999")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Warehouse not found" in data["detail"]

    def test_get_warehouse_inactive(self, authenticated_client: TestClient, db_session, test_warehouse):
        """Test getting inactive warehouse"""
        # Arrange - deactivate warehouse
        test_warehouse.is_active = False
        db_session.commit()

        # Act
        response = authenticated_client.get(f"/api/v1/warehouses/{test_warehouse.id}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Warehouse not found" in data["detail"]

    def test_get_warehouse_unauthorized(self, client: TestClient, test_warehouse):
        """Test getting warehouse without authentication"""
        # Act
        response = client.get(f"/api/v1/warehouses/{test_warehouse.id}")

        # Assert
        assert response.status_code == 403

    def test_warehouses_data_consistency(self, authenticated_client: TestClient, multiple_warehouses):
        """Test data consistency between list and individual warehouse endpoints"""
        # Act - get list of warehouses
        list_response = authenticated_client.get("/api/v1/warehouses/")
        assert list_response.status_code == 200
        warehouses_list = list_response.json()

        # Act & Assert - get each warehouse individually and compare
        for warehouse_summary in warehouses_list:
            warehouse_id = warehouse_summary["id"]
            
            detail_response = authenticated_client.get(f"/api/v1/warehouses/{warehouse_id}")
            assert detail_response.status_code == 200
            warehouse_detail = detail_response.json()
            
            # Compare key fields
            assert warehouse_detail["id"] == warehouse_summary["id"]
            assert warehouse_detail["name"] == warehouse_summary["name"]
            assert warehouse_detail["location"] == warehouse_summary["location"]
            assert warehouse_detail["is_active"] == warehouse_summary["is_active"]

    def test_warehouses_sorting(self, authenticated_client: TestClient, db_session, multiple_warehouses):
        """Test that warehouses are returned in a consistent order"""
        # Act
        response1 = authenticated_client.get("/api/v1/warehouses/")
        response2 = authenticated_client.get("/api/v1/warehouses/")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        warehouses1 = response1.json()
        warehouses2 = response2.json()
        
        # Order should be consistent
        warehouse_ids1 = [w["id"] for w in warehouses1]
        warehouse_ids2 = [w["id"] for w in warehouses2]
        assert warehouse_ids1 == warehouse_ids2

    def test_empty_warehouses_list(self, authenticated_client: TestClient, db_session):
        """Test getting warehouses when none exist (all inactive)"""
        # Arrange - deactivate all warehouses
        from app.models import Warehouse
        db_session.query(Warehouse).update({"is_active": False})
        db_session.commit()

        # Act
        response = authenticated_client.get("/api/v1/warehouses/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0