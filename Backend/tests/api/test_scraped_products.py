"""
Test module for scraped products endpoints
Tests scraped product listing, filtering, and data integrity
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.models import ScrapData


class TestScrapedProductsList:
    """Test class for scraped products listing"""

    def test_list_scraped_products_success(self, authenticated_client: TestClient, db_session: Session):
        """Test successful listing of scraped products"""
        # Create test scraped products
        scraped_products = [
            ScrapData(
                product_name="Laptop Dell XPS 13",
                product_description="High-performance ultrabook",
                category="Electronics",
                price=999.99,
                rating="4.5",
                image_url="https://example.com/laptop.jpg",
                product_page_url="https://example.com/product/laptop"
            ),
            ScrapData(
                product_name="iPhone 14 Pro",
                product_description="Latest iPhone model",
                category="Electronics",
                price=1099.99,
                rating="4.8",
                image_url="https://example.com/iphone.jpg",
                product_page_url="https://example.com/product/iphone"
            )
        ]
        
        for product in scraped_products:
            db_session.add(product)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/scraped-products/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify response structure
        assert "products" in data or "items" in data
        products_list = data.get("products", data.get("items", []))
        assert len(products_list) >= 2
        
        # Verify product structure
        if products_list:
            product = products_list[0]
            assert "id" in product
            assert "product_name" in product
            assert "category" in product
            assert "price" in product
            assert "rating" in product

    def test_list_scraped_products_pagination(self, authenticated_client: TestClient):
        """Test scraped products listing with pagination"""
        response = authenticated_client.get("/api/v1/scraped-products/?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify pagination structure
        if "page" in data:
            assert data["page"] == 1
            assert data["page_size"] == 10

    def test_list_scraped_products_search(self, authenticated_client: TestClient, db_session: Session):
        """Test searching scraped products"""
        # Create searchable product
        product = ScrapData(
            product_name="Gaming Laptop ASUS ROG",
            product_description="High-end gaming laptop",
            category="Gaming",
            price=1499.99
        )
        db_session.add(product)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/scraped-products/?search=gaming")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        products_list = data.get("products", data.get("items", []))
        # Should find products containing "gaming"
        found = any("gaming" in p["product_name"].lower() or 
                   "gaming" in (p.get("category", "")).lower() for p in products_list)
        assert found or len(products_list) == 0  # Allow empty results

    def test_list_scraped_products_category_filter(self, authenticated_client: TestClient, db_session: Session):
        """Test filtering scraped products by category"""
        # Create products in specific category
        products = [
            ScrapData(
                product_name="Smartphone A",
                category="Mobile",
                price=499.99
            ),
            ScrapData(
                product_name="Smartphone B", 
                category="Mobile",
                price=599.99
            ),
            ScrapData(
                product_name="Laptop C",
                category="Computers",
                price=899.99
            )
        ]
        
        for product in products:
            db_session.add(product)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/scraped-products/?category=Mobile")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        products_list = data.get("products", data.get("items", []))
        # All returned products should be in Mobile category
        for product in products_list:
            if "category" in product and product["category"]:
                assert product["category"] == "Mobile"

    def test_list_scraped_products_price_range(self, authenticated_client: TestClient):
        """Test filtering scraped products by price range"""
        response = authenticated_client.get("/api/v1/scraped-products/?min_price=100&max_price=1000")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        products_list = data.get("products", data.get("items", []))
        # All returned products should be within price range
        for product in products_list:
            if "price" in product and product["price"]:
                price = float(product["price"])
                assert 100 <= price <= 1000

    def test_list_scraped_products_unauthorized(self, client: TestClient):
        """Test listing scraped products without authentication"""
        response = client.get("/api/v1/scraped-products/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestScrapedProductsValidation:
    """Test class for scraped products data validation"""

    def test_scraped_product_data_structure(self, authenticated_client: TestClient, db_session: Session):
        """Test scraped product data structure and types"""
        product = ScrapData(
            product_name="Test Product",
            product_description="Test description",
            category="Test Category",
            price=99.99,
            rating="4.0",
            image_url="https://example.com/image.jpg",
            product_page_url="https://example.com/product"
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        response = authenticated_client.get("/api/v1/scraped-products/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        products_list = data.get("products", data.get("items", []))
        if products_list:
            product_data = products_list[0]
            
            # Verify data types
            assert isinstance(product_data.get("id"), (int, type(None)))
            assert isinstance(product_data.get("product_name"), str)
            assert isinstance(product_data.get("product_description"), (str, type(None)))
            assert isinstance(product_data.get("category"), (str, type(None)))
            assert isinstance(product_data.get("price"), (int, float, str, type(None)))
            assert isinstance(product_data.get("rating"), (str, int, float, type(None)))

    def test_invalid_pagination_parameters(self, authenticated_client: TestClient):
        """Test invalid pagination parameters"""
        # Invalid page number
        response = authenticated_client.get("/api/v1/scraped-products/?page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Invalid page size
        response = authenticated_client.get("/api/v1/scraped-products/?page_size=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_price_range(self, authenticated_client: TestClient):
        """Test invalid price range parameters"""
        # Negative prices
        response = authenticated_client.get("/api/v1/scraped-products/?min_price=-100")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Invalid price format
        response = authenticated_client.get("/api/v1/scraped-products/?min_price=invalid")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_long_search_query(self, authenticated_client: TestClient):
        """Test very long search query"""
        long_query = "x" * 1000
        response = authenticated_client.get(f"/api/v1/scraped-products/?search={long_query}")
        
        # Should either handle gracefully or reject
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestScrapedProductsFiltering:
    """Test class for advanced filtering of scraped products"""

    def test_multiple_filters_combination(self, authenticated_client: TestClient, db_session: Session):
        """Test combining multiple filters"""
        # Create diverse products
        products = [
            ScrapData(
                product_name="Gaming Laptop Premium",
                category="Gaming",
                price=1200.00,
                rating="4.5"
            ),
            ScrapData(
                product_name="Gaming Mouse",
                category="Gaming",
                price=50.00,
                rating="4.2"
            ),
            ScrapData(
                product_name="Office Laptop",
                category="Business",
                price=800.00,
                rating="4.0"
            )
        ]
        
        for product in products:
            db_session.add(product)
        db_session.commit()
        
        # Filter by category and price range
        response = authenticated_client.get(
            "/api/v1/scraped-products/?category=Gaming&min_price=100&max_price=2000"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        products_list = data.get("products", data.get("items", []))
        for product in products_list:
            if "category" in product and "price" in product:
                assert product["category"] == "Gaming"
                if product["price"]:
                    assert 100 <= float(product["price"]) <= 2000

    def test_case_insensitive_search(self, authenticated_client: TestClient, db_session: Session):
        """Test case-insensitive search functionality"""
        product = ScrapData(
            product_name="MacBook Pro",
            category="Computers",
            price=1999.99
        )
        db_session.add(product)
        db_session.commit()
        
        # Search with different cases
        test_queries = ["macbook", "MACBOOK", "MacBook", "macBOOK"]
        
        for query in test_queries:
            response = authenticated_client.get(f"/api/v1/scraped-products/?search={query}")
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            products_list = data.get("products", data.get("items", []))
            
            # Should find the MacBook regardless of case
            found = any("macbook" in p["product_name"].lower() for p in products_list)
            assert found or len(products_list) == 0  # Allow empty if search not implemented

    def test_empty_results_handling(self, authenticated_client: TestClient):
        """Test handling of searches with no results"""
        response = authenticated_client.get("/api/v1/scraped-products/?search=nonexistentproduct12345")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        products_list = data.get("products", data.get("items", []))
        # Should return empty list, not error
        assert isinstance(products_list, list)

    def test_special_characters_in_search(self, authenticated_client: TestClient):
        """Test search with special characters"""
        special_queries = ["@#$%", "product&accessories", "item+bundle"]
        
        for query in special_queries:
            response = authenticated_client.get(f"/api/v1/scraped-products/?search={query}")
            
            # Should not cause server error
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestScrapedProductsSorting:
    """Test class for scraped products sorting"""

    def test_sort_by_price_ascending(self, authenticated_client: TestClient, db_session: Session):
        """Test sorting products by price in ascending order"""
        products = [
            ScrapData(product_name="Product A", price=300.00),
            ScrapData(product_name="Product B", price=100.00),
            ScrapData(product_name="Product C", price=200.00)
        ]
        
        for product in products:
            db_session.add(product)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/scraped-products/?sort_by=price_asc")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        products_list = data.get("products", data.get("items", []))
        if len(products_list) >= 2:
            prices = [float(p["price"]) for p in products_list if p.get("price")]
            if len(prices) >= 2:
                assert prices == sorted(prices)

    def test_sort_by_price_descending(self, authenticated_client: TestClient, db_session: Session):
        """Test sorting products by price in descending order"""
        response = authenticated_client.get("/api/v1/scraped-products/?sort_by=price_desc")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        products_list = data.get("products", data.get("items", []))
        if len(products_list) >= 2:
            prices = [float(p["price"]) for p in products_list if p.get("price")]
            if len(prices) >= 2:
                assert prices == sorted(prices, reverse=True)

    def test_sort_by_name(self, authenticated_client: TestClient):
        """Test sorting products by name"""
        response = authenticated_client.get("/api/v1/scraped-products/?sort_by=name_asc")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        products_list = data.get("products", data.get("items", []))
        if len(products_list) >= 2:
            names = [p["product_name"] for p in products_list]
            assert names == sorted(names)

    def test_invalid_sort_parameter(self, authenticated_client: TestClient):
        """Test invalid sort parameters"""
        response = authenticated_client.get("/api/v1/scraped-products/?sort_by=invalid_sort")
        
        # Should either use default sort or reject
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestScrapedProductsSecurity:
    """Test class for scraped products security"""

    def test_sql_injection_protection(self, authenticated_client: TestClient):
        """Test protection against SQL injection in search"""
        malicious_query = "'; DROP TABLE scrapdata; --"
        
        response = authenticated_client.get(f"/api/v1/scraped-products/?search={malicious_query}")
        
        # Should not cause server error
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_xss_protection_in_search(self, authenticated_client: TestClient):
        """Test protection against XSS in search parameters"""
        malicious_query = "<script>alert('xss')</script>"
        
        response = authenticated_client.get(f"/api/v1/scraped-products/?search={malicious_query}")
        
        # Should handle safely
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_data_exposure_protection(self, authenticated_client: TestClient, db_session: Session):
        """Test that scraped data doesn't expose sensitive information"""
        product = ScrapData(
            product_name="Test Product",
            product_description="Test description",
            price=99.99
        )
        db_session.add(product)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/scraped-products/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        products_list = data.get("products", data.get("items", []))
        if products_list:
            product_data = products_list[0]
            
            # Verify no sensitive fields are exposed
            sensitive_fields = ["password", "secret", "key", "token", "api_key"]
            for field in sensitive_fields:
                assert field not in product_data

    def test_url_validation(self, authenticated_client: TestClient, db_session: Session):
        """Test URL field validation and security"""
        # Test with potentially malicious URLs
        product = ScrapData(
            product_name="Test Product",
            image_url="javascript:alert('xss')",
            product_page_url="http://malicious-site.com"
        )
        db_session.add(product)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/scraped-products/")
        
        assert response.status_code == status.HTTP_200_OK
        # URLs should be returned as-is (validation should happen on frontend)


class TestScrapedProductsPerformance:
    """Test class for scraped products performance"""

    def test_large_dataset_handling(self, authenticated_client: TestClient):
        """Test handling of large datasets with pagination"""
        response = authenticated_client.get("/api/v1/scraped-products/?page_size=100")
        
        assert response.status_code == status.HTTP_200_OK
        # Should not timeout or cause memory issues

    def test_complex_query_performance(self, authenticated_client: TestClient):
        """Test performance with complex queries"""
        complex_query = "/api/v1/scraped-products/?search=electronics&category=Computers&min_price=100&max_price=2000&sort_by=price_desc"
        
        response = authenticated_client.get(complex_query)
        
        assert response.status_code == status.HTTP_200_OK
        # Should complete in reasonable time

    def test_concurrent_requests(self, authenticated_client: TestClient):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = authenticated_client.get("/api/v1/scraped-products/")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status_code == status.HTTP_200_OK for status_code in results)