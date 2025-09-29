from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models import MovementType

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_admin: bool = False
    created_at: datetime

class User(UserInDB):
    pass

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Warehouse Schemas
class WarehouseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class WarehouseInDB(WarehouseBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class Warehouse(WarehouseInDB):
    pass

# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    unit_price: Optional[Decimal] = Field(None, ge=0)
    unit_of_measure: Optional[str] = Field(None, max_length=20)
    category: Optional[str] = Field(None, max_length=100)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    unit_price: Optional[Decimal] = Field(None, ge=0)
    unit_of_measure: Optional[str] = Field(None, max_length=20)
    category: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class ProductInDB(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

class Product(ProductInDB):
    total_stock: Optional[int] = 0  # Calculated field for total stock across all warehouses
    creator: Optional[User] = None  # User who created the product

class ProductWithStock(Product):
    warehouse_stock: List["WarehouseStock"] = []

# Stock-related schemas
class WarehouseStock(BaseModel):
    warehouse_id: int
    warehouse_name: str
    current_stock: int

# Stock Movement Schemas
class StockMovementBase(BaseModel):
    product_id: int
    warehouse_id: int
    movement_type: MovementType
    quantity: int
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    reference_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class StockMovementCreate(StockMovementBase):
    pass

class StockMovementInDB(StockMovementBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    total_cost: Optional[Decimal] = None
    created_at: datetime
    created_by: Optional[int] = None

class StockMovement(StockMovementInDB):
    product: Optional[Product] = None
    warehouse: Optional[Warehouse] = None
    creator: Optional[User] = None

# Stock Transfer Schemas
class StockTransferBase(BaseModel):
    product_id: int
    from_warehouse_id: int
    to_warehouse_id: int
    quantity: int = Field(..., gt=0)
    transfer_reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class StockTransferCreate(StockTransferBase):
    pass

class StockTransferUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|completed|cancelled)$")
    notes: Optional[str] = None

class StockTransferInDB(StockTransferBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    created_by: Optional[int] = None

class StockTransfer(StockTransferInDB):
    product: Optional[Product] = None
    from_warehouse: Optional[Warehouse] = None
    to_warehouse: Optional[Warehouse] = None
    creator: Optional[User] = None


# Scraped data schemas
class ScrapDataBase(BaseModel):
    product_name: str
    product_description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    rating: Optional[str] = None
    image_url: Optional[str] = None
    product_page_url: Optional[str] = None

class ScrapDataInDB(ScrapDataBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scraped_at: datetime

class ScrapData(ScrapDataInDB):
    pass

# Pagination Schema
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = Field(None, pattern="^(name_asc|name_desc|stock_asc|stock_desc|created_asc|created_desc)$")
    search: Optional[str] = Field(None, max_length=100)
    created_from_date: Optional[datetime] = None
    created_to_date: Optional[datetime] = None

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int

# Response Schemas
class ProductListResponse(BaseModel):
    items: List[Product]
    total: int
    page: int
    page_size: int
    total_pages: int

class StockMovementListResponse(BaseModel):
    items: List[StockMovement]
    total: int
    page: int
    page_size: int
    total_pages: int

class StockTransferListResponse(BaseModel):
    items: List[StockTransfer]
    total: int
    page: int
    page_size: int
    total_pages: int