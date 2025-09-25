import pytest
from fastapi.testclient import TestClient
from app.models import Product


@pytest.mark.integration
class TestProductsAPI:
    """Integration tests for products endpoints"""

    def test_create_product_success(self, authenticated_client: TestClient, db_session, test_user):
        """Test successful product creation"""
        # Arrange
        product_data = {
            "name": "New Test Product",
            "sku": "NEW001",
            "description": "A new test product",
            "unit_price": 15.99,
            "unit_of_measure": "piece",
            "category": "Electronics"
        }

        # Act
        response = authenticated_client.post("/api/v1/products/", json=product_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == product_data["name"]
        assert data["sku"] == product_data["sku"]
        assert data["description"] == product_data["description"]
        assert float(data["unit_price"]) == product_data["unit_price"]
        assert data["unit_of_measure"] == product_data["unit_of_measure"]
        assert data["category"] == product_data["category"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

        # Verify product was created in database
        db_product = db_session.query(Product).filter(Product.sku == product_data["sku"]).first()
        assert db_product is not None
        assert db_product.created_by == test_user.id

    def test_create_product_duplicate_sku(self, authenticated_client: TestClient, test_product):
        """Test creating product with duplicate SKU"""
        # Arrange
        product_data = {
            "name": "Another Product",
            "sku": test_product.sku,  # Use existing SKU
            "description": "Should fail"
        }

        # Act
        response = authenticated_client.post("/api/v1/products/", json=product_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Product with this SKU already exists" in data["detail"]

    def test_create_product_missing_required_fields(self, authenticated_client: TestClient):
        """Test creating product with missing required fields"""
        # Missing name
        response = authenticated_client.post("/api/v1/products/", json={"sku": "TEST002"})
        assert response.status_code == 422

        # Missing SKU
        response = authenticated_client.post("/api/v1/products/", json={"name": "Test Product"})
        assert response.status_code == 422

    def test_create_product_unauthorized(self, client: TestClient):
        """Test creating product without authentication"""
        # Arrange
        product_data = {
            "name": "Test Product",
            "sku": "TEST001"
        }

        # Act
        response = client.post("/api/v1/products/", json=product_data)

        # Assert
        assert response.status_code == 403

    def test_get_products_list(self, authenticated_client: TestClient, multiple_products):
        """Test getting paginated list of products"""
        # Act
        response = authenticated_client.get("/api/v1/products/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert len(data["items"]) <= data["page_size"]
        assert data["total"] >= len(multiple_products)

    def test_get_products_with_pagination(self, authenticated_client: TestClient, multiple_products):
        """Test getting products with custom pagination"""
        # Act
        response = authenticated_client.get("/api/v1/products/?page=1&page_size=2")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) <= 2

    def test_get_products_with_search(self, authenticated_client: TestClient, multiple_products):
        """Test getting products with search filter"""
        # Act
        response = authenticated_client.get("/api/v1/products/?search=Product 1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Should find products with "Product 1" in name
        matching_items = [item for item in data["items"] if "Product 1" in item["name"]]
        assert len(matching_items) > 0

    def test_get_products_with_sorting(self, authenticated_client: TestClient, multiple_products):
        """Test getting products with sorting"""
        # Act - sort by name ascending
        response = authenticated_client.get("/api/v1/products/?sort_by=name_asc")

        # Assert
        assert response.status_code == 200
        data = response.json()
        if len(data["items"]) > 1:
            # Verify ascending order
            names = [item["name"] for item in data["items"]]
            assert names == sorted(names)

    def test_get_products_unauthorized(self, client: TestClient):
        """Test getting products without authentication"""
        # Act
        response = client.get("/api/v1/products/")

        # Assert
        assert response.status_code == 403

    def test_get_product_by_id(self, authenticated_client: TestClient, test_product):
        """Test getting specific product by ID"""
        # Act
        response = authenticated_client.get(f"/api/v1/products/{test_product.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == test_product.name
        assert data["sku"] == test_product.sku
        assert "total_stock" in data
        assert "warehouse_stock" in data

    def test_get_product_not_found(self, authenticated_client: TestClient):
        """Test getting non-existent product"""
        # Act
        response = authenticated_client.get("/api/v1/products/99999")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Product not found" in data["detail"]

    def test_get_product_unauthorized(self, client: TestClient, test_product):
        """Test getting product without authentication"""
        # Act
        response = client.get(f"/api/v1/products/{test_product.id}")

        # Assert
        assert response.status_code == 403

    def test_update_product_success(self, authenticated_client: TestClient, test_product, db_session):
        """Test successful product update"""
        # Arrange
        update_data = {
            "name": "Updated Product Name",
            "unit_price": 25.99,
            "category": "Updated Category"
        }

        # Act
        response = authenticated_client.put(f"/api/v1/products/{test_product.id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == update_data["name"]
        assert float(data["unit_price"]) == update_data["unit_price"]
        assert data["category"] == update_data["category"]

        # Verify update in database
        db_session.refresh(test_product)
        assert test_product.name == update_data["name"]

    def test_update_product_sku_duplicate(self, authenticated_client: TestClient, multiple_products):
        """Test updating product with duplicate SKU"""
        # Arrange
        product1, product2 = multiple_products[0], multiple_products[1]
        update_data = {
            "sku": product2.sku  # Try to use second product's SKU
        }

        # Act
        response = authenticated_client.put(f"/api/v1/products/{product1.id}", json=update_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Product with this SKU already exists" in data["detail"]

    def test_update_product_not_found(self, authenticated_client: TestClient):
        """Test updating non-existent product"""
        # Arrange
        update_data = {"name": "Updated Name"}

        # Act
        response = authenticated_client.put("/api/v1/products/99999", json=update_data)

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Product not found" in data["detail"]

    def test_update_product_unauthorized(self, client: TestClient, test_product):
        """Test updating product without authentication"""
        # Arrange
        update_data = {"name": "Updated Name"}

        # Act
        response = client.put(f"/api/v1/products/{test_product.id}", json=update_data)

        # Assert
        assert response.status_code == 403

    def test_delete_product_success(self, authenticated_client: TestClient, test_product, db_session):
        """Test successful product soft deletion"""
        # Act
        response = authenticated_client.delete(f"/api/v1/products/{test_product.id}")

        # Assert
        assert response.status_code == 204

        # Verify soft deletion in database
        db_session.refresh(test_product)
        assert test_product.is_active is False

    def test_delete_product_not_found(self, authenticated_client: TestClient):
        """Test deleting non-existent product"""
        # Act
        response = authenticated_client.delete("/api/v1/products/99999")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Product not found" in data["detail"]

    def test_delete_product_unauthorized(self, client: TestClient, test_product):
        """Test deleting product without authentication"""
        # Act
        response = client.delete(f"/api/v1/products/{test_product.id}")

        # Assert
        assert response.status_code == 403

    def test_product_lifecycle(self, authenticated_client: TestClient, db_session, test_user):
        """Test complete product lifecycle: create, read, update, delete"""
        # Create
        product_data = {
            "name": "Lifecycle Product",
            "sku": "LIFE001",
            "description": "Product for lifecycle test",
            "unit_price": 10.0,
            "category": "Test"
        }
        
        create_response = authenticated_client.post("/api/v1/products/", json=product_data)
        assert create_response.status_code == 201
        created_product = create_response.json()
        product_id = created_product["id"]

        # Read
        get_response = authenticated_client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == 200

        # Update
        update_data = {"name": "Updated Lifecycle Product", "unit_price": 20.0}
        update_response = authenticated_client.put(f"/api/v1/products/{product_id}", json=update_data)
        assert update_response.status_code == 200
        updated_product = update_response.json()
        assert updated_product["name"] == update_data["name"]

        # Delete
        delete_response = authenticated_client.delete(f"/api/v1/products/{product_id}")
        assert delete_response.status_code == 204

        # Verify soft deletion
        db_product = db_session.query(Product).filter(Product.id == product_id).first()
        assert db_product.is_active is False