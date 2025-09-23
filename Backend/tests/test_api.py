import pytest
import pytest_asyncio
from httpx import AsyncClient
from main import app

class TestAuthAPI:
    """Test authentication API endpoints"""
    
    @pytest_asyncio.async_
    async def test_register_user(self, client: AsyncClient, clean_db, sample_user_data):
        """Test user registration"""
        response = await client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert data["full_name"] == sample_user_data["full_name"]
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "id" in data
        assert "created_at" in data
    
    @pytest_asyncio.async_
    async def test_register_duplicate_username(self, client: AsyncClient, clean_db, sample_user_data):
        """Test registering with duplicate username"""
        # Register first user
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Try to register with same username
        duplicate_data = sample_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        
        response = await client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    @pytest_asyncio.async_
    async def test_login_success(self, client: AsyncClient, clean_db, sample_user_data):
        """Test successful login"""
        # Register user first
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,  # Form data for OAuth2PasswordRequestForm
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest_asyncio.async_
    async def test_login_json_success(self, client: AsyncClient, clean_db, sample_user_data):
        """Test successful login with JSON payload"""
        # Register user first
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login with JSON
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        response = await client.post("/api/v1/auth/login-json", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest_asyncio.async_
    async def test_login_wrong_password(self, client: AsyncClient, clean_db, sample_user_data):
        """Test login with wrong password"""
        # Register user first
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Try to login with wrong password
        login_data = {
            "username": sample_user_data["username"],
            "password": "wrongpassword"
        }
        
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    @pytest_asyncio.async_
    async def test_login_nonexistent_user(self, client: AsyncClient, clean_db):
        """Test login with nonexistent user"""
        login_data = {
            "username": "nonexistent",
            "password": "password"
        }
        
        response = await client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

class TestProductAPI:
    """Test product API endpoints"""
    
    async def get_auth_headers(self, client: AsyncClient, user_data):
        """Helper to get authentication headers"""
        # Register and login
        await client.post("/api/v1/auth/register", json=user_data)
        
        login_response = await client.post("/api/v1/auth/login-json", json={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest_asyncio.async_
    async def test_create_product(self, client: AsyncClient, clean_db, sample_user_data, sample_product_data):
        """Test creating a product"""
        headers = await self.get_auth_headers(client, sample_user_data)
        
        response = await client.post(
            "/api/v1/products/",
            json=sample_product_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_product_data["name"]
        assert data["sku"] == sample_product_data["sku"]
        assert data["is_active"] is True
        assert "id" in data
    
    @pytest_asyncio.async_
    async def test_create_product_unauthorized(self, client: AsyncClient, clean_db, sample_product_data):
        """Test creating a product without authentication"""
        response = await client.post("/api/v1/products/", json=sample_product_data)
        
        assert response.status_code == 401
    
    @pytest_asyncio.async_
    async def test_list_products(self, client: AsyncClient, clean_db, sample_user_data, sample_product_data):
        """Test listing products"""
        headers = await self.get_auth_headers(client, sample_user_data)
        
        # Create a product first
        await client.post(
            "/api/v1/products/",
            json=sample_product_data,
            headers=headers
        )
        
        # List products
        response = await client.get("/api/v1/products/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert len(data["items"]) == 1
        assert data["total"] == 1
    
    @pytest_asyncio.async_
    async def test_get_product(self, client: AsyncClient, clean_db, sample_user_data, sample_product_data):
        """Test getting a specific product"""
        headers = await self.get_auth_headers(client, sample_user_data)
        
        # Create a product first
        create_response = await client.post(
            "/api/v1/products/",
            json=sample_product_data,
            headers=headers
        )
        product_id = create_response.json()["id"]
        
        # Get the product
        response = await client.get(f"/api/v1/products/{product_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == sample_product_data["name"]
        assert "total_stock" in data
        assert "warehouse_stock" in data
    
    @pytest_asyncio.async_
    async def test_update_product(self, client: AsyncClient, clean_db, sample_user_data, sample_product_data):
        """Test updating a product"""
        headers = await self.get_auth_headers(client, sample_user_data)
        
        # Create a product first
        create_response = await client.post(
            "/api/v1/products/",
            json=sample_product_data,
            headers=headers
        )
        product_id = create_response.json()["id"]
        
        # Update the product
        update_data = {"name": "Updated Product Name"}
        response = await client.put(
            f"/api/v1/products/{product_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product Name"
        assert data["sku"] == sample_product_data["sku"]  # Should remain unchanged
    
    @pytest_asyncio.async_
    async def test_delete_product(self, client: AsyncClient, clean_db, sample_user_data, sample_product_data):
        """Test deleting a product"""
        headers = await self.get_auth_headers(client, sample_user_data)
        
        # Create a product first
        create_response = await client.post(
            "/api/v1/products/",
            json=sample_product_data,
            headers=headers
        )
        product_id = create_response.json()["id"]
        
        # Delete the product
        response = await client.delete(f"/api/v1/products/{product_id}", headers=headers)
        
        assert response.status_code == 204
        
        # Verify product is not found
        get_response = await client.get(f"/api/v1/products/{product_id}", headers=headers)
        assert get_response.status_code == 404