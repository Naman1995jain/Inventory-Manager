// User Types
export interface User {
  id: number;
  email: string;
  created_at: string;
  is_admin?: boolean;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

// Auth Types
export interface Token {
  access_token: string;
  token_type: string;
}

// Product Types
export interface Product {
  id: number;
  name: string;
  sku: string;
  description?: string;
  unit_price?: number;
  unit_of_measure?: string;
  category?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: number;
  total_stock?: number;
  creator?: User;
}

export interface ProductCreate {
  name: string;
  sku: string;
  description?: string;
  unit_price?: number;
  unit_of_measure?: string;
  category?: string;
}

export interface ProductUpdate {
  name?: string;
  sku?: string;
  description?: string;
  unit_price?: number;
  unit_of_measure?: string;
  category?: string;
  is_active?: boolean;
}

export interface ProductWithStock extends Product {
  warehouse_stock: WarehouseStock[];
}

export interface WarehouseStock {
  warehouse_id: number;
  warehouse_name: string;
  current_stock: number;
}

// Warehouse Types
export interface Warehouse {
  id: number;
  name: string;
  location?: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Stock Movement Types
export enum MovementType {
  PURCHASE = 'purchase',
  SALE = 'sale',
  ADJUSTMENT = 'adjustment',
  DAMAGED = 'damaged',
  RETURN = 'return',
  TRANSFER_IN = 'transfer_in',
  TRANSFER_OUT = 'transfer_out'
}

export interface StockMovement {
  id: number;
  product_id: number;
  warehouse_id: number;
  movement_type: MovementType;
  quantity: number;
  unit_cost?: number;
  total_cost?: number;
  reference_number?: string;
  notes?: string;
  created_at: string;
  created_by?: number;
  product?: Product;
  warehouse?: Warehouse;
  creator?: User;
  // Additional fields from purchase-sale endpoint
  product_name?: string;
  warehouse_name?: string;
}

export interface StockMovementCreate {
  product_id: number;
  warehouse_id: number;
  movement_type: MovementType;
  quantity: number;
  unit_cost?: number;
  reference_number?: string;
  notes?: string;
}

// Stock Transfer Types
export interface StockTransfer {
  id: number;
  product_id: number;
  from_warehouse_id: number;
  to_warehouse_id: number;
  quantity: number;
  transfer_reference?: string;
  notes?: string;
  status: 'pending' | 'completed' | 'cancelled';
  created_at: string;
  completed_at?: string;
  created_by?: number;
  product?: Product;
  from_warehouse?: Warehouse;
  to_warehouse?: Warehouse;
  creator?: User;
}

export interface StockTransferCreate {
  product_id: number;
  from_warehouse_id: number;
  to_warehouse_id: number;
  quantity: number;
  transfer_reference?: string;
  notes?: string;
}

// Pagination Types
export interface PaginationParams {
  page: number;
  page_size: number;
  sort_by?: string;
  search?: string;
  created_from_date?: string;
  created_to_date?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// API Response Types
export type ProductListResponse = PaginatedResponse<Product>;
export type StockMovementListResponse = PaginatedResponse<StockMovement>;
export type StockTransferListResponse = PaginatedResponse<StockTransfer>;