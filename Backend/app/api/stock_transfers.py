from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import asyncio
from app.core.database import get_database
from app.core.dependencies import get_current_active_user
from app.core.permissions import OwnershipValidator
from app.services.stock_service import StockService
from app.api.websocket import broadcast_stock_transfer
from app.schemas.schemas import (
    StockTransfer, StockTransferCreate, StockTransferUpdate, StockTransferListResponse,
    PaginationParams, User
)
import math

router = APIRouter(prefix="/stock-transfers", tags=["Stock Transfers"])

@router.post("/", response_model=StockTransfer, status_code=status.HTTP_201_CREATED)
async def create_stock_transfer(
    transfer_data: StockTransferCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Create a stock transfer between warehouses - only for owned products"""
    # Check if user owns the product before allowing stock transfer
    OwnershipValidator.ensure_product_edit_permission(db, transfer_data.product_id, current_user)
    
    stock_service = StockService(db)
    
    try:
        transfer = stock_service.create_stock_transfer(transfer_data, current_user.id)
        transfer_dict = StockTransfer.model_validate(transfer).model_dump()
        
        # INSTANT WebSocket broadcast
        await broadcast_stock_transfer({
            "action": "created",
            "transfer": transfer_dict
        })
        
        return StockTransfer.model_validate(transfer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=StockTransferListResponse)
async def list_stock_transfers(
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
    """Get paginated list of stock transfers"""
    stock_service = StockService(db)
    
    params = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        search=search,
        created_from_date=created_from_date,
        created_to_date=created_to_date
    )
    
    transfers, total = stock_service.get_stock_transfers(params)
    total_pages = math.ceil(total / page_size)
    
    return StockTransferListResponse(
        items=[StockTransfer.model_validate(transfer) for transfer in transfers],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.put("/{transfer_id}/complete", response_model=StockTransfer)
async def complete_stock_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Complete a pending stock transfer - only owner can complete"""
    # Check ownership before allowing completion
    OwnershipValidator.ensure_stock_transfer_edit_permission(db, transfer_id, current_user)
    
    stock_service = StockService(db)
    
    try:
        transfer = stock_service.complete_stock_transfer(transfer_id, current_user.id)
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        transfer_dict = StockTransfer.model_validate(transfer).model_dump()
        
        # INSTANT WebSocket broadcast
        await broadcast_stock_transfer({
            "action": "completed",
            "transfer": transfer_dict
        })
        
        return StockTransfer.model_validate(transfer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{transfer_id}/cancel", response_model=StockTransfer)
async def cancel_stock_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Cancel a pending stock transfer - only owner can cancel"""
    # Check ownership before allowing cancellation
    OwnershipValidator.ensure_stock_transfer_edit_permission(db, transfer_id, current_user)
    
    stock_service = StockService(db)
    
    try:
        transfer = stock_service.cancel_stock_transfer(transfer_id)
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        transfer_dict = StockTransfer.model_validate(transfer).model_dump()
        
        # INSTANT WebSocket broadcast
        await broadcast_stock_transfer({
            "action": "cancelled",
            "transfer": transfer_dict
        })
        
        return StockTransfer.model_validate(transfer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )