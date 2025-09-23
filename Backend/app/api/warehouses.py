from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_database
from app.core.dependencies import get_current_active_user
from app.schemas.schemas import Warehouse, User
from app.models.models import Warehouse as WarehouseModel

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])

@router.get("/", response_model=list[Warehouse])
async def list_warehouses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get list of all active warehouses"""
    warehouses = db.query(WarehouseModel).filter(WarehouseModel.is_active == True).all()
    return [Warehouse.model_validate(warehouse) for warehouse in warehouses]

@router.get("/{warehouse_id}", response_model=Warehouse)
async def get_warehouse(
    warehouse_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get a specific warehouse by ID"""
    warehouse = db.query(WarehouseModel).filter(
        WarehouseModel.id == warehouse_id,
        WarehouseModel.is_active == True
    ).first()
    
    if not warehouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )
    
    return Warehouse.model_validate(warehouse)