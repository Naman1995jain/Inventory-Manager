import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.stock_service import StockService
from app.models import StockMovement, StockTransfer, Product, Warehouse, MovementType
from app.schemas.schemas import StockMovementCreate, StockTransferCreate, StockTransferUpdate


@pytest.mark.unit
class TestStockService:
    """Unit tests for StockService"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def stock_service(self, mock_db):
        """Create StockService instance with mock database"""
        return StockService(mock_db)

    def test_create_stock_movement_success(self, stock_service, mock_db):
        """Test successful stock movement creation"""
        # Arrange
        movement_data = StockMovementCreate(
            product_id=1,
            warehouse_id=1,
            movement_type=MovementType.PURCHASE,
            quantity=10,
            unit_cost=5.0,
            reference_number="PO001"
        )
        user_id = 1

        # Mock product exists
        mock_product = Mock(spec=Product)
        mock_product.is_active = True
        
        # Mock warehouse exists  
        mock_warehouse = Mock(spec=Warehouse)
        mock_warehouse.is_active = True

        # Mock queries for validation
        mock_product_query = Mock()
        mock_warehouse_query = Mock()
        
        def mock_query_side_effect(model):
            if model == Product:
                return mock_product_query
            elif model == Warehouse:
                return mock_warehouse_query
            return Mock()

        mock_db.query.side_effect = mock_query_side_effect
        
        mock_product_filter = Mock()
        mock_product_query.filter.return_value = mock_product_filter
        mock_product_filter.first.return_value = mock_product
        
        mock_warehouse_filter = Mock()
        mock_warehouse_query.filter.return_value = mock_warehouse_filter  
        mock_warehouse_filter.first.return_value = mock_warehouse

        # Mock new movement creation
        mock_new_movement = Mock(spec=StockMovement)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # Act
        with patch('app.services.stock_service.StockMovement') as mock_movement_model:
            mock_movement_model.return_value = mock_new_movement
            result = stock_service.create_stock_movement(movement_data, user_id)

        # Assert
        mock_movement_model.assert_called_once_with(
            **movement_data.model_dump(),
            total_cost=50.0,  # unit_cost * quantity
            created_by=user_id
        )
        mock_db.add.assert_called_once_with(mock_new_movement)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_new_movement)
        assert result == mock_new_movement

    def test_create_stock_movement_product_not_found(self, stock_service, mock_db):
        """Test stock movement creation with non-existent product"""
        # Arrange
        movement_data = StockMovementCreate(
            product_id=999,
            warehouse_id=1,
            movement_type=MovementType.PURCHASE,
            quantity=10
        )
        user_id = 1

        # Mock product doesn't exist
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        mock_db.query.return_value = mock_query

        # Act & Assert
        with pytest.raises(ValueError, match="Product not found or inactive"):
            stock_service.create_stock_movement(movement_data, user_id)

    def test_create_stock_movement_warehouse_not_found(self, stock_service, mock_db):
        """Test stock movement creation with non-existent warehouse"""
        # Arrange
        movement_data = StockMovementCreate(
            product_id=1,
            warehouse_id=999,
            movement_type=MovementType.PURCHASE,
            quantity=10
        )
        user_id = 1

        # Mock product exists but warehouse doesn't
        mock_product = Mock(spec=Product)
        mock_product.is_active = True

        def mock_query_side_effect(model):
            if model == Product:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = mock_product
                return mock_query
            elif model == Warehouse:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = None
                return mock_query

        mock_db.query.side_effect = mock_query_side_effect

        # Act & Assert
        with pytest.raises(ValueError, match="Warehouse not found or inactive"):
            stock_service.create_stock_movement(movement_data, user_id)

    @patch.object(StockService, 'get_product_stock_in_warehouse')
    def test_create_stock_movement_insufficient_stock(self, mock_get_stock, stock_service, mock_db):
        """Test outbound stock movement with insufficient stock"""
        # Arrange
        movement_data = StockMovementCreate(
            product_id=1,
            warehouse_id=1,
            movement_type=MovementType.SALE,
            quantity=-15  # Trying to remove 15 units
        )
        user_id = 1

        # Mock product and warehouse exist
        mock_product = Mock(spec=Product)
        mock_product.is_active = True
        mock_warehouse = Mock(spec=Warehouse)
        mock_warehouse.is_active = True

        def mock_query_side_effect(model):
            if model == Product:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = mock_product
                return mock_query
            elif model == Warehouse:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = mock_warehouse
                return mock_query

        mock_db.query.side_effect = mock_query_side_effect
        mock_get_stock.return_value = 10  # Only 10 units available

        # Act & Assert
        with pytest.raises(ValueError, match="Insufficient stock"):
            stock_service.create_stock_movement(movement_data, user_id)

    def test_get_product_stock_in_warehouse(self, stock_service, mock_db):
        """Test getting product stock in specific warehouse"""
        # Arrange
        product_id = 1
        warehouse_id = 1
        expected_stock = 25

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.scalar.return_value = expected_stock
        mock_db.query.return_value = mock_query

        # Act
        result = stock_service.get_product_stock_in_warehouse(product_id, warehouse_id)

        # Assert
        assert result == expected_stock

    def test_get_product_stock_in_warehouse_no_stock(self, stock_service, mock_db):
        """Test getting product stock when no stock exists"""
        # Arrange
        product_id = 1
        warehouse_id = 1

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.scalar.return_value = None
        mock_db.query.return_value = mock_query

        # Act
        result = stock_service.get_product_stock_in_warehouse(product_id, warehouse_id)

        # Assert
        assert result == 0

    def test_create_stock_transfer_success(self, stock_service, mock_db):
        """Test successful stock transfer creation"""
        # Arrange
        transfer_data = StockTransferCreate(
            product_id=1,
            from_warehouse_id=1,
            to_warehouse_id=2,
            quantity=5,
            transfer_reference="TRANS001"
        )
        user_id = 1

        # Mock product exists
        mock_product = Mock(spec=Product)
        mock_product.is_active = True
        
        # Mock warehouses exist
        mock_from_warehouse = Mock(spec=Warehouse)
        mock_from_warehouse.is_active = True
        mock_to_warehouse = Mock(spec=Warehouse)  
        mock_to_warehouse.is_active = True

        def mock_query_side_effect(model):
            if model == Product:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = mock_product
                return mock_query
            elif model == Warehouse:
                # First call for from_warehouse, second for to_warehouse
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                if not hasattr(mock_query, '_call_count'):
                    mock_query._call_count = 0
                mock_query._call_count += 1
                
                if mock_query._call_count == 1:
                    mock_filter.first.return_value = mock_from_warehouse
                else:
                    mock_filter.first.return_value = mock_to_warehouse
                return mock_query

        mock_db.query.side_effect = mock_query_side_effect

        # Mock stock check
        with patch.object(stock_service, 'get_product_stock_in_warehouse') as mock_get_stock:
            mock_get_stock.return_value = 10  # Sufficient stock

            mock_new_transfer = Mock(spec=StockTransfer)
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            # Act
            with patch('app.services.stock_service.StockTransfer') as mock_transfer_model:
                mock_transfer_model.return_value = mock_new_transfer
                result = stock_service.create_stock_transfer(transfer_data, user_id)

        # Assert
        mock_get_stock.assert_called_once_with(1, 1)
        mock_transfer_model.assert_called_once_with(
            **transfer_data.model_dump(),
            status="pending",
            created_by=user_id
        )
        assert result == mock_new_transfer

    def test_create_stock_transfer_same_warehouse(self, stock_service, mock_db):
        """Test stock transfer creation with same source and destination"""
        # Arrange
        transfer_data = StockTransferCreate(
            product_id=1,
            from_warehouse_id=1,
            to_warehouse_id=1,  # Same as from_warehouse_id
            quantity=5
        )
        user_id = 1

        # Act & Assert
        with pytest.raises(ValueError, match="Source and destination warehouses must be different"):
            stock_service.create_stock_transfer(transfer_data, user_id)

    @patch('app.services.stock_service.datetime')
    def test_complete_stock_transfer_success(self, mock_datetime, stock_service, mock_db):
        """Test successful stock transfer completion"""
        # Arrange
        transfer_id = 1
        user_id = 1
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now

        mock_transfer = Mock(spec=StockTransfer)
        mock_transfer.id = transfer_id
        mock_transfer.status = "pending"
        mock_transfer.product_id = 1
        mock_transfer.from_warehouse_id = 1
        mock_transfer.to_warehouse_id = 2
        mock_transfer.quantity = 5
        mock_transfer.notes = "Test transfer"

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_transfer
        mock_db.query.return_value = mock_query

        # Mock stock check
        with patch.object(stock_service, 'get_product_stock_in_warehouse') as mock_get_stock:
            mock_get_stock.return_value = 10  # Sufficient stock

            mock_db.add = Mock()
            mock_db.commit = Mock()
            mock_db.refresh = Mock()

            # Act
            result = stock_service.complete_stock_transfer(transfer_id, user_id)

        # Assert
        assert result == mock_transfer
        assert mock_transfer.status == "completed"
        assert mock_transfer.completed_at == mock_now
        assert mock_db.add.call_count == 2  # Two stock movements
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_transfer)

    def test_complete_stock_transfer_not_found(self, stock_service, mock_db):
        """Test completing non-existent stock transfer"""
        # Arrange
        transfer_id = 999
        user_id = 1

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        mock_db.query.return_value = mock_query

        # Act
        result = stock_service.complete_stock_transfer(transfer_id, user_id)

        # Assert
        assert result is None

    def test_complete_stock_transfer_not_pending(self, stock_service, mock_db):
        """Test completing stock transfer that's not pending"""
        # Arrange
        transfer_id = 1
        user_id = 1

        mock_transfer = Mock(spec=StockTransfer)
        mock_transfer.status = "completed"

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_transfer
        mock_db.query.return_value = mock_query

        # Act & Assert
        with pytest.raises(ValueError, match="Transfer is not in pending status"):
            stock_service.complete_stock_transfer(transfer_id, user_id)

    def test_cancel_stock_transfer_success(self, stock_service, mock_db):
        """Test successful stock transfer cancellation"""
        # Arrange
        transfer_id = 1

        mock_transfer = Mock(spec=StockTransfer)
        mock_transfer.status = "pending"

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_transfer
        mock_db.query.return_value = mock_query

        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        # Act
        result = stock_service.cancel_stock_transfer(transfer_id)

        # Assert
        assert result == mock_transfer
        assert mock_transfer.status == "cancelled"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_transfer)

    def test_cancel_stock_transfer_not_pending(self, stock_service, mock_db):
        """Test cancelling stock transfer that's not pending"""
        # Arrange
        transfer_id = 1

        mock_transfer = Mock(spec=StockTransfer)
        mock_transfer.status = "completed"

        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_transfer
        mock_db.query.return_value = mock_query

        # Act & Assert
        with pytest.raises(ValueError, match="Only pending transfers can be cancelled"):
            stock_service.cancel_stock_transfer(transfer_id)

    # Tests for new quantity calculation logic
    def test_calculate_movement_quantity_purchase(self, stock_service, mock_db):
        """Test quantity calculation for PURCHASE movement - should be positive"""
        # Act
        result = stock_service._calculate_movement_quantity(MovementType.PURCHASE, 10)
        
        # Assert
        assert result == 10  # Purchase should add to inventory (positive)

    def test_calculate_movement_quantity_sale(self, stock_service, mock_db):
        """Test quantity calculation for SALE movement - should be negative"""
        # Act
        result = stock_service._calculate_movement_quantity(MovementType.SALE, 10)
        
        # Assert
        assert result == -10  # Sale should subtract from inventory (negative)

    def test_calculate_movement_quantity_return(self, stock_service, mock_db):
        """Test quantity calculation for RETURN movement - should be positive"""
        # Act
        result = stock_service._calculate_movement_quantity(MovementType.RETURN, 5)
        
        # Assert
        assert result == 5  # Return should add to inventory (positive)

    def test_calculate_movement_quantity_damaged(self, stock_service, mock_db):
        """Test quantity calculation for DAMAGED movement - should be negative"""
        # Act
        result = stock_service._calculate_movement_quantity(MovementType.DAMAGED, 3)
        
        # Assert
        assert result == -3  # Damaged should subtract from inventory (negative)

    def test_calculate_movement_quantity_transfer_in(self, stock_service, mock_db):
        """Test quantity calculation for TRANSFER_IN movement - should be positive"""
        # Act
        result = stock_service._calculate_movement_quantity(MovementType.TRANSFER_IN, 15)
        
        # Assert
        assert result == 15  # Transfer in should add to inventory (positive)

    def test_calculate_movement_quantity_transfer_out(self, stock_service, mock_db):
        """Test quantity calculation for TRANSFER_OUT movement - should be negative"""
        # Act
        result = stock_service._calculate_movement_quantity(MovementType.TRANSFER_OUT, 8)
        
        # Assert
        assert result == -8  # Transfer out should subtract from inventory (negative)

    def test_calculate_movement_quantity_adjustment_positive(self, stock_service, mock_db):
        """Test quantity calculation for ADJUSTMENT movement with positive value"""
        # Act
        result = stock_service._calculate_movement_quantity(MovementType.ADJUSTMENT, 7)
        
        # Assert
        assert result == 7  # Positive adjustment should preserve sign

    def test_calculate_movement_quantity_adjustment_negative(self, stock_service, mock_db):
        """Test quantity calculation for ADJUSTMENT movement with negative value"""
        # Act
        result = stock_service._calculate_movement_quantity(MovementType.ADJUSTMENT, -12)
        
        # Assert
        assert result == -12  # Negative adjustment should preserve sign

    def test_calculate_movement_quantity_with_negative_input(self, stock_service, mock_db):
        """Test that inbound movements convert negative input to positive"""
        # Act
        result = stock_service._calculate_movement_quantity(MovementType.PURCHASE, -5)
        
        # Assert
        assert result == 5  # Should use absolute value for inbound movements

    def test_create_stock_movement_with_sale_logic(self, stock_service, mock_db):
        """Test stock movement creation with SALE type uses correct quantity calculation"""
        # Arrange
        movement_data = StockMovementCreate(
            product_id=1,
            warehouse_id=1,
            movement_type=MovementType.SALE,
            quantity=10,  # Input positive quantity
            unit_cost=5.0,
            reference_number="SALE001"
        )
        user_id = 1

        # Mock product and warehouse exist
        mock_product = Mock(spec=Product)
        mock_product.is_active = True
        mock_warehouse = Mock(spec=Warehouse)
        mock_warehouse.is_active = True

        # Mock current stock check (sufficient stock available)
        with patch.object(stock_service, 'get_product_stock_in_warehouse', return_value=50):
            def mock_query_side_effect(model):
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                
                if model == Product:
                    mock_filter.first.return_value = mock_product
                elif model == Warehouse:
                    mock_filter.first.return_value = mock_warehouse
                return mock_query

            mock_db.query.side_effect = mock_query_side_effect

            # Mock new movement creation
            mock_new_movement = Mock(spec=StockMovement)
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            # Act
            with patch('app.services.stock_service.StockMovement') as mock_movement_model:
                mock_movement_model.return_value = mock_new_movement
                result = stock_service.create_stock_movement(movement_data, user_id)

                # Assert - verify the movement was created with negative quantity for sale
                call_args = mock_movement_model.call_args[1]  # Get keyword arguments
                assert call_args['quantity'] == -10  # Should be negative for sale
                assert call_args['total_cost'] == 50.0  # unit_cost * abs(quantity)
                assert call_args['created_by'] == user_id

    def test_create_stock_movement_insufficient_stock_for_sale(self, stock_service, mock_db):
        """Test stock movement creation fails when insufficient stock for sale"""
        # Arrange
        movement_data = StockMovementCreate(
            product_id=1,
            warehouse_id=1,
            movement_type=MovementType.SALE,
            quantity=100,  # More than available
            reference_number="SALE002"
        )
        user_id = 1

        # Mock product and warehouse exist
        mock_product = Mock(spec=Product)
        mock_product.is_active = True
        mock_warehouse = Mock(spec=Warehouse)
        mock_warehouse.is_active = True

        # Mock current stock check (insufficient stock)
        with patch.object(stock_service, 'get_product_stock_in_warehouse', return_value=50):
            def mock_query_side_effect(model):
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                
                if model == Product:
                    mock_filter.first.return_value = mock_product
                elif model == Warehouse:
                    mock_filter.first.return_value = mock_warehouse
                return mock_query

            mock_db.query.side_effect = mock_query_side_effect

            # Act & Assert
            with pytest.raises(ValueError, match="Insufficient stock"):
                stock_service.create_stock_movement(movement_data, user_id)


