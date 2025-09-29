from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class MovementType(str, enum.Enum):
    """Enum for stock movement types"""
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    DAMAGED = "damaged"
    RETURN = "return"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="creator")

class Warehouse(Base):
    """Warehouse model for storing location information"""
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    location = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    stock_movements = relationship("StockMovement", back_populates="warehouse")
    stock_transfers_from = relationship("StockTransfer", foreign_keys="StockTransfer.from_warehouse_id", back_populates="from_warehouse")
    stock_transfers_to = relationship("StockTransfer", foreign_keys="StockTransfer.to_warehouse_id", back_populates="to_warehouse")

class Product(Base):
    """Product model for inventory items"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=True)
    unit_of_measure = Column(String(20), nullable=True)  # e.g., 'piece', 'kg', 'liter'
    category = Column(String(100), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="products", foreign_keys=[created_by])
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    creator = relationship("User")
    stock_movements = relationship("StockMovement", back_populates="product")
    stock_transfers = relationship("StockTransfer", back_populates="product")

class StockMovement(Base):
    """Stock movement model for tracking inventory changes"""
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    movement_type = Column(Enum(MovementType), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)  # Positive for inbound, negative for outbound
    unit_cost = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(10, 2), nullable=True)
    reference_number = Column(String(100), nullable=True, index=True)  # PO number, invoice number, etc.
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="stock_movements")
    warehouse = relationship("Warehouse", back_populates="stock_movements")
    creator = relationship("User")

class StockTransfer(Base):
    """Stock transfer model for moving inventory between warehouses"""
    __tablename__ = "stock_transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    from_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    to_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    transfer_reference = Column(String(100), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="stock_transfers")
    from_warehouse = relationship("Warehouse", foreign_keys=[from_warehouse_id], back_populates="stock_transfers_from")
    to_warehouse = relationship("Warehouse", foreign_keys=[to_warehouse_id], back_populates="stock_transfers_to")
    creator = relationship("User")


class ScrapData(Base):
    """Model to store scraped product data from external sites"""
    __tablename__ = "scrapdata"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(300), nullable=False, index=True)
    product_description = Column(Text, nullable=True)
    category = Column(String(150), nullable=True, index=True)
    price = Column(Numeric(10, 2), nullable=True)
    rating = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)
    product_page_url = Column(String(1000), nullable=True, unique=False)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())