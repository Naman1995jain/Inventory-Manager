from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_database
from app.core.dependencies import get_current_active_user
from app.core.permissions import OwnershipValidator
from app.services.stock_service import StockService
from app.schemas.schemas import (
    StockMovement, StockMovementCreate, StockMovementListResponse,
    PaginationParams, User
)
from typing import List
import math

router = APIRouter(prefix="/stock-movements", tags=["Stock Movements"])

@router.get("/purchase-sale", response_model=StockMovementListResponse)
async def list_purchase_sale_movements(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Fetch all purchase and sale movements with their quantity and unit cost
    """
    stock_service = StockService(db)
    
    movements = stock_service.get_purchase_sale_movements_all()
    
    # Convert SQLAlchemy objects to Pydantic models
    movement_list = [
        {
            **StockMovement.model_validate(movement[0]).model_dump(),
            "product_name": movement[1],
            "warehouse_name": movement[2]
        }
        for movement in movements
    ]
    
    return {
        "items": movement_list,
        "total": len(movement_list),
        "page": 1,
        "page_size": len(movement_list),
        "total_pages": 1
    }

@router.post("/", response_model=StockMovement, status_code=status.HTTP_201_CREATED)
async def create_stock_movement(
    movement_data: StockMovementCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Record a stock movement (purchase, sale, adjustment, etc.) - only for owned products"""
    # Check if user owns the product before allowing stock movement
    OwnershipValidator.ensure_product_edit_permission(db, movement_data.product_id, current_user)
    
    stock_service = StockService(db)
    
    try:
        movement = stock_service.create_stock_movement(movement_data, current_user.id)
        return StockMovement.model_validate(movement)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=StockMovementListResponse)
async def list_stock_movements(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(
        None, 
        pattern="^(created_asc|created_desc)$",
        description="Sort by field and direction"
    ),
    search: Optional[str] = Query(None, max_length=100, description="Search term"),
    created_from_date: Optional[datetime] = Query(None, description="Filter from date"),
    created_to_date: Optional[datetime] = Query(None, description="Filter to date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get paginated list of stock movements"""
    stock_service = StockService(db)
    
    params = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        search=search,
        created_from_date=created_from_date,
        created_to_date=created_to_date
    )
    
    movements, total = stock_service.get_stock_movements(params)
    total_pages = math.ceil(total / page_size)
    
    return StockMovementListResponse(
        items=[StockMovement.model_validate(movement) for movement in movements],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )