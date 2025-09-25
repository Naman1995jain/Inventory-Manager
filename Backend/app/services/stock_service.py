from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from typing import Optional, List, Tuple
from datetime import datetime
from app.models import StockMovement, StockTransfer, Product, Warehouse, MovementType
from app.schemas.schemas import StockMovementCreate, StockTransferCreate, StockTransferUpdate, PaginationParams

class StockService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_stock_movement(self, movement_data: StockMovementCreate, user_id: int) -> StockMovement:
        """Create a new stock movement with proper quantity handling based on movement type"""
        # Validate product and warehouse exist
        product = self.db.query(Product).filter(
            and_(Product.id == movement_data.product_id, Product.is_active == True)
        ).first()
        if not product:
            raise ValueError("Product not found or inactive")
        
        warehouse = self.db.query(Warehouse).filter(
            and_(Warehouse.id == movement_data.warehouse_id, Warehouse.is_active == True)
        ).first()
        if not warehouse:
            raise ValueError("Warehouse not found or inactive")
        
        # Calculate the actual quantity based on movement type
        actual_quantity = self._calculate_movement_quantity(
            movement_data.movement_type, 
            movement_data.quantity
        )
        
        # For outbound movements, check if sufficient stock is available
        if actual_quantity < 0:
            current_stock = self.get_product_stock_in_warehouse(
                movement_data.product_id, 
                movement_data.warehouse_id
            )
            if current_stock + actual_quantity < 0:
                raise ValueError(f"Insufficient stock. Available: {current_stock}, Requested: {abs(actual_quantity)}")
        
        # Calculate total cost using absolute quantity
        total_cost = None
        if movement_data.unit_cost is not None:
            total_cost = movement_data.unit_cost * abs(actual_quantity)
        
        # Create movement with calculated quantity
        movement_dict = movement_data.model_dump()
        movement_dict['quantity'] = actual_quantity
        
        db_movement = StockMovement(
            **movement_dict,
            total_cost=total_cost,
            created_by=user_id
        )
        
        self.db.add(db_movement)
        self.db.commit()
        self.db.refresh(db_movement)
        return db_movement
    
    def _calculate_movement_quantity(self, movement_type: MovementType, input_quantity: int) -> int:
        """
        Calculate the actual quantity for stock movement based on movement type.
        
        Business Logic:
        - Inbound movements (PURCHASE, RETURN, TRANSFER_IN): Always positive (add to inventory)
        - Outbound movements (SALE, DAMAGED, TRANSFER_OUT): Always negative (subtract from inventory)  
        - ADJUSTMENT: Preserves sign from input (can be positive or negative)
        
        Args:
            movement_type: The type of movement
            input_quantity: The quantity entered by user (should always be positive except for adjustments)
            
        Returns:
            The calculated quantity with proper sign for inventory calculation
        """
        # Use absolute value to ensure we work with positive numbers for most cases
        abs_quantity = abs(input_quantity)
        
        # Define inbound movement types (add to inventory)
        inbound_types = {MovementType.PURCHASE, MovementType.RETURN, MovementType.TRANSFER_IN}
        
        # Define outbound movement types (subtract from inventory)
        outbound_types = {MovementType.SALE, MovementType.DAMAGED, MovementType.TRANSFER_OUT}
        
        if movement_type in inbound_types:
            # Inbound movements are always positive
            return abs_quantity
        elif movement_type in outbound_types:
            # Outbound movements are always negative
            return -abs_quantity
        elif movement_type == MovementType.ADJUSTMENT:
            # Adjustments preserve the original sign (can be positive or negative)
            return input_quantity
        else:
            # Default case (should not happen with current enum)
            raise ValueError(f"Unknown movement type: {movement_type}")
    
    def get_product_stock_in_warehouse(self, product_id: int, warehouse_id: int) -> int:
        """Get current stock of a product in a specific warehouse"""
        result = self.db.query(
            func.coalesce(func.sum(StockMovement.quantity), 0)
        ).filter(
            and_(
                StockMovement.product_id == product_id,
                StockMovement.warehouse_id == warehouse_id
            )
        ).scalar()
        
        return result or 0
    
    def get_stock_movements(self, params: PaginationParams) -> Tuple[List[StockMovement], int]:
        """Get paginated list of stock movements"""
        query = self.db.query(StockMovement)
        
        # Apply search filter
        if params.search:
            search_term = f"%{params.search}%"
            query = query.join(Product).join(Warehouse).filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Warehouse.name.ilike(search_term),
                    StockMovement.reference_number.ilike(search_term),
                    StockMovement.notes.ilike(search_term)
                )
            )
        
        # Apply date filters
        if params.created_from_date:
            query = query.filter(StockMovement.created_at >= params.created_from_date)
        
        if params.created_to_date:
            query = query.filter(StockMovement.created_at <= params.created_to_date)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if params.sort_by:
            if params.sort_by == "created_asc":
                query = query.order_by(StockMovement.created_at.asc())
            elif params.sort_by == "created_desc":
                query = query.order_by(StockMovement.created_at.desc())
        else:
            query = query.order_by(StockMovement.created_at.desc())
        
        # Apply pagination
        offset = (params.page - 1) * params.page_size
        movements = query.offset(offset).limit(params.page_size).all()
        
        return movements, total
    
    def create_stock_transfer(self, transfer_data: StockTransferCreate, user_id: int) -> StockTransfer:
        """Create a new stock transfer"""
        # Validate product exists
        product = self.db.query(Product).filter(
            and_(Product.id == transfer_data.product_id, Product.is_active == True)
        ).first()
        if not product:
            raise ValueError("Product not found or inactive")
        
        # Validate warehouses exist and are different
        if transfer_data.from_warehouse_id == transfer_data.to_warehouse_id:
            raise ValueError("Source and destination warehouses must be different")
        
        from_warehouse = self.db.query(Warehouse).filter(
            and_(Warehouse.id == transfer_data.from_warehouse_id, Warehouse.is_active == True)
        ).first()
        if not from_warehouse:
            raise ValueError("Source warehouse not found or inactive")
        
        to_warehouse = self.db.query(Warehouse).filter(
            and_(Warehouse.id == transfer_data.to_warehouse_id, Warehouse.is_active == True)
        ).first()
        if not to_warehouse:
            raise ValueError("Destination warehouse not found or inactive")
        
        # Check if sufficient stock is available in source warehouse
        current_stock = self.get_product_stock_in_warehouse(
            transfer_data.product_id, 
            transfer_data.from_warehouse_id
        )
        if current_stock < transfer_data.quantity:
            raise ValueError(f"Insufficient stock in source warehouse. Available: {current_stock}, Requested: {transfer_data.quantity}")
        
        db_transfer = StockTransfer(
            **transfer_data.model_dump(),
            status="pending",
            created_by=user_id
        )
        
        self.db.add(db_transfer)
        self.db.commit()
        self.db.refresh(db_transfer)
        return db_transfer
    
    def complete_stock_transfer(self, transfer_id: int, user_id: int) -> Optional[StockTransfer]:
        """Complete a stock transfer by creating corresponding stock movements"""
        transfer = self.db.query(StockTransfer).filter(
            StockTransfer.id == transfer_id
        ).first()
        
        if not transfer:
            return None
        
        if transfer.status != "pending":
            raise ValueError("Transfer is not in pending status")
        
        # Check stock availability again (in case it changed)
        current_stock = self.get_product_stock_in_warehouse(
            transfer.product_id, 
            transfer.from_warehouse_id
        )
        if current_stock < transfer.quantity:
            raise ValueError(f"Insufficient stock in source warehouse. Available: {current_stock}, Required: {transfer.quantity}")
        
        try:
            # Create outbound movement from source warehouse using proper quantity calculation
            outbound_quantity = self._calculate_movement_quantity(MovementType.TRANSFER_OUT, transfer.quantity)
            outbound_movement = StockMovement(
                product_id=transfer.product_id,
                warehouse_id=transfer.from_warehouse_id,
                movement_type=MovementType.TRANSFER_OUT,
                quantity=outbound_quantity,
                reference_number=f"TRANSFER-{transfer.id}",
                notes=f"Transfer to warehouse {transfer.to_warehouse_id}: {transfer.notes or ''}",
                created_by=user_id
            )
            
            # Create inbound movement to destination warehouse using proper quantity calculation
            inbound_quantity = self._calculate_movement_quantity(MovementType.TRANSFER_IN, transfer.quantity)
            inbound_movement = StockMovement(
                product_id=transfer.product_id,
                warehouse_id=transfer.to_warehouse_id,
                movement_type=MovementType.TRANSFER_IN,
                quantity=inbound_quantity,
                reference_number=f"TRANSFER-{transfer.id}",
                notes=f"Transfer from warehouse {transfer.from_warehouse_id}: {transfer.notes or ''}",
                created_by=user_id
            )
            
            self.db.add(outbound_movement)
            self.db.add(inbound_movement)
            
            # Update transfer status
            transfer.status = "completed"
            transfer.completed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(transfer)
            
            return transfer
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def cancel_stock_transfer(self, transfer_id: int) -> Optional[StockTransfer]:
        """Cancel a pending stock transfer"""
        transfer = self.db.query(StockTransfer).filter(
            StockTransfer.id == transfer_id
        ).first()
        
        if not transfer:
            return None
        
        if transfer.status != "pending":
            raise ValueError("Only pending transfers can be cancelled")
        
        transfer.status = "cancelled"
        self.db.commit()
        self.db.refresh(transfer)
        
        return transfer
    
    def get_stock_transfers(self, params: PaginationParams) -> Tuple[List[StockTransfer], int]:
        """Get paginated list of stock transfers"""
        query = self.db.query(StockTransfer)
        
        # Apply search filter
        if params.search:
            search_term = f"%{params.search}%"
            query = query.join(Product).filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.sku.ilike(search_term),
                    StockTransfer.transfer_reference.ilike(search_term),
                    StockTransfer.notes.ilike(search_term),
                    StockTransfer.status.ilike(search_term)
                )
            )
        
        # Apply date filters
        if params.created_from_date:
            query = query.filter(StockTransfer.created_at >= params.created_from_date)
        
        if params.created_to_date:
            query = query.filter(StockTransfer.created_at <= params.created_to_date)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if params.sort_by:
            if params.sort_by == "created_asc":
                query = query.order_by(StockTransfer.created_at.asc())
            elif params.sort_by == "created_desc":
                query = query.order_by(StockTransfer.created_at.desc())
        else:
            query = query.order_by(StockTransfer.created_at.desc())
        
        # Apply pagination
        offset = (params.page - 1) * params.page_size
        transfers = query.offset(offset).limit(params.page_size).all()
        
        return transfers, total