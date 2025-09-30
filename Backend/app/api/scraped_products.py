from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime
from app.core.database import get_database
from app.schemas.schemas import ScrapData, ScrapDataInDB, PaginatedResponse
from app.models.models import ScrapData as ScrapDataModel

router = APIRouter(prefix="/scraped-products", tags=["Scraped"])


@router.get("/search", response_model=list[ScrapData])
async def search_scraped_products(
    query: str = Query(None, description="Search query for product name, description, or category"),
    db: Session = Depends(get_database),
):
    """Search through scraped products - returns all matching results"""
    base_query = db.query(ScrapDataModel)
    
    # Apply search filter if query is provided
    if query:
        search_filter = or_(
            ScrapDataModel.product_name.ilike(f"%{query}%"),
            ScrapDataModel.product_description.ilike(f"%{query}%"),
            ScrapDataModel.category.ilike(f"%{query}%")
        )
        base_query = base_query.filter(search_filter)
    
    # Get all matching items
    items = base_query.order_by(ScrapDataModel.scraped_at.desc()).all()
    
    return [ScrapData.model_validate(item) for item in items]

@router.get("/", response_model=list[ScrapData])
async def list_scraped_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_database),
):
    """Return paginated scraped products"""
    offset = (page - 1) * page_size
    items = db.query(ScrapDataModel).order_by(ScrapDataModel.scraped_at.desc()).offset(offset).limit(page_size).all()
    return [ScrapData.model_validate(item) for item in items]
