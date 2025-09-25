from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.models import Product, StockMovement, StockTransfer
from app.schemas.schemas import User

class OwnershipValidator:
    """Helper class to validate data ownership and permissions"""
    
    @staticmethod
    def can_edit_product(db: Session, product_id: int, current_user: User) -> bool:
        """Check if user can edit a product (owner or admin can edit)"""
        # Admin can edit any product
        if current_user.is_admin:
            return True
            
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        return product.created_by == current_user.id
    
    @staticmethod
    def can_edit_stock_movement(db: Session, movement_id: int, current_user: User) -> bool:
        """Check if user can edit a stock movement (owner or admin can edit)"""
        # Admin can edit any stock movement
        if current_user.is_admin:
            return True
            
        movement = db.query(StockMovement).filter(StockMovement.id == movement_id).first()
        if not movement:
            return False
        return movement.created_by == current_user.id
    
    @staticmethod
    def can_edit_stock_transfer(db: Session, transfer_id: int, current_user: User) -> bool:
        """Check if user can edit a stock transfer (owner or admin can edit)"""
        # Admin can edit any stock transfer
        if current_user.is_admin:
            return True
            
        transfer = db.query(StockTransfer).filter(StockTransfer.id == transfer_id).first()
        if not transfer:
            return False
        return transfer.created_by == current_user.id
    
    @staticmethod
    def ensure_product_edit_permission(db: Session, product_id: int, current_user: User):
        """Raise HTTP exception if user cannot edit product"""
        if not OwnershipValidator.can_edit_product(db, product_id, current_user):
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify products that you created"
            )
    
    @staticmethod
    def ensure_stock_movement_edit_permission(db: Session, movement_id: int, current_user: User):
        """Raise HTTP exception if user cannot edit stock movement"""
        if not OwnershipValidator.can_edit_stock_movement(db, movement_id, current_user):
            movement = db.query(StockMovement).filter(StockMovement.id == movement_id).first()
            if not movement:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Stock movement not found"
                )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify stock movements that you created"
            )
    
    @staticmethod
    def ensure_stock_transfer_edit_permission(db: Session, transfer_id: int, current_user: User):
        """Raise HTTP exception if user cannot edit stock transfer"""
        if not OwnershipValidator.can_edit_stock_transfer(db, transfer_id, current_user):
            transfer = db.query(StockTransfer).filter(StockTransfer.id == transfer_id).first()
            if not transfer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Stock transfer not found"
                )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify stock transfers that you created"
            )