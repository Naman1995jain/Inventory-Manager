import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.services.product_service import ProductService
from app.models import Product, StockMovement, Warehouse
from app.schemas.schemas import ProductCreate, ProductUpdate, PaginationParams


@pytest.mark.unit
class TestProductService:
    """Unit tests for ProductService"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def product_service(self, mock_db):
        """Create ProductService instance with mock database"""
        return ProductService(mock_db)

    def test_create_product_success(self, product_service, mock_db):
        """Test successful product creation"""
        # Arrange
        product_data = ProductCreate(
            name="Test Product",
            sku="TEST001",
            description="Test description",
            unit_price=10.50,
            unit_of_measure="piece",
            category="Test Category"
        )
        user_id = 1

        # Mock SKU doesn't exist
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        mock_db.query.return_value = mock_query

        mock_new_product = Mock(spec=Product)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # Act
        with patch('app.services.product_service.Product') as mock_product_model:
            mock_product_model.return_value = mock_new_product
            result = product_service.create_product(product_data, user_id)

        # Assert
        mock_db.query.assert_called_once_with(Product)
        mock_product_model.assert_called_once_with(
            **product_data.model_dump(),
            created_by=user_id
        )
        mock_db.add.assert_called_once_with(mock_new_product)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_new_product)
        assert result == mock_new_product

    def test_create_product_duplicate_sku(self, product_service, mock_db):
        """Test product creation with duplicate SKU"""
        # Arrange
        product_data = ProductCreate(
            name="Test Product",
            sku="EXISTING001",
            description="Test description"
        )
        user_id = 1

        # Mock existing product with same SKU
        existing_product = Mock(spec=Product)
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = existing_product
        mock_db.query.return_value = mock_query

        # Act & Assert
        with pytest.raises(ValueError, match="Product with this SKU already exists"):
            product_service.create_product(product_data, user_id)

    def test_get_product_exists(self, product_service, mock_db):
        """Test getting product that exists and is active"""
        # Arrange
        product_id = 1
        mock_product = Mock(spec=Product)
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_product
        mock_db.query.return_value = mock_query

        # Act
        result = product_service.get_product(product_id)

        # Assert
        mock_db.query.assert_called_once_with(Product)
        assert result == mock_product

    def test_get_product_not_exists(self, product_service, mock_db):
        """Test getting product that doesn't exist"""
        # Arrange
        product_id = 999
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        mock_db.query.return_value = mock_query

        # Act
        result = product_service.get_product(product_id)

        # Assert
        assert result is None

    @patch.object(ProductService, 'get_product')
    def test_get_product_with_stock_success(self, mock_get_product, product_service, mock_db):
        """Test getting product with stock information"""
        # Arrange
        product_id = 1
        mock_product = Mock(spec=Product)
        mock_get_product.return_value = mock_product

        # Mock warehouse stock query
        mock_stock_data = [
            Mock(id=1, name="Warehouse 1", current_stock=10),
            Mock(id=2, name="Warehouse 2", current_stock=5)
        ]
        
        mock_query = Mock()
        mock_outerjoin = Mock()
        mock_filter = Mock()
        mock_group_by = Mock()
        
        mock_query.outerjoin.return_value = mock_outerjoin
        mock_outerjoin.filter.return_value = mock_filter
        mock_filter.group_by.return_value = mock_group_by
        mock_group_by.all.return_value = mock_stock_data
        mock_db.query.return_value = mock_query

        # Act
        result = product_service.get_product_with_stock(product_id)

        # Assert
        mock_get_product.assert_called_once_with(product_id)
        assert result is not None
        assert result["product"] == mock_product
        assert result["total_stock"] == 15
        assert len(result["warehouse_stock"]) == 2

    @patch.object(ProductService, 'get_product')
    def test_get_product_with_stock_product_not_found(self, mock_get_product, product_service, mock_db):
        """Test getting product with stock when product doesn't exist"""
        # Arrange
        product_id = 999
        mock_get_product.return_value = None

        # Act
        result = product_service.get_product_with_stock(product_id)

        # Assert
        mock_get_product.assert_called_once_with(product_id)
        assert result is None

    def test_get_products_no_filters(self, product_service, mock_db):
        """Test getting products without filters"""
        # Arrange
        params = PaginationParams(page=1, page_size=20)
        
        mock_products = [Mock(spec=Product) for _ in range(3)]
        for i, product in enumerate(mock_products):
            product.id = i + 1
            product.total_stock = i * 10

        # Mock query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_count = Mock()
        mock_order_by = Mock()
        mock_offset = Mock()
        mock_limit = Mock()

        mock_query.filter.return_value = mock_filter
        mock_filter.count.return_value = 3
        mock_filter.order_by.return_value = mock_order_by
        mock_order_by.offset.return_value = mock_offset
        mock_offset.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_products

        mock_db.query.return_value = mock_query

        # Mock stock calculation for each product
        mock_db.query.return_value.filter.return_value.scalar.return_value = 0

        # Act
        products, total = product_service.get_products(params)

        # Assert
        assert len(products) == 3
        assert total == 3
        mock_db.query.assert_called_with(Product)

    def test_get_products_with_search(self, product_service, mock_db):
        """Test getting products with search filter"""
        # Arrange
        params = PaginationParams(page=1, page_size=20, search="test")
        
        # Mock query chain with search
        mock_query = Mock()
        mock_filter1 = Mock()
        mock_filter2 = Mock()
        mock_count = Mock()
        mock_order_by = Mock()
        mock_offset = Mock()
        mock_limit = Mock()

        mock_query.filter.return_value = mock_filter1
        mock_filter1.filter.return_value = mock_filter2
        mock_filter2.count.return_value = 1
        mock_filter2.order_by.return_value = mock_order_by
        mock_order_by.offset.return_value = mock_offset
        mock_offset.limit.return_value = mock_limit
        mock_limit.all.return_value = []

        mock_db.query.return_value = mock_query

        # Act
        products, total = product_service.get_products(params)

        # Assert
        assert len(products) == 0
        assert total == 1

    @patch.object(ProductService, 'get_product')
    def test_update_product_success(self, mock_get_product, product_service, mock_db):
        """Test successful product update"""
        # Arrange
        product_id = 1
        mock_product = Mock(spec=Product)
        mock_product.sku = "OLD001"
        mock_get_product.return_value = mock_product

        update_data = ProductUpdate(
            name="Updated Product",
            sku="NEW001",
            unit_price=20.0
        )

        # Mock SKU uniqueness check
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        mock_db.query.return_value = mock_query

        # Act
        result = product_service.update_product(product_id, update_data)

        # Assert
        mock_get_product.assert_called_once_with(product_id)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_product)
        assert result == mock_product

    @patch.object(ProductService, 'get_product')
    def test_update_product_not_found(self, mock_get_product, product_service, mock_db):
        """Test updating non-existent product"""
        # Arrange
        product_id = 999
        mock_get_product.return_value = None
        update_data = ProductUpdate(name="Updated Product")

        # Act
        result = product_service.update_product(product_id, update_data)

        # Assert
        mock_get_product.assert_called_once_with(product_id)
        assert result is None

    @patch.object(ProductService, 'get_product')
    def test_update_product_duplicate_sku(self, mock_get_product, product_service, mock_db):
        """Test updating product with duplicate SKU"""
        # Arrange
        product_id = 1
        mock_product = Mock(spec=Product)
        mock_product.sku = "OLD001"
        mock_get_product.return_value = mock_product

        update_data = ProductUpdate(sku="EXISTING001")

        # Mock existing product with new SKU
        existing_product = Mock(spec=Product)
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = existing_product
        mock_db.query.return_value = mock_query

        # Act & Assert
        with pytest.raises(ValueError, match="Product with this SKU already exists"):
            product_service.update_product(product_id, update_data)

    @patch.object(ProductService, 'get_product')
    def test_delete_product_success(self, mock_get_product, product_service, mock_db):
        """Test successful product soft deletion"""
        # Arrange
        product_id = 1
        mock_product = Mock(spec=Product)
        mock_get_product.return_value = mock_product

        # Act
        result = product_service.delete_product(product_id)

        # Assert
        mock_get_product.assert_called_once_with(product_id)
        assert mock_product.is_active is False
        mock_db.commit.assert_called_once()
        assert result is True

    @patch.object(ProductService, 'get_product')
    def test_delete_product_not_found(self, mock_get_product, product_service, mock_db):
        """Test deleting non-existent product"""
        # Arrange
        product_id = 999
        mock_get_product.return_value = None

        # Act
        result = product_service.delete_product(product_id)

        # Assert
        mock_get_product.assert_called_once_with(product_id)
        assert result is False