@pytest.mark.unit  
class TestStockServiceQuantityCalculation:
    """Test suite for the new quantity calculation logic in StockService"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def stock_service(self, mock_db):
        """Create StockService instance with mock database"""
        return StockService(mock_db)

    def test_calculate_movement_quantity_purchase_positive(self, stock_service):
        """Test PURCHASE movement type makes quantity positive"""
        result = stock_service._calculate_movement_quantity(MovementType.PURCHASE, 10)
        assert result == 10

    def test_calculate_movement_quantity_purchase_negative_input(self, stock_service):
        """Test PURCHASE movement type makes even negative input positive"""
        result = stock_service._calculate_movement_quantity(MovementType.PURCHASE, -10)
        assert result == 10

    def test_calculate_movement_quantity_sale_positive_input(self, stock_service):
        """Test SALE movement type makes positive input negative"""
        result = stock_service._calculate_movement_quantity(MovementType.SALE, 10)
        assert result == -10

    def test_calculate_movement_quantity_sale_negative_input(self, stock_service):
        """Test SALE movement type keeps negative input negative"""
        result = stock_service._calculate_movement_quantity(MovementType.SALE, -10)
        assert result == -10

    def test_calculate_movement_quantity_return_positive(self, stock_service):
        """Test RETURN movement type makes quantity positive"""
        result = stock_service._calculate_movement_quantity(MovementType.RETURN, 5)
        assert result == 5

    def test_calculate_movement_quantity_return_negative_input(self, stock_service):
        """Test RETURN movement type makes negative input positive"""
        result = stock_service._calculate_movement_quantity(MovementType.RETURN, -5)
        assert result == 5

    def test_calculate_movement_quantity_damaged_positive_input(self, stock_service):
        """Test DAMAGED movement type makes positive input negative"""
        result = stock_service._calculate_movement_quantity(MovementType.DAMAGED, 3)
        assert result == -3

    def test_calculate_movement_quantity_damaged_negative_input(self, stock_service):
        """Test DAMAGED movement type keeps negative input negative"""
        result = stock_service._calculate_movement_quantity(MovementType.DAMAGED, -3)
        assert result == -3

    def test_calculate_movement_quantity_transfer_in_positive(self, stock_service):
        """Test TRANSFER_IN movement type makes quantity positive"""
        result = stock_service._calculate_movement_quantity(MovementType.TRANSFER_IN, 8)
        assert result == 8

    def test_calculate_movement_quantity_transfer_in_negative_input(self, stock_service):
        """Test TRANSFER_IN movement type makes negative input positive"""
        result = stock_service._calculate_movement_quantity(MovementType.TRANSFER_IN, -8)
        assert result == 8

    def test_calculate_movement_quantity_transfer_out_positive_input(self, stock_service):
        """Test TRANSFER_OUT movement type makes positive input negative"""
        result = stock_service._calculate_movement_quantity(MovementType.TRANSFER_OUT, 6)
        assert result == -6

    def test_calculate_movement_quantity_transfer_out_negative_input(self, stock_service):
        """Test TRANSFER_OUT movement type keeps negative input negative"""
        result = stock_service._calculate_movement_quantity(MovementType.TRANSFER_OUT, -6)
        assert result == -6

    def test_calculate_movement_quantity_adjustment_positive(self, stock_service):
        """Test ADJUSTMENT movement type preserves positive input"""
        result = stock_service._calculate_movement_quantity(MovementType.ADJUSTMENT, 7)
        assert result == 7

    def test_calculate_movement_quantity_adjustment_negative(self, stock_service):
        """Test ADJUSTMENT movement type preserves negative input"""
        result = stock_service._calculate_movement_quantity(MovementType.ADJUSTMENT, -7)
        assert result == -7

    def test_calculate_movement_quantity_adjustment_zero(self, stock_service):
        """Test ADJUSTMENT movement type preserves zero input"""
        result = stock_service._calculate_movement_quantity(MovementType.ADJUSTMENT, 0)
        assert result == 0

    @patch.object(StockService, 'get_product_stock_in_warehouse')
    def test_create_stock_movement_with_quantity_calculation(self, mock_get_stock, stock_service, mock_db):
        """Test that create_stock_movement correctly applies quantity calculation for SALE"""
        # Arrange
        movement_data = StockMovementCreate(
            product_id=1,
            warehouse_id=1,
            movement_type=MovementType.SALE,
            quantity=10,  # User enters positive quantity
            unit_cost=5.0,
            reference_number="SALE001"
        )
        user_id = 1

        # Mock product and warehouse exist
        mock_product = Mock(spec=Product)
        mock_product.is_active = True
        mock_warehouse = Mock(spec=Warehouse)
        mock_warehouse.is_active = True

        # Mock current stock is sufficient
        mock_get_stock.return_value = 15  # More than the 10 we want to sell

        # Setup mock query responses
        def mock_query_side_effect(model):
            if model == Product:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = mock_product
                return mock_query
            elif model == Warehouse:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = mock_warehouse
                return mock_query
            return Mock()

        mock_db.query.side_effect = mock_query_side_effect

        # Mock movement creation
        mock_new_movement = Mock(spec=StockMovement)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # Act
        with patch('app.services.stock_service.StockMovement') as mock_movement_model:
            mock_movement_model.return_value = mock_new_movement
            result = stock_service.create_stock_movement(movement_data, user_id)

        # Assert - verify that the quantity was made negative for SALE movement
        expected_call_kwargs = {
            'product_id': 1,
            'warehouse_id': 1,
            'movement_type': MovementType.SALE,
            'quantity': -10,  # Should be negative for SALE
            'unit_cost': 5.0,
            'reference_number': 'SALE001',
            'notes': '',
            'total_cost': 50.0,  # unit_cost * abs(quantity)
            'created_by': user_id
        }
        mock_movement_model.assert_called_once_with(**expected_call_kwargs)
        assert result == mock_new_movement

    def test_calculate_movement_quantity_purchase(self, stock_service):
        """Test quantity calculation for purchase movements (should be positive)"""
        result = stock_service._calculate_movement_quantity(MovementType.PURCHASE, 10)
        assert result == 10  # Purchase adds to inventory

    def test_calculate_movement_quantity_sale(self, stock_service):
        """Test quantity calculation for sale movements (should be negative)"""
        result = stock_service._calculate_movement_quantity(MovementType.SALE, 10)
        assert result == -10  # Sale subtracts from inventory

    def test_calculate_movement_quantity_return(self, stock_service):
        """Test quantity calculation for return movements (should be positive)"""
        result = stock_service._calculate_movement_quantity(MovementType.RETURN, 5)
        assert result == 5  # Return adds to inventory

    def test_calculate_movement_quantity_damaged(self, stock_service):
        """Test quantity calculation for damaged movements (should be negative)"""
        result = stock_service._calculate_movement_quantity(MovementType.DAMAGED, 3)
        assert result == -3  # Damaged subtracts from inventory

    def test_calculate_movement_quantity_transfer_in(self, stock_service):
        """Test quantity calculation for transfer in movements (should be positive)"""
        result = stock_service._calculate_movement_quantity(MovementType.TRANSFER_IN, 8)
        assert result == 8  # Transfer in adds to inventory

    def test_calculate_movement_quantity_transfer_out(self, stock_service):
        """Test quantity calculation for transfer out movements (should be negative)"""
        result = stock_service._calculate_movement_quantity(MovementType.TRANSFER_OUT, 12)
        assert result == -12  # Transfer out subtracts from inventory

    def test_calculate_movement_quantity_adjustment_positive(self, stock_service):
        """Test quantity calculation for positive adjustment movements"""
        result = stock_service._calculate_movement_quantity(MovementType.ADJUSTMENT, 7)
        assert result == 7  # Positive adjustment adds to inventory

    def test_calculate_movement_quantity_adjustment_negative(self, stock_service):
        """Test quantity calculation for negative adjustment movements"""
        result = stock_service._calculate_movement_quantity(MovementType.ADJUSTMENT, -4)
        assert result == -4  # Negative adjustment subtracts from inventory

    def test_calculate_movement_quantity_handles_negative_input_for_outbound(self, stock_service):
        """Test that outbound movements handle negative input correctly (convert to absolute then make negative)"""
        # Even if user enters -10 for a sale, it should still be -10 (negative for outbound)
        result = stock_service._calculate_movement_quantity(MovementType.SALE, -10)
        assert result == -10  # Still negative for outbound

    def test_calculate_movement_quantity_handles_negative_input_for_inbound(self, stock_service):
        """Test that inbound movements handle negative input correctly (convert to absolute then make positive)"""
        # Even if user enters -10 for a purchase, it should be 10 (positive for inbound)
        result = stock_service._calculate_movement_quantity(MovementType.PURCHASE, -10)
        assert result == 10  # Converted to positive for inbound

    def test_create_stock_movement_with_sale_applies_correct_quantity(self, stock_service, mock_db):
        """Test that sale movements apply negative quantity correctly"""
        # Arrange
        movement_data = StockMovementCreate(
            product_id=1,
            warehouse_id=1,
            movement_type=MovementType.SALE,
            quantity=5,  # User enters positive 5
            unit_cost=10.0,
            reference_number="SALE001"
        )
        user_id = 1

        # Setup mocks for valid product and warehouse
        mock_product = Mock(spec=Product)
        mock_product.is_active = True
        mock_warehouse = Mock(spec=Warehouse)
        mock_warehouse.is_active = True

        def mock_query_side_effect(model):
            if model == Product:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = mock_product
                return mock_query
            elif model == Warehouse:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = mock_warehouse
                return mock_query
            return Mock()

        mock_db.query.side_effect = mock_query_side_effect

        # Mock sufficient stock check
        with patch.object(stock_service, 'get_product_stock_in_warehouse', return_value=10):
            mock_new_movement = Mock(spec=StockMovement)
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None

            # Act
            with patch('app.services.stock_service.StockMovement') as mock_movement_model:
                mock_movement_model.return_value = mock_new_movement
                result = stock_service.create_stock_movement(movement_data, user_id)

                # Assert that the movement was created with negative quantity for sale
                expected_call_kwargs = {
                    'product_id': 1,
                    'warehouse_id': 1,
                    'movement_type': MovementType.SALE,
                    'quantity': -5,  # Should be negative for sale
                    'unit_cost': 10.0,
                    'reference_number': 'SALE001',
                    'notes': '',
                    'total_cost': 50.0,
                    'created_by': user_id
                }
                mock_movement_model.assert_called_once_with(**expected_call_kwargs)

    def test_create_stock_movement_with_purchase_applies_correct_quantity(self, stock_service, mock_db):
        """Test that purchase movements apply positive quantity correctly"""
        # Arrange
        movement_data = StockMovementCreate(
            product_id=1,
            warehouse_id=1,
            movement_type=MovementType.PURCHASE,
            quantity=8,  # User enters positive 8
            unit_cost=15.0,
            reference_number="PO001"
        )
        user_id = 1

        # Setup mocks for valid product and warehouse
        mock_product = Mock(spec=Product)
        mock_product.is_active = True
        mock_warehouse = Mock(spec=Warehouse)
        mock_warehouse.is_active = True

        def mock_query_side_effect(model):
            if model == Product:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = mock_product
                return mock_query
            elif model == Warehouse:
                mock_query = Mock()
                mock_filter = Mock()
                mock_query.filter.return_value = mock_filter
                mock_filter.first.return_value = mock_warehouse
                return mock_query
            return Mock()

        mock_db.query.side_effect = mock_query_side_effect
        mock_new_movement = Mock(spec=StockMovement)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # Act
        with patch('app.services.stock_service.StockMovement') as mock_movement_model:
            mock_movement_model.return_value = mock_new_movement
            result = stock_service.create_stock_movement(movement_data, user_id)

            # Assert that the movement was created with positive quantity for purchase
            expected_call_kwargs = {
                'product_id': 1,
                'warehouse_id': 1,
                'movement_type': MovementType.PURCHASE,
                'quantity': 8,  # Should remain positive for purchase
                'unit_cost': 15.0,
                'reference_number': 'PO001',
                'notes': '',
                'total_cost': 120.0,
                'created_by': user_id
            }
            mock_movement_model.assert_called_once_with(**expected_call_kwargs)