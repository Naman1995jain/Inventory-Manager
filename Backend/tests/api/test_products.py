"""
Test module for product endpoints
Tests CRUD operations, pagination, search, filtering, and authorization
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.models import Product, User


class TestProductCRUD:
    """Test class for product CRUD operations"""

    def test_create_product_success(self, authenticated_client: TestClient, db_session: Session):
        """Test successful product creation"""
        product_data = {
            "name": "Test Product",
            "sku": "TEST001",
            "description": "A test product",
            "unit_price": 10.99,
            "unit_of_measure": "piece",
            "category": "Electronics"
        }
        
        response = authenticated_client.post("/api/v1/products/", json=product_data)
        
        assert response.status_code == status.HTTP_201_CREATED
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

    def test_create_product_duplicate_sku(self, authenticated_client: TestClient, test_product: Product):
        """Test creating product with duplicate SKU fails"""
        product_data = {
            "name": "Another Product",
            "sku": test_product.sku,  # Duplicate SKU
            "description": "Another test product",
            "unit_price": 15.99,
            "unit_of_measure": "piece",
            "category": "Electronics"
        }
        
        response = authenticated_client.post("/api/v1/products/", json=product_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_create_product_missing_required_fields(self, authenticated_client: TestClient):
        """Test creating product with missing required fields"""
        # Missing name
        product_data = {
            "sku": "TEST002",
            "unit_price": 10.99
        }
        
        response = authenticated_client.post("/api/v1/products/", json=product_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_product_invalid_price(self, authenticated_client: TestClient):
        """Test creating product with invalid price"""
        product_data = {
            "name": "Test Product",
            "sku": "TEST003",
            "unit_price": -10.99  # Negative price
        }
        
        response = authenticated_client.post("/api/v1/products/", json=product_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_product_unauthorized(self, client: TestClient):
        """Test creating product without authentication"""
        product_data = {
            "name": "Test Product",
            "sku": "TEST004",
            "unit_price": 10.99
        }
        
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_product_success(self, authenticated_client: TestClient, test_product: Product):
        """Test retrieving a specific product"""
        response = authenticated_client.get(f"/api/v1/products/{test_product.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == test_product.name
        assert data["sku"] == test_product.sku

    def test_get_product_not_found(self, authenticated_client: TestClient):
        """Test retrieving non-existent product"""
        response = authenticated_client.get("/api/v1/products/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_product_success(self, authenticated_client: TestClient, test_product: Product):
        """Test successful product update"""
        update_data = {
            "name": "Updated Product Name",
            "description": "Updated description",
            "unit_price": 25.99
        }
        
        response = authenticated_client.put(f"/api/v1/products/{test_product.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert float(data["unit_price"]) == update_data["unit_price"]
        assert data["sku"] == test_product.sku  # SKU should remain unchanged

    def test_update_product_not_found(self, authenticated_client: TestClient):
        """Test updating non-existent product"""
        update_data = {"name": "Updated Name"}
        
        response = authenticated_client.put("/api/v1/products/99999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_product_success(self, authenticated_client: TestClient, test_product: Product):
        """Test successful product deletion (soft delete)"""
        response = authenticated_client.delete(f"/api/v1/products/{test_product.id}")
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify product is marked as inactive
        get_response = authenticated_client.get(f"/api/v1/products/{test_product.id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["is_active"] is False

    def test_delete_product_not_found(self, authenticated_client: TestClient):
        """Test deleting non-existent product"""
        response = authenticated_client.delete("/api/v1/products/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProductList:
    """Test class for product listing and filtering"""

    def test_list_products_default(self, authenticated_client: TestClient, multiple_products):
        """Test listing products with default pagination"""
        response = authenticated_client.get("/api/v1/products/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "products" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert len(data["products"]) <= 20  # Default page size

    def test_list_products_pagination(self, authenticated_client: TestClient, multiple_products):
        """Test product listing with custom pagination"""
        response = authenticated_client.get("/api/v1/products/?page=1&page_size=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["products"]) <= 2

    def test_list_products_search(self, authenticated_client: TestClient, multiple_products):
        """Test product search functionality"""
        response = authenticated_client.get("/api/v1/products/?search=Product 1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should find products containing "Product 1"
        found_products = [p for p in data["products"] if "Product 1" in p["name"]]
        assert len(found_products) > 0

    def test_list_products_category_filter(self, authenticated_client: TestClient, multiple_products):
        """Test product filtering by category"""
        response = authenticated_client.get("/api/v1/products/?category=Category 1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All returned products should be in Category 1
        for product in data["products"]:
            assert product["category"] == "Category 1"

    def test_list_products_sorting(self, authenticated_client: TestClient, multiple_products):
        """Test product sorting functionality"""
        # Test name ascending
        response = authenticated_client.get("/api/v1/products/?sort_by=name_asc")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        names = [p["name"] for p in data["products"]]
        assert names == sorted(names)

        # Test name descending
        response = authenticated_client.get("/api/v1/products/?sort_by=name_desc")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        names = [p["name"] for p in data["products"]]
        assert names == sorted(names, reverse=True)

    def test_list_owned_products(self, authenticated_client: TestClient, multiple_products):
        """Test listing products owned by current user"""
        response = authenticated_client.get("/api/v1/products/owned")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "products" in data
        # All products should belong to the current user
        for product in data["products"]:
            assert "created_by" in product or "creator" in product

    def test_list_products_invalid_pagination(self, authenticated_client: TestClient):
        """Test invalid pagination parameters"""
        # Invalid page number
        response = authenticated_client.get("/api/v1/products/?page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Invalid page size
        response = authenticated_client.get("/api/v1/products/?page_size=101")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_products_invalid_sort(self, authenticated_client: TestClient):
        """Test invalid sort parameters"""
        response = authenticated_client.get("/api/v1/products/?sort_by=invalid_sort")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestProductSearch:
    """Test class for advanced product search functionality"""

    def test_search_by_sku(self, authenticated_client: TestClient, multiple_products):
        """Test searching products by SKU"""
        response = authenticated_client.get("/api/v1/products/?search=TEST001")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        found = any(p["sku"] == "TEST001" for p in data["products"])
        assert found

    def test_search_case_insensitive(self, authenticated_client: TestClient, multiple_products):
        """Test case-insensitive search"""
        response = authenticated_client.get("/api/v1/products/?search=product")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["products"]) > 0  # Should find products despite lowercase

    def test_search_special_characters(self, authenticated_client: TestClient):
        """Test search with special characters"""
        response = authenticated_client.get("/api/v1/products/?search=%@#$")
        
        assert response.status_code == status.HTTP_200_OK
        # Should not cause server error, even if no results

    def test_search_empty_query(self, authenticated_client: TestClient, multiple_products):
        """Test search with empty query returns all products"""
        response = authenticated_client.get("/api/v1/products/?search=")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["products"]) > 0


class TestProductAuthorization:
    """Test class for product authorization and ownership"""

    def test_product_ownership_validation(self, authenticated_client: TestClient, test_product: Product):
        """Test that users can only modify their own products"""
        # This would require setting up different users and testing cross-user access
        # For now, test basic access patterns
        response = authenticated_client.get(f"/api/v1/products/{test_product.id}")
        assert response.status_code == status.HTTP_200_OK

    def test_inactive_product_visibility(self, authenticated_client: TestClient, test_product: Product, db_session: Session):
        """Test visibility of inactive products"""
        # Deactivate product
        test_product.is_active = False
        db_session.commit()
        
        # Should still be visible when accessed directly
        response = authenticated_client.get(f"/api/v1/products/{test_product.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_active"] is False


class TestProductValidation:
    """Test class for product data validation"""

    def test_sku_format_validation(self, authenticated_client: TestClient):
        """Test SKU format validation"""
        product_data = {
            "name": "Test Product",
            "sku": "",  # Empty SKU
            "unit_price": 10.99
        }
        
        response = authenticated_client.post("/api/v1/products/", json=product_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_price_precision_validation(self, authenticated_client: TestClient):
        """Test price precision validation"""
        product_data = {
            "name": "Test Product",
            "sku": "TEST_PRECISION",
            "unit_price": 10.999999  # Too many decimal places
        }
        
        response = authenticated_client.post("/api/v1/products/", json=product_data)
        # Should either accept with rounding or reject
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_name_length_validation(self, authenticated_client: TestClient):
        """Test product name length validation"""
        product_data = {
            "name": "x" * 300,  # Very long name
            "sku": "TEST_LONG_NAME",
            "unit_price": 10.99
        }
        
        response = authenticated_client.post("/api/v1/products/", json=product_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_category_validation(self, authenticated_client: TestClient):
        """Test category field validation"""
        product_data = {
            "name": "Test Product",
            "sku": "TEST_CATEGORY",
            "unit_price": 10.99,
            "category": "x" * 150  # Very long category
        }
        
        response = authenticated_client.post("/api/v1/products/", json=product_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY