from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import Optional, List, Tuple
from datetime import datetime
from app.models import Product, StockMovement, Warehouse
from app.schemas.schemas import ProductCreate, ProductUpdate, PaginationParams, WarehouseStock

class ProductService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(self, product_data: ProductCreate, user_id: int) -> Product:
        """Create a new product"""
        # Check if SKU already exists
        existing_product = self.db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing_product:
            raise ValueError("Product with this SKU already exists")
        
        db_product = Product(
            **product_data.model_dump(),
            created_by=user_id
        )
        
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Get a product by ID"""
        return self.db.query(Product).filter(
            and_(Product.id == product_id, Product.is_active == True)
        ).first()
    
    def get_product_with_stock(self, product_id: int) -> Optional[dict]:
        """Get a product with its stock distribution across warehouses"""
        product = self.get_product(product_id)
        if not product:
            return None
        
        # Calculate stock per warehouse
        warehouse_stock = self.db.query(
            Warehouse.id,
            Warehouse.name,
            func.coalesce(func.sum(StockMovement.quantity), 0).label("current_stock")
        ).outerjoin(
            StockMovement,
            and_(
                StockMovement.warehouse_id == Warehouse.id,
                StockMovement.product_id == product_id
            )
        ).filter(Warehouse.is_active == True).group_by(
            Warehouse.id, Warehouse.name
        ).all()
        
        # Calculate total stock
        total_stock = sum(stock.current_stock for stock in warehouse_stock)
        
        return {
            "product": product,
            "total_stock": total_stock,
            "warehouse_stock": [
                WarehouseStock(
                    warehouse_id=stock.id,
                    warehouse_name=stock.name,
                    current_stock=stock.current_stock
                ) for stock in warehouse_stock
            ]
        }
    
    def get_products(self, params: PaginationParams, owner_id: Optional[int] = None) -> Tuple[List[Product], int]:
        """Get paginated list of products with stock information"""
        query = self.db.query(Product).options(
            joinedload(Product.creator)
        ).filter(Product.is_active == True)
        
        # Filter by owner if specified
        if owner_id is not None:
            query = query.filter(Product.created_by == owner_id)
        
        # Apply search filter
        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.category.ilike(search_term)
                )
            )
        
        # Apply date filters
        if params.created_from_date:
            query = query.filter(Product.created_at >= params.created_from_date)
        
        if params.created_to_date:
            query = query.filter(Product.created_at <= params.created_to_date)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if params.sort_by:
            if params.sort_by == "name_asc":
                query = query.order_by(Product.name.asc())
            elif params.sort_by == "name_desc":
                query = query.order_by(Product.name.desc())
            elif params.sort_by == "created_asc":
                query = query.order_by(Product.created_at.asc())
            elif params.sort_by == "created_desc":
                query = query.order_by(Product.created_at.desc())
            # Stock sorting will be handled after fetching products
        else:
            query = query.order_by(Product.created_at.desc())
        
        # Apply pagination
        offset = (params.page - 1) * params.page_size
        products = query.offset(offset).limit(params.page_size).all()
        
        # Add stock information to each product
        products_with_stock = []
        for product in products:
            # Calculate total stock for this product
            total_stock = self.db.query(
                func.coalesce(func.sum(StockMovement.quantity), 0)
            ).filter(StockMovement.product_id == product.id).scalar() or 0
            
            # Add total_stock as an attribute
            product.total_stock = total_stock
            products_with_stock.append(product)
        
        # Handle stock-based sorting
        if params.sort_by in ["stock_asc", "stock_desc"]:
            reverse = params.sort_by == "stock_desc"
            products_with_stock.sort(key=lambda p: p.total_stock, reverse=reverse)
        
        return products_with_stock, total
    
    def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update a product"""
        product = self.get_product(product_id)
        if not product:
            return None
        
        # Check SKU uniqueness if being updated
        if product_data.sku and product_data.sku != product.sku:
            existing_product = self.db.query(Product).filter(
                and_(Product.sku == product_data.sku, Product.id != product_id)
            ).first()
            if existing_product:
                raise ValueError("Product with this SKU already exists")
        
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def delete_product(self, product_id: int) -> bool:
        """Soft delete a product"""
        product = self.get_product(product_id)
        if not product:
            return False
        
        product.is_active = False
        self.db.commit()
        return True