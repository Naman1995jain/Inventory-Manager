from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import asyncio
from app.core.database import get_database
from app.core.dependencies import get_current_active_user
from app.core.permissions import OwnershipValidator
from app.services.product_service import ProductService
from app.api.websocket import broadcast_product_update, broadcast_dashboard_stats
from app.schemas.schemas import (
    Product, ProductCreate, ProductUpdate, ProductWithStock,
    ProductListResponse, PaginationParams, User
)
import math

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Create a new product"""
    product_service = ProductService(db)
    
    try:
        product = product_service.create_product(product_data, current_user.id)
        product_dict = Product.model_validate(product).model_dump()
        
        # INSTANT WebSocket broadcast - send immediately after DB save
        await broadcast_product_update({
            "action": "created",
            "product": product_dict
        })
        
        # Update dashboard stats instantly
        params = PaginationParams(page=1, page_size=1)
        _, total = product_service.get_products(params)
        await broadcast_dashboard_stats({
            "total_products": total
        })
        
        return Product.model_validate(product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(
        None, 
        pattern="^(name_asc|name_desc|stock_asc|stock_desc|created_asc|created_desc)$",
        description="Sort by field and direction"
    ),
    search: Optional[str] = Query(None, max_length=100, description="Search term"),
    created_from_date: Optional[datetime] = Query(None, description="Filter from date"),
    created_to_date: Optional[datetime] = Query(None, description="Filter to date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get paginated list of products with stock information"""
    product_service = ProductService(db)
    
    params = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        search=search,
        created_from_date=created_from_date,
        created_to_date=created_to_date
    )
    
    products, total = product_service.get_products(params)
    total_pages = math.ceil(total / page_size)
    
    return ProductListResponse(
        items=[Product.model_validate(product) for product in products],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/owned", response_model=ProductListResponse)
async def list_owned_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(
        None, 
        pattern="^(name_asc|name_desc|stock_asc|stock_desc|created_asc|created_desc)$",
        description="Sort by field and direction"
    ),
    search: Optional[str] = Query(None, max_length=100, description="Search term"),
    created_from_date: Optional[datetime] = Query(None, description="Filter from date"),
    created_to_date: Optional[datetime] = Query(None, description="Filter to date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get paginated list of products owned by current user"""
    product_service = ProductService(db)
    
    params = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        search=search,
        created_from_date=created_from_date,
        created_to_date=created_to_date
    )
    
    products, total = product_service.get_products(params, owner_id=current_user.id)
    total_pages = math.ceil(total / page_size)
    
    return ProductListResponse(
        items=[Product.model_validate(product) for product in products],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/deleted", response_model=ProductListResponse)
async def list_deleted_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(
        None, 
        pattern="^(name_asc|name_desc|stock_asc|stock_desc|created_asc|created_desc)$",
        description="Sort by field and direction"
    ),
    search: Optional[str] = Query(None, max_length=100, description="Search term"),
    created_from_date: Optional[datetime] = Query(None, description="Filter from date"),
    created_to_date: Optional[datetime] = Query(None, description="Filter to date"),
    owner_id: Optional[int] = Query(None, description="Filter by owner id"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get paginated list of soft-deleted products. Admins or owners can fetch."""
    product_service = ProductService(db)
    
    params = PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        search=search,
        created_from_date=created_from_date,
        created_to_date=created_to_date
    )
    
    # If owner_id specified, filter by owner; otherwise list all deleted products
    products, total = product_service.get_products(params, owner_id=owner_id, include_deleted=True)
    total_pages = math.ceil(total / page_size)
    
    return ProductListResponse(
        items=[Product.model_validate(product) for product in products],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{product_id}", response_model=ProductWithStock)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get product details with stock distribution"""
    product_service = ProductService(db)
    
    product_data = product_service.get_product_with_stock(product_id)
    if not product_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product_dict = Product.model_validate(product_data["product"]).model_dump()
    product_dict["total_stock"] = product_data["total_stock"]
    product_dict["warehouse_stock"] = [
        stock.model_dump() for stock in product_data["warehouse_stock"]
    ]
    
    return ProductWithStock(**product_dict)

@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Update product metadata - only owner can update"""
    # Check ownership before allowing update
    OwnershipValidator.ensure_product_edit_permission(db, product_id, current_user)
    
    product_service = ProductService(db)
    
    try:
        product = product_service.update_product(product_id, product_data)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product_dict = Product.model_validate(product).model_dump()
        
        # INSTANT WebSocket broadcast
        await broadcast_product_update({
            "action": "updated",
            "product": product_dict
        })
        
        return Product.model_validate(product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Soft delete a product - only owner can delete"""
    # Check ownership before allowing delete
    OwnershipValidator.ensure_product_edit_permission(db, product_id, current_user)
    
    product_service = ProductService(db)
    
    success = product_service.delete_product(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # INSTANT WebSocket broadcast
    await broadcast_product_update({
        "action": "deleted",
        "product_id": product_id
    })
    
    # Update dashboard stats instantly
    params = PaginationParams(page=1, page_size=1)
    _, total = product_service.get_products(params)
    await broadcast_dashboard_stats({
        "total_products": total
    })