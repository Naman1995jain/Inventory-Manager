from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_database
from app.schemas.schemas import ScrapData, ScrapDataInDB
from app.models.models import ScrapData as ScrapDataModel

router = APIRouter(prefix="/scraped-products", tags=["Scraped"])


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
